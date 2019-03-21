# Home Assistant InComfort

FORK OF https://github.com/royduin/home-assistant-incomfort

All credits go to Roy

## Additions to Roy's work
Add pressure, ch_temp, tap_temp and rf_message_rssi as device_state_attributes. And update to new custom_components structure of HA.

Intergas InComfort integration with Home Assistant.

<img src="https://raw.githubusercontent.com/anlupat/home-assistant-incomfort/master/card.png" width="250px" alt="Card">
<img src="https://raw.githubusercontent.com/anlupat/home-assistant-incomfort/master/popup.png" width="250px" alt="Popup">

## Installation

Put the `climate.py` file in `custom_components/InComfort` within your configuration directory. On Ubuntu for example: `~/.homeassistant/custom_components/InComfort`. After that configure it in the `configuration.yaml` file:
```
climate:
  - platform: InComfort
    name: Woonkamer
    host: 192.168.1.123
```
And change the `name` and `host` as wanted.

## Add sensor(s) for the UI

Sample:
```
- platform: template
  sensors:
    cv_pressure:
      friendly_name: "Water Pressure"
      unit_of_measurement: 'bar'
      icon_template: mdi:gauge
      value_template: "{{ state_attr('climate.Woonkamer', 'pressure') }}"
```

## Why is it not in the core of Home Assistant?

Because I'm not a Python developer. Can you get it there? As mentioned in [this](https://community.home-assistant.io/t/new-climate-thermostat-implementation-tips/74394) topic it should probably splitted into a seperated library where this integration talks with.


## Ideas, bugs or suggestions?
Please create a [issue](https://github.com/anlupat/home-assistant-incomfort/issues) or a [pull request](https://github.com/anlupat/home-assistant-incomfort/pulls).

## License
[MIT](LICENSE.md)
