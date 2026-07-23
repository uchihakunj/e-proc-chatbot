import json
import sys
sys.path.insert(0, '05_webui')
from actor_policy import classify_procurement_actor
from nlp_features import classify_intent
from fine_intent_policy import classify_fine_intent

data = json.load(open('eval/holdout_50/remaining_live_audit.json'))
for item in data:
    if int(item['id'].split('-')[1]) >= 27:
        q = item['question']
        expected_actor = item['expected_actor']
        expected_intent = item['expected_intent']
        actor, _ = classify_procurement_actor(q)
        coarse, _ = classify_intent(q)
        fine, _ = classify_fine_intent(q, actor, coarse)
        if actor != expected_actor or fine != expected_intent:
            print(f"{item['id']}: Exp ({expected_actor}, {expected_intent}) - Got ({actor}, {fine}) - Q: {q}")
