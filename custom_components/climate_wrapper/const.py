"""Constants for climate_wrapper."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "Climate Wrapper"
DOMAIN = "climate_wrapper"
VERSION = "0.1.0"

SAFETY_CHECK_TIMEOUT = 10
TEMPERATURE_DIFF = 1
TEMPERATURE_DIFF_TOLERANCE = 0.25

CONF_WRAPPED_CLIMATE = "wrapped_climate"
CONF_TEMPERATURE_SENSOR = "temperature_sensor"
CONF_TEMPERATURE_VARIANCE = "temperature_variance"
