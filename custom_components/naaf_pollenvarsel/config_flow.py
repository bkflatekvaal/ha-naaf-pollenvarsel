"""Config flow for NAAF Pollenvarsel."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig

from .api import NaafPollenApi, NaafPollenApiError, NaafPollenAuthError
from .const import CONF_DEVICE_KEY, CONF_REGION, DOMAIN, REGIONS


async def _validate(hass: HomeAssistant, data: dict) -> None:
    api = NaafPollenApi(
        async_get_clientsession(hass),
        data[CONF_DEVICE_KEY],
        data[CONF_API_KEY],
    )
    await api.async_get_forecast()


class NaafPollenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the NAAF Pollenvarsel config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle initial setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_REGION])
            self._abort_if_unique_id_configured()
            try:
                await _validate(self.hass, user_input)
            except NaafPollenAuthError:
                errors["base"] = "invalid_auth"
            except NaafPollenApiError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=REGIONS[user_input[CONF_REGION]],
                    data=user_input,
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): str,
                vol.Required(CONF_DEVICE_KEY): str,
                vol.Required(CONF_REGION, default="rogaland"): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            {"value": key, "label": name}
                            for key, name in REGIONS.items()
                        ],
                        mode="dropdown",
                    )
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
