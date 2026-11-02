import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    return mo, pl


@app.cell
def _(pl):
    df = pl.read_parquet('data/processed/wobs.parquet')
    df.schema
    return (df,)


@app.cell(hide_code=True)
def _(mo):
    search = mo.ui.text(
        placeholder="Search the Words of Brandon",
        label='Search Cosmere lore'
    
    )

    return (search,)


@app.cell
def _(
    conv_type_options,
    entity_options,
    intent_options,
    mo,
    search,
    tag_options,
):
    tag_filter = mo.ui.multiselect(
        options=tag_options,
        label="Filter by Arcanum tags"
    )

    intent_filter = mo.ui.multiselect(
        options=intent_options,
        label="Filter by intent"
    )

    entities_filter = mo.ui.multiselect(
        options=entity_options,
        label="Filter by entities"
    )

    type_filter = mo.ui.multiselect(
        options=conv_type_options,
        label="Filter by conversation types"
    )
    mo.vstack([
        search,
        tag_filter,
        type_filter,
        intent_filter,
        entities_filter
    
    ])
    return entities_filter, intent_filter, tag_filter, type_filter


@app.cell(hide_code=True)
def _(df, entities_filter, intent_filter, pl, search, tag_filter, type_filter):
    query = search.value.strip().lower()
    selected_tags = tag_filter.value
    selected_types = type_filter.value
    selected_entities = entities_filter.value
    selected_intents = intent_filter.value

    conditions = []

    if query:
        conditions.append(
            pl.col("full_text")
            .str.to_lowercase()
            .str.contains(query, literal=True)
        )

    if selected_tags:
        conditions.append(
            pl.col("arcanum_tags").list.eval(
                pl.element().is_in(selected_tags)
            ).list.any()
        )

    if selected_types:
        conditions.append(
            pl.col("conv_types").list.eval(
                pl.element().is_in(selected_types)
            ).list.any()
        )

    if selected_entities:
        conditions.append(
            pl.col("entities")
            .list.eval(
                pl.element()
                .struct.field("name")
            
            )
            .list.eval(
                pl.element().is_in(selected_entities)
            ).list.any()
        )




    filtered_results = (
        df.filter(pl.all_horizontal(conditions))
        if conditions
        else df
    )
    return (filtered_results,)


@app.cell(hide_code=True)
def _(page_results):
    display_results = page_results.select(
        "id",
        "date",
        "event",
        "question",
        "answer",
        "primary_intent",
        "arcanum_tags",
        "entities",
        "is_rafo",
        "is_confirmed",
        "intents"
    )
    return (display_results,)


@app.cell(hide_code=True)
def _(display_results, mo):
    cards = mo.vstack([
        mo.md(f"""
        ### {row["question"]}

        {row["answer"]}

        **Date:** {row["date"]}

        **Event:** {row["event"]}

        **Intents:** {" · ".join(row["intents"] or [])}

        ---
        """)
        for row in display_results.to_dicts()
    ])

    cards
    return


@app.cell
def _(get_page, mo, total_pages):
    mo.md(f"**Página {get_page()} de {total_pages}**")
    return


@app.cell(hide_code=True)
def _(get_page, mo, set_page, total_pages):
    previous_button = mo.ui.button(
        label="← Anterior",
        on_click=lambda _: set_page(max(1, get_page() - 1)),
        disabled=get_page() <= 1
    )

    next_button = mo.ui.button(
        label="Próxima →",
        on_click=lambda _: set_page(min(total_pages, get_page() + 1)),
        disabled=get_page() >= total_pages
    )
    mo.hstack([previous_button, next_button])
    return


@app.cell
def _(filtered_results, mo):
    page_size = 10
    get_page, set_page = mo.state(1)
    total_results = filtered_results.height
    total_pages = max(1, (total_results + page_size - 1) // page_size)
    return get_page, page_size, set_page, total_pages


@app.cell(hide_code=True)
def _(filtered_results, get_page, page_size):
    start = (get_page() - 1) * page_size
    page_results = filtered_results.slice(start, page_size)
    return (page_results,)


@app.cell(hide_code=True)
def _(df):
    tag_options = (
        df["arcanum_tags"]
        .explode()
        .drop_nulls()
        .unique()
        .sort()
        .to_list()
    )
    return (tag_options,)


@app.cell(hide_code=True)
def _(df):
    intent_options = (
        df["intents"]
        .explode()
        .drop_nulls()
        .unique()
        .sort()
        .to_list()
    )
    return (intent_options,)


@app.cell(hide_code=True)
def _(df, pl):
    entity_options = (
        df.select(
            pl.col("entities")
            .list.eval(
                pl.element().struct.field("name")
            )
            .explode()
            .alias("name")
        )
        .get_column("name")
        .drop_nulls()
        .unique()
        .sort()
        .to_list()
    )
    return (entity_options,)


@app.cell(hide_code=True)
def _(df):
    conv_type_options = (
        df["conv_types"]
        .explode()
        .drop_nulls()
        .unique()
        .sort()
        .to_list()
    )
    return (conv_type_options,)


@app.cell
def _(mo):
    botão = mo.ui.button(label='clique aqui')
    help(botão)
    return


if __name__ == "__main__":
    app.run()
