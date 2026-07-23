import sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open(r'reports\sarvam105b_test_20260717_153803.json', encoding='utf-8') as f:
    d = json.load(f)

done = d['summary']['done_so_far']
total = d['summary']['total']
results = d['results']
print(f'Progress: {done}/{total} questions answered')
print()

pass_c = partial_c = fail_c = 0
for r in results:
    g = r['grade']
    t = r['response_time_s']
    has_ans = 'OK' if r['final_answer'] else 'EMPTY!'
    qid = r['id']
    cite = r['citation_correctness']['score']
    concept = r['concepts_coverage']['score']
    ans_preview = r['final_answer'][:60].replace('\n', ' ') if r['final_answer'] else '[empty]'
    print(f"  {qid:3s} | {g:7s} | {t:5.1f}s | {has_ans} | cite:{cite} | concept:{concept}")
    print(f"       Answer: {ans_preview}")
    if g == 'PASS': pass_c += 1
    elif g == 'PARTIAL': partial_c += 1
    else: fail_c += 1

print()
print(f"So far -> PASS:{pass_c}  PARTIAL:{partial_c}  FAIL:{fail_c}")
