import yaml



def load_ontology(path="data/ontology/entities.yaml"):
    d = yaml.safe_load(open(path))
    return d
    