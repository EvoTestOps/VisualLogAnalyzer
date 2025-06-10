import polars as pl
from loglead import AnomalyDetector
from loglead.enhancers import EventLogEnhancer


class LogAnalyzer:
    def __init__(self, df=None, df_seq=None, item_list_col=None):
        self._df = df
        self._df_seq = df_seq
        self._item_list_col = item_list_col

        self._sad = AnomalyDetector()

        self._model_to_func = {
            "lr": self._train_lr,
            "kmeans": self._train_kmeans,
            "dt": self._train_dt,
        }

    def enhance(self, item_list_col="e_words"):
        enhancer = EventLogEnhancer(self._df)

        if item_list_col == "e_words":
            self._df = enhancer.words()
        elif item_list_col == "e_trigrams":
            self._df = enhancer.trigrams()
        elif item_list_col == "e_event_drain_id":
            self._df = enhancer.parse_drain()
        else:
            raise ValueError(f"Unsupported enhance: {item_list_col}")

        self._item_list_col = item_list_col

    def _train_lr(self):
        self._sad.train_LR()
        return self._sad.predict()

    def _train_kmeans(self):
        self._sad.train_KMeans()
        return self._sad.predict()

    def _train_dt(self):
        self._sad.train_DT()
        return self._sad.predict()

    def train_split(self, test_frac=0.9):
        # self._sad.item_list_col = item_list_col
        self._sad.item_list_col = self._item_list_col
        self._sad.numeric_cols = None
        self._sad.auc_roc = True
        self._sad.store_scores = True
        self._sad.test_train_split(self._df, test_frac=test_frac)

    def run_models(self, models):
        results = {}

        for model_name in models:
            train_func = self._model_to_func.get(model_name)
            if train_func:
                df_pred = train_func()
                results[model_name] = df_pred
            else:
                results[model_name] = {"error": f"Unsupported model '{model_name}'"}

        avg_scores = self._sad.storage.calculate_average_scores(
            score_type="accuracy"
        )  # TODO: Multiple score types

        results["avg_scores"] = pl.from_pandas(avg_scores)

        return results

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, new_df):
        self._df = new_df

    @property
    def df_seq(self):
        return self._df_seq

    @df_seq.setter
    def df_seq(self, new_df_seq):
        self._df_seq = new_df_seq

    @property
    def item_list_col(self):
        return self._item_list_col

    @item_list_col.setter
    def item_list_col(self, new):
        self._item_list_col = new
