from src.util.ontology_loader import load_ontology
from src.preprocessing.tag_entities import build_gazetteer,tag_text


ontology = load_ontology()
gaz = build_gazetteer(ontology)
text = "Would Nicrosil Compounding work with Hemalurgy on Scadrial?"

assert tag_text(text) == "{('planets', 'scadrial'), ('metals', 'nicrosil'), ('concepts', 'compounding'), ('magic_system', 'hemalurgy')}"