import polars as pl
from loglead import AnomalyDetector
from loglead.enhancers import EventLogEnhancer


class LogAnalyzer:
    def __init__(self, df=None, df_seq=None, item_list_col=None):
        self._df = df
        self._df_seq = df_seq
        self._item_list_col = item_list_col

        # self._sad = AnomalyDetector()
        self._sad = None

        self._model_to_func = {
            "lr": self._train_lr,
            "kmeans": self._train_kmeans,
            "dt": self._train_dt,
            "rm": self._train_rm,
            "oovd": self._train_oovd,
            "if": self._train_if,
        }

    # TODO: Change names since also predicts
    def _train_lr(self):
        self._sad.train_LR()
        return self._sad.predict()

    def _train_kmeans(self):
        self._sad.train_KMeans()
        return self._sad.predict()

    def _train_dt(self):
        self._sad.train_DT()
        return self._sad.predict()

    def _train_rm(self):
        self._sad.train_RarityModel()
        return self._sad.predict()

    def _train_oovd(self):
        self._sad.train_OOVDetector()
        return self._sad.predict()

    def _train_if(self):
        self._sad.train_IsolationForest()
        return self._sad.predict()

    def train_split(self, test_frac=0.9, sequence=False):
        # self._sad.item_list_col = item_list_col
        self._sad = AnomalyDetector()

        self._sad.item_list_col = self._item_list_col
        self._sad.numeric_cols = None
        self._sad.auc_roc = True
        self._sad.store_scores = False

        if sequence:
            self._sad.test_train_split(self._df_seq, test_frac=test_frac)
        else:
            self._sad.test_train_split(self._df, test_frac=test_frac)

    def manual_train_split(self, train_df, test_df):
        self._sad = AnomalyDetector(
            item_list_col=self._item_list_col,
            store_scores=False,
            auc_roc=True,
            numeric_cols=None,
            print_scores=False,  # will crash otherwise
        )

        self._sad.item_list_col = self._item_list_col
        self._sad.numeric_cols = None
        self._sad.auc_roc = True
        self._sad.store_scores = False

        self._sad.train_df = train_df
        self._sad.test_df = test_df

        self._sad.prepare_train_test_data()

    def run_models(self, models):
        if len(models) < 1:
            raise ValueError(
                "Error: No detectors selected. Select atleast one model to run analysis."
            )

        df_result = None
        for model_name in models:
            df_result = self._run_model(model_name, df_result)

        return df_result

    # Could possibly use sad.storage.test_results
    def _run_model(self, model_name, df_result):
        train_func = self._model_to_func.get(model_name)

        if not train_func:
            raise ValueError(f"error: Unsupported model {model_name}")

        predictions = train_func()

        if df_result is None:
            df_result = predictions.rename(
                {"pred_ano_proba": f"{model_name}_pred_ano_proba"}
            )
        else:
            predictions_series = predictions.select("pred_ano_proba").to_series()
            df_result = df_result.with_columns(
                predictions_series.alias(f"{model_name}_pred_ano_proba")
            )

        del predictions

        return df_result

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
