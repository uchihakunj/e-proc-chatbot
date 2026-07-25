import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "C:/Users/HP/Desktop/E-PROC-CHATBOT_ANTI_GRAVITY";
const OUT_DIR = path.join(ROOT, "docs", "reports");
const FINAL_PPTX = path.join(
  OUT_DIR,
  "CHiPS_eProc_Chatbot_Monthly_Presentation.pptx",
);
const QA_DIR = path.join(OUT_DIR, "monthly_presentation_preview");
const ASSET_DIR = path.join(OUT_DIR, "monthly_work_done_assets");

const W = 1280;
const H = 720;
const FRAME = { left: 72, top: 64, width: 1136, height: 592 };

async function writeBlob(filePath, blob) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

async function readImageBlob(imagePath) {
  const bytes = await fs.readFile(imagePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

function addFooter(slide, index) {
  const line = slide.shapes.add({
    geometry: "rect",
    position: { left: 72, top: 674, width: 1136, height: 2 },
    fill: "#d9e2ec",
    line: { style: "solid", fill: "#d9e2ec", width: 0 },
  });
  line.name = `footer-line-${index}`;

  const left = slide.shapes.add({
    geometry: "textbox",
    position: { left: 72, top: 682, width: 420, height: 22 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  left.text = "CHiPS e-Procurement AI Chatbot | Monthly Progress Presentation";
  left.text.style = { fontSize: 12, color: "slate-500" };

  const right = slide.shapes.add({
    geometry: "textbox",
    position: { left: 1100, top: 682, width: 108, height: 22 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  right.text = `${index}`;
  right.text.style = { fontSize: 12, color: "slate-500", alignment: "right" };
}

function addTitle(slide, title, eyebrow = "MONTHLY REVIEW") {
  const e = slide.shapes.add({
    geometry: "textbox",
    position: { left: 72, top: 40, width: 280, height: 24 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  e.text = eyebrow;
  e.text.style = { fontSize: 13, bold: true, color: "slate-500" };

  const t = slide.shapes.add({
    geometry: "textbox",
    position: { left: FRAME.left, top: 84, width: 900, height: 56 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  t.text = title;
  t.text.style = { fontSize: 34, bold: true, color: "slate-950" };
}

function addBulletBlock(slide, { left, top, width, title, items, accent = "#2563eb" }) {
  const box = slide.shapes.add({
    geometry: "roundRect",
    position: { left, top, width, height: 210 },
    fill: "white",
    line: { style: "solid", fill: "#dbe4ee", width: 1 },
    borderRadius: "rounded-xl",
    shadow: "shadow-sm",
  });

  const bar = slide.shapes.add({
    geometry: "rect",
    position: { left, top, width: 8, height: 210 },
    fill: accent,
    line: { style: "solid", fill: accent, width: 0 },
  });
  bar.name = `${title}-bar`;

  const heading = slide.shapes.add({
    geometry: "textbox",
    position: { left: left + 24, top: top + 18, width: width - 40, height: 28 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  heading.text = title;
  heading.text.style = { fontSize: 22, bold: true, color: "slate-900" };

  const body = slide.shapes.add({
    geometry: "textbox",
    position: { left: left + 24, top: top + 58, width: width - 36, height: 138 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  body.text = items.map((item) => `• ${item}`).join("\n");
  body.text.style = { fontSize: 18, color: "slate-700" };

  return box;
}

function addMetricCard(slide, { left, top, width, value, label, note }) {
  const box = slide.shapes.add({
    geometry: "roundRect",
    position: { left, top, width, height: 150 },
    fill: "#f8fafc",
    line: { style: "solid", fill: "#dbe4ee", width: 1 },
    borderRadius: "rounded-xl",
  });
  box.name = label;
  const v = slide.shapes.add({
    geometry: "textbox",
    position: { left: left + 20, top: top + 18, width: width - 40, height: 48 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  v.text = value;
  v.text.style = { fontSize: 32, bold: true, color: "slate-950" };
  const l = slide.shapes.add({
    geometry: "textbox",
    position: { left: left + 20, top: top + 68, width: width - 40, height: 32 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  l.text = label;
  l.text.style = { fontSize: 18, bold: true, color: "slate-700" };
  const n = slide.shapes.add({
    geometry: "textbox",
    position: { left: left + 20, top: top + 102, width: width - 40, height: 30 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  n.text = note;
  n.text.style = { fontSize: 14, color: "slate-500" };
}

async function build() {
  await fs.mkdir(OUT_DIR, { recursive: true });
  await fs.mkdir(QA_DIR, { recursive: true });

  const presentation = Presentation.create({
    slideSize: { width: W, height: H },
  });

  // Slide 1
  {
    const slide = presentation.slides.add();
    slide.background.fill = "white";
    const kicker = slide.shapes.add({
      geometry: "textbox",
      position: { left: 72, top: 72, width: 280, height: 26 },
      fill: "none",
      line: { style: "solid", fill: "none", width: 0 },
    });
    kicker.text = "MONTHLY PROGRESS PRESENTATION";
    kicker.text.style = { fontSize: 14, bold: true, color: "slate-500" };

    const title = slide.shapes.add({
      geometry: "textbox",
      position: { left: 72, top: 138, width: 760, height: 170 },
      fill: "none",
      line: { style: "solid", fill: "none", width: 0 },
    });
    title.text = "CHiPS e-Procurement AI Chatbot";
    title.text.style = { fontSize: 54, bold: true, color: "slate-950" };

    const sub = slide.shapes.add({
      geometry: "textbox",
      position: { left: 72, top: 320, width: 660, height: 120 },
      fill: "none",
      line: { style: "solid", fill: "none", width: 0 },
    });
    sub.text =
      "Department / Organization assigned: CHiPS, Government of Chhattisgarh\nReporting period: July 2026\nPresentation duration: 15 minutes + 5 minutes discussion";
    sub.text.style = { fontSize: 22, color: "slate-600" };

    const stripe = slide.shapes.add({
      geometry: "roundRect",
      position: { left: 870, top: 108, width: 310, height: 470 },
      fill: "#eff6ff",
      line: { style: "solid", fill: "#bfdbfe", width: 1 },
      borderRadius: "rounded-2xl",
    });
    stripe.name = "cover-panel";

    const summary = slide.shapes.add({
      geometry: "textbox",
      position: { left: 900, top: 160, width: 250, height: 350 },
      fill: "none",
      line: { style: "solid", fill: "none", width: 0 },
    });
    summary.text =
      "Focus this month\n\n• Improve answer quality\n• Strengthen routing and validation\n• Refine UI and voice support\n• Prepare demo-ready documentation";
    summary.text.style = { fontSize: 24, color: "slate-800" };
    addFooter(slide, 1);
  }

  // Slide 2
  {
    const slide = presentation.slides.add();
    slide.background.fill = "white";
    addTitle(slide, "The chatbot addresses a real procurement guidance gap");
    addBulletBlock(slide, {
      left: 72,
      top: 164,
      width: 520,
      title: "Problem statement",
      items: [
        "Procurement manuals and rules are lengthy and difficult to search quickly.",
        "Users need role-specific help for tenders, bids, vendor registration, EMD, and rules.",
        "Queries arrive in English, Hindi, and Hinglish, making manual support slower.",
      ],
    });
    addBulletBlock(slide, {
      left: 616,
      top: 164,
      width: 592,
      title: "Project objectives",
      items: [
        "Provide source-grounded conversational answers for CHiPS e-Procurement workflows.",
        "Support multilingual interactions with clear, context-aware responses.",
        "Reduce answer drift by improving routing, retrieval, and deterministic responders.",
      ],
      accent: "#0f766e",
    });
    addBulletBlock(slide, {
      left: 72,
      top: 404,
      width: 1136,
      title: "Key features",
      items: [
        "Multilingual chatbot widget, source-linked answers, quick prompt chips, PDF/source viewing, and voice support.",
        "Coverage across tender methods, bid submission, evaluation, registration, EMD, auctions, and procurement rules.",
      ],
      accent: "#7c3aed",
    });
    addFooter(slide, 2);
  }

  // Slide 3
  {
    const slide = presentation.slides.add();
    slide.background.fill = "white";
    addTitle(slide, "Methodology combined document processing, retrieval, and answer controls");
    const steps = [
      ["Document pipeline", "Preprocess PDFs, clean OCR, and prepare chunkable text from procurement manuals and rules."],
      ["Knowledge indexing", "Create embeddings, store searchable vectors, and attach metadata for better retrieval."],
      ["Query routing", "Classify actor, intent, and language before selecting response strategy."],
      ["Grounded response", "Retrieve top evidence, rerank context, and generate or serve deterministic answers."],
      ["Validation loop", "Run regression tests, live API checks, and benchmark/UAT reviews to refine quality."],
    ];
    steps.forEach((step, i) => {
      const top = 160 + i * 88;
      const circle = slide.shapes.add({
        geometry: "ellipse",
        position: { left: 88, top, width: 44, height: 44 },
        fill: "#2563eb",
        line: { style: "solid", fill: "#2563eb", width: 0 },
      });
      circle.text = `${i + 1}`;
      circle.text.style = { fontSize: 22, bold: true, color: "white", alignment: "center", valign: "middle" };
      const title = slide.shapes.add({
        geometry: "textbox",
        position: { left: 156, top: top - 2, width: 240, height: 28 },
        fill: "none",
        line: { style: "solid", fill: "none", width: 0 },
      });
      title.text = step[0];
      title.text.style = { fontSize: 22, bold: true, color: "slate-900" };
      const body = slide.shapes.add({
        geometry: "textbox",
        position: { left: 156, top: top + 28, width: 930, height: 46 },
        fill: "none",
        line: { style: "solid", fill: "none", width: 0 },
      });
      body.text = step[1];
      body.text.style = { fontSize: 18, color: "slate-600" };
    });
    addFooter(slide, 3);
  }

  // Slide 4
  {
    const slide = presentation.slides.add();
    slide.background.fill = "white";
    addTitle(slide, "System architecture separates UI, API, retrieval, and model layers");

    const boxes = [
      { left: 84, top: 210, width: 240, height: 120, title: "Web UI", lines: ["Portal page + chatbot widget", "Quick prompts, source drawer, voice controls"], fill: "#eff6ff" },
      { left: 380, top: 210, width: 240, height: 120, title: "Flask API", lines: ["Streaming answers", "Routing, diagnostics, language control"], fill: "#f8fafc" },
      { left: 676, top: 210, width: 240, height: 120, title: "Retrieval Layer", lines: ["Qdrant vector store", "Embedding + reranking context selection"], fill: "#f0fdf4" },
      { left: 972, top: 210, width: 224, height: 120, title: "LLM Layer", lines: ["Local Ollama-hosted models", "Final answer generation"], fill: "#fefce8" },
    ];
    boxes.forEach((b) => {
      slide.shapes.add({
        geometry: "roundRect",
        position: { left: b.left, top: b.top, width: b.width, height: b.height },
        fill: b.fill,
        line: { style: "solid", fill: "#cbd5e1", width: 1 },
        borderRadius: "rounded-xl",
      });
      const t = slide.shapes.add({
        geometry: "textbox",
        position: { left: b.left + 18, top: b.top + 16, width: b.width - 36, height: 30 },
        fill: "none",
        line: { style: "solid", fill: "none", width: 0 },
      });
      t.text = b.title;
      t.text.style = { fontSize: 22, bold: true, color: "slate-900", alignment: "center" };
      const txt = slide.shapes.add({
        geometry: "textbox",
        position: { left: b.left + 18, top: b.top + 54, width: b.width - 36, height: 52 },
        fill: "none",
        line: { style: "solid", fill: "none", width: 0 },
      });
      txt.text = b.lines.join("\n");
      txt.text.style = { fontSize: 17, color: "slate-600", alignment: "center" };
    });

    const stack = slide.shapes.add({
      geometry: "textbox",
      position: { left: 92, top: 408, width: 1110, height: 160 },
      fill: "none",
      line: { style: "solid", fill: "none", width: 0 },
    });
    stack.text =
      "Technology stack: Python 3.11, Flask, Node.js / Express, Qdrant, BGE-M3 embeddings, bge-reranker-v2-m3, local Ollama models, HTML/CSS/JavaScript, and browser-based speech support.";
    stack.text.style = { fontSize: 24, color: "slate-700", alignment: "center" };
    addFooter(slide, 4);
  }

  // Slide 5
  {
    const slide = presentation.slides.add();
    slide.background.fill = "white";
    addTitle(slide, "This month focused on UI polish, answer quality, and validation");
    addBulletBlock(slide, {
      left: 72,
      top: 164,
      width: 352,
      title: "Activities completed",
      items: [
        "Prepared monthly and project reports.",
        "Captured chatbot screenshots and demo assets.",
        "Reorganized project documentation and support files.",
      ],
    });
    addBulletBlock(slide, {
      left: 464,
      top: 164,
      width: 352,
      title: "Technical work",
      items: [
        "Added routing, context diagnostics, and language enforcement.",
        "Improved voice latency with browser STT fallback.",
        "Refined UI interactions and answer presentation flow.",
      ],
      accent: "#0f766e",
    });
    addBulletBlock(slide, {
      left: 856,
      top: 164,
      width: 352,
      title: "Quality work",
      items: [
        "Ran exact-answer validation and UAT quality audit.",
        "Added high-risk deterministic responders and regression cases.",
        "Documented benchmark outcomes and remaining defects.",
      ],
      accent: "#7c3aed",
    });
    addFooter(slide, 5);
  }

  // Slide 6
  {
    const slide = presentation.slides.add();
    slide.background.fill = "white";
    addTitle(slide, "Technical contributions improved correctness on sensitive procurement queries");
    const leftItems = [
      "Introduced direct anti-splitting guidance for purchase-splitting questions.",
      "Added explicit intent for vendor registration approval time.",
      "Added deterministic responses for DSC, eligibility, bid opening, and evaluation-report cases.",
    ];
    const rightItems = [
      "Extended regression coverage for routing and procurement workflows.",
      "Added exact-question answering metric to the benchmark runner.",
      "Improved UI support for Auto-Voice and browser-friendly interaction.",
    ];
    addBulletBlock(slide, {
      left: 72,
      top: 176,
      width: 540,
      title: "Backend / answer engine",
      items: leftItems,
    });
    addBulletBlock(slide, {
      left: 668,
      top: 176,
      width: 540,
      title: "Validation / UX",
      items: rightItems,
      accent: "#0f766e",
    });
    addFooter(slide, 6);
  }

  // Slide 7
  {
    const slide = presentation.slides.add();
    slide.background.fill = "white";
    addTitle(slide, "AI and data-science components power multilingual retrieval and grounded generation");
    slide.charts.add("bar", {
      position: { left: 88, top: 202, width: 450, height: 290 },
      categories: ["Retrieval", "Context", "Language", "Streaming"],
      series: [{ name: "Current metric", values: [80, 75, 97, 99], fill: "accent1" }],
      hasLegend: false,
      dataLabels: { showValue: true, position: "outEnd" },
      yAxis: { majorGridlines: { style: "solid", fill: "slate-200", width: 1 } },
    });
    const text = slide.shapes.add({
      geometry: "textbox",
      position: { left: 590, top: 190, width: 600, height: 330 },
      fill: "none",
      line: { style: "solid", fill: "none", width: 0 },
    });
    text.text =
      "Tools and technologies used\n\n• BGE-M3 for multilingual embeddings\n• bge-reranker-v2-m3 for reranking\n• Qdrant as vector database\n• Local LLMs through Ollama\n• Flask and Node.js for application delivery\n• Automated benchmark and regression scripts for evaluation";
    text.text.style = { fontSize: 22, color: "slate-700" };
    addFooter(slide, 7);
  }

  // Slide 8
  {
    const slide = presentation.slides.add();
    slide.background.fill = "white";
    addTitle(slide, "Progress is visible in targeted validation even as broad benchmark gaps remain");
    addMetricCard(slide, {
      left: 80,
      top: 170,
      width: 250,
      value: "49",
      label: "Regression tests passed",
      note: "Fine-intent, actor boundary, workflow checks",
    });
    addMetricCard(slide, {
      left: 360,
      top: 170,
      width: 250,
      value: "12 / 12",
      label: "Focused live checks passed",
      note: "Mean latency 1.51 seconds",
    });
    addMetricCard(slide, {
      left: 640,
      top: 170,
      width: 250,
      value: "37",
      label: "UAT remediation tests passed",
      note: "High-risk cases validated",
    });
    addMetricCard(slide, {
      left: 920,
      top: 170,
      width: 250,
      value: "120",
      label: "Production benchmark queries",
      note: "Used for gap discovery",
    });
    const note = slide.shapes.add({
      geometry: "roundRect",
      position: { left: 80, top: 380, width: 1090, height: 160 },
      fill: "#fff7ed",
      line: { style: "solid", fill: "#fdba74", width: 1 },
      borderRadius: "rounded-xl",
    });
    note.name = "milestone-note";
    const text = slide.shapes.add({
      geometry: "textbox",
      position: { left: 106, top: 408, width: 1040, height: 108 },
      fill: "none",
      line: { style: "solid", fill: "none", width: 0 },
    });
    text.text =
      "Progress against planned milestones\n\nThe planned milestone for this month was to move from broad prototype behavior toward more reliable, demo-ready procurement assistance. That milestone was partially achieved: focused validation improved significantly, but the full 120-query benchmark still shows major gaps in fallback reduction, actor classification, and procedural completeness.";
    text.text.style = { fontSize: 21, color: "slate-700" };
    addFooter(slide, 8);
  }

  // Slide 9 demo
  {
    const slide = presentation.slides.add();
    slide.background.fill = "white";
    addTitle(slide, "Demonstration: the chatbot now presents a cleaner and more usable interface");
    const img1 = await readImageBlob(path.join(ASSET_DIR, "chatbot_widget_open.png"));
    const img2 = await readImageBlob(path.join(ASSET_DIR, "chatbot_sample_answer.png"));

    slide.images.add({
      blob: img1,
      contentType: "image/png",
      alt: "Opened chatbot widget on portal page",
      fit: "cover",
      position: { left: 84, top: 176, width: 510, height: 360 },
      geometry: "roundRect",
      borderRadius: "rounded-xl",
    });
    slide.images.add({
      blob: img2,
      contentType: "image/png",
      alt: "Chatbot sample answer view",
      fit: "cover",
      position: { left: 640, top: 176, width: 510, height: 360 },
      geometry: "roundRect",
      borderRadius: "rounded-xl",
    });
    const c1 = slide.shapes.add({
      geometry: "textbox",
      position: { left: 84, top: 552, width: 510, height: 24 },
      fill: "none",
      line: { style: "solid", fill: "none", width: 0 },
    });
    c1.text = "Widget view: quick prompts, Auto-Voice, and multilingual entry";
    c1.text.style = { fontSize: 16, color: "slate-600", alignment: "center" };
    const c2 = slide.shapes.add({
      geometry: "textbox",
      position: { left: 640, top: 552, width: 510, height: 24 },
      fill: "none",
      line: { style: "solid", fill: "none", width: 0 },
    });
    c2.text = "Answer view: concise response + source visibility";
    c2.text.style = { fontSize: 16, color: "slate-600", alignment: "center" };
    addFooter(slide, 9);
  }

  // Slide 10
  {
    const slide = presentation.slides.add();
    slide.background.fill = "white";
    addTitle(slide, "The main challenges are accuracy gaps at scale and environment constraints");
    addBulletBlock(slide, {
      left: 72,
      top: 176,
      width: 540,
      title: "Challenges encountered",
      items: [
        "Broad benchmark still shows low pass rate and high fallback behavior.",
        "Actor and fine-intent errors affect retrieval and answer quality.",
        "Some UI/browser validation is blocked by local environment issues.",
      ],
    });
    addBulletBlock(slide, {
      left: 668,
      top: 176,
      width: 540,
      title: "Implications",
      items: [
        "Need tighter evidence contracts for sensitive procurement answers.",
        "Need stronger semantic UAT acceptance criteria, not only routing checks.",
        "Need continued live verification before wider deployment.",
      ],
      accent: "#b45309",
    });
    addFooter(slide, 10);
  }

  // Slide 11
  {
    const slide = presentation.slides.add();
    slide.background.fill = "white";
    addTitle(slide, "Next month’s plan focuses on targeted quality improvement and review support");
    addBulletBlock(slide, {
      left: 72,
      top: 176,
      width: 540,
      title: "Work plan for next month",
      items: [
        "Reduce fallback-heavy cases and improve procedural completeness.",
        "Re-run multilingual UAT with stricter semantic assertions.",
        "Continue UI verification and live demo readiness improvements.",
      ],
      accent: "#0f766e",
    });
    addBulletBlock(slide, {
      left: 668,
      top: 176,
      width: 540,
      title: "Support required",
      items: [
        "Feedback from IIIT-NR on evaluation focus and expected output quality.",
        "Department-side confirmation of priority use cases for the next validation cycle.",
        "Access/support for broader demo testing and deployment-readiness review.",
      ],
      accent: "#7c3aed",
    });
    const close = slide.shapes.add({
      geometry: "textbox",
      position: { left: 72, top: 440, width: 1136, height: 70 },
      fill: "none",
      line: { style: "solid", fill: "none", width: 0 },
    });
    close.text =
      "Central takeaway: the chatbot is now more structured, more grounded, and more demo-ready, but it still needs another cycle of focused quality work before it can be treated as broadly reliable.";
    close.text.style = { fontSize: 24, bold: true, color: "slate-900", alignment: "center" };
    addFooter(slide, 11);
  }

  for (const [idx, slide] of presentation.slides.items.entries()) {
    const stem = `slide-${String(idx + 1).padStart(2, "0")}`;
    await writeBlob(
      path.join(QA_DIR, `${stem}.png`),
      await presentation.export({ slide, format: "png", scale: 1 }),
    );
  }
  await writeBlob(
    path.join(QA_DIR, "deck-montage.webp"),
    await presentation.export({ format: "webp", montage: true, scale: 1 }),
  );

  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(FINAL_PPTX);
  console.log(FINAL_PPTX);
}

build().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
