"""Blink(1) Status Light integration."""
import logging

import homeassistant.util.color as color_util

# Import the device class from the component that you want to support
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_HS_COLOR,
    ColorMode,
    LightEntity,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Blink(1) light platform."""
    from blink1.blink1 import Blink1

    try:
        b1 = Blink1()
        async_add_entities([blink1_status(b1)])
        _LOGGER.info("Blink(1) device initialized successfully")
    except Exception as err:
        _LOGGER.error("Failed to initialize Blink(1) device: %s", err)
        _LOGGER.error("Please ensure the Blink(1) device is connected and you have the proper USB permissions")
        return False    


class blink1_status(LightEntity):
    """Representation of a BlinkLight Light."""

    def __init__(self, light):
        """Initialize a Blink(1) Status Light."""
        self._light = light
        self._name = "Blink1"
        self._state = None
        self._hs_color = [0, 0]
        self._brightness = 255
        # Generate unique_id from device serial if available, otherwise use fixed ID
        try:
            serial = light.get_serial_num()
            self._unique_id = f"blink1_{serial}"
        except (AttributeError, Exception):
            # Fallback to fixed ID if serial not available
            self._unique_id = "blink1_status_light"

    #new
    @property
    def supported_color_modes(self):
        """Return the supported color modes."""
        return {ColorMode.HS}

    #new
    @property
    def color_mode(self):
        """Return the current color mode."""
        return ColorMode.HS

    @property
    def brightness(self):
        """Read back the brightness of the light."""
        return self._brightness

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID for this light."""
        return self._unique_id

    @property
    def hs_color(self):
        """Return the color of this light."""
        return self._hs_color

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    async def async_turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        try:
            if ATTR_HS_COLOR in kwargs:
                self._hs_color = kwargs[ATTR_HS_COLOR]
            if ATTR_BRIGHTNESS in kwargs:
                self._brightness = kwargs[ATTR_BRIGHTNESS]

            # Werte validieren
            hs_color = [
                max(0, min(360, self._hs_color[0])),
                max(0, min(100, self._hs_color[1]))
            ]
            brightness = max(0, min(self._brightness, 255))

            self._state = True
            rgb_color = color_util.color_hsv_to_RGB(
                hs_color[0], hs_color[1], brightness / 255 * 100)

            await self.hass.async_add_executor_job(self._light.fade_to_rgb, 100, *rgb_color)

            _LOGGER.debug("Turned on light: HS=%s, Brightness=%d", hs_color, brightness)

        except Exception as e:
            _LOGGER.error("Failed to turn on the light: %s", e)

    async def async_turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        try:
            self._state = False

            await self.hass.async_add_executor_job(self._light.off)

            _LOGGER.debug("Turned off light.")
        except Exception as e:
            _LOGGER.error("Failed to turn off the light: %s", e)


    def update(self):
        """Fetch the latest state from the device."""
    #   """There is not data to get as we use an assumed state."""



