# Security Policy

## Supported versions

Only the latest GitHub release is supported with security fixes.

## Reporting a vulnerability

Please report security issues privately through [GitHub Security Advisories](https://github.com/sergej19882906/magisk-wifi-power-save-off/security/advisories/new). Do not attach device identifiers, Wi-Fi credentials, private keys, proprietary firmware images, or unredacted system dumps.

Include the module version, Android version, Magisk version, Wi-Fi driver, interface name, and minimum reproduction steps.

## Scope

The module runs as root during Magisk's late-start service stage, discovers an interface name from Android properties, and invokes `/system/bin/iw`. It does not use the network, Zygisk, bundled executables, broad SELinux policy changes, or `/system` overlays.

Unexpected arbitrary command execution, unsafe interface-name handling, privilege escalation, or failure to restore the saved state during normal removal is in scope. Increased energy consumption after disabling Wi-Fi power saving is expected behavior.
