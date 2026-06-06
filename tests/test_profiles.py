"""Tests for device profile loader."""

import pytest

from custom_components.levoit_fan_control.profiles import (
    InvalidProfileError,
    UnknownActionError,
    _validate_profile,
)


def test_valid_profile(sample_profile_data):
    """A well-formed profile parses correctly."""
    profile = _validate_profile(sample_profile_data, "test")
    assert profile.profile_id == "test"
    assert profile.manufacturer == "Levoit"
    assert profile.features.speeds == ["speed_1", "speed_2", "speed_3"]
    assert profile.features.oscillation == "toggle"


def test_missing_required_field(sample_profile_data):
    """Missing top-level field raises InvalidProfileError."""
    del sample_profile_data["address"]
    with pytest.raises(InvalidProfileError, match="address"):
        _validate_profile(sample_profile_data, "test")


def test_unsupported_protocol(sample_profile_data):
    """Unknown protocol raises InvalidProfileError."""
    sample_profile_data["protocol"] = "rc5"
    with pytest.raises(InvalidProfileError, match="unsupported protocol"):
        _validate_profile(sample_profile_data, "test")


def test_no_speeds(sample_profile_data):
    """Empty speeds list raises InvalidProfileError."""
    sample_profile_data["features"]["speeds"] = []
    with pytest.raises(InvalidProfileError, match="at least one speed"):
        _validate_profile(sample_profile_data, "test")


def test_speed_not_in_commands(sample_profile_data):
    """Speed action referencing missing command raises InvalidProfileError."""
    sample_profile_data["features"]["speeds"].append("speed_99")
    with pytest.raises(InvalidProfileError, match="speed_99"):
        _validate_profile(sample_profile_data, "test")


def test_oscillation_without_command(sample_profile_data):
    """Oscillation feature declared without command raises InvalidProfileError."""
    del sample_profile_data["commands"]["oscillation"]
    with pytest.raises(InvalidProfileError, match="oscillation"):
        _validate_profile(sample_profile_data, "test")


def test_make_command_valid(sample_profile_data):
    """make_command returns a NECCommand for a known action."""
    from infrared_protocols.commands.nec import NECCommand

    profile = _validate_profile(sample_profile_data, "test")
    cmd = profile.make_command("power")
    assert isinstance(cmd, NECCommand)


def test_make_command_unknown_action(sample_profile_data):
    """make_command raises UnknownActionError for undefined action."""
    profile = _validate_profile(sample_profile_data, "test")
    with pytest.raises(UnknownActionError):
        profile.make_command("nonexistent")
