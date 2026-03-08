from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from rehabi.calibration_dz import get_wilaya_calibration


@dataclass
class ClimateData:
    zone: str
    hdd18: float
    cdd26: float
    annual_horizontal_solar_kwh_m2: float
    heating_gains_utilization: float = 0.70
    cooling_gains_fraction: float = 0.45


CITY_CLIMATE: Dict[str, ClimateData] = {
    "paris": ClimateData(zone="H1a", hdd18=2400, cdd26=80, annual_horizontal_solar_kwh_m2=1150),
    "lille": ClimateData(zone="H1a", hdd18=2600, cdd26=60, annual_horizontal_solar_kwh_m2=1050),
    "strasbourg": ClimateData(zone="H1b", hdd18=2500, cdd26=90, annual_horizontal_solar_kwh_m2=1150),
    "lyon": ClimateData(zone="H1c", hdd18=2100, cdd26=150, annual_horizontal_solar_kwh_m2=1300),
    "nantes": ClimateData(zone="H2b", hdd18=1900, cdd26=60, annual_horizontal_solar_kwh_m2=1200),
    "bordeaux": ClimateData(zone="H2c", hdd18=1700, cdd26=120, annual_horizontal_solar_kwh_m2=1300),
    "marseille": ClimateData(zone="H3", hdd18=1200, cdd26=260, annual_horizontal_solar_kwh_m2=1550),
    "nice": ClimateData(zone="H3", hdd18=1000, cdd26=220, annual_horizontal_solar_kwh_m2=1600),
    "toulouse": ClimateData(zone="H2d", hdd18=1600, cdd26=180, annual_horizontal_solar_kwh_m2=1400),
}


ZONE_DEFAULT: Dict[str, ClimateData] = {
    "H1a": ClimateData(zone="H1a", hdd18=2450, cdd26=75, annual_horizontal_solar_kwh_m2=1120),
    "H1b": ClimateData(zone="H1b", hdd18=2500, cdd26=85, annual_horizontal_solar_kwh_m2=1140),
    "H1c": ClimateData(zone="H1c", hdd18=2200, cdd26=120, annual_horizontal_solar_kwh_m2=1230),
    "H2b": ClimateData(zone="H2b", hdd18=1900, cdd26=80, annual_horizontal_solar_kwh_m2=1250),
    "H2c": ClimateData(zone="H2c", hdd18=1750, cdd26=120, annual_horizontal_solar_kwh_m2=1320),
    "H2d": ClimateData(zone="H2d", hdd18=1650, cdd26=170, annual_horizontal_solar_kwh_m2=1380),
    "H3": ClimateData(zone="H3", hdd18=1100, cdd26=240, annual_horizontal_solar_kwh_m2=1570),
}


def get_climate(city: str, zone: str | None, country: str = "France") -> ClimateData:
    country_key = country.strip().lower()
    city_key = city.strip().lower()
    if country_key in {"algeria", "algerie", "dz"}:
        wilaya = get_wilaya_calibration(city_key)
        if wilaya:
            return ClimateData(
                zone=f"DZ-{wilaya.wilaya}",
                hdd18=wilaya.hdd18,
                cdd26=wilaya.cdd26,
                annual_horizontal_solar_kwh_m2=wilaya.annual_horizontal_solar_kwh_m2,
                heating_gains_utilization=wilaya.heating_gains_utilization,
                cooling_gains_fraction=wilaya.cooling_gains_fraction,
            )
        return ClimateData(
            zone="DZ-default",
            hdd18=1200,
            cdd26=450,
            annual_horizontal_solar_kwh_m2=1900,
            heating_gains_utilization=0.62,
            cooling_gains_fraction=0.58,
        )
    if city_key in CITY_CLIMATE:
        return CITY_CLIMATE[city_key]
    if zone and zone in ZONE_DEFAULT:
        return ZONE_DEFAULT[zone]
    return ZONE_DEFAULT["H2b"]


def orientation_factor(orientation: str) -> float:
    key = orientation.strip().lower()
    if key.startswith("s"):
        return 1.15
    if key.startswith("e") or key.startswith("w"):
        return 0.95
    if key.startswith("n"):
        return 0.65
    return 0.9
