"""API client for NAAF Pollenvarsel."""
from __future__ import annotations

from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession

from .const import API_BASE_URL, API_FORECAST_PATH


class NaafPollenApiError(Exception):
    """Base API error."""


class NaafPollenAuthError(NaafPollenApiError):
    """Authentication error."""


class NaafPollenApi:
    """Small async client for the Temalogic/NAAF pollen endpoint."""

    def __init__(
        self,
        session: ClientSession,
        device_key: str,
        api_key: str | None = None,
    ) -> None:
        self._session = session
        self._device_key = device_key
        self._api_key = api_key

    @property
    def headers(self) -> dict[str, str]:
        """Return the headers used by the Android app's pollen request."""
        return {
            "AppKey": self._api_key or "",
            "DeviceKey": self._device_key,
        }

    async def async_get_forecast(self) -> list[dict[str, Any]]:
        url = f"{API_BASE_URL}{API_FORECAST_PATH}"
        try:
            async with self._session.get(
                url,
                headers=self.headers,
                timeout=20,
            ) as response:
                if response.status in (401, 403):
                    raise NaafPollenAuthError(
                        f"API rejected credentials/device key ({response.status})"
                    )
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except NaafPollenAuthError:
            raise
        except (ClientResponseError, ClientError, TimeoutError) as err:
            raise NaafPollenApiError(str(err)) from err

        # PowerShell ConvertTo-Json can show a wrapper named 'value', but the
        # HTTP endpoint normally returns the forecast array directly. Accept
        # both shapes to make the client tolerant.
        if isinstance(payload, dict):
            if isinstance(payload.get("value"), list):
                payload = payload["value"]
            elif isinstance(payload.get("data"), list):
                payload = payload["data"]

        if not isinstance(payload, list):
            raise NaafPollenApiError("Unexpected API response format")
        return payload
