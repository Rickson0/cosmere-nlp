import json
from collections import defaultdict
from src.preprocessing.parse_wob import extract_answer_text, extract_full_text
from src.preprocessing.intent_classifier import classify_intent
from src.preprocessing.tag_entities import tag_text
from src.util.ontology_loader import load_entities


data = json.load(open("data/raw/wobs.json"))

rafo_by_topic = defaultdict(int)
total_by_topic = defaultdict(int)

for w in data:
    answer = extract_answer_text(w)
    intents = classify_intent(answer)
    is_rafo = "rafo" in intents

    tags = tag_text(extract_full_text(w))
    for tag in tags:
        total_by_topic[tag] += 1
        if is_rafo:
            rafo_by_topic[tag] += 1

rows = [
    (tag, rafo_by_topic[tag] / total_by_topic[tag], total_by_topic[tag])
    for tag in total_by_topic
    if total_by_topic[tag] >= 10  
]
rows.sort(key=lambda x: -x[1])

print("Top 20 tópicos por taxa de RAFO (min 20 menções):")
for tag, rate, total in rows[:20]:
    print(f"{rate:6.2%}  ({total:4d} menções)  {tag}")