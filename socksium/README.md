# socksium

Chromium on a throwaway profile through a SOCKS5 proxy on 127.0.0.1.

```
socksium                       # browse through port 1080
socksium -p 9050 example.com   # other port, open a url
```

- The script deletes the profile when Chromium exits.
- Chromium sends DNS lookups through the proxy, not to the local resolver.
- WebRTC sends no UDP outside the proxy.
- With no proxy on the port, the script stops and prints the ssh command.

Arguments after `-p port` go to Chromium: a url or a Chromium flag.

## Open the SOCKS tunnel with ssh

`ssh -D` starts a SOCKS5 proxy on a local port. The proxy sends each
connection out from the remote host.

```
ssh -D 1080 -N -f user@somehost   # start the proxy in the background
socksium                          # browse as somehost
```

- `-D 1080` listens on 127.0.0.1:1080.
- `-N` runs no remote command.
- `-f` puts ssh in the background after login.

Leave out `-f` to keep the tunnel in the terminal; Ctrl-C closes it.

## Install

Needs `chromium` on `PATH`.

```
make install            # → ~/.local/bin/socksium
```
