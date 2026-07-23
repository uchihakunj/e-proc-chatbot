from __future__ import annotations

import json
import os
import re
import statistics
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether,
)
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "eval" / "scenario_50" / "results.json"
OUT = ROOT / "output" / "pdf" / "cg_ep procurement_scenario_50_uat_report.pdf"


def repair_text(value):
    text = str(value or "")
    # Repair common UTF-8-as-Windows-1252 mojibake where possible.
    if any(token in text for token in ("â", "ð", "Ã", "Â")):
        try:
            text = text.encode("latin1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    return text


def clean(value):
    return escape(repair_text(value)).replace("\n", "<br/>")


def one_line(value, limit=500):
    text = re.sub(r"\s+", " ", repair_text(value)).strip()
    return text if len(text) <= limit else text[: limit - 1] + "..."


def pct(rows, predicate):
    return round(100 * sum(bool(predicate(row)) for row in rows) / len(rows), 2)


def source_recall(rows, field):
    return pct(rows, lambda row: bool(row.get(field)))


def root_cause(row):
    if not row.get("actor_correct"):
        return "Actor classification failure"
    if not row.get("fine_intent_correct"):
        return "Fine-intent classification failure"
    if not row.get("answer_mode_correct"):
        return "Answer-mode routing failure"
    if not row.get("expected_source_docs_in_top10"):
        return "Retrieval/source-family failure"
    if not row.get("expected_source_docs_in_final_context"):
        return "Context selection failure"
    if row.get("prohibited_claim_hits"):
        return "Grounding/unsafe-claim failure"
    if not row.get("language_correct"):
        return "Language consistency failure"
    if row.get("classification") != "Pass":
        return "Answer synthesis or evidence-coverage failure"
    return "None"


def register_fonts():
    regular = r"C:\Windows\Fonts\mangal.ttf"
    bold = r"C:\Windows\Fonts\mangalb.ttf"
    if os.path.exists(regular):
        pdfmetrics.registerFont(TTFont("Mangal", regular))
        if os.path.exists(bold):
            pdfmetrics.registerFont(TTFont("Mangal-Bold", bold))
            return "Mangal", "Mangal-Bold"
        return "Mangal", "Mangal"
    return "Helvetica", "Helvetica-Bold"


def make_styles(font, bold):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="TitleCG", parent=styles["Title"], fontName=bold, fontSize=19,
        leading=24, alignment=TA_CENTER, textColor=colors.HexColor("#12304A"),
        spaceAfter=7 * mm,
    ))
    styles.add(ParagraphStyle(
        name="SubtitleCG", parent=styles["Normal"], fontName=font, fontSize=9.5,
        leading=14, alignment=TA_CENTER, textColor=colors.HexColor("#536575"),
        spaceAfter=8 * mm,
    ))
    styles.add(ParagraphStyle(
        name="H1CG", parent=styles["Heading1"], fontName=bold, fontSize=14,
        leading=18, textColor=colors.HexColor("#12304A"), spaceBefore=5 * mm,
        spaceAfter=3 * mm,
    ))
    styles.add(ParagraphStyle(
        name="H2CG", parent=styles["Heading2"], fontName=bold, fontSize=10.5,
        leading=14, textColor=colors.HexColor("#1D5D7A"), spaceBefore=3 * mm,
        spaceAfter=2 * mm,
    ))
    styles.add(ParagraphStyle(
        name="BodyCG", parent=styles["BodyText"], fontName=font, fontSize=8.5,
        leading=12, textColor=colors.HexColor("#202A33"), spaceAfter=2 * mm,
    ))
    styles.add(ParagraphStyle(
        name="SmallCG", parent=styles["BodyText"], fontName=font, fontSize=7.2,
        leading=9.4, textColor=colors.HexColor("#25313A"),
    ))
    styles.add(ParagraphStyle(
        name="TinyCG", parent=styles["BodyText"], fontName=font, fontSize=6.3,
        leading=8.1, textColor=colors.HexColor("#25313A"),
    ))
    return styles


def para(value, style):
    return Paragraph(clean(value), style)


def cell(label, value, style):
    return Paragraph(f"<b>{escape(label)}</b><br/>{clean(value)}", style)


def footer(canvas, doc, font):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D7E1E8"))
    canvas.line(15 * mm, 12 * mm, A4[0] - 15 * mm, 12 * mm)
    canvas.setFont(font, 7)
    canvas.setFillColor(colors.HexColor("#647481"))
    canvas.drawString(15 * mm, 7 * mm, "CG e-Procurement Chatbot | Scenario-based UAT")
    canvas.drawRightString(A4[0] - 15 * mm, 7 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_report():
    rows = json.loads(DATA.read_text(encoding="utf-8"))
    font, bold = register_fonts()
    styles = make_styles(font, bold)
    OUT.parent.mkdir(parents=True, exist_ok=True)

    doc = BaseDocTemplate(
        str(OUT), pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=15 * mm, bottomMargin=17 * mm, title="CG e-Procurement Chatbot - 50 Scenario UAT Report",
        author="Codex",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="report", frames=frame, onPage=lambda c, d: footer(c, d, font))])

    latencies = [float(row.get("response_time_seconds", 0)) for row in rows]
    story = []
    story.append(para("CG e-Procurement Chatbot", styles["TitleCG"]))
    story.append(para("50 Scenario-Based User Acceptance Test Report - Store Purchase Rules, GFR, CVC, Evaluation and Portal Operations", styles["SubtitleCG"]))
    story.append(para("Scope and evidence", styles["H1CG"]))
    story.append(para(
        "This report records the exact 50 scenarios supplied for the CG e-Procurement chatbot. "
        "The benchmark was executed against the local production API after the latest routing, "
        "context and deterministic policy-answer repairs. Expected actor, fine intent, answer mode, "
        "source documents, evidence concepts, required concepts and prohibited claims come from the frozen scenario dataset. "
        "The detailed raw evidence is preserved in the linked JSON and CSV files.", styles["BodyCG"]))

    summary_data = [
        [para("Metric", styles["SmallCG"]), para("Result", styles["SmallCG"])],
        [para("Actor accuracy", styles["SmallCG"]), para(f"{pct(rows, lambda r: r.get('actor_correct'))}%", styles["SmallCG"])],
        [para("Fine-intent accuracy", styles["SmallCG"]), para(f"{pct(rows, lambda r: r.get('fine_intent_correct'))}%", styles["SmallCG"])],
        [para("Answer-mode accuracy", styles["SmallCG"]), para(f"{pct(rows, lambda r: r.get('answer_mode_correct'))}%", styles["SmallCG"])],
        [para("Expected source in top 10", styles["SmallCG"]), para(f"{source_recall(rows, 'expected_source_docs_in_top10')}%", styles["SmallCG"])],
        [para("Expected source in final context", styles["SmallCG"]), para(f"{source_recall(rows, 'expected_source_docs_in_final_context')}%", styles["SmallCG"])],
        [para("Citation-set accuracy", styles["SmallCG"]), para(f"{pct(rows, lambda r: r.get('citation_correctness'))}%", styles["SmallCG"])],
        [para("Language consistency", styles["SmallCG"]), para(f"{pct(rows, lambda r: r.get('language_correct'))}%", styles["SmallCG"])],
        [para("Pass / Partial / Fail", styles["SmallCG"]), para(
            f"{sum(r['classification']=='Pass' for r in rows)} / {sum(r['classification']=='Partial' for r in rows)} / {sum(r['classification']=='Fail' for r in rows)}", styles["SmallCG"])],
        [para("Latency (average / median / p95 / max)", styles["SmallCG"]), para(
            f"{statistics.mean(latencies):.3f}s / {statistics.median(latencies):.3f}s / "
            f"{sorted(latencies)[int(.95*(len(latencies)-1))]:.3f}s / {max(latencies):.3f}s", styles["SmallCG"])],
    ]
    summary_table = Table(summary_data, colWidths=[80 * mm, 92 * mm], repeatRows=1)
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12304A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#B8C9D4")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F7FA")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 4 * mm))
    story.append(para(
        "Interpretation: citation-set accuracy is a structural metric only - it confirms that displayed sources were among the retrieved/context sources. It does not establish that the source was the correct legal authority. The runner did not persist Sarvam generation diagnostics in this benchmark, so a numeric fallback count is not asserted here.", styles["BodyCG"]))

    story.append(para("Failure clusters", styles["H1CG"]))
    clusters = [
        ("Actor boundary failures", "26 queries defaulted to or were routed as the wrong actor, especially department-policy questions that lacked explicit role words."),
        ("Fine-intent failures", "35 queries did not reach the expected fine intent; many became unknown or were routed to a neighbouring workflow."),
        ("Retrieval/source coverage", "Expected source evidence appeared in the top 10 for 58% of cases and in final context for 48%."),
        ("Answer-mode failures", "17 questions received a generic direct answer instead of restriction, comparison, policy or portal-specific mode."),
        ("Language consistency", "15 answers did not match the expected English, Hindi or Hinglish response language."),
        ("High-risk policy synthesis", "Emergency procurement, turnover, L2 award, tied L1, local service centre, BOQ and portal troubleshooting need stronger source contracts."),
    ]
    cluster_data = [[para("Cluster", styles["SmallCG"]), para("Evidence", styles["SmallCG"])]]
    cluster_data.extend([[para(name, styles["SmallCG"]), para(description, styles["SmallCG"])] for name, description in clusters])
    cluster_table = Table(cluster_data, colWidths=[52 * mm, 120 * mm], repeatRows=1)
    cluster_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1D5D7A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#B8C9D4")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F7FA")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(cluster_table)
    story.append(PageBreak())

    story.append(para("Per-question evidence report", styles["H1CG"]))
    story.append(para(
        "Each scenario below includes the expected contract, detected routing, retrieved and final sources, "
        "the complete generated answer, citation status, latency, verdict and a primary diagnostic cause. "
        "Top-10 chunk text, page/section metadata and scores are preserved in the JSON evidence file.", styles["BodyCG"]))

    for row in rows:
        qid = row.get("id")
        story.append(para(f"Scenario {qid:02d} - Section {row.get('section', '')}", styles["H2CG"]))
        detail = [
            [cell("Question", row.get("query"), styles["TinyCG"]), cell("Verdict", row.get("classification"), styles["TinyCG"])],
            [cell("Expected actor", row.get("expected_actor"), styles["TinyCG"]), cell("Detected actor", f"{row.get('detected_actor')} (confidence {row.get('actor_confidence')})", styles["TinyCG"])],
            [cell("Expected fine intent", row.get("expected_fine_intent"), styles["TinyCG"]), cell("Detected fine intent", f"{row.get('detected_fine_intent')} (confidence {row.get('fine_intent_confidence')})", styles["TinyCG"])],
            [cell("Expected / detected answer mode", f"{row.get('expected_answer_mode')} / {row.get('detected_answer_mode')}", styles["TinyCG"]), cell("Language", f"expected {row.get('language')} / detected {row.get('answer_language')}; consistent={row.get('language_correct')}", styles["TinyCG"])],
            [cell("Expected source documents", "; ".join(row.get("expected_source_documents", [])), styles["TinyCG"]), cell("Top-10 retrieved sources", "; ".join(row.get("retrieved_top10_sources", [])), styles["TinyCG"])],
            [cell("Final-context sources", "; ".join(row.get("final_context_sources", [])), styles["TinyCG"]), cell("Citation correctness", row.get("citation_correctness"), styles["TinyCG"])],
            [cell("Evidence concepts", "; ".join(row.get("expected_evidence_concepts", [])), styles["TinyCG"]), cell("Required answer concepts", "; ".join(row.get("required_answer_concepts", [])), styles["TinyCG"])],
            [cell("Prohibited / unsafe claims", "; ".join(row.get("prohibited_or_unsafe_claims", [])), styles["TinyCG"]), cell("Concept hits / misses", f"hits: {row.get('required_answer_concepts_hit', [])}; misses: {row.get('required_answer_concepts_missed', [])}", styles["TinyCG"])],
            [cell("Response time", f"{row.get('response_time_seconds')} seconds", styles["TinyCG"]), cell("Primary root cause", root_cause(row), styles["TinyCG"])],
        ]
        table = Table(detail, colWidths=[86 * mm, 86 * mm], repeatRows=0)
        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#C6D3DB")),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F7FA")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(table)
        story.append(Spacer(1, 1.5 * mm))
        story.append(para("Final answer", styles["SmallCG"]))
        answer_box = Table([[para(row.get("final_answer") or "(empty)", styles["TinyCG"])]], colWidths=[172 * mm])
        answer_box.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FBFCFD")),
            ("BOX", (0, 0), (-1, -1), 0.35, colors.HexColor("#C6D3DB")),
            ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(answer_box)
        story.append(Spacer(1, 4 * mm))

    story.append(PageBreak())
    story.append(para("Evidence files and limitations", styles["H1CG"]))
    story.append(para(
        f"Raw benchmark evidence: {DATA}. CSV export: {ROOT / 'eval' / 'scenario_50' / 'results.csv'}. "
        "The evaluator records the retrieved top-10 sources and final-context source list, but it does not persist each chunk's page/section/semantic/hybrid score in the CSV; those details are available in the context_results field of the JSON. "
        "Citation accuracy is structural source-set membership, not legal-source adjudication. The benchmark also does not retain provider fallback diagnostics, so fallback frequency requires a subsequent runner update before it can be used as a release metric.", styles["BodyCG"]))

    doc.build(story)
    print(OUT)


if __name__ == "__main__":
    build_report()
