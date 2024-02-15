from dataclasses import dataclass
from homeassistant.components.climate.const import (
    HVACMode,
    HVACAction,
    ATTR_HVAC_ACTION,
    ATTR_CURRENT_TEMPERATURE,
)
from homeassistant.core import HomeAssistant
from homeassistant.const import ATTR_TEMPERATURE

from enum import StrEnum


@dataclass
class IntegrationState:
    enable: bool

    hvac_mode: HVACMode
    hvac_action: HVACAction
    temperature: float
    target_temperature: float

    @property
    def heating(self):
        return self.hvac_action == HVACAction.HEATING


class ClimateState:
    _hass: HomeAssistant

    entity_id: str
    hvac_mode: HVACMode
    hvac_action: HVACAction
    temperature: float
    target_temperature: float

    def __init__(self, hass: HomeAssistant, entity_id: str) -> None:
        self._hass = hass
        self.entity_id = entity_id

    @property
    def state(self):
        return self._hass.states.get(self.entity_id)

    @property
    def hvac_mode(self):
        return self.state.state

    @property
    def hvac_action(self):
        return self.state.attributes.get(ATTR_HVAC_ACTION)

    @property
    def temperature(self):
        return float(self.state.attributes.get(ATTR_CURRENT_TEMPERATURE))

    @property
    def target_temperature(self):
        return float(self.state.attributes.get(ATTR_TEMPERATURE))

    @property
    def difference(self):
        return self.target_temperature - self.temperature


class SensorState(StrEnum):
    NORMAL = "Normal Operation"
    EXTERNAL_CHANGE = "External Change Detected"
