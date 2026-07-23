import requests
import json
import time

QUESTIONS = [
    "What are the different methods of government procurement in Chhattisgarh?",
    "What is the difference between Open Tender and Limited Tender?",
    "In which situations can Single Tender be used?",
    "When is a Two-Stage Bidding process applicable?",
    "Can Reverse Auction be used for every procurement?",
    "What are the procurement methods available under the Chhattisgarh Store Purchase Rules?",
    "What is EMD and why is it required?",
    "Who is exempted from submitting EMD?",
    "When is the EMD refunded to the bidder?",
    "What should I do if my EMD payment fails but the amount is deducted?",
    "What is Performance Security and when is it required?",
    "Under what conditions can Performance Security be exempted?",
    "How do I register as a vendor on the Chhattisgarh e-Procurement portal?",
    "How do I submit my bid online after downloading the tender documents?",
    "What documents are required before submitting a bid?",
    "How can I issue a corrigendum after publishing a tender?",
    "Can a Joint Venture or Consortium participate in government tenders?",
    "How can I check whether a tender is still open or already closed?",
    "My department wants to purchase office furniture worth ₹8 lakh. Which procurement method should be followed according to the rules?",
    "Should I purchase through GeM or through the Chhattisgarh e-Procurement portal? What is the difference?"
]

URL = "http://127.0.0.1:5000/api/stream"

results = []

print(f"Testing {len(QUESTIONS)} questions using /api/stream...")
for i, q in enumerate(QUESTIONS):
    print(f"[{i+1}/{len(QUESTIONS)}] {q}")
    try:
        t0 = time.time()
        resp = requests.post(URL, json={"query": q}, stream=True, timeout=120)
        
        full_answer = ""
        sources = []
        
        for line in resp.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith("data: "):
                    try:
                        data = json.loads(line_str[6:])
                        if data.get("type") == "token":
                            full_answer += data.get("content", "")
                        elif data.get("type") == "done":
                            sources = data.get("sources", [])
                    except json.JSONDecodeError:
                        pass

        t1 = time.time()
        
        results.append({
            "question": q,
            "success": True,
            "time": f"{t1-t0:.2f}s",
            "answer": full_answer.strip(),
            "sources": sources
        })
    except Exception as e:
        print(f"Exception: {e}")
        results.append({
            "question": q,
            "success": False,
            "error": str(e)
        })

with open("scratch/batch_test_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("Done! Saved to scratch/batch_test_results.json")
