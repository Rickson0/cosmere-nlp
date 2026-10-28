from collections import defaultdict
from src.util.ontology_loader import load_intents
from src.preprocessing.intent_classifier import classify_intent
from src.preprocessing.tag_entities import tag_text
import json


def compute_rafo_rate(wobs_path):
    rafo_by_topic = defaultdict(int)
    total_by_topic = defaultdict(int)
    
    
    with open(wobs_path) as f:
        for line in f:
            wob = json.loads(line)
            text = wob.get("text", "")
            intent = classify_intent(text)
            tags = tag_text(text)
            for tag in tags:
                total_by_topic[tag] += 1
                if intent == "RAFO":
                    rafo_by_topic[tag]+= 1
    return {
        tag: {
            "rafo_rate": rafo_by_topic[tag] / total_by_topic[tag],
            "total": total_by_topic,
        }
        for tag in total_by_topic
    }
    