"""Sensors for NAAF Pollenvarsel."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import CONF_REGION, DISTRIBUTION_NAMES, POLLEN_TYPES, REGIONS
from .coordinator import NaafPollenCoordinator
from .entity import NaafPollenEntity

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class NaafPollenSensorDescription(SensorEntityDescription):
    pollen_id: str


SENSORS = tuple(
    NaafPollenSensorDescription(
        key=pollen_id,
        pollen_id=pollen_id,
        icon="mdi:flower-pollen",
    )
    for pollen_id in POLLEN_TYPES
)


def _region_for_day(day: dict[str, Any], region_id: str) -> dict[str, Any] | None:
    for region in day.get("regions", []):
        if region.get("id") == region_id:
            return region
    return None


def _pollen(region: dict[str, Any] | None, pollen_id: str) -> dict[str, Any] | None:
    if not region:
        return None
    for item in region.get("pollentypes", []):
        if item.get("id") == pollen_id:
            return item
    return None


def _level(value: Any) -> str:
    try:
        return DISTRIBUTION_NAMES.get(int(value), f"Ukjent ({value})")
    except (TypeError, ValueError):
        return "Under behandling"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[NaafPollenCoordinator],
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    region_id = entry.data[CONF_REGION]

    entities: list[SensorEntity] = [
        NaafPollenSensor(coordinator, region_id, description)
        for description in SENSORS
    ]
    entities.append(NaafPollenForecastSensor(coordinator, region_id))
    async_add_entities(entities)


class NaafPollenSensor(NaafPollenEntity, SensorEntity):
    """Pollen level for one pollen type."""

    entity_description: NaafPollenSensorDescription

    def __init__(
        self,
        coordinator: NaafPollenCoordinator,
        region_id: str,
        description: NaafPollenSensorDescription,
    ) -> None:
        super().__init__(coordinator, region_id)
        self.entity_description = description
        self._attr_has_entity_name = False
        self._attr_name = POLLEN_TYPES[description.pollen_id]
        # Keep the region in the suggested entity_id while showing only the pollen type in the UI.
        self._attr_suggested_object_id = f"{region_id}_{description.pollen_id}"
        self._attr_unique_id = f"{region_id}_{description.pollen_id}"

    @property
    def native_value(self) -> str | None:
        if not self.coordinator.data:
            return None
        region = _region_for_day(self.coordinator.data[0], self.region_id)
        pollen = _pollen(region, self.entity_description.pollen_id)
        return _level(pollen.get("distribution")) if pollen else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or []
        attrs: dict[str, Any] = {
            "region": REGIONS.get(self.region_id, self.region_id),
            "pollen_type": POLLEN_TYPES[self.entity_description.pollen_id],
        }

        if data:
            today_region = _region_for_day(data[0], self.region_id)
            today = _pollen(today_region, self.entity_description.pollen_id)
            attrs["date"] = data[0].get("date")
            if today:
                attrs["distribution"] = today.get("distribution")
                attrs["text_forecast"] = today.get("textForecast")

        if len(data) > 1:
            tomorrow_region = _region_for_day(data[1], self.region_id)
            tomorrow = _pollen(tomorrow_region, self.entity_description.pollen_id)
            attrs["tomorrow_date"] = data[1].get("date")
            if tomorrow:
                attrs["tomorrow_distribution"] = tomorrow.get("distribution")
                attrs["tomorrow_level"] = _level(tomorrow.get("distribution"))
                attrs["tomorrow_text_forecast"] = tomorrow.get("textForecast")

        return attrs


class NaafPollenForecastSensor(NaafPollenEntity, SensorEntity):
    """General text forecast for one region."""

    _attr_icon = "mdi:text-box-outline"

    def __init__(self, coordinator: NaafPollenCoordinator, region_id: str) -> None:
        super().__init__(coordinator, region_id)
        self._attr_has_entity_name = False
        self._attr_name = "Pollenvarsel"
        self._attr_suggested_object_id = f"{region_id}_pollenvarsel"
        self._attr_unique_id = f"{region_id}_pollenvarsel"

    @property
    def native_value(self) -> str | None:
        if not self.coordinator.data:
            return None
        region = _region_for_day(self.coordinator.data[0], self.region_id)
        return region.get("textForecast") if region else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or []
        attrs: dict[str, Any] = {
            "region": REGIONS.get(self.region_id, self.region_id),
        }

        if data:
            attrs["date"] = data[0].get("date")

        if len(data) > 1:
            tomorrow_region = _region_for_day(data[1], self.region_id)
            attrs["tomorrow_date"] = data[1].get("date")
            if tomorrow_region:
                attrs["tomorrow_text_forecast"] = tomorrow_region.get("textForecast")

        return attrs
