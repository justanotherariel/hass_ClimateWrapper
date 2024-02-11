"""Platform for climate integration."""
from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
import logging

from .state import IntegrationState
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the climate entity for Climate Wrapper."""
    async_add_entities([ClimateWrapperEntity(hass, config_entry.entry_id)], True)


class ClimateWrapperEntity(ClimateEntity):
    """Representation of a Climate Wrapper entity."""

    def __init__(self, hass: HomeAssistant, entry_id: str):
        """Initialize the Climate Wrapper."""
        self._hass = hass
        self._entry_id = entry_id
        self._data = hass.data[DOMAIN][self._entry_id]
        self._state: IntegrationState = self._data["state"]

        self._data["climate"] = self

        self._attr_name = self._data["conf"]["friendly_name"]
        self._attr_unique_id = self._attr_name.replace(" ", "_").lower()
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.AUTO, HVACMode.HEAT]

    @property
    def name(self):
        """Return the name of the entity."""
        return self._attr_name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._attr_unique_id

    @property
    def should_poll(self):
        return False

    @property
    def hvac_action(self):
        """Return the current HVAC action."""
        return self._state.hvac_action

    @property
    def hvac_mode(self):
        """Return the current HVAC mode."""
        return self._state.hvac_mode

    @property
    def hvac_modes(self):
        """Return the list of available HVAC modes."""
        return self._attr_hvac_modes

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._state.temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._state.target_temperature

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        target_temp = kwargs.get(ATTR_TEMPERATURE)
        if target_temp is not None:
            self._state.target_temperature = target_temp
            await self._data["logic"].update()
        else:
            _LOGGER.error("No target temperature provided")

    async def async_set_hvac_mode(self, hvac_mode: HVACMode):
        """Set new target HVAC mode."""
        self._state.hvac_mode = hvac_mode
        await self._data["logic"].update()
