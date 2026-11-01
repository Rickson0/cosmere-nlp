"""
Diagnóstico de casos capciosos no pipeline.
Roda todas as categorias e imprime PASS/FAIL por caso.
"""
from src.preprocessing.tag_entities import tag_text
from src.preprocessing.intent_classifier import classify_intent


# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════

def check_entities(texto, esperado):
    """
    - esperado == set()  → exige que NADA seja encontrado (exact)
    - esperado != set()  → exige que TODOS os esperados estejam no resultado (subset)
    """
    resultado = tag_text(texto)
    if not esperado:
        ok = len(resultado) == 0
    else:
        ok = esperado.issubset(resultado)
    return ok, resultado, esperado


def check_intent(texto, esperado):
    """esperado: set de strings (subset do resultado)."""
    resultado = set(classify_intent(texto))
    ok = esperado.issubset(resultado)
    return ok, resultado, esperado


def run_case(nome, ok, resultado, esperado):
    status = "✅ PASS" if ok else "❌ FAIL"
    print(f"{status}  {nome}")
    if not ok:
        print(f"        obtido:   {resultado}")
        print(f"        esperado: {esperado}")


# ═══════════════════════════════════════════════════════════════════
# CATEGORIA 1 — Shards que são palavras comuns
# ═══════════════════════════════════════════════════════════════════

def cat1_shards_comuns():
    print("\n" + "=" * 70)
    print("CATEGORIA 1 — Shards que são palavras comuns do inglês")
    print("=" * 70)

    casos = [
        ("odium minúsculo",        "I feel no odium toward him",       set()),
        ("ruin minúsculo",         "the ruin of the city",              set()),
        ("honor minúsculo",        "honor among thieves",               set()),
        ("cultivation minúsculo",  "crop cultivation techniques",       set()),
        ("preservation minúsculo", "art preservation is important",     set()),
        ("devotion minúsculo",     "family devotion matters",           set()),
        ("dominion minúsculo",     "colonial dominion ended",           set()),
        ("endowment minúsculo",    "university endowment fund",         set()),
        ("harmony minúsculo",      "living in harmony with nature",     set()),
        # CONTROLE — capitalizado DEVE casar (subset check, aceita outros)
        ("Odium capitalizado",     "Odium is a Shard",                  {("shards", "odium")}),
        ("Honor capitalizado",     "Honor was shattered",               {("shards", "honor")}),
    ]

    for nome, texto, esperado in casos:
        ok, resultado, esperado = check_entities(texto, esperado)
        run_case(f"[C1] {nome}", ok, resultado, esperado)


# ═══════════════════════════════════════════════════════════════════
# CATEGORIA 2 — Proxies genéricos demais
# ═══════════════════════════════════════════════════════════════════

def cat2_proxies_genericos():
    print("\n" + "=" * 70)
    print("CATEGORIA 2 — Proxies genéricos (falsos positivos esperados)")
    print("=" * 70)

    casos = [
        ("fill genérico",        "fill the cup with water",            set()),
        ("tap genérico",         "tap on the door three times",        set()),
        ("tapping genérico",     "tapping fingers nervously",          set()),
        ("burn genérico",        "burn the toast",                     set()),
        ("burn calories",        "burn calories at the gym",           set()),
        ("command genérico",     "command respect from peers",         set()),
        ("breath genérico",      "take a deep breath",                 set()),
        ("ideal genérico",       "ideal situation for growth",         set()),
        ("oath genérico",        "oath of office ceremony",            set()),
        ("surge genérico",       "storm surge warning issued",         set()),
        # CONTROLE — contexto Cosmere DEVE casar (subset, aceita outros)
        ("fill metalmind",       "fill the metalmind with strength",   {("magic_system", "feruchemy")}),
        ("burn steel",           "burn steel to push",                 {("magic_system", "allomancy")}),
        ("spike hemalúrgico",    "the spike is hemalurgic",            {("magic_system", "hemalurgy")}),
    ]

    for nome, texto, esperado in casos:
        ok, resultado, esperado = check_entities(texto, esperado)
        run_case(f"[C2] {nome}", ok, resultado, esperado)


# ═══════════════════════════════════════════════════════════════════
# CATEGORIA 3 — Intents contraditórios
# ═══════════════════════════════════════════════════════════════════

def cat3_intents_contraditorios():
    print("\n" + "=" * 70)
    print("CATEGORIA 3 — Intents contraditórios")
    print("=" * 70)

    casos = [
        ("absolutely not",       "Absolutely not.",                    {"denied"}),
        ("definitely not",       "Definitely not.",                    {"denied"}),
        ("certainly not",        "Certainly not.",                     {"denied"}),
        ("yes but no",           "Yes, but no.",                       {"confirmed", "denied"}),
        ("no, you're right",     "No, you're right.",                  {"confirmed"}),
        ("that's not incorrect", "That's not incorrect.",              {"confirmed"}),
        ("won't say no",         "I won't say no.",                    {"confirmed"}),
    ]

    for nome, texto, esperado in casos:
        ok, resultado, esperado = check_intent(texto, esperado)
        run_case(f"[C3] {nome}", ok, resultado, esperado)


# ═══════════════════════════════════════════════════════════════════
# CATEGORIA 4 — RAFOs disfarçados
# ═══════════════════════════════════════════════════════════════════

def cat4_rafos_disfarcados():
    print("\n" + "=" * 70)
    print("CATEGORIA 4 — RAFOs disfarçados (não contêm 'RAFO')")
    print("=" * 70)

    casos = [
        ("wait and see",         "You'll have to wait and see.",       {"rafo"}),
        ("keep reading",         "Keep reading.",                      {"rafo"}),
        ("would be telling",     "That would be telling.",             {"rafo"}),
        ("I can't say",          "I'm afraid I can't say.",            {"evasive"}),
        ("great question",       "That's a great question.",           {"evasive"}),
        ("nice try",             "Nice try.",                          {"evasive"}),
        ("RAFO literal",         "I'll RAFO that.",                    {"rafo"}),
    ]

    for nome, texto, esperado in casos:
        ok, resultado, esperado = check_intent(texto, esperado)
        run_case(f"[C4] {nome}", ok, resultado, esperado)


# ═══════════════════════════════════════════════════════════════════
# CATEGORIA 5 — Overlap de entidades e word boundary
# ═══════════════════════════════════════════════════════════════════

def cat5_overlap_entidades():
    print("\n" + "=" * 70)
    print("CATEGORIA 5 — Overlap de entidades e word boundary")
    print("=" * 70)

    casos = [
        ("Vindication",          "Vindication is not Vin",             {("character", "vin")}),
        ("odor não é Dor",       "the odor of the market",             set()),
        ("Vin's possessive",     "Vin's actions were heroic",          {("character", "vin")}),
        ("Kelsier + Thaidakar",  "Kelsier is Thaidakar",               {("character", "kelsier")}),
        ("Sazed + Harmony",      "Sazed became Harmony",               {("character", "sazed")}),
    ]

    for nome, texto, esperado in casos:
        ok, resultado, esperado = check_entities(texto, esperado)
        run_case(f"[C5] {nome}", ok, resultado, esperado)


# ═══════════════════════════════════════════════════════════════════
# CATEGORIA 6 — Contexto: pergunta vs. resposta
# ═══════════════════════════════════════════════════════════════════

def cat6_contexto():
    print("\n" + "=" * 70)
    print("CATEGORIA 6 — Contexto: pergunta vs. resposta")
    print("=" * 70)

    from src.preprocessing.parse_wob import extract_answer_text

    wob = {
        "id": 99999,
        "lines": [
            {"speaker": "Perguntador", "text": "<p>Is Nightblood a RAFO?</p>"},
            {"speaker": "Brandon Sanderson", "text": "<p>Yes.</p>"},
        ],
    }
    answer = extract_answer_text(wob)
    ok = "rafo" not in classify_intent(answer)
    run_case(
        "[C6] RAFO na pergunta não vira intent na resposta",
        ok,
        classify_intent(answer),
        "sem 'rafo'",
    )


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n🧪 Pipeline de diagnóstico — casos capciosos\n")

    cat1_shards_comuns()
    cat2_proxies_genericos()
    cat3_intents_contraditorios()
    cat4_rafos_disfarcados()
    cat5_overlap_entidades()
    cat6_contexto()

    print("\n" + "=" * 70)
    print("DIAGNÓSTICO CONCLUÍDO")
    print("=" * 70)