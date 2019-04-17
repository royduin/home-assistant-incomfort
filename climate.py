import json
import logging
import requests

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

DEFAULT_AUTH = False
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'intergas'

CONF_NAME = 'name'
CONF_HOST = 'host'
CONF_AUTH = 'auth'
CONF_USERNAME = 'username'
CONF_PASSWORD = 'password'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_NAME): cv.string,
    vol.Optional(CONF_AUTH, default=DEFAULT_AUTH): cv.boolean,
    vol.Optional(CONF_USERNAME, default=DEFAULT_USERNAME): cv.string,
    vol.Optional(CONF_PASSWORD, default=DEFAULT_PASSWORD): cv.string,
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
    auth = config.get(CONF_AUTH)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)

    add_devices([InComfortThermostat(name, host, auth, username, password)])


class InComfortThermostat(ClimateDevice):
    """Representation of a InComfort Thermostat device."""

    def __init__(self, name, host, auth, username, password):
        """Initialize the thermostat."""
        self.host = host
        self._name = name
        self._auth = auth
        self._username = username
        self._password = password
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

        if self._auth:
            requests.get('http://' + self.host + '/protect/data.json?heater=0&thermostat=0&setpoint=' +
                str((min(max(temperature, 5), 30) - 5.0) * 10), auth=(self._username, self._password))
        else:
            requests.get('http://' + self.host + '/data.json?heater=0&thermostat=0&setpoint=' +
                str((min(max(temperature, 5), 30) - 5.0) * 10))
        self._target_temperature = temperature

    def update(self):
        """Get the latest data."""
        if self._auth:
            req = requests.get('http://' + self.host + '/protect/data.json?heater=0', auth=(self._username, self._password))
        else:
            req = requests.get('http://' + self.host + '/data.json?heater=0')
        text = req.json()
        self.data = text
