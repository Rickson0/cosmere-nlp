import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import polars.selectors as cs
    import altair as alt
    import seaborn as sns
    import matplotlib.pyplot as plt
    from src.util.ontology_loader import load_ontology

    return alt, load_ontology, pl


@app.cell
def _(load_ontology, pl):
    df = pl.read_parquet('data/processed/wobs.parquet').with_columns(
        pl.col('event_date', 'date').str.to_date(),
        pl.col('year').str.to_date(format="%Y")
    )

    livros = pl.DataFrame(load_ontology(path='data/ontology/books.yaml')['books']).group_by('year').agg(
        pl.all()
    )
    livros
    return df, livros


@app.cell
def _(df, livros, pl):

    df_com_livros = df.join(livros.with_columns(pl.col('year').alias('ano_lancamento')), left_on='year_int', right_on='year', how='left')
    return (df_com_livros,)


@app.cell
def _(df_com_livros):
    df_com_livros
    return


@app.cell(hide_code=True)
def _(alt, df):
    # replace _df with your data source
    _chart = (
        alt.Chart(df['date', 'is_rafo'])
        .mark_bar()
        .encode(
            x=alt.X(field='date', type='temporal', title='Ano', timeUnit='year'),
            y=alt.Y(field='is_rafo', type='nominal', title='RAFOs', aggregate='count'),
            tooltip=[
                alt.Tooltip(field='date', timeUnit='year', title='Ano'),
                alt.Tooltip(field='is_rafo', aggregate='count', title='RAFOs')
            ]
        )
        .properties(
            title='Distribuição de RAFO por ano',
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


@app.cell(hide_code=True)
def _(df_com_livros, pl):
    taxa_rafo_ano_ano= df_com_livros.sort('date').group_by_dynamic('date',every='1y').agg(
        pl.col('is_rafo').sum().alias('quantidade_rafo'),
        pl.len().alias("quantidade_perguntas_total"),
        (pl.col('is_rafo').sum()/pl.len() * 100).round(2).alias('taxa_rafo')
    ).filter(pl.col('quantidade_rafo') >=50)
    taxa_rafo_ano_ano
    return (taxa_rafo_ano_ano,)


@app.cell(hide_code=True)
def _(alt, taxa_rafo_ano_ano):
    # replace _df with your data source
    _chart = (
        alt.Chart(taxa_rafo_ano_ano)
        .mark_line()
        .encode(
            x=alt.X(field='date', type='temporal', title='Ano', timeUnit='year'),
            y=alt.Y(field='taxa_rafo', type='quantitative', title='Porcentagem de RAFOs'),
            tooltip=[
                alt.Tooltip(field='date', timeUnit='year', title='Ano'),
                alt.Tooltip(field='taxa_rafo', format=',.2f', title='Porcentagem de RAFOs')
            ]
        )
        .properties(
            title='Taxa de RAFO por ano',
            height=290,
            width='container',
            config={
                'axis': {
                    'grid': True
                }
            }
        )
    )
    _chart
    return


@app.cell
def _(df_com_livros, pl):
    rolling_mean = df_com_livros.sort('date').with_columns(
        pl.col('is_rafo').rolling_mean_by(window_size='3y',by='date').alias('rolling_mean')
    )
    rolling_mean
    return (rolling_mean,)


@app.cell(hide_code=True)
def _(alt, pl, rolling_mean):


    df_plot = (
        rolling_mean
        .group_by('year')
        .agg([
            pl.col('rolling_mean').first(),
            pl.col('series').drop_nulls().first(),
            pl.col('name').explode().unique().str.join(', ').alias('nomes_livros'),
            pl.col('era').drop_nulls().first()
        ])
        .sort('year')
   
    )

    # 2. Linha principal suavizada com tom profissional
    linha = (
        alt.Chart(df_plot)
        .mark_line(
            color='#2b5c8f', 
            strokeWidth=2.5, 
            interpolate='monotone'
        )
        .encode(
            x=alt.X('year:T', title='Ano', timeUnit='year'),
            y=alt.Y('rolling_mean:Q', title='Média Móvel de Rafo'),
            tooltip=[
                alt.Tooltip('year:T', timeUnit='year', title='Ano'),
                alt.Tooltip('rolling_mean:Q', format=',.2f', title='Média Móvel')
            ]
        )
    )

    # 3. Pontos com borda branca (dá destaque sem poluir) e filtro limpo
    pontos = (
        alt.Chart(df_plot)
        .mark_point(
            size=140, 
            filled=True, 
            color='#d95f02',
            stroke='white',     # Borda branca separa os pontos visualmente
            strokeWidth=1.5,
            opacity=0.9
        )
        .encode(
            x=alt.X('year:T', timeUnit='year'),
            y=alt.Y('rolling_mean:Q'),
            tooltip=[
                alt.Tooltip('year:T', timeUnit='year', title='Ano'),
                alt.Tooltip('rolling_mean:Q', format=',.2f', title='Média Móvel'),
                alt.Tooltip('nomes_livros:N', title='Livro(s) Lançado(s)')
            ]
        )
        .transform_filter(
            "datum.nomes_livros !== null && datum.nomes_livros !== ''"
        )
    )

    # 4. Layout e grades mais suaves (menos agressivas aos olhos)
    _chart = (
        (linha + pontos)
        .properties(
            title=alt.TitleParams(
                text='Evolução da porcentagem de Rafo e Anos de Lançamento (Q >=50)',
                fontSize=14,
                anchor='start',
                offset=10
            ),
            height=300,
            width='container'
        )
        .configure_view(stroke=None)
        .configure_axis(
            gridColor='#f5f5f5',  # Grade bem sutil
            domainColor='#ddd',
            tickColor='#ddd',
            labelColor='#666',
            titleColor='#333'
        )
    )

    _chart
    return


@app.cell
def _(alt, pl, rolling_mean):


    df_plot_cosmere_lore = (
        rolling_mean.filter('is_cosmere_lore')
        .group_by('year')
        .agg([
            pl.col('rolling_mean').first(),
            pl.col('series').drop_nulls().first(),
            pl.col('name').explode().unique().str.join(', ').alias('nomes_livros'),
            pl.col('era').drop_nulls().first()
        ])
        .sort('year')

   
    )

    # 2. Linha principal suavizada com tom profissional
    linha_cosmere_lore = (
        alt.Chart(df_plot_cosmere_lore)
        .mark_line(
            color='#2b5c8f', 
            strokeWidth=2.5, 
            interpolate='monotone'
        )
        .encode(
            x=alt.X('year:T', title='Ano', timeUnit='year'),
            y=alt.Y('rolling_mean:Q', title='Média Móvel de Rafo'),
            tooltip=[
                alt.Tooltip('year:T', timeUnit='year', title='Ano'),
                alt.Tooltip('rolling_mean:Q', format=',.2f', title='Média Móvel')
            ]
        )
    )

    # 3. Pontos com borda branca (dá destaque sem poluir) e filtro limpo
    pontos_cosmere_lore = (
        alt.Chart(df_plot_cosmere_lore)
        .mark_point(
            size=140, 
            filled=True, 
            color='#d95f02',
            stroke='white',     # Borda branca separa os pontos visualmente
            strokeWidth=1.5,
            opacity=0.9
        )
        .encode(
            x=alt.X('year:T', timeUnit='year'),
            y=alt.Y('rolling_mean:Q'),
            tooltip=[
                alt.Tooltip('year:T', timeUnit='year', title='Ano'),
                alt.Tooltip('rolling_mean:Q', format=',.2f', title='Média Móvel'),
                alt.Tooltip('nomes_livros:N', title='Livro(s) Lançado(s)')
            ]
        )
        .transform_filter(
            "datum.nomes_livros !== null && datum.nomes_livros !== ''"
        )
    )

    # 4. Layout e grades mais suaves (menos agressivas aos olhos)
    _chart = (
        (linha_cosmere_lore + pontos_cosmere_lore)
        .properties(
            title=alt.TitleParams(
                text='Evolução da porcentagem de Rafo e Anos de Lançamento (Q >=50)',
                fontSize=14,
                anchor='start',
                offset=10
            ),
            height=300,
            width='container'
        )
        .configure_view(stroke=None)
        .configure_axis(
            gridColor='#f5f5f5',  # Grade bem sutil
            domainColor='#ddd',
            tickColor='#ddd',
            labelColor='#666',
            titleColor='#333'
        )
    )

    _chart
    return


@app.cell
def _(df_com_livros, pl):
    estatisticas_entities = df_com_livros.explode('entities').group_by('entities').agg(
        pl.col('year').first(),
        pl.col('entities').struct.field('category').first(),
        pl.col('entities').struct.field('name').first(),
        pl.len().filter(pl.col('is_rafo') == True).count().alias("quantidade_rafo"),
        pl.len().filter(pl.col('is_denied') == True).count().alias("quantidade_denied"),
        pl.len().filter(pl.col('is_confirmed') == True).count().alias("quantidade_confirmed"),
        pl.len().alias('quantidade_total'),
        pl.col('full_text').explode().str.join("\n\n")
    ).drop('entities').filter(pl.col('quantidade_total') >= 20)


    return (estatisticas_entities,)


@app.cell
def _(estatisticas_entities, pl):
    porcentagem_rafo_entidade = estatisticas_entities.with_columns(
        pl.col('category', 'name').explode(),
        porcentagem_rafo = (pl.col('quantidade_rafo') / pl.col('quantidade_total'))
    ).sort('porcentagem_rafo', descending=True)[:11]
    porcentagem_rafo_entidade
    return (porcentagem_rafo_entidade,)


@app.cell
def _(alt, porcentagem_rafo_entidade):
    # replace _df with your data source
    _chart = (
        alt.Chart(porcentagem_rafo_entidade)
        .mark_bar()
        .encode(
            x=alt.X(field='porcentagem_rafo', type='quantitative', title="Porcentagem rafo"),
            y=alt.Y(field='name', type='nominal',title='topico').sort('-x'),
            color=alt.Color(field='category', type='nominal'),
            tooltip=[
                alt.Tooltip(field='name'),
                alt.Tooltip(field='porcentagem_rafo', format=',.2f'),
                alt.Tooltip(field='category')
            ]
        )
        .properties(
            title="Top 10 com maior porcentagem de rafo (Quantidade de entradas >= 20)",
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
def _(df_com_livros, pl):
    publishing_vs_cosmere_lore= df_com_livros.explode('conv_types').filter((pl.col('conv_types') == 'cosmere_lore') | (pl.col('conv_types') == 'publishing' )).group_by('conv_types').agg(
        pl.col('entities').explode().struct.field('category').alias('categoria').unique(),
        pl.col('entities').explode().struct.field('name').alias('topico').unique(),
        pl.len().filter(pl.col('is_rafo') == True ).count().alias('quantidade_rafo'),
        pl.len().alias('quantidade_total'),
   
    )
    topico_exploded= publishing_vs_cosmere_lore.explode('topico')

    topicos_unicos_cosmere_lore=topico_exploded.filter(pl.col('conv_types') == 'cosmere_lore').join(topico_exploded.filter(pl.col('conv_types') == 'publishing'), on='topico', how='anti')

    topicos_unico_publishing = topico_exploded.filter(pl.col('conv_types') == 'publishing').join(topico_exploded.filter(pl.col('conv_types') == 'cosmere_lore'), on='topico', how='anti')
    return topicos_unico_publishing, topicos_unicos_cosmere_lore


@app.cell
def _(topicos_unicos_cosmere_lore):
    topicos_unicos_cosmere_lore.drop('categoria')
    return


@app.cell
def _(topicos_unico_publishing):
    topicos_unico_publishing.drop('categoria')
    return


@app.cell
def _(estatisticas_entities, pl):
    taxa_denied_vs_rafo=estatisticas_entities.with_columns(
        taxa_rafo=pl.col('quantidade_rafo')/pl.col('quantidade_total'),
        taxa_denied=pl.col('quantidade_denied')/pl.col('quantidade_total')
    )
    taxa_denied_vs_rafo
    return (taxa_denied_vs_rafo,)


@app.cell
def _(alt, taxa_denied_vs_rafo):
    # replace _df with your data source
    _chart = (
        alt.Chart(taxa_denied_vs_rafo.drop('full_text'))
        .mark_point()
        .encode(
            x=alt.X(field='taxa_rafo', type='quantitative',title='% Rafo'),
            y=alt.Y(field='taxa_denied', type='quantitative', title='% Denied'),
            color=alt.Color(field='name', type='nominal'),
            tooltip=[
                alt.Tooltip(field='taxa_rafo', format=',.2f'),
                alt.Tooltip(field='taxa_denied', format=',.2f'),
                alt.Tooltip(field='name')
            ]
        )
        .properties(
            height=290,
            width='container',
            config={
                'axis': {
                    'grid': True
                }
            }
        )
    )
    _chart
    return


@app.cell
def _(estatisticas_entities, pl):
    taxa_confirmed_vs_rafo=estatisticas_entities.with_columns(
        taxa_rafo=pl.col('quantidade_rafo')/pl.col('quantidade_total'),
        taxa_confirmed=pl.col('quantidade_confirmed')/pl.col('quantidade_total')
    )
    taxa_confirmed_vs_rafo
    return (taxa_confirmed_vs_rafo,)


@app.cell
def _(alt, taxa_confirmed_vs_rafo):
    # replace _df with your data source
    _chart = (
        alt.Chart(taxa_confirmed_vs_rafo.drop('full_text'))
        .mark_point()
        .encode(
            x=alt.X(field='taxa_rafo', type='quantitative', title="% Rafo"),
            y=alt.Y(field='taxa_confirmed', type='quantitative', title="% Confirmed"),
            color=alt.Color(field='name', type='nominal'),
            tooltip=[
                alt.Tooltip(field='taxa_rafo', format=',.2f'),
                alt.Tooltip(field='taxa_confirmed', format=',.2f'),
                alt.Tooltip(field='name')
            ]
        )
        .properties(
            height=290,
            width='container',
            config={
                'axis': {
                    'grid': True
                }
            }
        )
    )
    _chart
    return


@app.cell
def _(df_com_livros, pl):
    df_com_livros.group_by('paraphrased').agg(
        pl.col('is_rafo').mean(),
        pl.len().alias('quantidade_total'),
  
    )
    return


@app.cell
def _(df_com_livros, pl):
    df_com_livros.explode('entities').filter(pl.col('paraphrased') == True).group_by('entities').len().group_by(pl.col('entities').struct.field('category')).len()
    return


@app.cell
def _(df_com_livros):
    livros_lancamento= df_com_livros.explode('name')['ano_lancamento','name'].drop_nulls().unique()
    livros_lancamento
    return (livros_lancamento,)


@app.cell
def _(df_com_livros, livros_lancamento):
 
    efeito_livro_recente= df_com_livros.explode('ent_books').join(livros_lancamento, left_on='ent_books', right_on='name', how='left')



    return (efeito_livro_recente,)


@app.cell
def _(efeito_livro_recente):
    efeito_livro_recente['ent_books','ano_lancamento']
    return


@app.cell
def _(df_com_livros):
    df_com_livros
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
