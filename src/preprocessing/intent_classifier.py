import json, yaml
import re
from src.util.ontology_loader import load_intents


def classify_intent(brandon_text):
    intents = load_intents()['intent_labels']
    text = brandon_text.lower()
    hits = []
    for intent in intents:
        patterns = intent.get("patterns",)
        for p in patterns:
            p = str(p).lower()
            if re.search(rf"\b{re.escape(p)}\b", text):
                hits.append(intent.get("name", "unknown").lower())
                break  
    return hits or ["other"]


