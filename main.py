from __future__ import annotations

import argparse
import json
from pathlib import Path

from rehabi.decision import compute_multicriteria_scores
from rehabi.engine import compare_all_scenarios, scenario_to_dict
from rehabi.io import build_model, load_input
from rehabi.profiles import apply_profile_defaults
from rehabi.report import generate_markdown_report, write_audit_pro_pdf, write_pdf_report, write_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simulateur de rehabilitation energetique (niveau 1 + niveau 2 simplifie)")
    parser.add_argument("--input", required=True, help="Fichier JSON d'entree")
    parser.add_argument("--output", default="outputs", help="Dossier de sortie")
    parser.add_argument(
        "--scenarios",
        nargs="*",
        default=None,
        help="Liste de scenarios a executer (sinon tous).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = load_input(args.input)
    building = build_model(data)

    if bool(data.get("use_profile_defaults", True)):
        building = apply_profile_defaults(building)

    results = compare_all_scenarios(building, args.scenarios)
    scoring = compute_multicriteria_scores(results, data.get("multicriteria_weights"))

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    result_payload = [scenario_to_dict(r) for r in results]
    for item in result_payload:
        sname = item["scenario_name"]
        item["multicriteria"] = scoring.get(sname, {})

    json_payload = {
        "input_summary": {
            "city": building.general.city,
            "country": building.general.country,
            "building_type": building.general.building_type,
            "construction_year": building.general.construction_year,
            "surface_m2": building.general.habitable_area_m2,
            "currency": building.economics.currency,
        },
        "multicriteria_weights": data.get("multicriteria_weights"),
        "results": result_payload,
    }
    (out_dir / "results.json").write_text(json.dumps(json_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    report_md = generate_markdown_report(building, results)
    write_report(str(out_dir / "report.md"), report_md)
    try:
        write_pdf_report(str(out_dir / "report.pdf"), "Rapport de rehabilitation energetique", report_md)
    except Exception as exc:
        print(f"PDF non genere ({exc}). Installez reportlab pour activer l'export PDF.")
    try:
        write_audit_pro_pdf(
            str(out_dir / "report_audit_pro.pdf"),
            building,
            results,
            data.get("Indice de performance globale (/100)"),
        )
    except Exception as exc:
        print(f"PDF audit pro non genere ({exc}). Installez reportlab pour activer l'export PDF.")

    print(f"Simulation terminee. Fichiers generes dans: {out_dir.resolve()}")


if __name__ == "__main__":
    main()
