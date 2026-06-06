"""Fan platform for Levoit Fan (IR) integration."""

from __future__ import annotations

import math

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.components.infrared import InfraredEmitterConsumerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util.percentage import (
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from .const import CONF_INFRARED_EMITTER_ENTITY_ID, CONF_PROFILE_ID
from .entity import LevoitIrEntity
from .profiles import UnknownActionError, get_profile

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Levoit IR fan from config entry."""
    profile = get_profile(entry.data[CONF_PROFILE_ID])
    infrared_entity_id = entry.data[CONF_INFRARED_EMITTER_ENTITY_ID]
    async_add_entities([LevoitIrFan(entry, profile, infrared_entity_id)])


class LevoitIrFan(LevoitIrEntity, InfraredEmitterConsumerEntity, FanEntity):
    """Levoit IR fan entity."""

    _attr_assumed_state = True
    _attr_name = None

    def __init__(self, entry: ConfigEntry, profile, infrared_entity_id: str) -> None:
        """Initialize the fan entity."""
        super().__init__(entry, profile, unique_id_suffix="fan")
        self._profile = profile
        self._infrared_emitter_entity_id = infrared_entity_id

        # Build supported features from profile
        features = FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
        if profile.features.speeds:
            features |= FanEntityFeature.SET_SPEED
            self._attr_speed_count = len(profile.features.speeds)
            self._speed_range = (1, len(profile.features.speeds))
        if profile.features.oscillation:
            features |= FanEntityFeature.OSCILLATE
        self._attr_supported_features = features

        # Assumed state tracking
        self._is_on = False
        self._current_percentage: int | None = None
        self._oscillating = False

    @property
    def is_on(self) -> bool:
        """Return true if fan is on."""
        return self._is_on

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        return self._current_percentage

    @property
    def oscillating(self) -> bool | None:
        """Return true if fan is oscillating."""
        if self._profile.features.oscillation is None:
            return None
        return self._oscillating

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs,
    ) -> None:
        """Turn on the fan."""
        if not self._is_on:
            await self._send_profile("power")
            self._is_on = True
        if percentage is not None:
            await self._set_speed_by_percentage(percentage)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the fan."""
        if self._is_on:
            await self._send_profile("power")
            self._is_on = False
            self.async_write_ha_state()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the fan speed percentage."""
        if percentage == 0:
            await self.async_turn_off()
            return
        if not self._is_on:
            await self._send_profile("power")
            self._is_on = True
        await self._set_speed_by_percentage(percentage)
        self.async_write_ha_state()

    async def async_oscillate(self, oscillating: bool) -> None:
        """Oscillate the fan."""
        if self._profile.features.oscillation == "toggle":
            # Only send if desired state differs from current
            if oscillating != self._oscillating:
                await self._send_profile("oscillation")
                self._oscillating = oscillating
        else:
            action = "oscillation_on" if oscillating else "oscillation_off"
            await self._send_profile(action)
            self._oscillating = oscillating
        self.async_write_ha_state()

    async def _set_speed_by_percentage(self, percentage: int) -> None:
        """Map percentage to a speed action and send it."""
        speed_idx = math.ceil(
            percentage_to_ranged_value(self._speed_range, percentage)
        ) - 1
        speed_idx = max(0, min(speed_idx, len(self._profile.features.speeds) - 1))
        action = self._profile.features.speeds[speed_idx]
        await self._send_profile(action)
        self._current_percentage = ranged_value_to_percentage(
            self._speed_range, speed_idx + 1
        )

    async def _send_profile(self, action: str) -> None:
        """Build and send an IR command for the given action."""
        cmd = self._profile.make_command(action)
        await self._send_command(cmd)
