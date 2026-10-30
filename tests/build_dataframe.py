import json
import polars as pl
from src.preprocessing.parse_wob import (
    extract_answer_text, extract_question_text, extract_full_text
)
from src.preprocessing.intent_classifier import classify_intent
from src.preprocessing.classify_conversation import (
    load_conversation_types, classify_conversation
)
from src.preprocessing.tag_entities import tag_text

INTENT_ORDER = ["rafo", "denied", "confirmed", "evasive", "annotation", "joke"]

def build_rows(wobs_path="data/raw/wobs.json"):
    data = json.load(open(wobs_path))
    conv_types = load_conversation_types()
    rows = []

    for w in data:
        answer   = extract_answer_text(w)
        question = extract_question_text(w)
        full     = extract_full_text(w)
        intents  = classify_intent(answer)
        conv     = classify_conversation(question)
        entities = tag_text(full)

        # entidades por categoria (listas)
        by_cat = {}
        for cat, name in entities:
            by_cat.setdefault(cat, []).append(name)

        rows.append({
            "id":            w["id"],
            "event":         w.get("event_name"),
            "event_date":    w.get("event_date"),
            "date":          w.get("date"),
            "year":          (w.get("date") or "")[:4] or None,
            "paraphrased":   w.get("paraphrased", False),
            "arcanum_tags":  w.get("tags", []),
            "question":      question,
            "answer":        answer,
            "full_text":     full,
            "answer_len":    len(answer),
            # intents
            "intents":         intents,
            "is_rafo":         "rafo" in intents,
            "is_confirmed":    "confirmed" in intents,
            "is_denied":       "denied" in intents,
            "is_evasive":      "evasive" in intents,
            "is_annotation":   "annotation" in intents,
            "is_joke":         "joke" in intents,
            "primary_intent":  next((i for i in INTENT_ORDER if i in intents), "other"),
            # conversa
            "conv_types":        conv,
            "is_cosmere_lore":   "cosmere_lore" in conv,
            "is_writing_craft":  "writing_craft" in conv,
            "is_publishing":     "publishing" in conv,
            "is_personal":       "personal_life" in conv,
            # entidades
            "entities":          sorted(entities),
            "entity_count":      len(entities),
            "entity_categories": sorted(by_cat.keys()),
            "ent_shards":        by_cat.get("shards", []),
            "ent_planets":       by_cat.get("planets", []),
            "ent_magic_system":  by_cat.get("magic_system", []),
            "ent_metals":        by_cat.get("metals", []),
            "ent_concepts":      by_cat.get("concepts", []),
            "ent_character":     by_cat.get("character", []),
            "ent_locations":     by_cat.get("locations", []),
            "ent_books":         by_cat.get("books", []),
        })
    return rows


def build_dataframe(wobs_path="data/raw/wobs.json") -> pl.DataFrame:
    rows = build_rows(wobs_path)

    # Schema explícito evita inferência errada em listas vazias
    schema = {
        "id": pl.Int64,
        "event": pl.Utf8,
        "event_date": pl.Utf8,
        "date": pl.Utf8,
        "year": pl.Utf8,
        "paraphrased": pl.Boolean,
        "arcanum_tags": pl.List(pl.Utf8),
        "question": pl.Utf8,
        "answer": pl.Utf8,
        "full_text": pl.Utf8,
        "answer_len": pl.Int64,
        "intents": pl.List(pl.Utf8),
        "is_rafo": pl.Boolean,
        "is_confirmed": pl.Boolean,
        "is_denied": pl.Boolean,
        "is_evasive": pl.Boolean,
        "is_annotation": pl.Boolean,
        "is_joke": pl.Boolean,
        "primary_intent": pl.Utf8,
        "conv_types": pl.List(pl.Utf8),
        "is_cosmere_lore": pl.Boolean,
        "is_writing_craft": pl.Boolean,
        "is_publishing": pl.Boolean,
        "is_personal": pl.Boolean,
        "entities": pl.List(pl.Struct({"category": pl.Utf8, "name": pl.Utf8})),
        "entity_count": pl.Int64,
        "entity_categories": pl.List(pl.Utf8),
        "ent_shards": pl.List(pl.Utf8),
        "ent_planets": pl.List(pl.Utf8),
        "ent_magic_system": pl.List(pl.Utf8),
        "ent_metals": pl.List(pl.Utf8),
        "ent_concepts": pl.List(pl.Utf8),
        "ent_character": pl.List(pl.Utf8),
        "ent_locations": pl.List(pl.Utf8),
        "ent_books": pl.List(pl.Utf8),
    }

    # entities vem como set de tuplas; converte para lista de dicts para Polars
    for r in rows:
        r["entities"] = [{"category": c, "name": n} for c, n in r["entities"]]

    df = pl.DataFrame(rows, schema=schema)

    # Extrai colunas booleanas de "tem entidade X"
    for cat in ["shards", "planets", "magic_system", "metals",
                "concepts", "character", "locations", "books"]:
        df = df.with_columns(
            pl.col(f"ent_{cat}").list.len().alias(f"n_{cat}"),
            (pl.col(f"ent_{cat}").list.len() > 0).alias(f"has_{cat}"),
        )

    # year como inteiro para facilitar groupby temporal
    df = df.with_columns(
        pl.col("year").cast(pl.Int32, strict=False).alias("year_int")
    )

    return df


if __name__ == "__main__":
    df = build_dataframe()
    df.write_parquet("data/processed/wobs.parquet")

    print(f"{df.height} WoBs | "
          f"{df['is_rafo'].sum()} RAFO ({df['is_rafo'].mean():.2%})")
    print(df.select(["id", "primary_intent", "is_rafo", "entity_count"]).head(5))