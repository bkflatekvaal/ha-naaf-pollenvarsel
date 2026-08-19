"""NAAF Pollenvarsel integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NaafPollenApi, NaafPollenApiError, NaafPollenAuthError
from .const import CONF_API_KEY, CONF_DEVICE_KEY, DOMAIN
from .coordinator import NaafPollenCoordinator

PLATFORMS = [Platform.SENSOR]

type NaafConfigEntry = ConfigEntry[NaafPollenCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: NaafConfigEntry) -> bool:
    """Set up NAAF Pollenvarsel from a config entry."""
    api = NaafPollenApi(
        async_get_clientsession(hass),
        entry.data[CONF_DEVICE_KEY],
        entry.data.get(CONF_API_KEY),
    )
    coordinator = NaafPollenCoordinator(hass, api)

    try:
        await coordinator.async_config_entry_first_refresh()
    except NaafPollenAuthError as err:
        raise ConfigEntryAuthFailed(str(err)) from err
    except NaafPollenApiError as err:
        raise ConfigEntryNotReady(str(err)) from err

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: NaafConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
