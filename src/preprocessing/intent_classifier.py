import json
import yaml
import re
from src.util.ontology_loader import load_intents


import re
from functools import lru_cache


@lru_cache(maxsize=1)
def get_compiled_intents(path="data/ontology/intents.yaml"):

    with open(path) as f:
        data = yaml.safe_load(f)

    if isinstance(data, dict):
        intents = next((v for v in data.values() if isinstance(v, list)), [])
    else:
        intents = data

    compiled = []
    for intent in intents:
        name = (intent.get("name") or "unknown").lower()
        patterns = intent.get("patterns") or []
        regexes = []
        for p in patterns:
            p = str(p).strip()
            if not p:
                continue
            try:
                regexes.append(re.compile(p, re.IGNORECASE | re.MULTILINE))
            except re.error as e:
                print(f"[aviso] pattern inválido em '{name}': {p!r} → {e}")
        compiled.append((name, regexes))
    return compiled


def classify_intent(answer_text):
    hits = []
    for name, regexes in get_compiled_intents():
        for rx in regexes:
            if rx.search(answer_text):
                hits.append(name)
                break
    return hits or ["other"]
