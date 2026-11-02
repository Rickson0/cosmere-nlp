# Cosmere NLP

> Análise de NLP aplicada a 16.382 Words of Brandon (WoBs) do Arcanum — classificando intents, detectando entidades do Cosmere e quantificando a evasividade do autor por tópico.

![Python](https://img.shields.io/badge/python-3.11+-blue)
![Polars](https://img.shields.io/badge/polars-fast-yellow)
![Status](https://img.shields.io/badge/status-pesquisa%20pessoal-orange)

## TL;DR

Pipeline de ciência de dados que processa o corpus completo de Q&As do Brandon Sanderson (16.382 WoBs, 2008–2026) para responder uma pergunta simples: **quais tópicos o autor mais esconde?**

**Achado principal:** Sanderson esconde o **futuro**, não o **passado**. Tópicos ligados ao endgame do Cosmere e à Era Espacial têm taxa de RAFO 2–3× acima da média. Tópicos já explorados nos livros (Allomancia, Vin, Elend, Kelsier) ficam abaixo da média. A taxa média de RAFO no corpus é **12,68%**.

O projeto passou por **três iterações de limpeza** depois que uma análise de casos capciosos revelou bugs sistemáticos de case-sensitivity, colisão de aliases e proxies genéricos. Cada iteração está documentada abaixo com o impacto real nos números.

---

## Para avaliadores (recrutadores, banca, curiosos)

**O que este projeto demonstra:**

- **NLP aplicado em corpus real** — 16k documentos, classificação multi-label, extração de entidades com ontologia curada
- **Engenharia de dados** — pipeline reprodutível em Polars, Parquet, regex compilado com `lru_cache` (~100× speedup)
- **Design de ontologia** — 4 YAMLs independentes (entidades, intents, tipos de conversa, bibliografia) com aliases, proxies e flags de case-sensitivity
- **Rigor analítico** — 3 iterações de limpeza documentadas com impacto mensurável; análise de casos capciosos que revelou bugs que a validação inicial não pegava
- **Análise exploratória com hipótese** — tese clara ("futuro vs. passado"), validação contra gold set manual, limitações honestas

**Como reproduzir:**

```bash
git clone https://github.com/<seu-usuario>/cosmere-nlp.git
cd cosmere-nlp
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Coloque o dump do Arcanum em data/raw/wobs.json
python -m src.build_dataframe       # → data/processed/wobs.parquet
marimo edit notebooks/01_analysis.py

Arquivos-chave para revisão:

    src/build_dataframe.py — pipeline JSON → Parquet com schema explícito

    src/preprocessing/tag_entities.py — detecção de entidades com regex compilado + dois dicionários (case-sensitive e case-insensitive)

    src/preprocessing/intent_classifier.py — classificador de intents com cache

    data/ontology/entities.yaml — ontologia de ~200 entidades do Cosmere

    tests/test_pipeline.py — 16 testes pytest (happy path + edge cases)

    tests/sandbox_edge_cases.py — 35 casos capciosos com PASS/FAIL visual

Achados principais
O padrão: Sanderson esconde o futuro, não o passado
Categoria	Taxa de RAFO	Exemplos
Meta-segredos do Cosmere	25–32%	Adonalsium (28,9%, 280), Dawnshard (28,8%, 132), Vessel (27,6%, 152), Perpendicularity (31,6%, 95)
Shards ativas na trama	20–33%	Autonomy (33,3%, 132), Cultivation (31,5%, 165), Odium (25,7%, 358), Honor (22,2%, 770)
Mecânicas não resolvidas	18–41%	Nicrosil (40,8%, 49), Voidbinding (27,8%, 18), Compounding (21,3%, 94)
Personagens em transição	14–24%	Nightblood (23,6%, 406), Taravangian (21,6%, 116), Worldhopper (22,3%, 197)
Passado já explicado	3–17%	Allomancy (7,2%, 2.204), Vin (3,6%, 579), Elend (2,9%, 383), Hemalurgia (14,5%, 592)
A anomalia Nicrosil

Nicrosil tem 40,8% de RAFO em 49 menções — 3,2× a média global. É o único metal com taxa altíssima. Todas as outras entidades no topo são conceitos meta (Adonalsium, Dawnshard, Vessel) ou Shards ativas. Nicrosil destoa porque representa o hack da Era 3 (Compounding, Soulbearer, unkeyed Investiture) — o que o Sanderson não quer revelar.
O fandom estava errado sobre Hemalurgia

Hemalurgia tem 14,5% de RAFO em 592 menções — praticamente na média global. O fandom suspeita há anos que Hemalurgia é o tópico mais escondido, mas os dados dizem o contrário: o sistema foi exaustivamente explicado na Era 1, e o Sanderson responde com tranquilidade. O que ele não responde é sobre o que vem depois — a Era 3, o endgame, o Cosmere meta.
Metodologia
Três eixos ortogonais

Cada WoB é descrita em três dimensões independentes:
Eixo	Pergunta que responde	Valores
Entidades	Sobre o quê?	hemalurgy, nicrosil, scadrial
Tipo de conversa	Qual domínio?	cosmere_lore, publishing, writing_craft
Intent	Como o Brandon responde?	rafo, confirmed, denied, evasive

Uma WoB pode ser cosmere_lore + hemalurgy + rafo ao mesmo tempo. As taxas são controladas por tipo de conversa para evitar viés (perguntas de publicação inflam a taxa dos tópicos).
Classificação de intents

Classificador baseado em regex com âncoras de word-boundary, IGNORECASE | MULTILINE, e padrões compilados uma vez com lru_cache. Validado contra gold set manual pequeno (41 WoBs, 4 RAFOs positivos) com 100% precisão e recall — mas essa validação é frágil e precisa ser expandida.
Detecção de entidades

Regex única compilada por gazetteer com cache. Suporta:

    aliases — variações diretas de nome (Vasher → Zahel, Kalad, Warbreaker...)

    proxies — termos associados que indicam o conceito (spike → Hemalurgia, metalmind → Feruquemia)

    requires_capitalization — para palavras comuns que são nomes de entidades (Odium, Ruin, Reason, Connection, Beautiful)

Modelo de dados

Parquet com uma linha por WoB e ~35 colunas: metadados, textos, intents booleanos, tipos de conversa, entidades (lista de structs), entidades por categoria (ent_shards, ent_metals, etc.) e booleanos derivados (has_metals, n_shards).
Iterações de limpeza

O pipeline passou por três iterações de correção após uma análise de casos capciosos que revelou bugs que a validação inicial não pegava. Cada iteração está documentada com impacto mensurável:
Iteração 1 — Case-sensitivity

Bug: Shards cujos nomes são palavras comuns do inglês (Ruin, Honor, Odium, Cultivation, Preservation, Devotion, Dominion, Endowment, Harmony) eram taggeadas em contextos não-Cosmere ("the ruin of the city", "honor among thieves").

Fix: requires_capitalization: true em 9 Shards.

Impacto: Odium subiu de 15,6% (32 menções contaminadas) para 25,7% (358 menções limpas). Honor caiu de 27,7% (311) para 22,2% (770 — amostra mais que dobrou com amostras legítimas capitalizadas).
Iteração 2 — Colisão de aliases

Bug: Taravangian tinha "Odium" e "Retribution" como aliases em character; Sazed tinha "Harmony". Resultado: perguntas sobre as Esquirlas eram taggeadas como personagens.

Fix: Remover aliases de Shard dos personagens. As Esquirlas já estão mapeadas em shards: com o Vessel como alias.

Impacto: Taravangian caiu de 441 para 116 menções (removeu contaminação cruzada). Retribution apareceu como Shard separada (21,4%, 117 menções).
Iteração 3 — Proxies genéricos

Bug: fill, tap, burn, command, breath, ideal, oath, surge casavam em contextos comuns ("fill the cup", "burn the toast", "take a deep breath").

Fix: Remover esses proxies. Manter só termos claramente Cosmere (metalmind, spike, spren, lifeless).

Impacto: Feruquemia subiu de 14,9% (592) para 17,1% (474 — amostra 20% menor, taxa 15% maior). Awakening caiu de 570 para 220 menções. Allomancia manteve 7,2% mas com amostra menor.
O caso mais dramático: Reason

Antes dos fixes: 697 menções, 7,3% de RAFO. Parecia um tópico importante.

Depois dos fixes: desapareceu do ranking (abaixo do threshold de 20 menções).

O que aconteceu: 100% das 697 menções eram a palavra comum "reason" em minúsculo. A Esquirla Reason, quando capitalizada, aparece em menos de 20 WoBs. O ranking antigo era um artefato, não um padrão.

Esse caso é a evidência mais forte de que a limpeza valeu a pena — e de que a análise inicial tinha bugs sistemáticos que inflavam entidades com nomes comuns.
Estrutura do projeto
text

cosmere-nlp/
├── data/
│   ├── raw/
│   │   └── wobs.json              # dump do Arcanum (16.382 WoBs)
│   ├── processed/
│   │   └── wobs.parquet           # dataframe unificado
│   └── ontology/
│       ├── entities.yaml          # ~200 entidades + aliases + proxies
│       ├── intents.yaml           # tipos de resposta (RAFO, confirmed...)
│       ├── conversation_types.yaml
│       └── books.yaml             # bibliografia com anos de lançamento
├── src/
│   ├── preprocessing/
│   │   ├── parse_wob.py
│   │   ├── tag_entities.py        # dois gazetteers (case-sensitive e insensitive)
│   │   ├── intent_classifier.py
│   │   └── classify_conversation.py
│   ├── build_dataframe.py         # JSON → Parquet (Polars)
│   └── analysis/
├── notebooks/
│   └── 01_analysis.py             # exploração interativa em Marimo
├── tests/
│   ├── test_pipeline.py           # 16 testes pytest
│   └── sandbox_edge_cases.py      # 35 casos capciosos
└── README.md

Limitações conhecidas

    Validação frágil — gold set tem só 4 RAFOs positivos. A precisão de 100% é anedótica; precisa ser expandida usando a tag #rafo do Arcanum como seed + revisão manual de amostra estratificada.

    Proxies removidos — burn, surge, command, breath, ideal, oath foram removidos por serem ambíguos. Isso significa que WoBs que só mencionam "burn steel" (sem "Allomancy") não detectam o sistema. Recall caiu, precisão subiu.

    Tag #rafo do Arcanum é proxy, não ground truth — curada por humanos, com falsos positivos e falsos negativos. Se for usada como validação, precisa de revisão manual.

    Palavras capitalizadas no início de frase — "Reason I said that is..." ainda casa com a Esquirla Reason (inglês capitaliza toda palavra no início de frase). Aceitável como ruído residual.

    Apenas inglês — o corpus é ~99% em inglês.

    Flag paraphrased — mantida no dataset, mas não filtrada. Análises futuras devem considerar filtrar por ela.

Roadmap

    ☑

    Parse do corpus (16.382 WoBs)
    ☑

    Classificação em três eixos
    ☑

    Detecção de entidades com aliases + proxies + requires_capitalization
    ☑

    3 iterações de limpeza documentadas
    ☑

    Análise de casos capciosos (35 casos)
    ☑

    Taxa de RAFO por entidade
    ☑

    Pipeline Parquet com Polars
    □

    Dashboard em Marimo consolidando os achados
    □

    Gold set expandido com revisão manual de amostra
    □

    Análise temporal (RAFO por ano)
    □

    Análise de cluster (Nicrosil + Identity + Connection)

Sobre este projeto

Este é um projeto de pesquisa pessoal, feito para explorar NLP aplicado a um corpus do qual eu gosto. Não está aberto a pull requests — mas feedback via issue, comentário no 17th Shard ou mensagem direta é bem-vindo.

Se você quiser usar o código, os dados ou a metodologia para algo seu, fique à vontade. A licença é MIT.
Agradecimentos

    Brandon Sanderson e Dragonsteel — por construir um universo que vale a pena analisar

    O Arcanum (wob.coppermind.net) — por curar 16.000+ WoBs

    O 17th Shard — por 15 anos de RAFOs, teorias e obsessão saudável

Licença

MIT — porque conhecimento sobre o Cosmere deve ser preservado, não destruído.