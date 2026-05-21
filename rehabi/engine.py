from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List, Optional

from rehabi.climate import get_climate, orientation_factor
from rehabi.models import BuildingInput, ScenarioResults, ThermalResults
from rehabi.scenarios import SCENARIO_FUNCTIONS


def _safe_get(dct: Dict[str, float], key: str, default: float) -> float:
    return float(dct.get(key, default))


def _estimate_energy_class(consumption_kwh_m2: float) -> str:
    thresholds = [
        ("A", 50),
        ("B", 90),
        ("C", 150),
        ("D", 230),
        ("E", 330),
        ("F", 450),
    ]
    for label, max_value in thresholds:
        if consumption_kwh_m2 <= max_value:
            return label
    return "G"


def calculate_thermal_performance(building: BuildingInput) -> ThermalResults:
    from rehabi.scenarios.profil import apply_profile_defaults
    building = apply_profile_defaults(building)
    
    climate = get_climate(building.general.city, building.general.climate_zone, building.general.country)

    volume = building.geometry.volume_m3
    if volume is None or volume <= 0:
        volume = (
            building.general.habitable_area_m2
            * building.general.ceiling_height_m
            * max(1, building.general.floors)
        )

    h_walls = building.envelope.walls.u_value_w_m2k * building.geometry.wall_area_m2
    h_roof = building.envelope.roof.u_value_w_m2k * building.geometry.roof_area_m2
    h_floor = building.envelope.floor.u_value_w_m2k * building.geometry.floor_area_m2
    h_windows = building.envelope.windows.u_value_w_m2k * building.geometry.window_area_m2
    h_trans = h_walls + h_roof + h_floor + h_windows

    h_vent = 0.34 * building.ventilation.air_change_rate_ach * volume
    h_total = h_trans + h_vent

    orientation_gain = orientation_factor(building.geometry.orientation)
    solar_gains = (
        building.geometry.window_area_m2
        * climate.annual_horizontal_solar_kwh_m2
        * building.envelope.window_solar_factor_g
        * orientation_gain
        * 0.35
    )

    internal_gains = (
        building.occupancy.occupants
        * 0.1
        * building.occupancy.occupied_hours_per_day
        * 365
    )

    heating_gains_utilized = climate.heating_gains_utilization * (solar_gains + internal_gains)
    cooling_extra_load = climate.cooling_gains_fraction * (solar_gains + internal_gains)

    heating_need = max(0.0, h_total * climate.hdd18 * 24 / 1000 - heating_gains_utilized)
    cooling_need = max(0.0, h_total * climate.cdd26 * 24 / 1000 + cooling_extra_load)

    heating_eff = max(0.35, building.systems.heating.efficiency)
    cooling_cop = max(1.5, building.systems.cooling.cop_eer)
    heating_final = heating_need / heating_eff
    cooling_final = cooling_need / cooling_cop
    dhw = max(0.0, building.systems.dhw_energy_kwh_year)

    annual_final_energy = heating_final + cooling_final + dhw

    p = building.economics.energy_price_eur_kwh
    c = building.economics.co2_factor_kg_kwh

    heat_carrier = building.systems.heating.energy_carrier
    cool_carrier = building.systems.cooling.energy_carrier
    price_heat = _safe_get(p, heat_carrier, _safe_get(p, "electricity", 0.2))
    price_cool = _safe_get(p, cool_carrier, _safe_get(p, "electricity", 0.2))
    price_dhw = _safe_get(p, "dhw", _safe_get(p, heat_carrier, 0.2))

    co2_heat = _safe_get(c, heat_carrier, _safe_get(c, "electricity", 0.06))
    co2_cool = _safe_get(c, cool_carrier, _safe_get(c, "electricity", 0.06))
    co2_dhw = _safe_get(c, "dhw", _safe_get(c, heat_carrier, 0.06))

    annual_cost = heating_final * price_heat + cooling_final * price_cool + dhw * price_dhw
    annual_co2 = heating_final * co2_heat + cooling_final * co2_cool + dhw * co2_dhw

    consumption_kwh_m2 = annual_final_energy / max(1.0, building.general.habitable_area_m2)
    energy_class = _estimate_energy_class(consumption_kwh_m2)

    return ThermalResults(
        h_trans_w_k=h_trans,
        h_vent_w_k=h_vent,
        h_total_w_k=h_total,
        annual_heating_need_kwh=heating_need,
        annual_cooling_need_kwh=cooling_need,
        annual_final_energy_kwh=annual_final_energy,
        annual_cost_eur=annual_cost,
        annual_co2_kg=annual_co2,
        energy_class_estimate=energy_class,
    )


def compare_with_scenario(building: BuildingInput, scenario_name: str) -> ScenarioResults:
    if scenario_name not in SCENARIO_FUNCTIONS:
        raise ValueError(f"Scenario inconnu: {scenario_name}")

    baseline = calculate_thermal_performance(building)
    renovated_building = SCENARIO_FUNCTIONS[scenario_name](building)
    renovated = calculate_thermal_performance(renovated_building)

    annual_savings_kwh = baseline.annual_final_energy_kwh - renovated.annual_final_energy_kwh
    annual_savings_eur = baseline.annual_cost_eur - renovated.annual_cost_eur
    annual_co2_reduction_kg = baseline.annual_co2_kg - renovated.annual_co2_kg

    renovation_cost = float(building.economics.renovation_cost_eur.get(scenario_name, 0.0))
    subsidies = float(building.economics.subsidies_eur.get(scenario_name, 0.0))
    net_investment = max(0.0, renovation_cost - subsidies)
    payback = (net_investment / annual_savings_eur) if annual_savings_eur > 0 else None

    notes: List[str] = []
    if payback is None and net_investment > 0:
        notes.append("Retour sur investissement non défini (économies annuelles nulles ou négatives).")

    return ScenarioResults(
        scenario_name=scenario_name,
        baseline=baseline,
        renovated=renovated,
        annual_savings_kwh=annual_savings_kwh,
        annual_savings_eur=annual_savings_eur,
        annual_co2_reduction_kg=annual_co2_reduction_kg,
        renovation_cost_eur=renovation_cost,
        subsidies_eur=subsidies,
        net_investment_eur=net_investment,
        payback_years=payback,
        notes=notes,
    )


def compare_all_scenarios(building: BuildingInput, scenarios: Optional[List[str]] = None) -> List[ScenarioResults]:
    to_run = scenarios or list(SCENARIO_FUNCTIONS.keys())
    return [compare_with_scenario(building, name) for name in to_run]


def scenario_to_dict(result: ScenarioResults) -> Dict[str, object]:
    return {
        "scenario_name": result.scenario_name,
        "baseline": asdict(result.baseline),
        "renovated": asdict(result.renovated),
        "annual_savings_kwh": result.annual_savings_kwh,
        "annual_savings_eur": result.annual_savings_eur,
        "annual_co2_reduction_kg": result.annual_co2_reduction_kg,
        "renovation_cost_eur": result.renovation_cost_eur,
        "subsidies_eur": result.subsidies_eur,
        "net_investment_eur": result.net_investment_eur,
        "payback_years": result.payback_years,
        "notes": result.notes,
    }
