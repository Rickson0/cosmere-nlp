# todo **T6.4** — Rodar distribuição de `intent` no corpus (2 min)
from src.preprocessing.intent_classifier import classify_intent
from src.preprocessing.parse_wob import extract_answer_text
from src.util.json_loader import load_raw
from collections import Counter


def intent_distribution(data):
    intent_counter = Counter()
    for item in data:
        resposta = extract_answer_text(item)
        intent = tuple(classify_intent(resposta))
        intent_counter[intent] += 1
    return intent_counter
