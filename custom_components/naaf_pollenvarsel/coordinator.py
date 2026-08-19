"""Data coordinator for NAAF Pollenvarsel."""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NaafPollenApi, NaafPollenApiError, NaafPollenAuthError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN


class NaafPollenCoordinator(DataUpdateCoordinator[list[dict[str, Any]]]):
    """Fetch all regions in one coordinated request."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: NaafPollenApi,
        update_interval: timedelta = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        self.api = api
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> list[dict[str, Any]]:
        try:
            return await self.api.async_get_forecast()
        except NaafPollenAuthError:
            raise
        except NaafPollenApiError as err:
            raise UpdateFailed(f"Error communicating with NAAF pollen API: {err}") from err
