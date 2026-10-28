import yaml

path = "data/ontology/entities.yaml"

def load_ontology():
    d = yaml.safe_load(open(path))
    return d
    