import polars as pl
import umap
from sklearn.feature_extraction.text import CountVectorizer


def create_umap_embeddings(documents):
    vectorizer = CountVectorizer(
        tokenizer=lambda x: x, preprocessor=None, token_pattern=None, lowercase=False
    )

    dtm = vectorizer.fit_transform(documents)
    reducer = umap.UMAP()
    embeddings = reducer.fit_transform(dtm.toarray())

    return embeddings


def create_umap_df(df, embeddings) -> pl.DataFrame:
    runs = df.select("run").sort("run").unique().to_series().to_list()

    umap_df = pl.DataFrame(
        {
            "UMAP1": embeddings[:, 0],
            "UMAP2": embeddings[:, 1],
            "run": runs,
        }
    )

    return umap_df
