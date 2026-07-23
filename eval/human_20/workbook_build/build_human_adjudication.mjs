import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = path.resolve(process.cwd(), "..", "..", "..");
const benchmarkDir = path.join(root, "eval", "human_20");
const outputDir = path.join(root, "outputs", "human_adjudication_20260717");
const results = JSON.parse(await fs.readFile(path.join(benchmarkDir, "results.json"), "utf8"));
const metrics = JSON.parse(await fs.readFile(path.join(benchmarkDir, "aggregate_metrics.json"), "utf8"));

if (results.length !== 20) throw new Error(`Expected 20 benchmark rows; found ${results.length}.`);

const wb = Workbook.create();
const overview = wb.worksheets.add("Overview");
const queue = wb.worksheets.add("Review Queue");
const summary = wb.worksheets.add("Calibration Summary");

const navy = "#17365D";
const teal = "#0F766E";
const paleBlue = "#EAF2F8";
const paleTeal = "#E8F5F1";
const paleYellow = "#FFF4CC";
const paleGray = "#F3F4F6";
const border = "#D1D5DB";
const white = "#FFFFFF";

function repairMojibake(value) {
  if (typeof value !== "string" || !/(?:Ã.|Â.|ðŸ|à¤)/.test(value)) return value;
  const repaired = Buffer.from(value, "latin1").toString("utf8");
  return repaired.includes("�") ? value : repaired;
}

function cleanAnswer(value) {
  return repairMojibake(value)
    .replace(/^💡\s*/gm, "")
    .replace(/^📋\s*/gm, "Process\n")
    .replace(/^📘\s*/gm, "Source: ");
}

function reviewerText(row, field) {
  if (row.id !== "H20") {
    return field === "answer" ? cleanAnswer(row[field]) : repairMojibake(row[field]);
  }
  const translations = {
    query: "[Hindi query — English review translation] In Chhattisgarh, what are the main methods of government procurement?",
    answer: "[Hindi chatbot answer — English review translation] The Chhattisgarh Store Purchase Rules govern procurement by covered State departments and offices. The answer identifies approved channels such as GeM, Single/Limited/Open Tender methods, permitted direct or inter-departmental purchase, and controls over specifications, competition, evaluation and award. Source: Chhattisgarh Store Purchase Rules.",
    reference_answer: "[Hindi reviewer reference — English review translation] Depending on the applicable rules, routes may include GeM or the State online portal, tender procurement, purchase from another government department or undertaking, and permitted special purchase in exceptional situations such as disaster or law-and-order emergencies. Each route remains subject to applicable conditions and approvals.",
  };
  return translations[field] || repairMojibake(row[field]);
}

function setTitle(sheet, range, text) {
  sheet.getRange(range).merge();
  const cell = sheet.getRange(range);
  cell.values = [[text]];
  cell.format = {
    fill: navy,
    font: { bold: true, color: white, size: 16 },
    horizontalAlignment: "left",
    verticalAlignment: "center",
  };
  cell.format.rowHeight = 28;
}

function section(sheet, range, text) {
  sheet.getRange(range).merge();
  const cell = sheet.getRange(range);
  cell.values = [[text]];
  cell.format = {
    fill: teal,
    font: { bold: true, color: white, size: 11 },
    verticalAlignment: "center",
  };
  cell.format.rowHeight = 22;
}

function header(sheet, range) {
  const cell = sheet.getRange(range);
  cell.format = {
    fill: navy,
    font: { bold: true, color: white },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "all", style: "thin", color: border },
  };
}

// Overview
overview.showGridLines = false;
setTitle(overview, "A1:H1", "CHiPS e-Procurement Chatbot — Human Adjudication Pack");
overview.getRange("A3:H3").merge();
overview.getRange("A3").values = [[
  "Purpose: independently validate the automated benchmark and calibrate the LLM-as-a-judge scores against reviewer judgments. This workbook is evaluation-only; it does not change the production chatbot."
]];
overview.getRange("A3").format = { fill: paleBlue, wrapText: true, verticalAlignment: "center" };
overview.getRange("A3").format.rowHeight = 36;

section(overview, "A5:D5", "Latest automated benchmark (frozen 20-query set)");
overview.getRange("A6:B16").values = [
  ["Metric", "Latest result"],
  ["Actor accuracy", metrics.actor_accuracy_percent / 100],
  ["Fine-intent accuracy", metrics.fine_intent_accuracy_percent / 100],
  ["Expected source recall — top 10", metrics.expected_source_recall_top10_percent / 100],
  ["Expected source recall — final context", metrics.expected_source_recall_final_context_percent / 100],
  ["Expected chunk-evidence coverage", metrics.expected_chunk_evidence_coverage_top10_percent / 100],
  ["Literal response-keyword coverage", metrics.literal_response_keyword_coverage_percent / 100],
  ["Reference-answer BGE cosine", metrics.reference_answer_cosine_mean],
  ["Reference-aware LLM judge pass rate", metrics.llm_judge_with_reference_pass_percent / 100],
  ["Fallback count", metrics.fallback_count],
  ["P95 latency (seconds)", metrics.latency_seconds.p95],
];
header(overview, "A6:B6");
overview.getRange("A7:A16").format = { fill: paleGray, font: { bold: true }, borders: { preset: "inside", style: "thin", color: border } };
overview.getRange("B7:B16").format = { borders: { preset: "inside", style: "thin", color: border }, horizontalAlignment: "right" };
overview.getRange("B7:B12").format.numberFormat = "0.0%";
overview.getRange("B13").format.numberFormat = "0.0000";
overview.getRange("B14").format.numberFormat = "0.0%";
overview.getRange("B15").format.numberFormat = "0";
overview.getRange("B16").format.numberFormat = "0.000";

section(overview, "E5:H5", "Reviewer instructions");
overview.getRange("E6:H12").merge();
overview.getRange("E6").values = [[
  "For each item in Review Queue:\n"
  + "1. Read the question, chatbot answer, final sources and reviewer reference.\n"
  + "2. Score factual correctness, completeness, workflow/role safety and helpfulness from 1–5.\n"
  + "3. Mark citation relevance as Pass or Fail.\n"
  + "4. Give an overall verdict: Pass, Partial or Fail, then add notes for any material issue.\n\n"
  + "Do not penalise a correct paraphrase, different wording, or a source-grounded refusal to invent unsupported values."
]];
overview.getRange("E6").format = { fill: paleYellow, wrapText: true, verticalAlignment: "top", borders: { preset: "outside", style: "thin", color: border } };
overview.getRange("E6").format.rowHeight = 125;

section(overview, "A19:H19", "Acceptance criteria after human review");
overview.getRange("A20:D25").values = [
  ["Criterion", "Target", "How calculated", "Reason"],
  ["Completed reviews", "At least 18 of 20", "All four 1–5 ratings and an overall verdict entered", "Enough coverage to judge the evaluator"],
  ["Human pass rate", "At least 90%", "Overall verdict = Pass and reviewer mean >= 4", "Release-quality answer set"],
  ["Judge–human agreement", "At least 80%", "Both automated reference-aware judge and human verdict agree on pass/non-pass", "LLM judge becomes a monitored secondary metric"],
  ["Workflow safety", "No score below 4", "Reviewer workflow/role-safety rating", "No unsafe buyer/vendor/operator leakage"],
  ["Citation relevance", "No citation Fail", "Reviewer citation-relevance field", "Displayed sources must support the answer"],
];
header(overview, "A20:D20");
overview.getRange("A21:D25").format = { wrapText: true, verticalAlignment: "top", borders: { preset: "inside", style: "thin", color: border } };
overview.getRange("A21:D25").format.rowHeight = 36;

overview.getRange("A1:H25").format.font = { name: "Aptos", size: 10 };
overview.getRange("A1").format.font = { name: "Aptos Display", bold: true, color: white, size: 16 };
overview.getRange("A1:A25").format.columnWidth = 28;
overview.getRange("B1:B25").format.columnWidth = 18;
overview.getRange("C1:C25").format.columnWidth = 38;
overview.getRange("D1:D25").format.columnWidth = 34;
overview.getRange("E1:H25").format.columnWidth = 24;
overview.freezePanes.freezeRows(1);

// Review Queue
queue.showGridLines = false;
setTitle(queue, "A1:V1", "Human Review Queue — Frozen 20-Query Benchmark");
queue.getRange("A2:V2").merge();
queue.getRange("A2").values = [[
  "Blue columns contain benchmark evidence. Yellow columns are reviewer inputs. Reviewer Mean and Judge vs Human are formula-driven after review."
]];
queue.getRange("A2").format = { fill: paleBlue, wrapText: true };

const headers = [[
  "ID", "Persona", "Language", "User Question", "Chatbot Answer", "Expected Actor", "Detected Actor",
  "Expected Intent", "Detected Intent", "Final Source Documents", "Reviewer Reference Answer",
  "LLM Judge — No Reference", "LLM Judge — With Reference", "Factual Correctness (1–5)",
  "Completeness (1–5)", "Workflow / Role Safety (1–5)", "Helpfulness (1–5)",
  "Citation Relevance", "Overall Verdict", "Reviewer Mean", "Judge vs Human", "Reviewer Notes"
]];
queue.getRange("A4:V4").values = headers;
header(queue, "A4:V4");
queue.getRange("A4:V4").format.rowHeight = 42;

const rows = results.map((row) => [
  row.id,
  repairMojibake(row.persona),
  repairMojibake(row.language),
  reviewerText(row, "query"),
  reviewerText(row, "answer"),
  repairMojibake(row.expected_actor),
  repairMojibake(row.detected_actor),
  repairMojibake(row.expected_fine_intent),
  repairMojibake(row.detected_fine_intent),
  repairMojibake((row.final_sources || []).join("; ")),
  reviewerText(row, "reference_answer"),
  row.llm_judge_without_reference?.score ?? "",
  row.llm_judge_with_reference?.score ?? "",
  "", "", "", "", "", "", "", "", "",
]);
queue.getRange("A5:V24").values = rows;
queue.getRange("A5:M24").format = { wrapText: true, verticalAlignment: "top", borders: { preset: "inside", style: "thin", color: border } };
queue.getRange("N5:S24").format = { fill: paleYellow, wrapText: true, verticalAlignment: "top", borders: { preset: "inside", style: "thin", color: border } };
queue.getRange("T5:U24").format = { fill: paleTeal, wrapText: true, verticalAlignment: "top", borders: { preset: "inside", style: "thin", color: border } };
queue.getRange("V5:V24").format = { fill: paleYellow, wrapText: true, verticalAlignment: "top", borders: { preset: "inside", style: "thin", color: border } };
queue.getRange("L5:M24").format.numberFormat = "0.0";
queue.getRange("N5:Q24").format.numberFormat = "0.0";
queue.getRange("T5:T24").format.numberFormat = "0.0";
queue.getRange("A5:V24").format.rowHeight = 105;

for (let row = 5; row <= 24; row += 1) {
  queue.getRange(`T${row}`).formulas = [[`=IF(COUNT(N${row}:Q${row})<4,"",AVERAGE(N${row}:Q${row}))`]];
  queue.getRange(`U${row}`).formulas = [[`=IF(OR(T${row}="",S${row}=""),"",IF(AND(T${row}>=4,S${row}="Pass",M${row}>=4),"Agree",IF(AND(T${row}<4,S${row}<>"Pass",M${row}<4),"Agree","Review")))`]];
}
queue.getRange("N5:Q24").dataValidation = { rule: { type: "list", values: ["1", "2", "3", "4", "5"] } };
queue.getRange("R5:R24").dataValidation = { rule: { type: "list", values: ["Pass", "Fail"] } };
queue.getRange("S5:S24").dataValidation = { rule: { type: "list", values: ["Pass", "Partial", "Fail"] } };
queue.getRange("N5:Q24").conditionalFormats.add("colorScale", { colors: ["#FEE2E2", "#FEF3C7", "#DCFCE7"] });
queue.getRange("R5:S24").conditionalFormats.add("containsText", { text: "Fail", format: { fill: "#FECACA", font: { color: "#991B1B", bold: true } } });
queue.getRange("U5:U24").conditionalFormats.add("containsText", { text: "Review", format: { fill: "#FDE68A", font: { color: "#92400E", bold: true } } });

const widths = {
  A: 8, B: 16, C: 12, D: 34, E: 52, F: 20, G: 20, H: 26, I: 26, J: 34, K: 52,
  L: 13, M: 13, N: 14, O: 14, P: 16, Q: 14, R: 14, S: 14, T: 13, U: 14, V: 34,
};
for (const [column, width] of Object.entries(widths)) queue.getRange(`${column}:${column}`).format.columnWidth = width;
queue.freezePanes.freezeRows(4);
queue.freezePanes.freezeColumns(3);

// Calibration Summary
summary.showGridLines = false;
setTitle(summary, "A1:H1", "Human Adjudication and LLM-Judge Calibration Summary");
summary.getRange("A3:H3").merge();
summary.getRange("A3").values = [[
  "Complete the yellow reviewer cells in Review Queue. This sheet updates automatically and shows whether the LLM judge is sufficiently aligned with human reviewers."
]];
summary.getRange("A3").format = { fill: paleBlue, wrapText: true };
section(summary, "A5:D5", "Review completion and outcomes");
summary.getRange("A6:B14").values = [
  ["Metric", "Current value"],
  ["Completed reviews", ""],
  ["Human Pass", ""],
  ["Human Partial", ""],
  ["Human Fail", ""],
  ["Human pass rate", ""],
  ["Judge–human agreements", ""],
  ["Judge–human agreement rate", ""],
  ["Workflow-safety scores below 4", ""],
];
header(summary, "A6:B6");
summary.getRange("A7:A14").format = { fill: paleGray, font: { bold: true }, borders: { preset: "inside", style: "thin", color: border } };
summary.getRange("B7:B14").format = { fill: paleTeal, borders: { preset: "inside", style: "thin", color: border }, horizontalAlignment: "right" };
summary.getRange("B7").formulas = [["=COUNT('Review Queue'!$T$5:$T$24)"]];
summary.getRange("B8").formulas = [["=COUNTIF('Review Queue'!$S$5:$S$24,\"Pass\")"]];
summary.getRange("B9").formulas = [["=COUNTIF('Review Queue'!$S$5:$S$24,\"Partial\")"]];
summary.getRange("B10").formulas = [["=COUNTIF('Review Queue'!$S$5:$S$24,\"Fail\")"]];
summary.getRange("B11").formulas = [["=IF(B7=0,\"\",B8/B7)"]];
summary.getRange("B12").formulas = [["=COUNTIF('Review Queue'!$U$5:$U$24,\"Agree\")"]];
summary.getRange("B13").formulas = [["=IF(B7=0,\"\",B12/B7)"]];
summary.getRange("B14").formulas = [["=IF(B7=0,\"\",COUNTIFS('Review Queue'!$P$5:$P$24,\"<4\",'Review Queue'!$P$5:$P$24,\"<>\"))"]];
summary.getRange("B11:B13").format.numberFormat = "0.0%";

section(summary, "E5:H5", "Acceptance check");
summary.getRange("E6:H11").values = [
  ["Criterion", "Target", "Formula result", "Status"],
  ["Review coverage", ">= 18", "", ""],
  ["Human pass rate", ">= 90%", "", ""],
  ["Judge–human agreement", ">= 80%", "", ""],
  ["Workflow safety", "0 below 4", "", ""],
  ["Citation relevance", "0 Fail", "", ""],
];
header(summary, "E6:H6");
summary.getRange("E7:H11").format = { wrapText: true, borders: { preset: "inside", style: "thin", color: border } };
summary.getRange("G7").formulas = [["=B7"]];
summary.getRange("G8").formulas = [["=B11"]];
summary.getRange("G9").formulas = [["=B13"]];
summary.getRange("G10").formulas = [["=B14"]];
summary.getRange("G11").formulas = [["=IF(B7=0,\"\",COUNTIF('Review Queue'!$R$5:$R$24,\"Fail\"))"]];
summary.getRange("H7").formulas = [["=IF(G7=\"\",\"Pending\",IF(G7>=18,\"Pass\",\"Pending\"))"]];
summary.getRange("H8").formulas = [["=IF(G8=\"\",\"Pending\",IF(G8>=90%,\"Pass\",\"Review\"))"]];
summary.getRange("H9").formulas = [["=IF(G9=\"\",\"Pending\",IF(G9>=80%,\"Pass\",\"Review\"))"]];
summary.getRange("H10").formulas = [["=IF(G10=\"\",\"Pending\",IF(G10=0,\"Pass\",\"Review\"))"]];
summary.getRange("H11").formulas = [["=IF(G11=\"\",\"Pending\",IF(G11=0,\"Pass\",\"Review\"))"]];
summary.getRange("G8:G9").format.numberFormat = "0.0%";
summary.getRange("H7:H11").conditionalFormats.add("containsText", { text: "Pass", format: { fill: "#DCFCE7", font: { color: "#166534", bold: true } } });
summary.getRange("H7:H11").conditionalFormats.add("containsText", { text: "Review", format: { fill: "#FDE68A", font: { color: "#92400E", bold: true } } });
summary.getRange("H7:H11").conditionalFormats.add("containsText", { text: "Pending", format: { fill: paleGray, font: { color: "#4B5563" } } });

summary.getRange("A17:H17").merge();
summary.getRange("A17").values = [[
  "Interpretation: do not promote the LLM judge to a release gate until the acceptance checks pass after independent reviewer completion. Until then, use it as a monitored secondary metric alongside source/chunk evidence and human review."
]];
summary.getRange("A17").format = { fill: paleYellow, wrapText: true, verticalAlignment: "center", borders: { preset: "outside", style: "thin", color: border } };
summary.getRange("A17").format.rowHeight = 42;
summary.getRange("A1:H17").format.font = { name: "Aptos", size: 10 };
summary.getRange("A1").format.font = { name: "Aptos Display", bold: true, color: white, size: 16 };
summary.getRange("A1:A17").format.columnWidth = 30;
summary.getRange("B1:B17").format.columnWidth = 18;
summary.getRange("C1:C17").format.columnWidth = 20;
summary.getRange("D1:D17").format.columnWidth = 20;
summary.getRange("E1:H17").format.columnWidth = 22;
summary.freezePanes.freezeRows(1);

await fs.mkdir(outputDir, { recursive: true });
const inspection = await wb.inspect({
  kind: "table",
  range: "Review Queue!A1:V9",
  include: "values,formulas",
  tableMaxRows: 9,
  tableMaxCols: 22,
});
await fs.writeFile(path.join(outputDir, "inspection.ndjson"), inspection.ndjson, "utf8");
const errorScan = await wb.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "formula error scan",
});
await fs.writeFile(path.join(outputDir, "formula_errors.ndjson"), errorScan.ndjson, "utf8");
for (const sheetName of ["Overview", "Review Queue", "Calibration Summary"]) {
  const preview = await wb.render({ sheetName, autoCrop: "all", scale: 1, format: "png" });
  await fs.writeFile(path.join(outputDir, `${sheetName.replace(/ /g, "_")}.png`), new Uint8Array(await preview.arrayBuffer()));
}
const xlsx = await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(path.join(outputDir, "CHiPS_Human_Adjudication_Pack.xlsx"));
console.log(JSON.stringify({ outputDir, workbook: path.join(outputDir, "CHiPS_Human_Adjudication_Pack.xlsx") }));
