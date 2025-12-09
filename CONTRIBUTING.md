# Contributing to Blink(1) Status Light Integration

Thank you for your interest in contributing to this Home Assistant custom component! This guide is designed to help both human developers and AI coding assistants understand how to work with this codebase effectively.

## For AI Coding Assistants

This repository includes specific instructions for AI assistants:
- **GitHub Copilot**: See `.github/copilot-instructions.md`
- **Claude**: This file and `ARCHITECTURE.md` provide context
- **Other AI Agents**: Follow the guidelines below

### Quick Context for AI Agents

**What is this?**
A Home Assistant custom component that controls Blink(1) USB LED lights.

**Key fact**: This is a fork that updates the ColorMode implementation to work with modern Home Assistant versions.

**Critical files**:
- `custom_components/blink1_status/light.py` - Main implementation
- `custom_components/blink1_status/manifest.json` - Integration metadata

**Don't break**:
- ColorMode.HS implementation (this is the main improvement)
- Async patterns for I/O operations
- Home Assistant light entity conventions

## General Contribution Guidelines

### Code Style

1. **Follow Home Assistant coding standards**
   - Use async/await for I/O operations
   - Use type hints where helpful
   - Follow PEP 8 style guide

2. **Logging**
   - Use `_LOGGER.debug()` for verbose information
   - Use `_LOGGER.error()` for errors
   - Include context in log messages

3. **Error Handling**
   - Wrap device operations in try/except blocks
   - Never let exceptions crash the integration
   - Log meaningful error messages

### Testing

This integration requires physical hardware (Blink(1) USB device) for full testing.

**Manual Testing Steps**:
1. Install the integration in Home Assistant
2. Add to configuration.yaml:
   ```yaml
   light:
     - platform: blink1_status
   ```
3. Restart Home Assistant
4. Test via Developer Tools → Services:
   - `light.turn_on` with different colors and brightness
   - `light.turn_off`
5. Verify LED responds correctly

**Color Testing**:
- Pure red (H=0, S=100)
- Pure green (H=120, S=100)
- Pure blue (H=240, S=100)
- White (H=0, S=0, B=255)
- Various brightness levels (0-255)

### Version Compatibility

- **Home Assistant**: 2021.12+ (ColorMode enum introduced)
- **Python**: 3.8+ (Home Assistant requirement)
- **blink1 library**: Latest version from PyPI

### Making Changes

#### Before You Start

1. **Understand the current implementation**
   - Read `light.py` completely
   - Understand ColorMode.HS pattern
   - Review Home Assistant light entity docs

2. **Identify dependencies**
   - What other code might be affected?
   - Are Home Assistant API changes needed?
   - Does manifest.json need updating?

#### When Writing Code

1. **Maintain ColorMode implementation**
   - This is the primary improvement in this fork
   - Don't revert to old color mode patterns
   - Keep `supported_color_modes` and `color_mode` properties

2. **Preserve async patterns**
   ```python
   # Correct - non-blocking
   await self.hass.async_add_executor_job(self._light.fade_to_rgb, ...)

   # Wrong - blocking
   self._light.fade_to_rgb(...)
   ```

3. **Validate inputs**
   ```python
   # Always validate color/brightness ranges
   hs_color = [
       max(0, min(360, self._hs_color[0])),  # Hue: 0-360
       max(0, min(100, self._hs_color[1]))   # Saturation: 0-100
   ]
   brightness = max(0, min(self._brightness, 255))  # Brightness: 0-255
   ```

4. **Update version numbers**
   - Increment version in `manifest.json`
   - Follow semantic versioning (major.minor.patch)

#### After Making Changes

1. **Test thoroughly**
   - Verify all color modes work
   - Test edge cases (brightness 0, 255)
   - Ensure graceful handling of disconnected device

2. **Update documentation**
   - Update README.md if user-facing changes
   - Update this file if contribution process changes
   - Update ARCHITECTURE.md if structure changes

3. **Commit with clear messages**
   ```
   Good: "Fix brightness validation to prevent overflow"
   Bad: "fix bug"
   ```

### Common Modification Scenarios

#### Adding a New Feature

Example: Adding effect support

1. Check if `blink1` library supports the feature
2. Add property to `blink1_status` class
3. Add to `supported_features` if needed
4. Implement service call handler
5. Update manifest version
6. Document in README.md

#### Fixing a Bug

Example: Color conversion issue

1. Identify the root cause
2. Write test case (if possible)
3. Fix the issue
4. Verify fix with physical device
5. Update version in manifest.json
6. Document the fix in commit message

#### Updating Dependencies

Example: New Home Assistant version

1. Check Home Assistant breaking changes
2. Update code to match new APIs
3. Update version requirement in manifest.json
4. Test with target Home Assistant version
5. Update README.md with new requirements

## Project Architecture

See `ARCHITECTURE.md` for detailed information about:
- Directory structure
- Module dependencies
- Data flow
- Integration lifecycle

## Pull Request Process

1. **Fork the repository** (if you haven't already)

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the guidelines above
   - Test thoroughly
   - Update documentation

4. **Commit your changes**
   ```bash
   git commit -m "Description of changes"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request**
   - Describe what changed and why
   - Reference any related issues
   - Include testing notes

## Questions or Issues?

- **Bugs**: Open an issue on GitHub
- **Feature requests**: Open an issue with [Feature Request] tag
- **Questions**: Open a discussion or issue

## License

This project has no specific license attached per the original author. Contributions are accepted with the understanding that they will be used in the same manner.

## Acknowledgments

- Original repository: https://github.com/tnagels/ha-blink1_status
- Thanks to Qu3uk for HACS integration work
- Home Assistant community for documentation and support
