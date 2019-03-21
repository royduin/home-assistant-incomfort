import json
import logging

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from urllib.request import urlopen
from homeassistant.components.climate import (ClimateDevice, PLATFORM_SCHEMA)
from homeassistant.components.climate.const import (
    STATE_HEAT, SUPPORT_TARGET_TEMPERATURE)
from homeassistant.const import (
    TEMP_CELSIUS, ATTR_TEMPERATURE)

_LOGGER = logging.getLogger(__name__)

ATTR_PRESSURE = 'pressure'
ATTR_RSSI = 'rf_message_rssi'
ATTR_CH_TEMP = 'ch_temp'
ATTR_TAP_TEMP = 'tap_temp'

CONF_NAME = 'name'
CONF_HOST = 'host'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_NAME): cv.string,
})


def _lsbmsb(lsb, msb):
    temp = (lsb + msb*256) / 100.0
    if temp == 327.67:
        return 5
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
        self._pressure = None
        self._rf_message_rssi = None
        self._ch_temp = None
        self._tap_temp = None
        self._state = None
        self.data = None
        self.update()

    @property
    def state(self):
        """Return the current state."""
        if self.data is not None:
            if self.data['displ_code'] == 0:
                self._state = 'Opentherm'
            elif self.data['displ_code'] == 15:
                self._state = 'Boiler External'
            elif self.data['displ_code'] == 24:
                self._state = 'Frost'
            elif self.data['displ_code'] == 37:
                self._state = 'Central Heating RF'
            elif self.data['displ_code'] == 51:
                self._state = 'Tapwater Internal'
            elif self.data['displ_code'] == 85:
                self._state = 'Sensortest'
            elif self.data['displ_code'] == 102:
                self._state = 'Zone-heating'
            elif self.data['displ_code'] == 126:
                self._state = 'Standby'
            elif self.data['displ_code'] == 153:
                self._state = 'Postrun Boiler'
            elif self.data['displ_code'] == 170:
                self._state = 'Service'
            elif self.data['displ_code'] == 204:
                self._state = 'Tapwater'
            elif self.data['displ_code'] == 231:
                self._state = 'Postrun Central Heating'
            elif self.data['displ_code'] == 240:
                self._state = 'Boiler Internal'
            elif self.data['displ_code'] == 255:
                self._state = 'Buffer'
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
            self._current_temperature = _lsbmsb(
                self.data['room_temp_1_lsb'], self.data['room_temp_1_msb'])
        else:
            self._current_temperature = None
        return self._current_temperature

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        attr = {}
        super_attr = super().device_state_attributes
        if super_attr is not None:
            attr.update(super_attr)

        if self.data is not None:
            attr[ATTR_PRESSURE] = _lsbmsb(
                self.data['ch_pressure_lsb'], self.data['ch_pressure_msb'])
            attr[ATTR_RSSI] = self.data['rf_message_rssi']
            attr[ATTR_CH_TEMP] = _lsbmsb(
                self.data['ch_temp_lsb'], self.data['ch_temp_msb'])
            attr[ATTR_TAP_TEMP] = _lsbmsb(
                self.data['tap_temp_lsb'], self.data['tap_temp_msb'])
        else:
            attr[ATTR_PRESSURE] = None
            attr[ATTR_RSSI] = None
            attr[ATTR_CH_TEMP] = None
            attr[ATTR_TAP_TEMP] = None
        return attr

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        if self.data is not None:
            self._target_temperature = _lsbmsb(
                self.data['room_temp_set_1_lsb'], self.data['room_temp_set_1_msb'])
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

        urlopen('http://' + self.host + '/data.json?heater=0&thermostat=0&setpoint=' +
                str((min(max(temperature, 5), 30) - 5.0) * 10))
        self._target_temperature = temperature

    def update(self):
        """Get the latest data."""
        response = urlopen('http://' + self.host + '/data.json?heater=0')
        string = response.read().decode('utf-8')
        self.data = json.loads(string)
