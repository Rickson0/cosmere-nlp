import json, yaml
import re
from src.util.ontology_loader import load_intents


def classify_intent(brandon_text):
    intents = load_intents()
    text = brandon_text.lower()
    hits = []
    for intent in intents:
        patterns = intent.get("patterns") or []
        for p in patterns:
            p = str(p).lower()
            # \b garante que "no" não casa em "not", "know", etc.
            if re.search(rf"\b{re.escape(p)}\b", text):
                hits.append(intent.get("name", "unknown").lower())
                break  # uma hit por intent basta
    return hits or ["other"]


