#!/system/bin/sh

MODDIR=${0%/*}
LOG_FILE="$MODDIR/service.log"
PID_FILE="$MODDIR/service.pid"
STATE_FILE="$MODDIR/.previous_power_save"
IW=/system/bin/iw
GETPROP=/system/bin/getprop
SLEEP=/system/bin/sleep

cleanup() {
  rm -f "$PID_FILE"
}

restore_power_save() {
  interface=$($GETPROP wifi.active.interface)
  [ -n "$interface" ] || interface=$($GETPROP wifi.interface)
  [ -n "$interface" ] || interface=wlan0
  previous=$(/system/bin/cat "$STATE_FILE" 2>/dev/null)

  if [ -d "/sys/class/net/$interface" ]; then
    case "$previous" in
      on|off) $IW dev "$interface" set power_save "$previous" 2>/dev/null || true ;;
    esac
  fi
}

trap cleanup EXIT INT TERM
echo $$ > "$PID_FILE"
exec > "$LOG_FILE" 2>&1
echo "start: $(date)"
echo "context: $(id)"

last_interface=
last_state=

while true; do
  if [ -f "$MODDIR/disable" ] || [ -f "$MODDIR/remove" ]; then
    restore_power_save
    echo "$(date): module disabled or marked for removal"
    exit 0
  fi

  interface=$($GETPROP wifi.active.interface)
  [ -n "$interface" ] || interface=$($GETPROP wifi.interface)
  [ -n "$interface" ] || interface=wlan0

  if [ -d "/sys/class/net/$interface" ]; then
    state=$($IW dev "$interface" get power_save 2>/dev/null)

    if [ ! -f "$STATE_FILE" ]; then
      case "$state" in
        "Power save: on") echo on > "$STATE_FILE" ;;
        "Power save: off") echo off > "$STATE_FILE" ;;
      esac
    fi

    if [ "$state" != "Power save: off" ]; then
      if $IW dev "$interface" set power_save off; then
        state=$($IW dev "$interface" get power_save 2>/dev/null)
        echo "$(date): $interface: $state"
      else
        echo "$(date): error: unable to disable power save on $interface"
      fi
    elif [ "$interface" != "$last_interface" ] || [ "$state" != "$last_state" ]; then
      echo "$(date): $interface: $state"
    fi

    last_interface=$interface
    last_state=$state
  fi

  $SLEEP 30
done
