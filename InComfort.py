import json
import logging

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from urllib.request import urlopen
from homeassistant.components.climate import (
    STATE_HEAT, ClimateDevice, SUPPORT_TARGET_TEMPERATURE, PLATFORM_SCHEMA)
from homeassistant.const import (
    TEMP_CELSIUS, ATTR_TEMPERATURE)

CONF_NAME = 'name'
CONF_HOST = 'host'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_NAME): cv.string,
})

def _lsbmsb(lsb, msb):
    temp = (lsb + msb*256) / 100.0
    if temp == 327.67:
        return 0
    else:
        return temp

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the InComfort thermostat."""

    name = config.get(CONF_NAME)
    host = config.get(CONF_HOST)

    add_devices([InComfortThermostat(name, host)])

class InComfortThermostat(ClimateDevice):
    """Representation of a InComfort Thermostat device."""

    def __init__(self, name, host):
        """Initialize the thermostat."""
        self.host = host
        self._name = name
        self._current_temperature = None
        self._target_temperature = None
        self._state = None
        self.data = None
        self.update()

    @property
    def state(self):
        """Return the current state."""
        if self.data is not None:
            if bool(self.data['IO'] & 8):
                self._state = 'Verwarmen'
            else:
                self._state = 'Standby'
        else:
            self._state = None
        return self._state

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_TARGET_TEMPERATURE

    @property
    def name(self):
        """Return the name of the thermostat, if any."""
        return self._name

    @property
    def temperature_unit(self):
        """Return the unit of measurement which this thermostat uses."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        if self.data is not None:
            self._current_temperature = _lsbmsb(self.data['room_temp_1_lsb'], self.data['room_temp_1_msb'])
        else:
            self._current_temperature = None
        return self._current_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        if self.data is not None:
            self._target_temperature = _lsbmsb(self.data['room_temp_set_1_lsb'], self.data['room_temp_set_1_msb'])
        else:
            self._target_temperature = None
        return self._target_temperature

    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        urlopen('http://' + self.host + '/data.json?heater=0&thermostat=0&setpoint=' + str((min(max(temperature, 5), 30) - 5.0) * 10))
        self._target_temperature = temperature

    def update(self):
        """Get the latest data."""
        response = urlopen('http://' + self.host + '/data.json?heater=0')
        string = response.read().decode('utf-8')
        self.data = json.loads(string)
