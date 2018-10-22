# Home Assistant InComfort

Intergas InComfort integration with Home Assistant.

- Feature request: https://community.home-assistant.io/t/intergas-incomfort-lan2rf-gateway/23967
- Development talk: https://community.home-assistant.io/t/new-climate-thermostat-implementation-tips/74394

<img src="https://raw.githubusercontent.com/royduin/home-assistant-incomfort/master/card.png" width="250px" alt="Card">
<img src="https://raw.githubusercontent.com/royduin/home-assistant-incomfort/master/popup.png" width="250px" alt="Popup">

## Installation

Put the `InComfort.py` file in `custom_components/climate` within your configuration directory. On Ubuntu for example: `~/.homeassistant/custom_components/climate`. After that configure it in the `configuration.yaml` file:
```
climate:
  - platform: InComfort
    name: Woonkamer
    host: 192.168.1.139
```
And change the `name` and `host` as wanted.

## Why is it not in the core of Home Assistant?

Because I'm not a Python developer. Can you get it there? As mentioned in [this](https://community.home-assistant.io/t/new-climate-thermostat-implementation-tips/74394) topic it should probably splitted into a seperated library where this integration talks with.

## TODO

- Refactor? I'm not sure everything I did is correct, but it works.
- Add it to the Home Assistant core.

## Ideas, bugs or suggestions?
Please create a [issue](https://github.com/royduin/home-assistant-incomfort/issues) or a [pull request](https://github.com/royduin/home-assistant-incomfort/pulls).

## License
[MIT](LICENSE.md)
