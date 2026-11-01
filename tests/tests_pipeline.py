import json
from src.build_dataframe import build_dataframe
from src.preprocessing.tag_entities import tag_text
from src.preprocessing.parse_wob import strip_html
from src.preprocessing.intent_classifier import classify_intent


def test_strip_html_remove_tags():
    assert strip_html("<p>Hello</p>") == "Hello"


def test_strip_html_remove_italico():
    assert strip_html("*hesitantly* Yes") == "hesitantly Yes"


def test_strip_html_texto_vazio():
    assert strip_html("") == ""


def test_rafo_simples():
    assert "rafo" in classify_intent("I'm gonna go ahead and RAFO that.")


def test_rafo_no_inicio():
    assert "rafo" in classify_intent("RAFO. Next question.")


def test_confirmacao():
    assert "confirmed" in classify_intent("Yes, that is correct.")


def test_negacao():
    assert "denied" in classify_intent("No, that's not quite right.")


def test_texto_neutro():
    assert classify_intent("The way it works is...") == ["other"]


def test_detecta_nicrosil():
    tags = tag_text("Nicrosil Compounding is weird.")
    assert ("metals", "nicrosil") in tags


def test_detecta_hemalurgia_por_proxy():
    tags = tag_text("You need a spike for that.")
    assert ("magic_system", "hemalurgy") in tags


def test_nao_detecta_em_texto_vazio():
    assert tag_text("") == set()


def test_pipeline_roda_com_amostra():
    with open("data/raw/wobs.json") as f:
        amostra = json.load(f)[:10]

    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        json.dump(amostra, tmp)
        tmp_path = tmp.name

    try:
        df = build_dataframe(tmp_path)
        assert df.height == 10
        assert "is_rafo" in df.columns
        assert "entities" in df.columns
    finally:
        os.unlink(tmp_path)


def test_reason_lowercase_nao_bate():

    assert tag_text("for some reason I don't know") == set()


def test_reason_capital_bate():

    tags = tag_text("Reason is a shard.")
    assert ("shards", "reason") in tags


def test_beautiful_minusculo_nao_bate():
    assert tag_text("what a beautiful day") == set()


def test_beautiful_capital_bate():
    tags = tag_text("Beautiful is a parrot.")
    assert ("character", "beautiful") in tags
