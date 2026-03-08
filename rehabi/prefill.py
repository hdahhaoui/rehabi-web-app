from __future__ import annotations

from typing import Dict

from rehabi.calibration_dz import (
    ALGERIA_DEFAULT_CO2_KG_KWH,
    ALGERIA_DEFAULT_ENERGY_PRICES_DZD_KWH,
    get_wilaya_calibration,
)
from rehabi.profiles import PROFILE_DEFAULTS


def _period_from_year(year: int) -> str:
    if year < 1980:
        return "before_1980"
    if year <= 2000:
        return "1980_2000"
    return "recent"


def _building_key(building_type: str) -> str:
    key = building_type.strip().lower()
    if "app" in key:
        return "appartement"
    return "maison"


def prefill_defaults(building_type: str, year: int, wilaya: str, area_m2: float) -> Dict[str, object]:
    bkey = _building_key(building_type)
    period = _period_from_year(year)
    profile = PROFILE_DEFAULTS.get((bkey, period), PROFILE_DEFAULTS[("maison", "1980_2000")])
    calib = get_wilaya_calibration(wilaya)

    floors = 1 if bkey == "maison" else 1
    height = 2.8
    window_ratio = 0.18 if bkey == "maison" else 0.22
    wall_area = area_m2 * (2.2 if bkey == "maison" else 1.6)
    roof_area = area_m2 if bkey == "maison" else area_m2 * 0.6
    floor_area = area_m2
    window_area = area_m2 * window_ratio
    volume = area_m2 * height * floors

    if calib and calib.cdd26 > 900:
        default_cooling_cop = 3.2
        default_window_g = 0.45
    else:
        default_cooling_cop = 2.8
        default_window_g = 0.55

    return {
        "multicriteria_weights": {
            "energy": 0.25,
            "cost": 0.35,
            "co2": 0.25,
            "summer_comfort": 0.15,
        },
        "general": {
            "country": "Algeria",
            "city": wilaya,
            "climate_zone": "DZ",
            "building_type": bkey,
            "construction_year": year,
            "habitable_area_m2": area_m2,
            "floors": floors,
            "ceiling_height_m": height,
        },
        "geometry": {
            "wall_area_m2": round(wall_area, 1),
            "roof_area_m2": round(roof_area, 1),
            "floor_area_m2": round(floor_area, 1),
            "window_area_m2": round(window_area, 1),
            "orientation": "south",
            "volume_m3": round(volume, 1),
        },
        "envelope": {
            "walls": {"material": "Maconnerie", "thickness_m": 0.2, "u_value_w_m2k": profile["u_wall"]},
            "roof": {"material": "Toiture terrasse", "thickness_m": 0.2, "u_value_w_m2k": profile["u_roof"]},
            "floor": {"material": "Dalle beton", "thickness_m": 0.2, "u_value_w_m2k": profile["u_floor"]},
            "windows": {"material": "Vitrage courant", "thickness_m": 0.006, "u_value_w_m2k": profile["u_window"]},
            "window_solar_factor_g": default_window_g,
        },
        "ventilation": {
            "ventilation_type": "naturelle",
            "air_change_rate_ach": profile["ach"],
            "airtightness_level": "moyenne",
        },
        "systems": {
            "heating": {
                "system_type": "Chaudiere gaz",
                "efficiency": 0.85,
                "nominal_power_kw": 20.0,
                "energy_carrier": "gas",
            },
            "cooling": {
                "system_type": "Split",
                "cop_eer": default_cooling_cop,
                "nominal_power_kw": 6.0,
                "energy_carrier": "electricity",
            },
            "dhw_energy_kwh_year": max(1600.0, area_m2 * 18.0),
        },
        "occupancy": {
            "occupants": max(2, int(area_m2 / 45)),
            "heating_setpoint_c": 20.0,
            "cooling_setpoint_c": 26.0,
            "occupied_hours_per_day": 14.0,
        },
        "economics": {
            "currency": "DZD",
            "energy_price_eur_kwh": ALGERIA_DEFAULT_ENERGY_PRICES_DZD_KWH,
            "co2_factor_kg_kwh": ALGERIA_DEFAULT_CO2_KG_KWH,
            "renovation_cost_eur": {
                "isolation_murs": area_m2 * 12000,
                "isolation_toiture": area_m2 * 7000,
                "remplacement_fenetres": area_m2 * 9000,
                "pac_chauffage": area_m2 * 10000,
                "renovation_globale": area_m2 * 32000,
            },
            "subsidies_eur": {
                "isolation_murs": area_m2 * 1500,
                "isolation_toiture": area_m2 * 900,
                "remplacement_fenetres": area_m2 * 1000,
                "pac_chauffage": area_m2 * 1600,
                "renovation_globale": area_m2 * 4500,
            },
        },
    }
