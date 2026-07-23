import json
import os
from collections import Counter

def main():
    metrics_path = 'eval/evaluation_metrics.json'
    report_path = 'eval/evaluation_report.md'
    
    if not os.path.exists(metrics_path):
        print("Metrics file not found. Run evaluator.py first.")
        return
        
    with open(metrics_path, 'r', encoding='utf-8') as f:
        metrics = json.load(f)
        
    total_questions = len(metrics)
    if total_questions == 0:
        return
        
    # Overall KPIs
    retrieval_acc = sum(1 for m in metrics if m['retrieval_accurate']) / total_questions * 100
    
    strict_intent_acc = sum(1 for m in metrics if m['intent_status'] == 'Correct') / total_questions * 100
    equivalent_intent_acc = sum(1 for m in metrics if m['intent_status'] in ['Correct', 'Equivalent']) / total_questions * 100
    functional_intent_acc = sum(1 for m in metrics if m['intent_status'] in ['Correct', 'Equivalent', 'Fallback']) / total_questions * 100
    
    answer_acc = sum(1 for m in metrics if m['answer_accurate']) / total_questions * 100
    hallucination_rate = sum(1 for m in metrics if m['hallucination']) / total_questions * 100
    
    avg_latency = sum(m['response_time_ms'] for m in metrics) / total_questions
    latencies = sorted([m['response_time_ms'] for m in metrics])
    p95_latency = latencies[int(0.95 * total_questions) - 1] if total_questions >= 20 else latencies[-1]
    
    avg_prompt = sum(m['prompt_tokens'] for m in metrics) / total_questions
    avg_output = sum(m['output_tokens'] for m in metrics) / total_questions
    
    # Error Analysis
    errors = [m['error_type'] for m in metrics if m['error_type'] is not None]
    error_counts = Counter(errors)
    
    # Category Performance
    categories = {}
    for m in metrics:
        cat = m['category']
        if cat not in categories:
            categories[cat] = {'total': 0, 'ans_acc': 0, 'ret_acc': 0}
        categories[cat]['total'] += 1
        if m['answer_accurate']: categories[cat]['ans_acc'] += 1
        if m['retrieval_accurate']: categories[cat]['ret_acc'] += 1
        
    # Correlation
    wrong_strict_intents = [m for m in metrics if m['intent_status'] != 'Correct']
    total_wrong_intents = len(wrong_strict_intents)
    retrieval_success_when_wrong = sum(1 for m in wrong_strict_intents if m['retrieval_accurate'])
    answer_success_when_wrong = sum(1 for m in wrong_strict_intents if m['answer_accurate'])
    
    ret_corr = (retrieval_success_when_wrong / total_wrong_intents * 100) if total_wrong_intents else 0
    ans_corr = (answer_success_when_wrong / total_wrong_intents * 100) if total_wrong_intents else 0
    
    # Markdown Report Generation
    report = f"""# Chatbot Evaluation Report

## Overall Performance Dashboard

| Metric | Value |
|--------|-------|
| Questions Tested | {total_questions} |
| Strict Intent Accuracy | {strict_intent_acc:.1f}% |
| Equivalent Intent Accuracy | {equivalent_intent_acc:.1f}% |
| Functional Intent Accuracy | {functional_intent_acc:.1f}% |
| Retrieval Accuracy | {retrieval_acc:.1f}% |
| Answer Accuracy | {answer_acc:.1f}% |
| Hallucination Rate | {hallucination_rate:.1f}% |
| Average Latency | {avg_latency/1000:.2f}s |
| Pass Rate | {answer_acc:.1f}% |

## Intent Failure Correlation
When the strict intent was "wrong" ({total_wrong_intents} queries):
- **Retrieval Succeeded**: {ret_corr:.1f}% of the time
- **Answer Succeeded**: {ans_corr:.1f}% of the time

## Category-wise Performance

| Category | Total | Answer Accuracy | Retrieval Accuracy |
|----------|-------|-----------------|--------------------|
"""
    for cat, data in categories.items():
        ans_pct = (data['ans_acc'] / data['total']) * 100
        ret_pct = (data['ret_acc'] / data['total']) * 100
        report += f"| {cat} | {data['total']} | {ans_pct:.1f}% | {ret_pct:.1f}% |\n"

    report += "\n## Error Analysis\n\n"
    if error_counts:
        for err, count in error_counts.most_common():
            report += f"- **{err}**: {count}\n"
    else:
        report += "No errors detected.\n"

    report += "\n## Top Failed Questions\n\n"
    failed = [m for m in metrics if m['error_type'] is not None][:20]
    for f in failed:
        report += f"**Q{f['id']} ({f['category']})**: Error: {f['error_type']}\n"
        
    report += "\n## Recommendations\n"
    if functional_intent_acc >= 90 and ret_corr >= 50:
        report += "- **Intent Classification is Compensated**: Although strict intent accuracy may be low, the fallback logic accurately defaults to general searches, allowing hybrid retrieval to succeed in most cases. Improving the intent classifier would NOT materially improve the chatbot.\n"
    else:
        report += "- **Improve Intent Classification**: The pipeline is failing to retrieve documents when the intent falls back or mismatches. Upgrading the intent classifier is recommended to improve retrieval filtering.\n"
        
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"Report generated at {report_path}")

if __name__ == "__main__":
    main()
