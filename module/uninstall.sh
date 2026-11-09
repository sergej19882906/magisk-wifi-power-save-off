#!/system/bin/sh

MODDIR=${0%/*}
PID_FILE="$MODDIR/service.pid"
STATE_FILE="$MODDIR/.previous_power_save"
IW=/system/bin/iw
GETPROP=/system/bin/getprop

: > "$MODDIR/disable"
pid=$(/system/bin/cat "$PID_FILE" 2>/dev/null)
case "$pid" in
  *[!0-9]*|'') ;;
  *) /system/bin/kill "$pid" 2>/dev/null || true ;;
esac
/system/bin/sleep 1

interface=$($GETPROP wifi.active.interface)
[ -n "$interface" ] || interface=$($GETPROP wifi.interface)
[ -n "$interface" ] || interface=wlan0
previous=$(/system/bin/cat "$STATE_FILE" 2>/dev/null)

if [ -d "/sys/class/net/$interface" ]; then
  case "$previous" in
    on|off) $IW dev "$interface" set power_save "$previous" 2>/dev/null || true ;;
  esac
fi
