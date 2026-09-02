#!/bin/bash
# Stubs bluetoothctl and pactl, so this runs with no adapter and no daemon.
set -u
cd "$(dirname "$0")"

stub=$(mktemp -d)
trap 'rm -f "$stub"/*; rmdir "$stub"' EXIT
PATH="$stub:$PATH"
fail=0

check() { # name, expected-substring, actual
    if [[ "$3" == *"$2"* ]]; then
        echo "ok   $1"
    else
        echo "FAIL $1: expected '$2' in '$3'"
        fail=1
    fi
}

mkstub() { printf '%s\n' "$2" > "$stub/$1"; chmod +x "$stub/$1"; }

# No paired audio device.
mkstub bluetoothctl '#!/bin/sh
exit 0'
mkstub pactl '#!/bin/sh
exit 0'
check "no headphones" "no paired headphones" "$(./bhctl 2>&1)"
./bhctl >/dev/null 2>&1; check "no headphones exits 1" "1" "$?"

# A paired, connected headset.
mkstub bluetoothctl '#!/bin/bash
case "$1 $2" in
  "devices Paired") echo "Device AA:BB:CC:DD:EE:FF Cans" ;;
  "info AA:BB:CC:DD:EE:FF")
      printf "\tName: Cans\n\tConnected: ${CONN:-yes}\n\tBattery Percentage: 0x46 (70)\n\tUUID: Audio Sink\n" ;;
  "connect "*) [ -n "${NOCONNECT:-}" ] && exit 1 || exit 0 ;;
  *) exit 0 ;;
esac'
mkstub pactl '#!/bin/bash
case "$1 $2 $3" in
  "list short cards") echo "1	bluez_card.AA_BB_CC_DD_EE_FF	module" ;;
  "list cards ") printf "bluez_card.AA_BB_CC_DD_EE_FF\n\tActive Profile: ${PROF:-a2dp-sink}\n" ;;
  "set-card-profile "*) echo "set $3" ;;
esac'

check "status connected"  "Cans  connected  70%  hifi (LDAC)" "$(./bhctl)"
check "status mic mode"   "mic (narrowband)"      "$(PROF=headset-head-unit ./bhctl)"
check "status off"        "Cans  off"             "$(CONN=no ./bhctl)"
check "hifi sets a2dp"    "set a2dp-sink"         "$(./bhctl hifi)"
check "mic sets hfp"      "set headset-head-unit" "$(./bhctl mic)"
check "off is quiet"      ""                      "$(./bhctl off)"
check "connect failure"   "power-cycle"           "$(CONN=no NOCONNECT=1 ./bhctl hifi 2>&1)"
check "help"              "bluetooth headphones control" "$(./bhctl -h)"
check "unknown command"   "unknown command: zz"   "$(./bhctl zz 2>&1)"
./bhctl zz >/dev/null 2>&1; check "unknown exits 1" "1" "$?"

# Card never appears: must fail loudly, not hang.
mkstub pactl '#!/bin/sh
exit 0'
out=$(timeout 20 ./bhctl hifi 2>&1); check "no card fails loud" "is wireplumber running?" "$out"

[ $fail -eq 0 ] && echo "all passed" || echo "FAILURES"
exit $fail
