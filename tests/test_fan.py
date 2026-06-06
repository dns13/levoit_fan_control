"""Tests for fan entity logic."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.levoit_fan_control.fan import LevoitIrFan
from custom_components.levoit_fan_control.profiles import _validate_profile


def make_fan(sample_profile_data):
    """Build a LevoitIrFan with a mocked entry and profile."""
    profile = _validate_profile(sample_profile_data, "test")
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.title = "Test Fan"
    fan = LevoitIrFan(entry, profile, "infrared.test_emitter")
    fan._send_command = AsyncMock()
    return fan


@pytest.mark.asyncio
async def test_turn_on_sends_power(sample_profile_data):
    """Turning on a fan that is off sends the power command."""
    fan = make_fan(sample_profile_data)
    assert not fan.is_on
    await fan.async_turn_on()
    assert fan.is_on
    fan._send_command.assert_called_once()


@pytest.mark.asyncio
async def test_turn_on_idempotent(sample_profile_data):
    """Turning on a fan that is already on does not send power again."""
    fan = make_fan(sample_profile_data)
    fan._is_on = True
    await fan.async_turn_on()
    fan._send_command.assert_not_called()


@pytest.mark.asyncio
async def test_turn_off_sends_power(sample_profile_data):
    """Turning off a fan that is on sends the power command."""
    fan = make_fan(sample_profile_data)
    fan._is_on = True
    await fan.async_turn_off()
    assert not fan.is_on
    fan._send_command.assert_called_once()


@pytest.mark.asyncio
async def test_turn_off_idempotent(sample_profile_data):
    """Turning off a fan that is already off sends nothing."""
    fan = make_fan(sample_profile_data)
    await fan.async_turn_off()
    fan._send_command.assert_not_called()


@pytest.mark.asyncio
async def test_set_percentage_selects_correct_speed(sample_profile_data):
    """set_percentage maps 100% to the highest speed."""
    fan = make_fan(sample_profile_data)
    fan._is_on = True
    await fan.async_set_percentage(100)
    # With 3 speeds, 100% → speed_3 (index 2)
    cmd = fan._send_command.call_args[0][0]
    assert cmd.command == sample_profile_data["commands"]["speed_3"]


@pytest.mark.asyncio
async def test_set_percentage_zero_turns_off(sample_profile_data):
    """Setting percentage to 0 turns the fan off."""
    fan = make_fan(sample_profile_data)
    fan._is_on = True
    await fan.async_set_percentage(0)
    assert not fan.is_on


@pytest.mark.asyncio
async def test_oscillate_toggle_only_sends_on_change(sample_profile_data):
    """Toggle oscillation only sends a command when desired state differs."""
    fan = make_fan(sample_profile_data)
    fan._oscillating = False
    await fan.async_oscillate(True)
    assert fan.oscillating is True
    fan._send_command.assert_called_once()
    fan._send_command.reset_mock()

    # Requesting the same state → no command
    await fan.async_oscillate(True)
    fan._send_command.assert_not_called()
