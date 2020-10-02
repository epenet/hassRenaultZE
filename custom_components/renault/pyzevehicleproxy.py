"""Proxy to handle account communication with Renault servers via PyZE."""
from datetime import timedelta
import logging

from pyze.api import Vehicle

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, MODEL_SUPPORTS_LOCATION

DEFAULT_SCAN_INTERVAL = timedelta(seconds=60)
LONG_SCAN_INTERVAL = timedelta(minutes=10)

LOGGER = logging.getLogger(__name__)


class PyzeVehicleProxy:
    """Handle vehicle communication with Renault servers via PyZE."""

    def __init__(self, hass, vehicle_link, pyze_vehicle: Vehicle):
        """Initialise vehicle proxy."""
        self.hass = hass
        self._vehicle_link = vehicle_link
        self._pyze_vehicle = pyze_vehicle
        self._device_info = None
        self.coordinators = {}
        self.async_initialise = self._async_initialise()
        self.hvac_target_temperature = 21

    @property
    def device_info(self):
        """Return a device description for device registry."""
        return self._device_info

    @property
    def registration(self):
        """Return the registration of the vehicle."""
        return self._vehicle_link["vehicleDetails"]["registrationNumber"]

    @property
    def vin(self):
        """Return the VIN of the vehicle."""
        return self._vehicle_link["vin"]

    async def _async_initialise(self):
        """Load available sensors."""
        brand = self._vehicle_link["brand"]
        model_label = self._vehicle_link["vehicleDetails"]["model"]["label"]
        registration_number = self._vehicle_link["vehicleDetails"]["registrationNumber"]
        model_code = self._vehicle_link["vehicleDetails"]["model"]["code"]
        self._device_info = {
            "identifiers": {(DOMAIN, self.vin)},
            "manufacturer": brand.capitalize(),
            "model": model_label.capitalize(),
            "name": registration_number,
            "sw_version": model_code,
        }

        self.coordinators["battery"] = DataUpdateCoordinator(
            self.hass,
            LOGGER,
            # Name of the data. For logging purposes.
            name=f"{self.vin} battery",
            update_method=self.get_battery_status,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.coordinators["mileage"] = DataUpdateCoordinator(
            self.hass,
            LOGGER,
            # Name of the data. For logging purposes.
            name=f"{self.vin} mileage",
            update_method=self.get_mileage,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=LONG_SCAN_INTERVAL,
        )
        self.coordinators["charge_mode"] = DataUpdateCoordinator(
            self.hass,
            LOGGER,
            # Name of the data. For logging purposes.
            name=f"{self.vin} charge_mode",
            update_method=self.get_charge_mode,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.coordinators["hvac_status"] = DataUpdateCoordinator(
            self.hass,
            LOGGER,
            # Name of the data. For logging purposes.
            name=f"{self.vin} hvac_status",
            update_method=self.get_hvac_status,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        if model_code in MODEL_SUPPORTS_LOCATION:
            self.coordinators["location"] = DataUpdateCoordinator(
                self.hass,
                LOGGER,
                # Name of the data. For logging purposes.
                name=f"{self.vin} location",
                update_method=self.get_location,
                # Polling interval. Will only be polled if there are subscribers.
                update_interval=DEFAULT_SCAN_INTERVAL,
            )
        for key in self.coordinators:
            await self.coordinators[key].async_refresh()

    async def get_battery_status(self):
        """Get battery_status."""
        return await self.hass.async_add_executor_job(self._pyze_vehicle.battery_status)

    async def get_charge_mode(self):
        """Get charge_mode."""
        return await self.hass.async_add_executor_job(self._pyze_vehicle.charge_mode)

    async def get_hvac_status(self):
        """Get hvac_status."""
        return await self.hass.async_add_executor_job(self._pyze_vehicle.hvac_status)

    async def get_location(self):
        """Get location."""
        return await self.hass.async_add_executor_job(self._pyze_vehicle.location)

    async def get_mileage(self):
        """Get mileage."""
        return await self.hass.async_add_executor_job(self._pyze_vehicle.mileage)
