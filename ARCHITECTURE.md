# Architecture Documentation

This document provides a detailed technical overview of the Blink(1) Status Light integration for Home Assistant. It's designed to help developers and AI coding assistants understand the codebase structure and implementation details.

## Overview

**Type**: Home Assistant Custom Component
**Domain**: `blink1_status`
**Platform**: Light
**Integration Pattern**: Platform-based (not config flow)

This integration provides a simple bridge between Home Assistant's light entity platform and the Blink(1) USB LED device. It uses assumed state (no read-back from device) and supports color and brightness control.

## Compatibility

**Current Status**: ✅ **Fully compatible with Home Assistant 2025.12 and future versions**

**Home Assistant Version Requirements**:
- **Minimum**: 2021.12+ (ColorMode enum introduced)
- **Tested**: 2025.12 (latest as of January 2025)
- **Future**: Compatible through 2026+ (no breaking changes affect this integration)

**Key Compliance**:
- ✅ `ColorMode.HS` properly implemented (mandatory since 2025.3)
- ✅ `supported_color_modes` property (required)
- ✅ `integration_type` field in manifest.json (will be mandatory)
- ✅ `iot_class` field in manifest.json (recommended)
- ✅ `unique_id` property for entity registry
- ✅ Async methods for all I/O operations
- ✅ Proper error handling in setup and operations

**Future-Proof**:
- No deprecated APIs used
- No planned breaking changes affect this integration
- Template entity deprecation (2026.6) does not apply
- Modern color mode implementation ensures long-term compatibility

## Directory Structure

```
ha-blink1_status/
├── .github/
│   └── copilot-instructions.md      # GitHub Copilot specific guidance
├── custom_components/
│   └── blink1_status/
│       ├── __init__.py               # Integration entry point (minimal)
│       ├── light.py                  # Light platform implementation
│       └── manifest.json             # Integration metadata
├── ARCHITECTURE.md                   # This file
├── CONTRIBUTING.md                   # Contribution guidelines
├── README.md                         # User documentation
├── hacs.json                         # HACS integration metadata
└── requirements.txt                  # Python dependencies
```

## Component Files

### `custom_components/blink1_status/__init__.py`

**Purpose**: Integration initialization
**Size**: Minimal (docstring only)
**Content**:
```python
"""Blink(1) Status Light integration"""
```

**Why so minimal?**: This is a platform-based integration. Setup happens in `light.py`, not the main init file.

### `custom_components/blink1_status/light.py`

**Purpose**: Core implementation
**Lines**: ~125 lines
**Key Components**:

1. **Imports** (lines 1-12)
   - Standard library: `logging`
   - Home Assistant core: `color_util`
   - Light platform: `LightEntity`, `ColorMode`, attributes
   - External: `blink1.blink1.Blink1` (lazy import in setup)
   - Cleaned up: Removed unused `voluptuous` and `config_validation` imports

2. **Platform Setup** (lines 17-28)
   ```python
   async def async_setup_platform(hass, config, async_add_entities, discovery_info=None)
   ```
   - Called by Home Assistant during integration load
   - Imports and initializes Blink1 device
   - Creates and registers the light entity
   - **Includes error handling**: Catches device initialization failures
   - Logs helpful error messages for troubleshooting

3. **Entity Class** (lines 31+)
   ```python
   class blink1_status(LightEntity)
   ```
   - Implements Home Assistant's `LightEntity` interface
   - Manages device state and communication
   - Handles color space conversions
   - Includes `unique_id` for entity registry support

### `custom_components/blink1_status/manifest.json`

**Purpose**: Integration metadata for Home Assistant

**Structure**:
```json
{
  "domain": "blink1_status",              // Unique identifier
  "name": "Blink(1) Status Light",        // Display name
  "documentation": "...",                 // GitHub URL
  "dependencies": [],                     // No HA integration deps
  "codeowners": [],                       // No specific owners
  "requirements": ["blink1"],             // PyPI package dependency
  "version": "0.3.0",                     // Current version
  "integration_type": "device",           // Integration type (device, not hub)
  "iot_class": "assumed_state"            // IoT class (no state read-back)
}
```

**Version History**:
- 0.1.x: Original implementation
- 0.2.x: ColorMode update (this fork)
- 0.3.x: Future-proofing updates (manifest fields, unique_id, error handling)

## Class Architecture

### `blink1_status` Entity Class

#### State Variables

```python
self._light: Blink1           # Device handle
self._name: str = "Blink1"    # Entity name
self._state: bool | None      # On/Off state
self._hs_color: list          # [Hue, Saturation]
self._brightness: int = 255   # 0-255 (default full brightness)
self._unique_id: str          # Unique identifier (from serial or fixed)
```

**State Management**: Entirely local, no device read-back.

#### Properties

| Property | Type | Purpose | Returns |
|----------|------|---------|---------|
| `name` | str | Entity display name | `"Blink1"` |
| `unique_id` | str | Unique entity identifier | Device serial or fixed ID |
| `is_on` | bool | Current on/off state | `self._state` |
| `hs_color` | tuple | Current HS color | `self._hs_color` |
| `brightness` | int | Current brightness (0-255) | `self._brightness` |
| `supported_color_modes` | set | Color modes supported | `{ColorMode.HS}` |
| `color_mode` | ColorMode | Current color mode | `ColorMode.HS` |

#### Methods

**`async_turn_on(**kwargs)`** (lines 71-95)

Flow:
1. Extract `ATTR_HS_COLOR` and `ATTR_BRIGHTNESS` from kwargs
2. Update internal state variables
3. Validate ranges:
   - Hue: 0-360°
   - Saturation: 0-100%
   - Brightness: 0-255
4. Convert HS + Brightness → RGB:
   ```python
   rgb_color = color_util.color_hsv_to_RGB(
       hs_color[0], hs_color[1], brightness / 255 * 100
   )
   ```
5. Send to device (non-blocking):
   ```python
   await self.hass.async_add_executor_job(
       self._light.fade_to_rgb, 100, *rgb_color
   )
   ```
6. Update `self._state = True`
7. Log result (debug level)
8. Catch and log any exceptions

**`async_turn_off(**kwargs)`** (lines 97-106)

Flow:
1. Update `self._state = False`
2. Send off command to device:
   ```python
   await self.hass.async_add_executor_job(self._light.off)
   ```
3. Log result (debug level)
4. Catch and log any exceptions

**`update()`** (lines 109-111)

Empty implementation - device doesn't support state queries.

## Data Flow

### Turn On Light with Color

```
Home Assistant UI/Automation
    ↓
    service: light.turn_on
    data:
      entity_id: light.blink1
      hs_color: [120, 100]
      brightness: 200
    ↓
blink1_status.async_turn_on()
    ↓
    Extract hs_color & brightness
    ↓
    Validate ranges
    ↓
    Convert HS+Brightness → RGB
    ↓
    [HS: 120°, 100%] + [B: 200/255]
    ↓
    [RGB: ~0, 200, 0]  (green)
    ↓
    async_add_executor_job()
    ↓
    [Executor Thread]
    blink1.fade_to_rgb(100, 0, 200, 0)
    ↓
    [USB Communication]
    Blink(1) Device glows green
```

### State Management

```
                    ┌─────────────────┐
                    │  Home Assistant │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ blink1_status   │
                    │   Entity        │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Internal State  │
                    │ _state: bool    │
                    │ _hs_color       │
                    │ _brightness     │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  blink1 Library │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  USB Device     │
                    │  (No readback)  │
                    └─────────────────┘
```

**Key Point**: State flows one direction only (HA → Device). No feedback loop.

## Color Space Conversions

### HS Color Mode

Home Assistant uses:
- **Hue**: 0-360° (color wheel position)
- **Saturation**: 0-100% (color intensity)
- **Brightness**: 0-255 (light intensity)

Blink(1) uses:
- **RGB**: 0-255 per channel

### Conversion Process

```python
# Step 1: Get HS color and brightness from Home Assistant
hs_color = [120, 100]  # Green at full saturation
brightness = 200       # ~78% brightness

# Step 2: Normalize brightness to 0-100 for HSV
value = brightness / 255 * 100  # 78.4%

# Step 3: Convert HSV → RGB
rgb_color = color_util.color_hsv_to_RGB(
    hs_color[0],    # Hue: 120
    hs_color[1],    # Saturation: 100
    value           # Value: 78.4
)
# Result: (0, 200, 0) approximately

# Step 4: Send to device
fade_to_rgb(100, *rgb_color)  # 100ms fade
```

### Special Cases

| Input | Conversion | Output |
|-------|------------|--------|
| H=0, S=0, B=255 | White | RGB(255, 255, 255) |
| H=any, S=0, B=0 | Black/Off | RGB(0, 0, 0) |
| H=0, S=100, B=255 | Pure Red | RGB(255, 0, 0) |
| H=120, S=100, B=255 | Pure Green | RGB(0, 255, 0) |
| H=240, S=100, B=255 | Pure Blue | RGB(0, 0, 255) |

## Threading and Async

### Why Executor Jobs?

Home Assistant's event loop is single-threaded. Blocking I/O (like USB communication) would freeze the entire system.

**Pattern**:
```python
# Wrong - blocks event loop
self._light.fade_to_rgb(100, r, g, b)

# Correct - runs in thread pool
await self.hass.async_add_executor_job(
    self._light.fade_to_rgb, 100, r, g, b
)
```

### Thread Safety

The `blink1` library is not explicitly thread-safe, but:
- Only one entity instance exists
- All calls go through the async event loop
- Serialization is implicit through await

**No additional locking needed** in this simple case.

## Error Handling

### Current Implementation

Both `async_turn_on()` and `async_turn_off()` use try/except:

```python
try:
    # Device operation
    await self.hass.async_add_executor_job(...)
    _LOGGER.debug("Success message")
except Exception as e:
    _LOGGER.error("Failed: %s", e)
```

### Failure Scenarios

1. **Device not found** (setup)
   - Happens in `async_setup_platform()`
   - No try/except - will fail integration load
   - User sees error in HA logs

2. **Device disconnected** (runtime)
   - Exception caught in turn_on/turn_off
   - Error logged, integration continues
   - State becomes stale (assumed state)

3. **USB permission denied**
   - Similar to device disconnected
   - Logged as error
   - Requires OS-level fix (udev rules)

### No Retry Logic

Failures are logged but not retried. Rationale:
- USB errors are usually persistent (disconnected, permissions)
- Retrying would delay response without benefit
- User can manually retry from HA UI

## Dependencies

### External Libraries

**blink1** (`pip install blink1`)
- Pure Python library for Blink(1) USB devices
- Uses `hidapi` under the hood
- Main API used:
  - `Blink1()` - Initialize device
  - `fade_to_rgb(ms, r, g, b)` - Fade to color
  - `off()` - Turn off

### Home Assistant Core

**Minimum Version**: 2021.12+ (ColorMode enum introduced)

**Used APIs**:
- `homeassistant.components.light.LightEntity`
- `homeassistant.components.light.ColorMode`
- `homeassistant.util.color.color_hsv_to_RGB()`
- `hass.async_add_executor_job()`

**Deprecated APIs Avoided**:
- Old color mode strings (`SUPPORT_COLOR`, etc.)
- Synchronous `turn_on`/`turn_off` methods

## Integration Lifecycle

### Startup Sequence

```
1. Home Assistant starts
   ↓
2. Loads custom_components/blink1_status
   ↓
3. Reads manifest.json
   ↓
4. Installs requirements: pip install blink1
   ↓
5. Reads configuration.yaml
   ↓
6. Finds light platform: blink1_status
   ↓
7. Calls async_setup_platform() in light.py
   ↓
8. Imports blink1 library
   ↓
9. Initializes Blink1() device
   ↓
10. Creates blink1_status entity
    ↓
11. Registers with async_add_entities()
    ↓
12. Entity appears as light.blink1
    ↓
13. Ready for service calls
```

### Configuration

**configuration.yaml**:
```yaml
light:
  - platform: blink1_status
```

**No options** - the integration auto-discovers the USB device.

### Shutdown

No special cleanup needed:
- Python garbage collection handles `Blink1` object
- USB device released automatically
- No persistent connections to close

## Debugging

### Enable Debug Logging

**configuration.yaml**:
```yaml
logger:
  default: info
  logs:
    custom_components.blink1_status: debug
```

### Common Log Messages

**Successful turn on**:
```
DEBUG: Turned on light: HS=[120, 100], Brightness=200
```

**Successful turn off**:
```
DEBUG: Turned off light.
```

**Device error**:
```
ERROR: Failed to turn on the light: [Errno 19] No such device
```

### Troubleshooting Steps

1. **Check logs**: Look for ERROR or EXCEPTION messages
2. **Verify USB**: `lsusb | grep ThingM` (Blink1 manufacturer)
3. **Check permissions**: User must have USB device access
4. **Test library**: `python -c "from blink1.blink1 import Blink1; b=Blink1(); print('OK')"`

## Future Considerations

### Potential Improvements

1. **Multiple Device Support**
   - Current: Single device only
   - Enhancement: Detect and expose all connected Blink(1)s

2. **Effect Support**
   - Current: Static colors only
   - Enhancement: Add fade, pulse, pattern effects

3. **Config Flow**
   - Current: YAML configuration
   - Enhancement: UI-based setup

4. **Device Detection**
   - Current: Fails silently if no device
   - Enhancement: Graceful fallback, warnings in UI

### Breaking Changes to Avoid

- Don't remove `ColorMode.HS` support
- Don't break assumed state behavior
- Don't change entity name/ID (breaks existing configs)

## References

- [Home Assistant Light Integration Docs](https://developers.home-assistant.io/docs/core/entity/light)
- [Blink(1) Hardware](https://blink1.thingm.com/)
- [blink1-python Library](https://github.com/todbot/blink1-python)
- [Original Repository](https://github.com/tnagels/ha-blink1_status)

## Document Maintenance

**Last Updated**: 2025-12-09
**Version**: 0.2.1

When updating this document:
- Keep code examples in sync with actual implementation
- Update version numbers
- Add new sections for significant features
- Maintain consistency with CONTRIBUTING.md
