from collections import defaultdict, Counter
from src.preprocessing.classify_conversation import classify_conversation
from src.preprocessing.parse_wob import extract_question_text
from src.util.json_loader import load_raw


def conv_type_rate(data):
    conversation_types = Counter()
    type_rate = {}
    registros = len(data)
    for w in data:
        pergunta = extract_question_text(w)
        tipo = classify_conversation(pergunta)
        for i in tipo:
            conversation_types[i] += 1
    for key, value in conversation_types.items():
        type_rate[key] = value/registros
    return type_rate
