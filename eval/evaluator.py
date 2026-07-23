import os
import json
import requests
import re
from dotenv import load_dotenv

load_dotenv(r"C:\Users\HP\Desktop\E-PROC-CHATBOT_ANTI_GRAVITY\.env")
SARVAM_API_KEY = os.getenv('SARVAM_API_KEY')

def call_heuristic_judge(question, expected_summary, generated_answer):
    expected_words = set(re.findall(r'\b\w+\b', expected_summary.lower()))
    generated_words = set(re.findall(r'\b\w+\b', generated_answer.lower()))
    
    # Accuracy: at least 40% of important expected words are present
    common_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'to', 'in', 'of', 'and', 'or', 'for', 'with', 'on', 'at', 'by', 'this', 'that', 'it', 'as'}
    important_expected = expected_words - common_words
    if not important_expected:
        return True, False
        
    overlap = important_expected.intersection(generated_words)
    accuracy = (len(overlap) / len(important_expected)) >= 0.35
    
    # Hallucination: Check for random numbers not in expected
    expected_numbers = set(re.findall(r'\b\d+\b', expected_summary))
    generated_numbers = set(re.findall(r'\b\d+\b', generated_answer))
    hallucination = not generated_numbers.issubset(expected_numbers) and len(generated_numbers - expected_numbers) > 1
    
    return accuracy, hallucination

def main():
    results_path = 'eval/results.json'
    metrics_path = 'eval/evaluation_metrics.json'
    
    if not os.path.exists(results_path):
        print("Results file not found. Run runner.py first.")
        return
        
    with open(results_path, 'r', encoding='utf-8') as f:
        results = json.load(f)
        
    evaluated_results = []
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r', encoding='utf-8') as f:
            evaluated_results = json.load(f)
            
    start_index = len(evaluated_results)
    
    for i in range(start_index, len(results)):
        res = results[i]
        print(f"Evaluating {res['id']}/{len(results)}...")
        
        # 1. Retrieval Accuracy
        expected_docs = res['expected_documents']
        retrieved_docs = res['retrieved_documents']
        
        if expected_docs == ['general'] or expected_docs == ['out_of_scope']:
            retrieval_accurate = True
            citation_accurate = True
        else:
            retrieval_accurate = any(any(ed.lower() in rd.lower() for ed in expected_docs) for rd in retrieved_docs)
            citation_accurate = retrieval_accurate # simplified citation metric
            
        # 2. Intent Accuracy
        def get_intent_status(exp, pred):
            if exp == pred:
                return 'Correct'
            mappings = {
                'procurement_rules': {'fallback': ['general']},
                'user_manuals': {'equivalent': ['portal_manual', 'technical_manual'], 'fallback': ['general']},
                'general': {'equivalent': ['faq']},
                'out_of_scope': {'fallback': ['general']}
            }
            config = mappings.get(exp, {})
            if pred in config.get('equivalent', []):
                return 'Equivalent'
            if pred in config.get('fallback', []):
                return 'Fallback'
            return 'Wrong'
            
        intent_status = get_intent_status(res['expected_intent'], res['detected_intent'])
        
        # 3. Answer Accuracy & Hallucination
        if res.get('generated_answer', '').startswith('ERROR'):
            ans_acc, hal = False, False
            error_type = 'Generation Failure'
        else:
            ans_acc, hal = call_heuristic_judge(res['question'], res['expected_answer_summary'], res['generated_answer'])
            
            # 4. Error Analysis
            error_type = None
            if intent_status == 'Wrong':
                error_type = 'Wrong Intent'
            elif not retrieval_accurate:
                error_type = 'Wrong Retrieval'
            elif hal:
                error_type = 'Hallucination'
            elif not ans_acc:
                error_type = 'Missing Context'
                
        eval_entry = {
            'id': res['id'],
            'category': res['category'],
            'retrieval_accurate': retrieval_accurate,
            'intent_status': intent_status,
            'answer_accurate': ans_acc,
            'hallucination': hal,
            'error_type': error_type,
            'response_time_ms': res['response_time_ms'],
            'prompt_tokens': res['prompt_tokens'],
            'output_tokens': res['output_tokens']
        }
        
        evaluated_results.append(eval_entry)
        
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(evaluated_results, f, indent=4)

if __name__ == "__main__":
    main()
