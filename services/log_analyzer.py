from loglead import AnomalyDetector


class LogAnalyzer:
    def __init__(self, df=None, item_list_col=None):
        self._df = df
        self._item_list_col = item_list_col

        self._sad = None

        self._model_to_func = {
            "kmeans": self._train_kmeans,
            "rm": self._train_rm,
            "oovd": self._train_oovd,
            "if": self._train_if,
        }

    # TODO: Change names since also predicts
    def _train_kmeans(self):
        self._sad.train_KMeans()
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

    def train_split(self, test_frac=0.9):
        self._sad = AnomalyDetector(
            item_list_col=self._item_list_col,
            store_scores=False,
            auc_roc=True,
            numeric_cols=None,
            print_scores=False,
        )

        self._sad.test_train_split(self._df, test_frac=test_frac)

    def manual_train_split(self, train_df, test_df):
        self._sad = AnomalyDetector(
            item_list_col=self._item_list_col,
            store_scores=False,
            auc_roc=True,
            numeric_cols=None,
            print_scores=False,  # will crash otherwise
        )

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

        if self._sad is None:
            raise ValueError("Anomaly detector has not been initialized.")

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
    def item_list_col(self):
        return self._item_list_col

    @item_list_col.setter
    def item_list_col(self, new):
        self._item_list_col = new
