"""Climate Wrapper Logic."""
from __future__ import annotations

from datetime import timedelta
from homeassistant.core import HomeAssistant, Event, Context
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.components.climate import HVACAction
from homeassistant.components.persistent_notification import (
    async_create as async_create_notification,
    async_dismiss as async_dismiss_notification,
)
from homeassistant.components.climate.const import HVACMode
from homeassistant.const import ATTR_TEMPERATURE
import logging
import math

from .state import IntegrationState, ClimateState
from .const import (
    DOMAIN,
    SAFETY_CHECK_TIMEOUT,
    TEMPERATURE_DIFF,
    TEMPERATURE_DIFF_TOLERANCE,
)

_LOGGER = logging.getLogger(__name__)


class Logic:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self._hass = hass
        self._entry_id = entry.entry_id
        self._data = hass.data[DOMAIN][self._entry_id]
        self._state: IntegrationState = self._data["state"]

        # Save important entities
        self._wrapped_climate_id = self._data["conf"]["wrapped_climate_id"]
        self._wrapped_climate = ClimateState(hass, self._wrapped_climate_id)
        self._temperature_sensor_id = self._data["conf"]["temperature_sensor_id"]

        # Internal States
        self._last_context = None
        self._safety_check_timeout = 0
        self._offset = 1  # In °C

        # Update Temperature
        self._state.temperature = float(
            self._hass.states.get(self._temperature_sensor_id).state
        )

        # Setup Climate Listener
        self._data["callbacks"].append(
            async_track_state_change_event(
                hass, [self._wrapped_climate_id], self._wrapped_climate_state_change
            )
        )

        # Setup Temperature Sensor Listener
        self._data["callbacks"].append(
            async_track_state_change_event(
                hass,
                [self._temperature_sensor_id],
                self._temperature_sensor_state_change,
            )
        )

        # Periodic Safety Check
        self._data["callbacks"].append(
            async_track_time_interval(
                self._hass, self._periodic_safety_check, timedelta(minutes=1)
            )
        )

        self._hass.add_job(self.update)

    #
    # Callbacks
    #

    async def _wrapped_climate_state_change(self, event: Event):
        """Handle state changes of the wrapped climate entity."""
        new_state = event.data.get("new_state")
        if new_state is None:
            return

        # Target Temperature Changed
        new_target_temp = new_state.attributes.get(ATTR_TEMPERATURE)
        if (
            new_target_temp != self._state.target_temperature
            and event.context != self._last_context
        ):
            async_create_notification(
                self._hass,
                title="Climate Wrapper | External Temperature Change",
                message=f"Climate target temperature change (to {new_target_temp}) detected.",
            )
            self._hass.async_add_job(self._data["sensor"].external_change)

        await self.update()

    async def _temperature_sensor_state_change(self, event: Event):
        """Handle state changes of the temperature sensor."""
        new_state = event.data.get("new_state")
        if new_state is None:
            return

        # Set current temperature
        if new_state.state is not None:
            self._state.temperature = float(new_state.state)

        await self.update()

    async def _periodic_safety_check(self, _):
        """Evaluate the current state and check if everything is functioning correctly."""
        error = False

        # Check HVACAction
        if self._state.hvac_action != self._wrapped_climate.hvac_action:
            if self._safety_check_timeout >= SAFETY_CHECK_TIMEOUT:
                error = True
                async_create_notification(
                    self._hass,
                    title="Climate Wrapper | Safety Check",
                    message=f"""
                        Safety check failed: Heating Action mismatch.
                        -> Currently {self._wrapped_climate.hvac_action}
                        -> Should be {self._state.hvac_action}
                        Please check manually.""",
                    notification_id="climate_wrapper.safety_check_action",
                )

        # Check TargetTemperature-Temperature Difference
        expected_diff = TEMPERATURE_DIFF * (1 if self._state.heating else -1)
        if not math.isclose(
            expected_diff,
            self._wrapped_climate.difference,
            abs_tol=TEMPERATURE_DIFF_TOLERANCE,
        ):
            error = True
            if self._safety_check_timeout >= SAFETY_CHECK_TIMEOUT:
                async_create_notification(
                    self._hass,
                    title="Climate Wrapper | Safety Check",
                    message=f"""
                        Safety check failed: Temperature Difference mismatch.
                        -> Current Temperature: {self._wrapped_climate.temperature}
                        -> Target Temperature: {self._wrapped_climate.target_temperature}
                        -> Should be: {self._wrapped_climate.temperature + expected_diff}
                        Please check manually.""",
                    notification_id="climate_wrapper.safety_check_difference",
                )

        # Increase Timeout
        if error:
            self._safety_check_timeout += 1
        else:
            async_dismiss_notification(
                self._hass, "climate_wrapper.safety_check_action"
            )
            async_dismiss_notification(
                self._hass, "climate_wrapper.safety_check_difference"
            )
            self._safety_check_timeout = 0

    #
    # Control Functions
    #

    async def update(self):
        if self._state.hvac_mode == HVACMode.OFF:
            self.hvac_action = HVACAction.IDLE

        elif self._state.hvac_mode == HVACMode.HEAT:
            self.hvac_action = HVACAction.HEATING

        elif self._state.hvac_mode == HVACMode.AUTO:
            await self._update_action_via_auto()

        await self._set_wrapped_climate()

        if self._data["climate"] is not None:
            self._data["climate"].async_write_ha_state()
        if self._data["sensor"] is not None:
            self._data["sensor"].async_write_ha_state()

    async def _set_wrapped_climate(self):
        # Check if update is necessary
        expected_diff = TEMPERATURE_DIFF * (1 if self._state.heating else -1)
        if not math.isclose(
            expected_diff,
            self._wrapped_climate.difference,
            abs_tol=TEMPERATURE_DIFF_TOLERANCE,
        ):
            self._last_context = Context()

            # Update Wrapped Climate to reflect status
            await self._hass.services.async_call(
                "climate",
                "set_temperature",
                {
                    "entity_id": self._wrapped_climate_id,
                    "temperature": self._wrapped_climate.temperature + expected_diff,
                },
                context=self._last_context,
            )

    async def _update_action_via_auto(self):
        # If heating -> Does it need to be turned off?
        if self._state.heating:
            max_temp = (
                self._state.target_temperature
                + self._data["conf"]["temperature_variance"]
            )
            if self._state.temperature > max_temp:
                self._state.hvac_action = HVACAction.IDLE

        # If not heating -> Does it need to be turned on?
        else:
            min_temp = (
                self._state.target_temperature
                - self._data["conf"]["temperature_variance"]
            )
            if self._state.temperature < min_temp:
                self._state.hvac_action = HVACAction.HEATING
