import json
from src.preprocessing.parse_wob import extract_brandon_text, extract_question_text, extract_full_text
from src.preprocessing.classify_conversation import  classify_conversation
from src.preprocessing.intent_classifier import  classify_intent
from src.preprocessing.tag_entities import  tag_text
from src.util.ontology_loader import load_ontology

gold = json.load(open("data/processed/gold.json"))
raw = json.load(open("data/raw/wobs.json"))


for w in raw[:10]:
    q   = extract_question_text(w)
    b   = extract_brandon_text(w)
    full = extract_full_text(w)
    print({
        "id": w["id"],
        "entities":   list(tag_text(full)),
        "conv_type":  classify_conversation(q),
        "intent":     classify_intent(b),
        "question": q,
        "brandon": b,
        "has_rafo_tag": "rafo" in w.get("tags", []) or "rafo-plus" in w.get("tags", []),
    })