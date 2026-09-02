# bhctl

Bluetooth headphones from the terminal — **three words, no GUI.**

`bluetoothctl` handles the radio link, `pactl` handles where audio goes, and
neither knows about the other. Connecting headphones means driving both, with
a hard constraint on top: Bluetooth carries either high-quality playback *or*
the microphone, never both. `bhctl` collapses that into three commands and one
status line.

```
$ bhctl
WH-1000XM5  connected  70%  hifi (LDAC)
```

## ELI13

Your headphones can do two jobs, but only one at a time. Playing music, they
get a fat pipe and sound great — and the microphone is switched off entirely.
The moment something wants the mic, the pipe shrinks to about a sixth and
everything sounds like a phone call. That's Bluetooth itself, not your laptop:
your phone does exactly the same thing, it just never tells you.

So there are really three states — good sound, working mic, or disconnected —
and `bhctl` gives each one a word.

## Install

```
make install            # → ~/.local/bin/bhctl
make test               # stubs the system tools; no adapter needed
```

Needs `bluez` (the `bluetoothctl` command) and PipeWire with WirePlumber.

## Use

```
bhctl            state: name, connection, battery, current mode
bhctl hifi       connect, A2DP playback (LDAC/AAC), mic dead
bhctl mic        connect, headset mic live, playback narrowband
bhctl off        disconnect, audio back to the laptop speakers
bhctl -h         help
```

Pair the headphones once with `bluetoothctl` (`scan on`, `pair <mac>`,
`trust <mac>`). After that `bhctl` finds them by itself — it takes the first
paired device advertising an audio sink, so there is no MAC to configure.

## You will rarely type hifi or mic

WirePlumber switches the profile on its own: a call app opens the microphone,
the card flips to HFP, and it flips back to A2DP when the app lets go. Being
`trust`ed, the headphones also reconnect and grab the default sink whenever you
power them on.

`hifi` and `mic` are for the cases that escape it — an app that opens the mic
without asking WirePlumber, or one that exits badly and leaves the card stuck
in narrowband. `bhctl` on its own tells you which state you are actually in,
which is usually the whole question.

## Limits

- **One pair of headphones.** First paired audio sink wins. Two pairs, and it
  picks whichever `bluetoothctl` lists first.
- **`hifi` and `off` are not symmetric.** Disconnecting always works;
  reconnecting can fail with `br-connection-page-timeout`, because a headset in
  standby stops answering. Power-cycle it — no laptop-side fix exists.
- **Codec is not chosen here.** A2DP picks the best profile the card offers
  (LDAC on Sony gear); the bitrate inside LDAC then floats with RF conditions
  and nothing reports that. `pw-top` shows what the sink is really doing.
