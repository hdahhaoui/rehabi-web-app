from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file

from rehabi.calibration_dz import ALGERIA_WILAYA_CLIMATE
from rehabi.decision import compute_multicriteria_scores
from rehabi.engine import compare_all_scenarios, scenario_to_dict
from rehabi.io import build_model
from rehabi.prefill import prefill_defaults
from rehabi.profiles import apply_profile_defaults
from rehabi.report import generate_markdown_report, write_audit_pro_pdf, write_pdf_report, write_report


app = Flask(__name__)
LATEST_OUTPUT = None


@app.get("/")
def index():
    wilayas = sorted({v.wilaya for v in ALGERIA_WILAYA_CLIMATE.values()})
    return render_template("index.html", wilayas=wilayas)


@app.post("/api/prefill")
def api_prefill():
    payload = request.get_json(force=True)
    building_type = str(payload.get("building_type", "maison"))
    year = int(payload.get("construction_year", 1995))
    wilaya = str(payload.get("wilaya", "Alger"))
    area_m2 = float(payload.get("habitable_area_m2", 120))
    defaults = prefill_defaults(building_type, year, wilaya, area_m2)
    return jsonify(defaults)


@app.post("/api/simulate")
def api_simulate():
    payload = request.get_json(force=True)
    building = build_model(payload)
    if bool(payload.get("use_profile_defaults", False)):
        building = apply_profile_defaults(building)

    results = compare_all_scenarios(building)
    scoring = compute_multicriteria_scores(results, payload.get("multicriteria_weights"))
    result_payload = [scenario_to_dict(r) for r in results]
    for item in result_payload:
        item["multicriteria"] = scoring.get(item["scenario_name"], {})

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path("web_outputs") / stamp
    global LATEST_OUTPUT
    LATEST_OUTPUT = out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "results.json").write_text(
        json.dumps({"results": result_payload}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    report_md = generate_markdown_report(building, results)
    write_report(str(out_dir / "report.md"), report_md)

    pdf_generated = True
    audit_pdf_generated = True
    try:
        write_pdf_report(str(out_dir / "report.pdf"), "Rapport de rehabilitation energetique", report_md)
    except Exception:
        pdf_generated = False
    try:
        write_audit_pro_pdf(
            str(out_dir / "report_audit_pro.pdf"),
            building,
            results,
            payload.get("multicriteria_weights"),
        )
    except Exception:
        audit_pdf_generated = False

    return jsonify(
        {
            "results": result_payload,
            "report_md_path": str((out_dir / "report.md").resolve()),
            "report_pdf_path": str((out_dir / "report.pdf").resolve()),
            "report_audit_pro_pdf_path": str((out_dir / "report_audit_pro.pdf").resolve()),
            "pdf_generated": pdf_generated,
            "audit_pdf_generated": audit_pdf_generated,
            "multicriteria_weights": payload.get("multicriteria_weights"),
            "currency": building.economics.currency,
        }
    )

@app.route("/download/report-pdf")
def download_pdf():
    global LATEST_OUTPUT
    return send_file(LATEST_OUTPUT / "report.pdf", as_attachment=True)


@app.route("/download/report-md")
def download_md():
    global LATEST_OUTPUT
    return send_file(LATEST_OUTPUT / "report.md", as_attachment=True)


@app.route("/download/report-audit")
def download_audit():
    global LATEST_OUTPUT
    return send_file(LATEST_OUTPUT / "report_audit_pro.pdf", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
