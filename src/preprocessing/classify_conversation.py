from src.util.ontology_loader import load_conversation_types
def classify_conversation(question_text):
    text = question_text.lower()
    hits = []
    types = load_conversation_types()
    for t in types:
        if t['patterns'] and any(p.lower() in text for p in t["patterns"]):
            hits.append(t["name"])
    return hits or ["cosmere_lore"]
    