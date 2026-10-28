import json, yaml
from src.util.ontology_loader import load_ontology


def classify_intent(text):
    intents = load_ontology(path='data/ontology/intents.yaml')['intent_labels']
    text_lower = text.lower()
    for intent in intents:
        for pattern in intent["patterns"]:
            if pattern.lower() in text_lower:
                return intent['name']
    return "NONE"


