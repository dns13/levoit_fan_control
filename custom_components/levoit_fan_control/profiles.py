"""Device profile loader for Levoit Fan (IR) integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from infrared_protocols.commands.nec import NECCommand


_PROFILES_DIR = Path(__file__).parent / "profiles"
_VALID_PROTOCOLS = {"nec", "nec_extended"}


class UnknownActionError(KeyError):
    """Raised when a profile does not define a requested action."""


class InvalidProfileError(ValueError):
    """Raised when a profile YAML file fails validation."""


@dataclass
class DeviceProfile:
    """A parsed and validated device profile."""

    profile_id: str
    manufacturer: str
    model: str
    display_name: str
    protocol: str
    address: int
    commands: dict[str, int]
    features: _Features

    def make_command(self, action: str) -> NECCommand:
        """Build an InfraredCommand for the given action key."""
        if action not in self.commands:
            raise UnknownActionError(f"Action '{action}' not defined in profile '{self.profile_id}'")
        return NECCommand(
            address=self.address,
            command=self.commands[action],
        )


@dataclass
class _Features:
    power: str  # "toggle" or "discrete"
    speeds: list[str]
    oscillation: str | None = None  # "toggle", "discrete", or None


def _validate_profile(data: dict[str, Any], profile_id: str) -> DeviceProfile:
    required = ("manufacturer", "model", "display_name", "protocol", "address", "commands", "features")
    for key in required:
        if key not in data:
            raise InvalidProfileError(f"Profile '{profile_id}' missing required field: {key}")

    if data["protocol"] not in _VALID_PROTOCOLS:
        raise InvalidProfileError(
            f"Profile '{profile_id}' has unsupported protocol '{data['protocol']}'. "
            f"Supported: {_VALID_PROTOCOLS}"
        )

    feat = data["features"]
    if "speeds" not in feat or not feat["speeds"]:
        raise InvalidProfileError(f"Profile '{profile_id}' must define at least one speed in features.speeds")

    # Validate all referenced speed/feature actions exist in commands
    for action in feat["speeds"]:
        if action not in data["commands"]:
            raise InvalidProfileError(
                f"Profile '{profile_id}' feature speed '{action}' not found in commands"
            )

    oscillation = feat.get("oscillation")
    if oscillation and "oscillation" not in data["commands"]:
        raise InvalidProfileError(
            f"Profile '{profile_id}' declares oscillation feature but 'oscillation' command is missing"
        )

    return DeviceProfile(
        profile_id=profile_id,
        manufacturer=data["manufacturer"],
        model=data["model"],
        display_name=data["display_name"],
        protocol=data["protocol"],
        address=data["address"],
        commands=data["commands"],
        features=_Features(
            power=feat.get("power", "toggle"),
            speeds=feat["speeds"],
            oscillation=oscillation,
        ),
    )


@lru_cache(maxsize=1)
def load_all_profiles() -> dict[str, DeviceProfile]:
    """Load and cache all YAML profiles from the profiles/ directory."""
    profiles: dict[str, DeviceProfile] = {}
    for path in sorted(_PROFILES_DIR.glob("*.yaml")):
        profile_id = path.stem
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        profiles[profile_id] = _validate_profile(data, profile_id)
    return profiles


def get_profile(profile_id: str) -> DeviceProfile:
    """Return a specific profile by ID, raising KeyError if not found."""
    return load_all_profiles()[profile_id]


def list_profiles() -> dict[str, str]:
    """Return a mapping of profile_id -> display_name for UI selectors."""
    return {pid: p.display_name for pid, p in load_all_profiles().items()}
