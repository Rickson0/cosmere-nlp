import yaml, re
from pathlib import Path
from src.util.ontology_loader import load_entities


# src/preprocessing/tag_entities.py
COMMON_WORD_ALIASES = {
    "beautiful", "reason", "will", "may", "grace", "hope",
    "faith", "valor", "mercy", "invention", "whimsy",
    "dominion", "devotion", "ambition", "endowment",
}
    
def build_gazetteer(ontology):
    gaz = {}
    for category, items in ontology.items():
        for item in items:
            name = item["name"].lower()
            aliases = item.get("aliases", [])
            for alias in [name] + aliases:
                gaz[alias.lower()] = (category, name)
    return gaz
       
def tag_text(text):
    gezetteer = build_gazetteer(load_entities())
    text_lower = text.lower()
    tags = set()
    for alias, (category, name) in gezetteer.items():
        if re.search(rf"\b{re.escape(alias)}\b", text_lower):
            tags.add((category, name))
    return tags




