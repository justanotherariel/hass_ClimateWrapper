"""Config flow for Climate Wrapper integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_FRIENDLY_NAME
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.climate import DOMAIN as CLIMATE_DOMAIN
from homeassistant.helpers import selector


from .const import (
    DOMAIN,
    CONF_WRAPPED_CLIMATE,
    CONF_TEMPERATURE_SENSOR,
    CONF_TEMPERATURE_VARIANCE,
)


class ClimateWrapperConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Climate Wrapper."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ClimateWrapperOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Validate user input and proceed with setup
            return self.async_create_entry(title="Climate Wrapper", data=user_input)

        # Input schema for the user configuration
        data_schema = vol.Schema(
            {
                vol.Required(CONF_FRIENDLY_NAME): str,
                vol.Required(CONF_WRAPPED_CLIMATE): selector.selector(
                    {"entity": {"domain": CLIMATE_DOMAIN}}
                ),
                vol.Required(CONF_TEMPERATURE_SENSOR): selector.selector(
                    {"entity": {"domain": SENSOR_DOMAIN, "device_class": "temperature"}}
                ),
                vol.Required(CONF_TEMPERATURE_VARIANCE): float,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )


class ClimateWrapperOptionsFlowHandler(config_entries.OptionsFlow):
    """Climate Wrapper config flow options handler."""

    def __init__(self, config_entry):
        """Initialize Climate Wrapper options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle an options flow for Climate Wrapper."""
        errors = {}

        if user_input is not None:
            # Update the configuration entry
            return self.async_create_entry(title="", data=user_input)

        # Prepare the default values for the form
        current_config = self.config_entry.options or self.config_entry.data
        default_name = current_config.get(CONF_FRIENDLY_NAME, "")
        default_wrapped_climate = current_config.get(CONF_WRAPPED_CLIMATE, "")
        default_temperature_sensor = current_config.get(CONF_TEMPERATURE_SENSOR, "")
        default_temperature_variance = current_config.get(
            CONF_TEMPERATURE_VARIANCE, 0.0
        )

        # Input schema for the user configuration
        data_schema = vol.Schema(
            {
                vol.Required(CONF_FRIENDLY_NAME, default=default_name): str,
                vol.Required(
                    CONF_WRAPPED_CLIMATE, default=default_wrapped_climate
                ): selector.selector({"entity": {"domain": CLIMATE_DOMAIN}}),
                vol.Required(
                    CONF_TEMPERATURE_SENSOR, default=default_temperature_sensor
                ): selector.selector(
                    {"entity": {"domain": SENSOR_DOMAIN, "device_class": "temperature"}}
                ),
                vol.Required(
                    CONF_TEMPERATURE_VARIANCE, default=default_temperature_variance
                ): float,
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=data_schema, errors=errors
        )
