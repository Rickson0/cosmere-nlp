import json
from src.preprocessing.parse_wob import extract_answer_text
from src.preprocessing.intent_classifier import classify_intent


def is_rafo(answer_text):
    return "rafo" in classify_intent(answer_text)


def evaluate_against_gold(gold_path, wobs_path):
   
    gold = json.load(open(gold_path))
    gold_by_id = {g["id"]: g["rafo"] for g in gold}

    data = json.load(open(wobs_path))
    data_by_id = {w["id"]: w for w in data}

    tp = fp = fn = tn = 0
    errors = []

    for wob_id, truth in gold_by_id.items():
        w = data_by_id.get(wob_id)
        if not w:
            errors.append((wob_id, "MISSING", "WoB não está no corpus"))
            continue

        answer = extract_answer_text(w)
        pred = is_rafo(answer)

        if pred and truth:
            tp += 1
        elif pred and not truth:
            fp += 1
            errors.append((wob_id, "FP", answer[:120]))
        elif not pred and truth:
            fn += 1
            errors.append((wob_id, "FN", answer[:120]))
        else:
            tn += 1

    precision = tp / (tp + fp) if tp + fp else 0
    recall    = tp / (tp + fn) if tp + fn else 0
    f1        = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0

    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "errors": errors,
    }


def evaluate_on_corpus(wobs_path):
   
    from collections import Counter

    data = json.load(open(wobs_path))
    intent_counter = Counter()
    rafo_count = 0

    for w in data:
        answer = extract_answer_text(w)
        intents = classify_intent(answer)
        for i in intents:
            intent_counter[i] += 1
        if "rafo" in intents:
            rafo_count += 1

    total = len(data)
    return {
        "total": total,
        "rafo_count": rafo_count,
        "rafo_rate": rafo_count / total if total else 0,
        "intent_distribution": dict(intent_counter),
    }


def print_report_gold(result):
    print("=== VALIDAÇÃO CONTRA GOLD SET ===")
    print(f"TP={result['tp']}  FP={result['fp']}  FN={result['fn']}  TN={result['tn']}")
    print(f"Precisão: {result['precision']:.2%}")
    print(f"Recall:   {result['recall']:.2%}")
    print(f"F1:       {result['f1']:.2%}")
    if result["errors"]:
        print(f"\n--- {len(result['errors'])} erros ---")
        for wob_id, tipo, trecho in result["errors"]:
            print(f"[{tipo}] id={wob_id}: {trecho!r}")


def print_report_corpus(result):
    print("=== ANÁLISE NO CORPUS ===")
    print(f"Total de WoBs: {result['total']}")
    print(f"WoBs com RAFO: {result['rafo_count']} ({result['rafo_rate']:.2%})")
    print("\nDistribuição de intents:")
    for intent, count in sorted(result["intent_distribution"].items(), key=lambda x: -x[1]):
        print(f"  {count:5d}  {intent}")


if __name__ == "__main__":
    # 1. Validar contra gold
    gold_result = evaluate_against_gold(
        gold_path="data/processed/gold.json",
        wobs_path="data/raw/wobs.json",
    )
    print_report_gold(gold_result)

    print()

    # 2. Rodar no corpus inteiro
    corpus_result = evaluate_on_corpus("data/raw/wobs.json")
    print_report_corpus(corpus_result)