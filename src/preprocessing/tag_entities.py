import yaml
import re
from pathlib import Path
from src.util.ontology_loader import load_entities
from functools import lru_cache

COMMON_WORD_ALIASES = {
    "beautiful", "reason", "will", "may", "grace", "hope",
    "faith", "valor", "mercy", "invention", "whimsy",
    "dominion", "devotion", "ambition", "endowment",
}


def build_gazetteer(ontology):
    aliases_gaz = {}
    caps_gaz = {}

    for category, items in ontology.items():
        for item in items:
            name = item["name"]
            requires_caps = item.get("requires_capitalization", False)

            for alias in [name] + item.get("aliases", []):
                if requires_caps:
                    caps_gaz[alias] = (category, name.lower())       # ← SEM .lower()
                else:
                    aliases_gaz[alias.lower()] = (category, name.lower())

            for proxy in item.get("proxies", []):
                aliases_gaz[proxy.lower()] = (category, name.lower())

    return aliases_gaz, caps_gaz

@lru_cache(maxsize=1)
def get_matcher():
    aliases_gaz, caps_gaz = build_gazetteer(load_entities())

    alias_pattern = re.compile(
        r'\b(?:' + '|'.join(re.escape(a)
                            for a in sorted(aliases_gaz, key=len, reverse=True)) + r')\b',
        re.IGNORECASE,
    )
    caps_pattern = re.compile(
        r'\b(?:' + '|'.join(re.escape(a)
                            for a in sorted(caps_gaz, key=len, reverse=True)) + r')\b',
    ) if caps_gaz else None

    return aliases_gaz, caps_gaz, alias_pattern, caps_pattern


def tag_text(text):
    aliases_gaz, caps_gaz, alias_pattern, caps_pattern = get_matcher()
    tags = set()

    for match in alias_pattern.finditer(text):
        key = match.group(0).lower()
        if key in aliases_gaz:
            tags.add(aliases_gaz[key])

    if caps_pattern:
        for match in caps_pattern.finditer(text):
            key = match.group(0)                                  # ← SEM .lower()
            if key in caps_gaz:
                tags.add(caps_gaz[key])

    return tags
