#!/system/bin/sh

IW=/system/bin/iw
GETPROP=/system/bin/getprop
STATE_FILE="$MODPATH/.previous_power_save"
OLD_STATE=/data/adb/modules/wifi_power_save_off/.previous_power_save

set_perm "$MODPATH/service.sh" 0 0 0755
set_perm "$MODPATH/uninstall.sh" 0 0 0755

if [ -f "$OLD_STATE" ]; then
  cp -af "$OLD_STATE" "$STATE_FILE"
else
  interface=$($GETPROP wifi.active.interface)
  [ -n "$interface" ] || interface=$($GETPROP wifi.interface)
  [ -n "$interface" ] || interface=wlan0
  state=$($IW dev "$interface" get power_save 2>/dev/null)

  case "$state" in
    "Power save: on") echo on > "$STATE_FILE" ;;
    "Power save: off") echo off > "$STATE_FILE" ;;
  esac
fi

[ -f "$STATE_FILE" ] && set_perm "$STATE_FILE" 0 0 0600
