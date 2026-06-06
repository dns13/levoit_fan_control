"""Base entity for Levoit Fan (IR) integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .profiles import DeviceProfile


class LevoitIrEntity(Entity):
    """Base entity providing common device info for a Levoit IR-controlled device."""

    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, profile: DeviceProfile, unique_id_suffix: str) -> None:
        """Initialize the base entity."""
        self._attr_unique_id = f"{entry.entry_id}_{unique_id_suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer=profile.manufacturer,
            model=profile.model,
        )
