"""NAAF Pollenvarsel integration."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NaafPollenApi, NaafPollenApiError, NaafPollenAuthError
from .const import (
    CONF_API_KEY,
    CONF_DEVICE_KEY,
    CONF_POLL_INTERVAL,
    DEFAULT_POLL_INTERVAL_MINUTES,
    DOMAIN,
)
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
    coordinator = NaafPollenCoordinator(
        hass,
        api,
        timedelta(
            minutes=entry.options.get(
                CONF_POLL_INTERVAL,
                DEFAULT_POLL_INTERVAL_MINUTES,
            )
        ),
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except NaafPollenAuthError as err:
        raise ConfigEntryAuthFailed(str(err)) from err
    except NaafPollenApiError as err:
        raise ConfigEntryNotReady(str(err)) from err

    entry.runtime_data = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_reload_entry(hass: HomeAssistant, entry: NaafConfigEntry) -> None:
    """Reload an entry when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: NaafConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
