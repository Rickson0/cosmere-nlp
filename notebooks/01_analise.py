import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import polars.selectors as cs

    return (pl,)


@app.cell
def _(pl):
    df = pl.read_parquet('data/processed/wobs.parquet')
    return (df,)


@app.cell
def _(df):
    df
    return


if __name__ == "__main__":
    app.run()
