"""Base entity for NAAF Pollenvarsel."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, REGIONS
from .coordinator import NaafPollenCoordinator


class NaafPollenEntity(CoordinatorEntity[NaafPollenCoordinator]):
    """Base entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: NaafPollenCoordinator, region_id: str) -> None:
        super().__init__(coordinator)
        self.region_id = region_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, region_id)},
            name=f"NAAF Pollenvarsel – {REGIONS.get(region_id, region_id)}",
            manufacturer="Norges Astma- og Allergiforbund",
            model="Pollenvarsel",
            configuration_url="https://pollenvarsel.naaf.no/charts/forecast",
        )
