import sys
import os
import json
import time
import requests
from dotenv import load_dotenv

os.environ["ENVIRONMENT"] = "production"
sys.path.insert(0, r"C:\Users\HP\Desktop\E-PROC-CHATBOT_ANTI_GRAVITY\04_embeddings_and_kg\scripts")
sys.path.insert(0, r"C:\Users\HP\Desktop\E-PROC-CHATBOT_ANTI_GRAVITY\05_webui")

load_dotenv(r"C:\Users\HP\Desktop\E-PROC-CHATBOT_ANTI_GRAVITY\.env")
SARVAM_API_KEY = os.getenv('SARVAM_API_KEY')

import app
rag_pipeline = app._rag_module

def main():
    dataset_path = 'eval/dataset.json'
    results_path = 'eval/results.json'
    
    if not os.path.exists(dataset_path):
        print(f"Error: {dataset_path} not found.")
        return
        
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
        
    results = []
    if os.path.exists(results_path):
        with open(results_path, 'r', encoding='utf-8') as f:
            results = json.load(f)
            
    # Resume from where we left off
    start_index = len(results)
    
    if start_index >= len(dataset):
        print("All questions already processed.")
        return
        
    print(f"Resuming from question {start_index + 1}/{len(dataset)}...")
    
    url = "https://api.sarvam.ai/v1/chat/completions"
    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json"
    }

    for i in range(start_index, len(dataset)):
        entry = dataset[i]
        q = entry['question']
        print(f"[{i+1}/{len(dataset)}] Processing: {q}")
        
        t_start = time.perf_counter()
        
        # 1. Retrieve Context
        t0 = time.perf_counter()
        context_results = rag_pipeline.retrieve_context(q)
        qdrant_time = (time.perf_counter() - t0) * 1000
        
        # 2. Build Context
        builder = getattr(rag_pipeline, 'build_adaptive_context', None)
        prompt_context = builder(
            q,
            context_results,
            source_name_resolver=app.get_actual_filename,
        )
        
        context_text = prompt_context['context_text']
        source_refs = prompt_context['source_refs']
        detected_intent = rag_pipeline.classify_intent(q)
             
        _lang = app.detect_query_language(q)
        
        _q_type = prompt_context.get('query_type', 'factual')
        _length_instruction = ""
        if _q_type == 'factual':
            _length_instruction = "\\n\\nLENGTH CONSTRAINT: Limit your response to 100-150 words."
        elif _q_type == 'procedural':
            _length_instruction = "\\n\\nLENGTH CONSTRAINT: Limit your response to 150-250 words."
        elif _q_type == 'comparison':
            _length_instruction = "\\n\\nLENGTH CONSTRAINT: Limit your response to 200-300 words."
        else:
            _length_instruction = "\\n\\nLENGTH CONSTRAINT: Maximum 350 words. Be concise."

        ollama_system = app.PROCUREMENT_SYSTEM_PROMPT.strip() + app.language_directive(_lang) + _length_instruction
        ollama_user = f"Context:\n{context_text}\n\nQuestion: {q}\n\nAnswer:"
        
        payload = {
            "model": "sarvam-30b",
            "messages": [
                {"role": "system", "content": ollama_system},
                {"role": "user", "content": ollama_user}
            ],
            "temperature": 0,
            "stream": True,
            "max_tokens": 4096
        }
        
        prompt_str = "\n".join([m.get('content', '') for m in payload['messages']])
        prompt_tokens = len(prompt_str.split())
        
        generated_text = ""
        
        try:
            with requests.post(url, headers=headers, json=payload, stream=True, timeout=60) as r:
                if r.status_code == 200:
                    for line in r.iter_lines():
                        if line and b"data: " in line and b"[DONE]" not in line:
                            try:
                                j = json.loads(line.decode('utf-8')[6:])
                                if 'choices' in j and len(j['choices']) > 0:
                                    chunk = j['choices'][0].get('delta', {}).get('content') or ''
                                    generated_text += chunk
                            except Exception:
                                pass
                else:
                    generated_text = f"ERROR: API returned {r.status_code}"
        except Exception as e:
            generated_text = f"ERROR: Exception occurred - {str(e)}"
            
        t_total = (time.perf_counter() - t_start) * 1000
        output_tokens = len(generated_text.split())
        
        result_entry = {
            'id': i + 1,
            'question': q,
            'category': entry['category'],
            'expected_intent': entry['expected_intent'],
            'expected_documents': entry['expected_documents'],
            'expected_answer_summary': entry['expected_answer_summary'],
            'detected_intent': detected_intent,
            'retrieved_documents': source_refs,
            'final_sources': source_refs,
            'response_time_ms': t_total,
            'prompt_tokens': prompt_tokens,
            'output_tokens': output_tokens,
            'generated_answer': generated_text.strip()
        }
        
        results.append(result_entry)
        
        # Save progress
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4)
            
        # Sleep slightly to avoid rate limits
        time.sleep(1.0)

if __name__ == "__main__":
    main()
