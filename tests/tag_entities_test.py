from src.util.ontology_loader import load_ontology
from src.util.json_loader import load_raw
from src.preprocessing.parse_wob import extract_answer_text


data = load_raw()[1]

print(extract_answer_text(data))






