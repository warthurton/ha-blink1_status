# GitHub Copilot Instructions

## Project Overview

This is a Home Assistant custom component that integrates Blink(1) USB LED status lights. The integration allows users to control Blink(1) devices through Home Assistant's light entity platform.

**Repository**: Fork of https://github.com/tnagels/ha-blink1_status
**Updated Feature**: Modern ColorMode implementation compatible with current Home Assistant versions

## Project Structure

```
ha-blink1_status/
├── custom_components/
│   └── blink1_status/
│       ├── __init__.py          # Minimal integration initialization
│       ├── light.py             # Main light entity implementation
│       └── manifest.json        # Integration metadata and dependencies
├── README.md                    # User-facing documentation
└── hacs.json                    # HACS integration metadata
```

## Key Files and Their Purpose

### `custom_components/blink1_status/light.py`
The main implementation file containing:
- `async_setup_platform()`: Platform setup function
- `blink1_status` class: LightEntity implementation for Blink(1) device
- Color mode support using `ColorMode.HS` (Hue/Saturation)
- Async methods for turning light on/off with color and brightness control

### `custom_components/blink1_status/manifest.json`
Integration metadata:
- Domain: `blink1_status`
- Dependency: `blink1` Python package
- Version: 0.3.0
- Integration Type: `device` (single device, not a hub)
- IoT Class: `assumed_state` (no device read-back)

## Compatibility & Compliance

**Home Assistant Versions**: 2021.12+ (tested with 2025.12)

**Compliance Status**: ✅ Fully compliant with 2025.12 requirements and future-proof

Key compliance features:
- ✅ `ColorMode.HS` properly implemented (mandatory since 2025.3)
- ✅ `supported_color_modes` and `color_mode` properties (required)
- ✅ `integration_type: device` in manifest (will be mandatory)
- ✅ `iot_class: assumed_state` in manifest (recommended)
- ✅ `unique_id` property for entity registry
- ✅ Error handling in setup and operations
- ✅ No deprecated APIs used

## Technical Guidelines

### Home Assistant Integration Standards

1. **Platform Type**: This is a light platform integration
2. **Color Mode**: Uses `ColorMode.HS` (Hue/Saturation) - this is the updated implementation
3. **State Management**: Uses assumed state (no read-back from device)
4. **Async Pattern**: All I/O operations use `hass.async_add_executor_job()` for thread safety
5. **Entity Registry**: Supports `unique_id` based on device serial number

### Code Patterns to Follow

#### Entity Properties
- Always use `@property` decorators for entity attributes
- Return cached state values from the entity instance
- Implement `supported_color_modes` and `color_mode` properties

#### Async Operations
```python
# Correct pattern for blocking I/O
await self.hass.async_add_executor_job(self._light.fade_to_rgb, 100, *rgb_color)
```

#### Color Conversion
```python
# HS color from Home Assistant → RGB for Blink(1)
rgb_color = color_util.color_hsv_to_RGB(
    hs_color[0], hs_color[1], brightness / 255 * 100
)
```

### Dependencies

- **blink1**: Python library for Blink(1) USB device communication
- **homeassistant**: Core Home Assistant libraries
- **voluptuous**: Configuration validation (imported but not actively used)

### Important Constraints

1. **Blink(1) Device Limitations**:
   - USB device, must be locally connected
   - No state read-back capability (assumed state)
   - Uses fade_to_rgb() for smooth color transitions (100ms default)

2. **Home Assistant Compatibility**:
   - Must use modern `ColorMode` enum (not legacy color mode strings)
   - Async methods required for turn_on/turn_off
   - Follow Home Assistant entity naming conventions

3. **Error Handling**:
   - Log errors using `_LOGGER.error()`
   - Log debug info using `_LOGGER.debug()`
   - Handle exceptions gracefully to avoid integration crashes

## Development Guidelines

### When Adding Features

1. **Always maintain backward compatibility** with Home Assistant's light platform API
2. **Test color conversions** - HS color space must correctly map to RGB
3. **Validate input ranges**:
   - Hue: 0-360
   - Saturation: 0-100
   - Brightness: 0-255
4. **Use async/await** for any I/O operations
5. **Update manifest.json version** when making changes

### When Fixing Bugs

1. Check Home Assistant breaking changes for the target version
2. Verify `ColorMode` usage matches current Home Assistant API
3. Test with actual Blink(1) hardware if possible
4. Validate color conversion edge cases (black, white, pure colors)

### Testing Considerations

- This integration requires physical Blink(1) hardware
- Test with Home Assistant's Developer Tools → Services
- Verify color accuracy visually
- Test brightness range (0-255)
- Verify graceful handling when device is disconnected

## Common Tasks

### Updating Color Mode Implementation
The main update in this fork was migrating from old color mode strings to the new `ColorMode` enum:
```python
# OLD (deprecated)
SUPPORT_COLOR = ...

# NEW (current)
@property
def supported_color_modes(self):
    return {ColorMode.HS}
```

### Adding New Features
When adding features:
1. Check if the `blink1` library supports the feature
2. Add property methods following Home Assistant patterns
3. Update the manifest version
4. Document in README.md

### Debugging
- Enable debug logging in Home Assistant configuration:
  ```yaml
  logger:
    default: info
    logs:
      custom_components.blink1_status: debug
  ```
- Check Home Assistant logs for error messages
- Verify USB device permissions on the host system

## Resources

- [Home Assistant Light Integration Docs](https://developers.home-assistant.io/docs/core/entity/light)
- [Blink(1) Python Library](https://github.com/todbot/blink1-python)
- [Home Assistant Custom Components](https://developers.home-assistant.io/docs/creating_component_index)
- [HACS Documentation](https://hacs.xyz/)

## Notes for AI Assistants

- This is a **fork** with specific ColorMode updates - preserve those changes
- The codebase is intentionally minimal - don't over-engineer
- Always consider Home Assistant version compatibility
- Device I/O is blocking - must use executor jobs
- No configuration options needed - works out of the box
