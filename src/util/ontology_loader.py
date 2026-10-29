import yaml


def load_ontology(path="data/ontology/entities.yaml"):
    return yaml.safe_load(open(path))


def load_entities():
    return load_ontology("data/ontology/entities.yaml")


def load_intents():
    data = load_ontology("data/ontology/intents.yaml")
    return data


def load_conversation_types():
    return load_ontology("data/ontology/conversation_types.yaml")
