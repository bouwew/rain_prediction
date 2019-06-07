from homeassistant.helpers.entity import Entity
from homeassistant.const import (CONF_NAME)
import logging
import time
from datetime import timedelta
from homeassistant.util import Throttle

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=5)
ATTR_DATA = 'Data'
ATTR_TOTAL = 'Total'
ATTR_AVERAGE = 'Average'
ATTR_TIMEFRAME = 'Timeframe'
ATTR_UPDATED = 'Update'
CONF_TIMEFRAME = 'timeframe'

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the buienradar rain platform."""
    name = config.get(CONF_NAME)
    latitude = hass.config.latitude
    longitude = hass.config.longitude
    timeframe = config.get(CONF_TIMEFRAME)
    add_devices([BuienradarRainSensor(name, latitude, longitude, timeframe)])

class BuienradarRainSensor(Entity):
    """Representation of a Sensor."""
    def __init__(self, name, latitude, longitude, timeframe):
        """Initialize the sensor."""
        import pybuienradar
        self._buienradar = pybuienradar.forecast(
            latitude, longitude)
        self._timeframe = timeframe
        self._state = None
        self._name = name
        self._unit_of_measurement = 'mm/h'
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        """bouwew: added ATTR_DATA: self.data_array to show the list of obtained data in the sensor"""
        if self.data is not None:
            return {
                ATTR_DATA: self.data_array, 
                ATTR_TOTAL: self.data['totalrain'] ,
                ATTR_AVERAGE: self.data['averagerain'],
                ATTR_TIMEFRAME: self.data['timeframe'],
                ATTR_UPDATED: self.data['time']
            }

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data and updates the state."""
        now = time.strftime("%H:%M")
        self.data = self._buienradar.get_forecast(now, self._timeframe)
        """bouwew: also output the obtained data"""
        self.data_array = self._buienradar.get_forecast_data()
        self._state = self.data["averagerain"]
