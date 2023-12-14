"""Platform for switch integration."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from datetime import datetime, date


from .state import IntegrationState
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the switch for Custom Integration."""
    async_add_entities([CustomSwitch(hass, config_entry.entry_id)], True)


class CustomSwitch(SwitchEntity):
    """Representation of a Custom Switch."""

    def __init__(self, hass: HomeAssistant, entry_id: str):
        """Initialize the switch."""
        self._hass = hass
        self._entry_id = entry_id
        self._data = hass.data[DOMAIN][self._entry_id]
        self._state: IntegrationState = self._data["state"]

        self._data["switch"] = self

        self._attr_name = (
            f"Enable Wrapper for {self._data['conf']['wrapped_climate_id']}"
        )
        self._attr_unique_id = (
            f"enable_{self._data['conf']['friendly_name'].replace(' ', '_').lower()}"
        )

    @property
    def name(self):
        """Return the name of the switch."""
        return self._attr_name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._attr_unique_id

    @property
    def is_on(self):
        """Return the state of the switch."""
        return self._state.enable

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        self._state.enable = True
        await self._data["logic"].update()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        self._state.enable = False
        self.async_write_ha_state()
