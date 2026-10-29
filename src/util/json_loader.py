import json


def load_json(path):
    return json.load(open(path))


def load_raw():
    return load_json("data/raw/wobs.json")


def load_gold():
    return load_json("data/processed/gold.json")
