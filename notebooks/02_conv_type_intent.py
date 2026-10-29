import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from src.preprocessing.classify_conversation import classify_conversation
    from src.preprocessing.intent_classifier import classify_intent
    from src.util.json_loader import load_raw
    from src.preprocessing.parse_wob import extract_answer_text,extract_question_text, extract_full_text
    from collections import Counter
    import polars as pl

    return (
        Counter,
        classify_conversation,
        classify_intent,
        extract_full_text,
        load_raw,
        pl,
    )


@app.cell
def _(Counter, load_raw):
    data = load_raw()
    lista_conversation_intent = []
    tipo_conversa = Counter()
    intents = Counter()
    return data, intents, tipo_conversa


@app.cell
def _(
    classify_conversation,
    classify_intent,
    data,
    extract_full_text,
    intents,
    tipo_conversa,
):
    for item in data:
        text = extract_full_text(item)
        tipo = tuple(classify_conversation(text))
        intent = tuple(classify_intent(text))
        tipo_conversa[tipo] +=1
        intents[intent] +=1
   
    return


@app.cell
def _(pl, tipo_conversa):
    series_tipo = pl.Series(tipo_conversa)
    return


@app.cell
def _(intents, pl):
    series_intent = pl.Series(intents)
    return


if __name__ == "__main__":
    app.run()
