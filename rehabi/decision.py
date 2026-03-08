from __future__ import annotations

from typing import Dict, List

from rehabi.models import ScenarioResults


DEFAULT_MULTICRITERIA_WEIGHTS: Dict[str, float] = {
    "energy": 0.25,
    "cost": 0.35,
    "co2": 0.25,
    "summer_comfort": 0.15,
}


def normalize_weights(weights: Dict[str, float] | None) -> Dict[str, float]:
    if not weights:
        return dict(DEFAULT_MULTICRITERIA_WEIGHTS)

    merged = dict(DEFAULT_MULTICRITERIA_WEIGHTS)
    for key in merged:
        if key in weights:
            merged[key] = max(0.0, float(weights[key]))

    total = sum(merged.values())
    if total <= 0:
        return dict(DEFAULT_MULTICRITERIA_WEIGHTS)
    return {k: v / total for k, v in merged.items()}


def compute_multicriteria_scores(
    results: List[ScenarioResults],
    weights: Dict[str, float] | None = None,
) -> Dict[str, Dict[str, float]]:
    w = normalize_weights(weights)

    energy_vals = [max(0.0, r.annual_savings_kwh) for r in results]
    cost_vals = [max(0.0, r.annual_savings_eur) for r in results]
    co2_vals = [max(0.0, r.annual_co2_reduction_kg) for r in results]
    comfort_vals = [
        max(0.0, r.baseline.annual_cooling_need_kwh - r.renovated.annual_cooling_need_kwh)
        for r in results
    ]

    max_energy = max(energy_vals) if energy_vals else 0.0
    max_cost = max(cost_vals) if cost_vals else 0.0
    max_co2 = max(co2_vals) if co2_vals else 0.0
    max_comfort = max(comfort_vals) if comfort_vals else 0.0

    scored: Dict[str, Dict[str, float]] = {}
    for idx, r in enumerate(results):
        e_raw = energy_vals[idx]
        c_raw = cost_vals[idx]
        co2_raw = co2_vals[idx]
        comfort_raw = comfort_vals[idx]

        e_norm = (e_raw / max_energy) if max_energy > 0 else 0.0
        c_norm = (c_raw / max_cost) if max_cost > 0 else 0.0
        co2_norm = (co2_raw / max_co2) if max_co2 > 0 else 0.0
        comfort_norm = (comfort_raw / max_comfort) if max_comfort > 0 else 0.0

        total = 100.0 * (
            w["energy"] * e_norm
            + w["cost"] * c_norm
            + w["co2"] * co2_norm
            + w["summer_comfort"] * comfort_norm
        )

        scored[r.scenario_name] = {
            "total_score_100": total,
            "energy_score_100": 100.0 * e_norm,
            "cost_score_100": 100.0 * c_norm,
            "co2_score_100": 100.0 * co2_norm,
            "summer_comfort_score_100": 100.0 * comfort_norm,
            "energy_savings_kwh": e_raw,
            "cost_savings": c_raw,
            "co2_reduction_kg": co2_raw,
            "summer_comfort_gain_kwh": comfort_raw,
            "weight_energy": w["energy"],
            "weight_cost": w["cost"],
            "weight_co2": w["co2"],
            "weight_summer_comfort": w["summer_comfort"],
        }
    return scored

