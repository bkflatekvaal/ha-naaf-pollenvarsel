# ha-naaf-pollenvarsel

Custom Home Assistant integration for pollen forecasts from Norges Astma- og Allergiforbund (NAAF).

## Status

Early development version. The integration uses the API endpoint discovered in the NAAF Pollenvarsel Android app:

`https://apigw.temalogic.com/naaf-prod/pollen-api/pollen/allRegionsForecast`

The Android app generates its `deviceKey` with a random UUID and stores/reuses it. The config flow therefore creates a UUID automatically.

## Installation

### HACS custom repository

1. Add this GitHub repository to HACS as an **Integration** custom repository.
2. Install **NAAF Pollenvarsel**.
3. Restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration → NAAF Pollenvarsel**.
5. Enter the API key, select a region, and finish setup.

## Configuration

Open the integration's **Configure** dialog to change its polling interval. The default is 60 minutes, and the supported range is 15 to 1440 minutes. Each configured region has its own interval.

### Manual

Copy `custom_components/naaf_pollenvarsel` to the `custom_components` directory in your Home Assistant config folder and restart Home Assistant.

## Entities

One sensor is created for each pollen type:

- Bjørk
- Burot
- Gress
- Hassel
- Or
- Salix

The state is the current forecast level:

| distribution | State |
|---:|---|
| 0 | Ingen spredning |
| 1 | Beskjeden spredning |
| 2 | Moderat spredning |
| 3 | Kraftig spredning |
| 4 | Ekstrem spredning |

Each entity also exposes the numeric `distribution`, forecast text and tomorrow's forecast as attributes.

## Authentication note

The Android app sends the configured API key in the `AppKey` header and its persistent UUID in the `DeviceKey` header. The config flow generates and persists the device key automatically.

## Data source

NAAF / Temalogic pollen forecast API. This project is unofficial and is not affiliated with NAAF or Temalogic.
