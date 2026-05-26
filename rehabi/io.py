from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from rehabi.models import (
    BuildingInput,
    CoolingSystem,
    Economics,
    Envelope,
    EnvelopeElement,
    GeneralData,
    Geometry,
    HeatingSystem,
    Occupancy,
    Systems,
    Ventilation,
)


def _req(d: Dict[str, Any], key: str) -> Any:
    if key not in d:
        raise KeyError(f"Champ manquant: {key}")
    return d[key]


def load_input(path: str) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_model(data: Dict[str, Any]) -> BuildingInput:
    g = _req(data, "general")
    geom = _req(data, "geometry")
    env = _req(data, "envelope")
    vent = _req(data, "ventilation")
    sys = _req(data, "systems")
    occ = _req(data, "occupancy")
    eco = _req(data, "economics")

    model = BuildingInput(
        general=GeneralData(
            building_type=str(_req(g, "building_type")),
            construction_year=int(_req(g, "construction_year")),
            city=str(_req(g, "city")),
            climate_zone=g.get("climate_zone"),
            country=str(g.get("country", "France")),
            habitable_area_m2=float(_req(g, "habitable_area_m2")),
            floors=int(_req(g, "floors")),
            ceiling_height_m=float(_req(g, "ceiling_height_m")),
        ),
        geometry=Geometry(
            wall_area_m2=float(_req(geom, "wall_area_m2")),
            roof_area_m2=float(_req(geom, "roof_area_m2")),
            floor_area_m2=float(_req(geom, "floor_area_m2")),
            window_area_m2=float(_req(geom, "window_area_m2")),
            orientation=str(_req(geom, "orientation")),
            volume_m3=float(geom["volume_m3"]) if "volume_m3" in geom else None,
        ),
        envelope=Envelope(
            walls=EnvelopeElement(
                material=str(_req(env["walls"], "material")),
                thickness_m=float(_req(env["walls"], "thickness_m")),
                u_value_w_m2k=float(_req(env["walls"], "u_value_w_m2k")),
            ),
            roof=EnvelopeElement(
                material=str(_req(env["roof"], "material")),
                thickness_m=float(_req(env["roof"], "thickness_m")),
                u_value_w_m2k=float(_req(env["roof"], "u_value_w_m2k")),
            ),
            floor=EnvelopeElement(
                material=str(_req(env["floor"], "material")),
                thickness_m=float(_req(env["floor"], "thickness_m")),
                u_value_w_m2k=float(_req(env["floor"], "u_value_w_m2k")),
            ),
            windows=EnvelopeElement(
                material=str(_req(env["windows"], "material")),
                thickness_m=float(_req(env["windows"], "thickness_m")),
                u_value_w_m2k=float(_req(env["windows"], "u_value_w_m2k")),
            ),
            window_solar_factor_g=float(env.get("window_solar_factor_g", 0.55)),
        ),
        ventilation=Ventilation(
            ventilation_type=str(_req(vent, "ventilation_type")),
            air_change_rate_ach=float(_req(vent, "air_change_rate_ach")),
            airtightness_level=str(_req(vent, "airtightness_level")),
        ),
        systems=Systems(
            heating=HeatingSystem(
                system_type=str(_req(sys["heating"], "system_type")),
                efficiency=float(_req(sys["heating"], "efficiency")),
                nominal_power_kw=float(_req(sys["heating"], "nominal_power_kw")),
                energy_carrier=str(_req(sys["heating"], "energy_carrier")),
            ),
            cooling=CoolingSystem(
                system_type=str(_req(sys["cooling"], "system_type")),
                cop_eer=float(_req(sys["cooling"], "cop_eer")),
                nominal_power_kw=float(_req(sys["cooling"], "nominal_power_kw")),
                energy_carrier=str(_req(sys["cooling"], "energy_carrier")),
            ),
            dhw_energy_kwh_year=float(_req(sys, "dhw_energy_kwh_year")),
        ),
        occupancy=Occupancy(
            occupants=int(_req(occ, "occupants")),
            heating_setpoint_c=float(_req(occ, "heating_setpoint_c")),
            cooling_setpoint_c=float(_req(occ, "cooling_setpoint_c")),
            occupied_hours_per_day=float(_req(occ, "occupied_hours_per_day")),
        ),
        economics=Economics(
            energy_price_eur_kwh={k: float(v) for k, v in _req(eco, "energy_price_eur_kwh").items()},
            co2_factor_kg_kwh={k: float(v) for k, v in _req(eco, "co2_factor_kg_kwh").items()},
            currency=str(eco.get("currency", "EUR")),
            renovation_cost_eur={k: float(v) for k, v in eco.get("renovation_cost_eur", {}).items()},
            subsidies_eur={k: float(v) for k, v in eco.get("subsidies_eur", {}).items()},
        ),
    )
    return model
