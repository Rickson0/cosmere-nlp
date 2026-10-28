import yaml, re
from pathlib import Path


def load_ontology(path="data/ontology/entities.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)
    
def build_gazetteer(ontology):
    gaz = {}
    for category, items in ontology.items():
        for item in items:
            name = item["name"].lower()
            aliases = item.get("aliases", [])
            for alias in [name] + aliases:
                gaz[alias.lower()] = (category, name)
    return gaz
    
    
def tag_text(text, gezetteer):
    text_lower = text.lower()
    tags = set()
    for alias, (category, name) in gezetteer.items():
        if re.search(rf"\b{re.escape(alias)}\b", text_lower):
            tags.add((category, name))
    return tags



ontology = load_ontology()
gaz = build_gazetteer(ontology)
text = "Would Nicrosil Compounding work with Hemalurgy on Scadrial?"
print(tag_text(text, gaz))
