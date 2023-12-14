""" Climate Wrapper for Home Assistant. """
from __future__ import annotations

import asyncio
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    Platform,
    CONF_FRIENDLY_NAME,
)
import logging

from .logic import Logic
from .state import IntegrationState
from .const import (
    DOMAIN,
    CONF_WRAPPED_CLIMATE,
    CONF_TEMPERATURE_SENSOR,
    CONF_TEMPERATURE_VARIANCE,
)

from homeassistant.components.climate.const import HVACAction, HVACMode


_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.SENSOR, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Climate Wrapper from a config entry."""

    # Initialize the shared Data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "conf": {
            "friendly_name": entry.data[CONF_FRIENDLY_NAME],
            "wrapped_climate_id": entry.data[CONF_WRAPPED_CLIMATE],
            "temperature_sensor_id": entry.data[CONF_TEMPERATURE_SENSOR],
            "temperature_variance": entry.data[CONF_TEMPERATURE_VARIANCE],
        },
        "state": IntegrationState(
            enable=True,
            hvac_action=HVACAction.IDLE,
            hvac_mode=HVACMode.AUTO,
            temperature=None,
            target_temperature=20.0,
        ),
        "logic": None,
        "climate": None,
        "sensor": None,
        "switch": None,
        "callbacks": [],
    }

    # Check for availability of entities
    wrapped_climate_id = entry.data[CONF_WRAPPED_CLIMATE]
    temperature_sensor_id = entry.data[CONF_TEMPERATURE_SENSOR]

    async def entity_available(entity_id: str) -> bool:
        """Wait until an entity is available."""

        MAX_TIMEOUT = 60
        timeout = 0
        while not hass.states.get(entity_id):
            timeout += 1
            if timeout >= MAX_TIMEOUT:
                return False
            await asyncio.sleep(0.5)
        return True

    await asyncio.gather(
        entity_available(wrapped_climate_id), entity_available(temperature_sensor_id)
    )

    # Init Logic
    hass.data[DOMAIN][entry.entry_id]["logic"] = Logic(hass, entry)

    # Init Components
    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Retrieve the list of callbacks
    callback_list = hass.data[DOMAIN][entry.entry_id].get("callbacks", [])

    # Loop over the callback list and cancel each
    for cancel_callback in callback_list:
        if callable(cancel_callback):
            cancel_callback()

    # Clean up the data
    hass.data[DOMAIN].pop(entry.entry_id)

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
