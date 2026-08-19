"""Constants for NAAF Pollenvarsel."""
from __future__ import annotations

from datetime import timedelta

DOMAIN = "naaf_pollenvarsel"
NAME = "NAAF Pollenvarsel"

API_BASE_URL = "https://apigw.temalogic.com/naaf-prod/pollen-api"
API_FORECAST_PATH = "/pollen/allRegionsForecast"

CONF_REGION = "region"
CONF_DEVICE_KEY = "device_key"
CONF_API_KEY = "api_key"

DEFAULT_SCAN_INTERVAL = timedelta(hours=1)
CONF_POLL_INTERVAL = "poll_interval"
DEFAULT_POLL_INTERVAL_MINUTES = 60
MIN_POLL_INTERVAL_MINUTES = 15
MAX_POLL_INTERVAL_MINUTES = 1440

REGIONS: dict[str, str] = {
    "ostlandetMedOslo": "Østlandet med Oslo",
    "sorlandet": "Sørlandet",
    "rogaland": "Rogaland",
    "hordaland": "Hordaland",
    "sognOgFjordane": "Sogn og Fjordane",
    "moreOgRomsdal": "Møre og Romsdal",
    "indreOstlandet": "Indre Østlandet",
    "sentraleFjellstrokISorNorge": "Sentrale fjellstrøk i Sør-Norge",
    "trondelag": "Trøndelag",
    "nordland": "Nordland",
    "troms": "Troms",
    "finnmark": "Finnmark",
}

POLLEN_TYPES: dict[str, str] = {
    "bjork": "Bjørk",
    "burot": "Burot",
    "gress": "Gress",
    "hassel": "Hassel",
    "or": "Or",
    "salix": "Salix",
}

DISTRIBUTION_NAMES: dict[int, str] = {
    0: "Ingen",
    1: "Beskjeden",
    2: "Moderat",
    3: "Kraftig",
    4: "Ekstrem",
}
