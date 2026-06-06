# Device Profile Schema

A profile YAML file describes an IR-controlled fan device. Place it in this `profiles/` directory — the integration picks it up automatically on restart, no code changes required.

## Required Fields

| Field | Type | Description |
|---|---|---|
| `manufacturer` | string | Brand name (e.g. `Levoit`) |
| `model` | string | Model number (e.g. `TF-F361-WEU`) |
| `display_name` | string | Human-readable name shown in the UI |
| `protocol` | string | IR protocol: `nec` or `nec_extended` |
| `address` | int | NEC address (hex, e.g. `0xFB04`) |
| `commands` | map | Action name → NEC command byte (hex) |
| `features` | map | See below |

## `features` Fields

| Field | Type | Description |
|---|---|---|
| `power` | `toggle` or `discrete` | `toggle`: single code for on+off. `discrete`: needs `power_on` + `power_off` in commands. |
| `speeds` | list of strings | List of action names (must exist in `commands`) ordered slowest→fastest |
| `oscillation` | `toggle`, `discrete`, or omit | Oscillation control. `toggle`: single `oscillation` command. `discrete`: needs `oscillation_on` + `oscillation_off`. Omit if not supported. |

## Minimal Example

```yaml
manufacturer: Acme
model: AF-1234
display_name: Acme Tower Fan (AF-1234)
protocol: nec
address: 0x1234
commands:
  power: 0x01
  speed_1: 0x02
  speed_2: 0x03
features:
  power: toggle
  speeds: [speed_1, speed_2]
```
