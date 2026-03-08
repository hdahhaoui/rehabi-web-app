from __future__ import annotations

from dataclasses import replace

from rehabi.models import BuildingInput, EnvelopeElement


def _period_from_year(year: int) -> str:
    if year < 1980:
        return "before_1980"
    if year <= 2000:
        return "1980_2000"
    return "recent"


PROFILE_DEFAULTS = {
    ("maison", "before_1980"): {"u_wall": 1.3, "u_roof": 0.9, "u_floor": 0.9, "u_window": 4.0, "ach": 1.0},
    ("maison", "1980_2000"): {"u_wall": 0.8, "u_roof": 0.45, "u_floor": 0.6, "u_window": 2.8, "ach": 0.7},
    ("maison", "recent"): {"u_wall": 0.35, "u_roof": 0.2, "u_floor": 0.3, "u_window": 1.4, "ach": 0.4},
    ("appartement", "before_1980"): {"u_wall": 1.1, "u_roof": 0.8, "u_floor": 0.8, "u_window": 3.5, "ach": 0.8},
    ("appartement", "1980_2000"): {"u_wall": 0.7, "u_roof": 0.35, "u_floor": 0.45, "u_window": 2.4, "ach": 0.55},
    ("appartement", "recent"): {"u_wall": 0.3, "u_roof": 0.18, "u_floor": 0.25, "u_window": 1.3, "ach": 0.35},
}


def apply_profile_defaults(building: BuildingInput) -> BuildingInput:
    btype = building.general.building_type.strip().lower()
    period = _period_from_year(building.general.construction_year)
    defaults = PROFILE_DEFAULTS.get((btype, period))
    if not defaults:
        return building

    envelope = replace(
        building.envelope,
        walls=EnvelopeElement(
            material=building.envelope.walls.material,
            thickness_m=building.envelope.walls.thickness_m,
            u_value_w_m2k=defaults["u_wall"],
        ),
        roof=EnvelopeElement(
            material=building.envelope.roof.material,
            thickness_m=building.envelope.roof.thickness_m,
            u_value_w_m2k=defaults["u_roof"],
        ),
        floor=EnvelopeElement(
            material=building.envelope.floor.material,
            thickness_m=building.envelope.floor.thickness_m,
            u_value_w_m2k=defaults["u_floor"],
        ),
        windows=EnvelopeElement(
            material=building.envelope.windows.material,
            thickness_m=building.envelope.windows.thickness_m,
            u_value_w_m2k=defaults["u_window"],
        ),
    )
    ventilation = replace(building.ventilation, air_change_rate_ach=defaults["ach"])
    return replace(building, envelope=envelope, ventilation=ventilation)

