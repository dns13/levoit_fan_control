# Levoit Fan (IR) — Home Assistant Integration

A HACS-installable Home Assistant integration to control Levoit (and other) IR-controlled fans via any configured IR emitter (e.g. ESPHome IR proxy).

## Requirements

- Home Assistant 2026.4 or newer (requires the built-in `infrared` domain)
- An IR emitter configured in Home Assistant (e.g. via the [ESPHome IR/RF Proxy](https://esphome.io/components/ir_rf_proxy/))

## Installation via HACS

1. Open HACS → Integrations → ⋮ → Custom Repositories
2. Add this repository URL with category **Integration**
3. Install "Levoit Fan (IR)" and restart Home Assistant

## Setup

1. Go to *Settings → Devices & Services → Add Integration*
2. Search for "Levoit Fan (IR)"
3. Select your fan model and the IR emitter to use

## Supported features

- Power on/off
- Speed control (4 levels mapped to HA percentage)
- Oscillation toggle

## Adding a new device

No Python code required. Just add a YAML file to `custom_components/levoit_fan_control/profiles/`:

```yaml
manufacturer: Acme
model: AF-1234
display_name: Acme Tower Fan (AF-1234)
protocol: nec
address: 0x1234    # NEC address from your remote
commands:
  power: 0x01
  speed_1: 0x02
  speed_2: 0x03
  oscillation: 0x04
features:
  power: toggle
  speeds: [speed_1, speed_2]
  oscillation: toggle
```

See [`custom_components/levoit_fan_control/profiles/SCHEMA.md`](custom_components/levoit_fan_control/profiles/SCHEMA.md) for the full schema.

## Finding your IR codes

If you have an IR receiver configured in Home Assistant, you can use it to learn codes from your original remote. The captured NEC address and command bytes go directly into the profile.

## Levoit TF-F361-WEU codes

Edit `custom_components/levoit_fan_control/profiles/levoit_tf_f361_weu.yaml` and replace the placeholder `address` and command bytes with your actual NEC codes.
