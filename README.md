# Cosmere Nlp

Analisar os Word of Brandon
## Iterações de limpeza

O pipeline passou por três iterações de correção após análise de casos capciosos:

1. **Case-sensitivity fix** — `requires_capitalization: true` em 9 Shards cujos nomes são palavras comuns do inglês (Odium, Ruin, Honor, Cultivation, Preservation, Devotion, Dominion, Endowment, Harmony). Reduziu falsos positivos em ~800 menções.

2. **Alias collision fix** — removidos aliases de Shard dos personagens (Taravangian não tem mais "Odium" como alias, Sazed não tem mais "Harmony"). Eliminou contaminação cruzada em ~400 menções.

3. **Proxy cleanup** — removidos proxies genéricos (`fill`, `tap`, `burn`, `command`, `breath`, `ideal`, `oath`, `surge`) que casavam em contextos não-Cosmere. Reduziu amostras em ~40%, mas elevou a taxa de RAFO dos sistemas em 2–3 pontos percentuais.