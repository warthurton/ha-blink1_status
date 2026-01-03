# Blink(1) Status Light Integration

A Home Assistant custom component for controlling Blink(1) USB LED status lights.

**Forked from**: https://github.com/tnagels/ha-blink1_status

## Features

- ✅ Full color control (Hue/Saturation)
- ✅ Brightness control (0-255)
- ✅ Modern ColorMode implementation
- ✅ Compatible with Home Assistant 2025.12+
- ✅ Future-proof (no deprecated APIs)
- ✅ HACS compatible

## Compatibility

**Home Assistant Version**: 2021.12 or newer (tested with 2025.12)

This integration is fully compatible with current and future Home Assistant versions:
- Uses modern `ColorMode.HS` implementation (required since 2025.3)
- Includes `integration_type` and `iot_class` in manifest (future requirements)
- No deprecated APIs or patterns
- Properly implements async operations for all I/O

**Version**: 0.3.0


### Installation

Copy this folder to `<config_dir>/custom_components/blink1/`. Thanks to the work of Qu3uk you can now also add this repo to HACS for easy installation.


Add the following entry in your `configuration.yaml`:

```yaml
light:
  - platform: blink1_status 
```

### Remarks
- Use at your own risk. This is far from complete, but for me it works.
- Feel free to do anything with the code, for my work there is no license attached.
