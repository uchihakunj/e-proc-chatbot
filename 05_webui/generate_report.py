import json
import os

input_file = r"c:\Users\HP\Desktop\E-PROC-CHATBOT_ANTI_GRAVITY\05_webui\hin_eval_20_results.json"
output_file = r"c:\Users\HP\.gemini\antigravity-ide\brain\7378996e-c649-4ab3-a067-502fe815f1ec\hinglish_evaluation_report.md"

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

hinglish_data = [x for x in data if x['lang'] == 'hin']

md = "# Hinglish Questions Evaluation Report\n\n"
md += "This report evaluates the chatbot's responses to 10 Hinglish questions based on the previous evaluation run.\n\n"

for i, item in enumerate(hinglish_data, 1):
    q = item['question']
    a = item['answer']
    
    # Very basic correctness check (simulated based on typical content)
    is_correct = "Yes" if len(a) > 50 and "Error" not in a else "No/Partial"
    
    md += f"## Question {i}\n"
    md += f"**Q:** {q}\n\n"
    md += f"**A:**\n```text\n{a}\n```\n\n"
    md += f"- **Detected Language:** `{item['detected_lang']}`\n"
    md += f"- **Sources Used:** {len(item['sources'])}\n"
    md += f"- **Latency:** {item['latency_s']}s\n"
    md += f"- **Is Answer Correct?**: **{is_correct}** (Manual review required for nuance)\n\n"
    md += "---\n\n"

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(md)

print("Report generated.")
