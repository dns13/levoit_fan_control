"""Tests for config flow."""

from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_abort_no_emitters(hass):
    """Config flow aborts when no IR emitters are available."""
    from homeassistant.data_entry_flow import FlowResultType

    with (
        patch(
            "homeassistant.components.infrared.async_get_emitters",
            return_value=[],
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            "levoit_fan_control",
            context={"source": "user"},
        )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "no_emitters"


@pytest.mark.asyncio
async def test_happy_path(hass, sample_profile_data):
    """Config flow creates entry with valid input."""
    from homeassistant.data_entry_flow import FlowResultType

    from custom_components.levoit_fan_control.profiles import _validate_profile

    profile = _validate_profile(sample_profile_data, "test_profile")

    with (
        patch(
            "homeassistant.components.infrared.async_get_emitters",
            return_value=["infrared.my_transmitter"],
        ),
        patch(
            "custom_components.levoit_fan_control.config_flow.list_profiles",
            return_value={"test_profile": profile.display_name},
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            "levoit_fan_control",
            context={"source": "user"},
        )
        assert result["type"] == FlowResultType.FORM

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                "profile_id": "test_profile",
                "infrared_emitter_entity_id": "infrared.my_transmitter",
            },
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"]["profile_id"] == "test_profile"
    assert result["data"]["infrared_emitter_entity_id"] == "infrared.my_transmitter"
