"""Platform for sensor integration."""
import asyncio
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from datetime import datetime, date


from .state import IntegrationState, SensorState
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the sensor for Climate Wrapper."""
    async_add_entities([ClimateWrapperSensor(hass, config_entry.entry_id)], True)


class ClimateWrapperSensor(SensorEntity):
    """Representation of a Climate Wrapper Sensor."""

    def __init__(self, hass: HomeAssistant, entry_id: str):
        """Initialize the sensor."""
        self._hass = hass
        self._entry_id = entry_id
        self._data = hass.data[DOMAIN][self._entry_id]
        self._state: IntegrationState = self._data["state"]

        self._data["sensor"] = self

        self._attr_name = (
            f"Last external change of {self._data['conf']['wrapped_climate_id']}"
        )
        self._attr_unique_id = (
            self._data["conf"]["friendly_name"].replace(" ", "_").lower()
        )
        self._attr_state: SensorState = SensorState.NORMAL
        self._attr_state_attributes = {"last_changed": "never"}

        # Interal States
        self._changes_today = 0
        self._last_reset = date.today()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._attr_unique_id

    @property
    def should_poll(self):
        return False

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._attr_state

    @property
    def state_attributes(self):
        """Return the state attributes of the sensor."""
        return self._attr_state_attributes

    async def external_change(self):
        # Reset the counter if a new day has started
        if date.today() > self._last_reset:
            self._changes_today = 0
            self._last_reset = date.today()

        self._changes_today += 1
        self._attr_state_attributes = {
            "last_changed": datetime.now().strftime("%a @ %H:%M"),
            "changes_today": self._changes_today,
        }

        self._attr_state = SensorState.EXTERNAL_CHANGE
        self.async_write_ha_state()
        await asyncio.sleep(1)
        self._attr_state = SensorState.NORMAL
        self.async_write_ha_state()
