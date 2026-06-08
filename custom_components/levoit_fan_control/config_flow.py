"""Config flow for Levoit Fan (IR) integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import infrared
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import CONF_INFRARED_EMITTER_ENTITY_ID, CONF_PROFILE_ID, DOMAIN
from .profiles import list_profiles


class LevoitFanConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Levoit Fan (IR)."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        emitters = infrared.async_get_emitters(self.hass)
        if not emitters:
            return self.async_abort(reason="no_emitters")

        profiles = await self.hass.async_add_executor_job(list_profiles)
        if not profiles:
            return self.async_abort(reason="no_profiles")

        errors: dict[str, str] = {}

        if user_input is not None:
            profile_id = user_input[CONF_PROFILE_ID]
            infrared_entity_id = user_input[CONF_INFRARED_EMITTER_ENTITY_ID]
            title = profiles[profile_id]
            return self.async_create_entry(
                title=title,
                data={
                    CONF_PROFILE_ID: profile_id,
                    CONF_INFRARED_EMITTER_ENTITY_ID: infrared_entity_id,
                },
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_PROFILE_ID): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            {"value": pid, "label": name}
                            for pid, name in profiles.items()
                        ],
                        mode=SelectSelectorMode.LIST,
                    )
                ),
                vol.Required(CONF_INFRARED_EMITTER_ENTITY_ID): EntitySelector(
                    EntitySelectorConfig(
                        domain="infrared",
                        device_class="emitter",
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
