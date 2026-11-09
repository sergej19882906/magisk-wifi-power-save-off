# Magisk Wi-Fi Power Save Off

[Русская версия](README.ru.md)

A Magisk module that disables Linux Wi-Fi power saving with `iw` and checks the active Wi-Fi interface every 30 seconds. If the driver or firmware enables power saving again after reconnecting or restarting, the module turns it off again.

This can help Android TV devices whose Wi-Fi becomes unreachable or drops during idle or standby. It does not replace correct router configuration and cannot fix every vendor driver or firmware issue.

## Important warning

Disabling Wi-Fi power saving can increase standby power consumption and device temperature. It may reduce battery life on battery-powered devices. This module is intended primarily for mains-powered Android TV hardware.

The module runs a small shell loop that wakes every 30 seconds. It does not modify `/system`, use Zygisk, install native binaries, or access the network.

## Requirements

- A rooted Android device with Magisk.
- `/system/bin/iw` with `get power_save` and `set power_save` support.
- A driver that exposes power-save control through nl80211.

Tested on:

- Xiaomi `MiTV-AFKR0`
- Android 14 (SDK 34)
- Magisk 31.1
- MediaTek `mt7663_usb`, interface `wlan0`
- SELinux enforcing

Other devices and drivers may work, but are not currently verified.

## Installation

1. Download the installable ZIP and `SHA256SUMS` from the latest [GitHub release](https://github.com/sergej19882906/magisk-wifi-power-save-off/releases/latest).
2. Verify the ZIP checksum.
3. Open Magisk, select **Modules → Install from storage**, and choose the downloaded ZIP.
4. Reboot the device.

Do not install GitHub's automatically generated **Source code** archive. Use the ZIP attached to the release.

## Verification

After rebooting, run:

```sh
su -c 'iw dev wlan0 get power_save'
```

Expected output:

```text
Power save: off
```

If the Wi-Fi interface has another name, find it with:

```sh
getprop wifi.active.interface
```

Diagnostic log:

```sh
su -c 'cat /data/adb/modules/wifi_power_save_off/service.log'
```

## How it works

- At installation, the module records the current `power_save` state when possible.
- At boot, `service.sh` discovers the active interface from Android properties and falls back to `wlan0`.
- Every 30 seconds it checks the driver's state and changes it to `off` when necessary.
- When disabled or marked for removal, it restores the state saved during installation.

## Disable and uninstall

- **Disable:** Disable the module in Magisk. The running loop detects the disable marker, restores the saved state, and exits; reboot to complete the normal Magisk disable flow.
- **Uninstall:** Remove the module through Magisk. `uninstall.sh` stops the loop and restores the saved state on a best-effort basis. Reboot afterward.

Manual rollback:

```sh
su -c 'iw dev wlan0 set power_save on'
```

## Troubleshooting

### `iw` reports `command failed` or does not show a state

The driver may not support nl80211 power-save control, the interface name may differ, or vendor SELinux policy may block the operation. Remove or disable the module.

### Wi-Fi still disconnects

The cause may be deep suspend, a vendor service unloading the USB Wi-Fi driver, access-point behavior, DHCP expiration, RF interference, or firmware bugs. This module only controls the driver's Wi-Fi power-save flag. A separate kernel wakelock may also be needed if the device enters deep suspend.

### Increased temperature or power use

Disable or uninstall the module and reboot. Increased power consumption is an expected possible effect.

## Build from source

Python 3 is the only build dependency:

```sh
python scripts/build.py
python scripts/verify.py
```

Outputs:

```text
dist/magisk-wifi-power-save-off-vX.Y.Z.zip
dist/SHA256SUMS
```

The build is byte-for-byte reproducible.

## License

[MIT](LICENSE) © 2026 sergej19882906
