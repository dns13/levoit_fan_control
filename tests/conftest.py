"""Test configuration for levoit_fan_control."""

import pytest


@pytest.fixture
def sample_profile_data():
    """Valid profile data for testing."""
    return {
        "manufacturer": "Levoit",
        "model": "TF-F361-WEU",
        "display_name": "Levoit Tower Fan (TF-F361-WEU)",
        "protocol": "nec",
        "address": 0x1234,
        "commands": {
            "power": 0x01,
            "speed_1": 0x02,
            "speed_2": 0x03,
            "speed_3": 0x04,
            "oscillation": 0x05,
        },
        "features": {
            "power": "toggle",
            "speeds": ["speed_1", "speed_2", "speed_3"],
            "oscillation": "toggle",
        },
    }
