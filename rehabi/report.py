from __future__ import annotations

from pathlib import Path
from typing import List

from rehabi.decision import compute_multicriteria_scores
from rehabi.models import BuildingInput, ScenarioResults


def _fmt(v: float, ndigits: int = 1) -> str:
    return f"{v:,.{ndigits}f}".replace(",", " ")


def _fmt_optional(v: float | None, ndigits: int = 1) -> str:
    if v is None:
        return "N/A"
    return _fmt(v, ndigits)


def generate_markdown_report(building: BuildingInput, results: List[ScenarioResults]) -> str:
    lines: List[str] = []
    currency = building.economics.currency
    lines.append("# Rapport de rehabilitation energetique")
    lines.append("")
    lines.append("## Donnees batiment")
    lines.append(f"- Type: {building.general.building_type}")
    lines.append(f"- Annee construction: {building.general.construction_year}")
    lines.append(f"- Ville: {building.general.city}")
    lines.append(f"- Surface habitable: {_fmt(building.general.habitable_area_m2, 0)} m2")
    lines.append(f"- Volume: {_fmt(building.geometry.volume_m3 or 0.0, 0)} m3 (0 si auto-calcule)")
    lines.append("")
    lines.append("## Resultats par scenario")
    lines.append("")

    for r in results:
        lines.append(f"### {r.scenario_name}")
        lines.append(
            f"- Besoin chauffage avant/apres: {_fmt(r.baseline.annual_heating_need_kwh, 0)} / {_fmt(r.renovated.annual_heating_need_kwh, 0)} kWh/an"
        )
        lines.append(
            f"- Besoin climatisation avant/apres: {_fmt(r.baseline.annual_cooling_need_kwh, 0)} / {_fmt(r.renovated.annual_cooling_need_kwh, 0)} kWh/an"
        )
        lines.append(
            f"- Conso finale avant/apres: {_fmt(r.baseline.annual_final_energy_kwh, 0)} / {_fmt(r.renovated.annual_final_energy_kwh, 0)} kWh/an"
        )
        lines.append(f"- Cout energetique avant/apres: {_fmt(r.baseline.annual_cost_eur, 0)} / {_fmt(r.renovated.annual_cost_eur, 0)} {currency}/an")
        lines.append(f"- Emissions CO2 avant/apres: {_fmt(r.baseline.annual_co2_kg, 0)} / {_fmt(r.renovated.annual_co2_kg, 0)} kgCO2/an")
        lines.append(f"- Economie annuelle: {_fmt(r.annual_savings_eur, 0)} {currency}/an")
        lines.append(f"- Gain energie: {_fmt(r.annual_savings_kwh, 0)} kWh/an")
        lines.append(f"- Reduction CO2: {_fmt(r.annual_co2_reduction_kg, 0)} kgCO2/an")
        lines.append(f"- Investissement net: {_fmt(r.net_investment_eur, 0)} {currency}")
        lines.append(f"- Temps de retour: {_fmt_optional(r.payback_years, 1)} ans")
        if r.notes:
            lines.append(f"- Notes: {'; '.join(r.notes)}")
        lines.append("")

    return "\n".join(lines)


def write_report(path: str, content: str) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")


def write_pdf_report(path: str, title: str, markdown_content: str) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(output), pagesize=A4)
    width, height = A4
    margin = 40
    y = height - margin

    # Register Unicode-friendly font fallback if present.
    try:
        pdfmetrics.registerFont(TTFont("DejaVu", "DejaVuSans.ttf"))
        font_name = "DejaVu"
    except Exception:
        font_name = "Helvetica"

    c.setFont(font_name, 14)
    c.drawString(margin, y, title)
    y -= 24
    c.setFont(font_name, 10)

    for raw_line in markdown_content.splitlines():
        line = raw_line.strip()
        if line.startswith("#"):
            line = line.lstrip("#").strip()
        if not line:
            y -= 8
        else:
            wrapped = _wrap_text(line, max_chars=110)
            for wline in wrapped:
                c.drawString(margin, y, wline)
                y -= 14
                if y < margin:
                    c.showPage()
                    c.setFont(font_name, 10)
                    y = height - margin
        if y < margin:
            c.showPage()
            c.setFont(font_name, 10)
            y = height - margin

    c.save()


def _wrap_text(text: str, max_chars: int) -> List[str]:
    if len(text) <= max_chars:
        return [text]
    words = text.split()
    lines: List[str] = []
    cur = ""
    for word in words:
        tentative = f"{cur} {word}".strip()
        if len(tentative) <= max_chars:
            cur = tentative
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def write_audit_pro_pdf(
    path: str,
    building: BuildingInput,
    results: List[ScenarioResults],
    multicriteria_weights: dict[str, float] | None = None,
) -> None:
    from datetime import datetime

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(output), pagesize=A4)
    width, height = A4
    margin = 18 * mm
    y = height - margin
    draw_frame()
    logo_path = "static/logo.png"

    if Path(logo_path).exists():
        c.drawImage(
            logo_path,
            width/2 - 25*mm,
            height - 60*mm,
            width=50*mm,
            height=50*mm,
            preserveAspectRatio=True,
            mask='auto'
        )
    from pathlib import Path

    logo_path = "static/logo.png"

    try:
        pdfmetrics.registerFont(TTFont("DejaVu", "DejaVuSans.ttf"))
        font_regular = "DejaVu"
    except Exception:
        font_regular = "Helvetica"

   def new_page() -> float:
       c.showPage()
       draw_frame()  
       return height - margin

    def ensure_space(ypos: float, needed: float) -> float:
        if ypos - needed < margin:
            return new_page()
        return ypos

    def draw_title(text: str, ypos: float) -> float:
        c.setFont(font_regular, 18)
        c.setFillColor(colors.HexColor("#0f4c81"))
        c.drawString(margin, ypos, text)
        return ypos - 12 * mm

    def draw_h2(text: str, ypos: float) -> float:
        ypos = ensure_space(ypos, 12 * mm)
        c.setFont(font_regular, 13)
        c.setFillColor(colors.HexColor("#14324f"))
        c.drawString(margin, ypos, text)
        return ypos - 7 * mm

    def draw_line(text: str, ypos: float, size: int = 10) -> float:
        ypos = ensure_space(ypos, 8 * mm)
        c.setFont(font_regular, size)
        c.setFillColor(colors.black)
        for segment in _wrap_text(text, 105):
            ypos = ensure_space(ypos, 6 * mm)
            c.drawString(margin, ypos, segment)
            ypos -= 5 * mm
        return ypos

    # Cover page
    draw_logo()
    c.setFont(font_regular, 20)
    c.setFillColor(colors.HexColor("#0f4c81"))

    c.drawCentredString(
        width/2,
        height - 90*mm,
        "RAPPORT D'AUDIT ENERGETIQUE"
    )
c.setFont(font_regular, 10)

c.drawCentredString(
    width/2,
    height - 120*mm,
    f"{building.general.city} - {building.general.construction_year}"
)
    y = draw_line(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", y)
    y = draw_line(f"Projet: {building.general.building_type} - {building.general.city} ({building.general.country})", y)
    y = draw_line(f"Surface habitable: {_fmt(building.general.habitable_area_m2, 0)} m2", y)
    y = draw_line(f"Annee de construction: {building.general.construction_year}", y)
    y = draw_line("Objectif: comparer des scenarios de rehabilitation (energie, cout, CO2, ROI).", y)
    y = draw_line("Contenu: hypotheses, resultats comparatifs et recommandations priorisees.", y)

    y = new_page()

    # Hypotheses section
    y = draw_h2("1) Hypotheses de calcul", y)
    y = draw_line("Modele: Niveau 1 solide + apports simplifies niveau 2.", y)
    y = draw_line("Transmission: Q_trans = U x A x deltaT", y)
    y = draw_line("Ventilation: Q_vent = 0.34 x n x V x deltaT", y)
    y = draw_line(
        f"Enveloppe U (W/m2.K): murs={building.envelope.walls.u_value_w_m2k:.2f}, toiture={building.envelope.roof.u_value_w_m2k:.2f}, sol={building.envelope.floor.u_value_w_m2k:.2f}, fenetres={building.envelope.windows.u_value_w_m2k:.2f}",
        y,
    )
    y = draw_line(
        f"Ventilation/infiltration: n={building.ventilation.air_change_rate_ach:.2f} vol/h, volume={_fmt(building.geometry.volume_m3 or 0.0, 0)} m3",
        y,
    )
    y = draw_line(
        f"Systemes: chauffage={building.systems.heating.system_type} (eta={building.systems.heating.efficiency:.2f}), clim={building.systems.cooling.system_type} (COP/EER={building.systems.cooling.cop_eer:.2f})",
        y,
    )
    y = draw_line(
        f"Energie/prix ({building.economics.currency}/kWh): {building.economics.energy_price_eur_kwh}",
        y,
    )
    y = draw_line(f"Facteurs CO2 (kgCO2/kWh): {building.economics.co2_factor_kg_kwh}", y)

    y = new_page()

    scores = compute_multicriteria_scores(results, multicriteria_weights)

    # Comparative table
    y = draw_h2("2) Tableau comparatif des scenarios", y)
    headers = ["Scenario", "Score/100", "Economie/an", "CO2 evit.", "ROI (ans)"]
    col_x = [margin, margin + 58 * mm, margin + 84 * mm, margin + 126 * mm, margin + 158 * mm]
    row_h = 8 * mm

    def draw_table_header(ypos: float) -> float:
        c.setFillColor(colors.HexColor("#e6eff8"))
        c.rect(margin, ypos - row_h + 1.2 * mm, width - 2 * margin, row_h, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#0b2e4f"))
        c.setFont(font_regular, 9)
        for i, h in enumerate(headers):
            c.drawString(col_x[i], ypos - 5 * mm, h)
        c.setFillColor(colors.black)
        return ypos - row_h

    y = ensure_space(y, 20 * mm)
    y = draw_table_header(y)

    ranked = sorted(
        results,
        key=lambda r: scores.get(r.scenario_name, {}).get("total_score_100", 0.0),
        reverse=True,
    )
    for r in ranked:
        y = ensure_space(y, 10 * mm)
        c.setFont(font_regular, 9)
        c.drawString(col_x[0], y - 5 * mm, r.scenario_name[:24])
        c.drawString(col_x[1], y - 5 * mm, f"{scores[r.scenario_name]['total_score_100']:.1f}")
        c.drawString(col_x[2], y - 5 * mm, f"{_fmt(r.annual_savings_eur, 0)} {building.economics.currency}")
        c.drawString(col_x[3], y - 5 * mm, f"{_fmt(r.annual_co2_reduction_kg, 0)} kg")
        roi_txt = "N/A" if r.payback_years is None else f"{r.payback_years:.1f}"
        c.drawString(col_x[4], y - 5 * mm, roi_txt)
        c.setStrokeColor(colors.HexColor("#d8e3f0"))
        c.line(margin, y - row_h + 1 * mm, width - margin, y - row_h + 1 * mm)
        y -= row_h

    y -= 4 * mm

    # Prioritized recommendations
    y = draw_h2("3) Recommandations priorisees", y)
    recommendations = _build_prioritized_recommendations(ranked, scores)
    for idx, rec in enumerate(recommendations, start=1):
        y = draw_line(f"{idx}. {rec}", y)

    y = draw_h2("4) Conclusion", y)
    best = ranked[0] if ranked else None
    if best:
        best_score = scores[best.scenario_name]["total_score_100"]
        y = draw_line(
            f"Scenario prioritaire recommande: {best.scenario_name} (score {best_score:.1f}/100, ROI {best.payback_years:.1f} ans, economie {_fmt(best.annual_savings_eur,0)} {building.economics.currency}/an)."
            if best.payback_years is not None
            else f"Scenario pertinent energetiquement: {best.scenario_name} (score {best_score:.1f}/100, ROI non definissable).",
            y,
        )
    y = draw_line("Pour validation execution, completer avec devis entreprises, audit sur site et donnees meteo locales detaillees.", y)

    c.save()
    def draw_logo():
        if Path(logo_path).exists():
            c.drawImage(
                logo_path,
                margin,
                height - 45 * mm,
                width=35 * mm,
                height=35 * mm,
                preserveAspectRatio=True,
                mask='auto'
            )
def draw_frame():
    c.setStrokeColor(colors.HexColor("#0f4c81"))
    c.setLineWidth(1)
    c.rect(10, 10, width - 20, height - 20)

def _build_prioritized_recommendations(
    ranked: List[ScenarioResults],
    scores: dict[str, dict[str, float]],
) -> List[str]:
    recs: List[str] = []
    for r in ranked:
        if r.annual_savings_eur <= 0:
            continue
        s = scores.get(r.scenario_name, {})
        total_score = s.get("total_score_100", 0.0)
        comfort = s.get("summer_comfort_score_100", 0.0)
        if r.payback_years is not None and r.payback_years <= 7:
            recs.append(
                f"Priorite haute: {r.scenario_name} - score {total_score:.1f}/100, ROI court ({r.payback_years:.1f} ans), confort ete {comfort:.1f}/100."
            )
        elif r.payback_years is not None and r.payback_years <= 12:
            recs.append(
                f"Priorite moyenne: {r.scenario_name} - score {total_score:.1f}/100, ROI acceptable ({r.payback_years:.1f} ans)."
            )
        else:
            recs.append(
                f"Priorite basse: {r.scenario_name} - score {total_score:.1f}/100, gains techniques interessants mais ROI long."
            )
    if not recs:
        recs.append("Aucune priorite claire: verifier les hypotheses de prix energie, cout travaux et performances reelles.")
    return recs[:5]
