"""Config flow for NAAF Pollenvarsel."""
from __future__ import annotations

import uuid

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig

from .api import NaafPollenApi, NaafPollenApiError, NaafPollenAuthError
from .const import (
    CONF_DEVICE_KEY,
    CONF_POLL_INTERVAL,
    CONF_REGION,
    DEFAULT_POLL_INTERVAL_MINUTES,
    DOMAIN,
    MAX_POLL_INTERVAL_MINUTES,
    MIN_POLL_INTERVAL_MINUTES,
    REGIONS,
)


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

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Return the options flow handler."""
        return NaafPollenOptionsFlow()

    async def async_step_user(self, user_input=None):
        """Handle initial setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Match the Android app: generate the device key once and persist
            # it in the config entry after successful validation.
            user_input[CONF_DEVICE_KEY] = str(uuid.uuid4())

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


class NaafPollenOptionsFlow(config_entries.OptionsFlow):
    """Handle configurable integration options."""

    async def async_step_init(self, user_input=None):
        """Configure the polling interval."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_POLL_INTERVAL,
            DEFAULT_POLL_INTERVAL_MINUTES,
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_POLL_INTERVAL,
                        default=current_interval,
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(
                            min=MIN_POLL_INTERVAL_MINUTES,
                            max=MAX_POLL_INTERVAL_MINUTES,
                        ),
                    )
                }
            ),
        )
