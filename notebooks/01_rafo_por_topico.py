import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    from src.util.json_loader import load_raw
    from src.analysis.rafo_rate_by_topic import rafo_rate_by_topic
    import polars as pl
    from collections import defaultdict
    import altair as alt

    return alt, load_raw, pl, rafo_rate_by_topic


@app.cell
def _(load_raw):
    data = load_raw()
    return (data,)


@app.cell
def _(data, rafo_rate_by_topic):
    resultado = rafo_rate_by_topic(data)
    return (resultado,)


@app.cell
def _(resultado):
    lista_de_topicos = []
    for topico, taxa, quantidade in resultado:
        lista_de_topicos.append({
            "topico": topico,
            "quantidade":quantidade,
            "taxa": taxa
        })
    lista_de_topicos
    return (lista_de_topicos,)


@app.cell
def _(lista_de_topicos, pl):
    df = pl.DataFrame(lista_de_topicos)

    novo_df = (
        df.select(
            pl.col('topico').list.get(0).alias('Tema'),
            pl.col('topico').list.get(1).alias('Assunto'),
            pl.col('quantidade'),
            pl.col('taxa')
        )
    )


    return (novo_df,)


@app.cell
def _(novo_df, pl):
    perguntas_por_tema=novo_df.group_by("Tema").agg(
        pl.col('quantidade').sum().alias('volume_perguntas')
    ).sort('volume_perguntas',descending=True)
    return (perguntas_por_tema,)


@app.cell
def _(alt, perguntas_por_tema):
    # replace _df with your data source
    _chart = (
        alt.Chart(perguntas_por_tema)
        .mark_bar()
        .encode(
            x=alt.X(field='volume_perguntas', type='quantitative', title='Perguntas', aggregate='sum', sort='ascending'),
            y=alt.Y(field='Tema', type='nominal', title='Tema'),
            color=alt.Color(field='Tema', type='nominal', scale={
                'scheme': 'category10'
            }),
       
        
        )
        .properties(
            height=290,
            width='container',
            config={
                'axis': {
                    'grid': False
                }
            }
        )
    )
    _chart
    return


@app.cell
def _():
    return


@app.cell
def _(novo_df):
    novo_df.sort('quantidade', descending=True)[:11]
    return


@app.cell
def _(novo_df):
    novo_df.sort('taxa', descending=True)[:10]
    return


if __name__ == "__main__":
    app.run()
