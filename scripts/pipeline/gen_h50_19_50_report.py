import json
import os
import requests
import sys

from eval.holdout_50.run_holdout import RAW

def extract_answer(stream_text):
    buf = []
    lines = stream_text.splitlines()
    for line in lines:
        if line.startswith("data: "):
            data = line[6:]
            if data == "[DONE]":
                break
            try:
                msg = json.loads(data)
                if msg.get("type") == "token":
                    buf.append(msg.get("content", ""))
            except:
                pass
    return "".join(buf)

def main():
    print("Starting generation for H50-19 to H50-50...")
    report_lines = ["# Manager-Demo Response Comparison (H50-19 to H50-50)\n"]
    
    # We filter for questions 19 to 50
    # The RAW data starts at H50-01. So index 18 is H50-19.
    subset = RAW[18:50]
    
    for row in subset:
        qid = row[0]
        question = row[1]
        print(f"Processing {qid}...")
        
        payload = {
            "query": question,
            "session_id": "manager-demo-test"
        }
        
        try:
            resp = requests.post("http://localhost:5000/api/stream", json=payload, stream=True)
            if resp.status_code == 200:
                answer = extract_answer(resp.text)
            else:
                answer = f"ERROR: {resp.status_code}"
        except Exception as e:
            answer = f"REQUEST FAILED: {e}"
            
        report_lines.append(f"## {qid}: {question}")
        report_lines.append("### Generated Conversational Answer")
        report_lines.append(answer)
        report_lines.append("\n---\n")

    report_path = "C:/Users/HP/.gemini/antigravity-ide/brain/0e69020d-2845-431f-b942-94737012a41d/QA_H50_19_50_Comparison_Report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print(f"Report saved to {report_path}")

if __name__ == "__main__":
    main()
