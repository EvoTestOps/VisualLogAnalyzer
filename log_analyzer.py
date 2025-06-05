import polars as pl
from loglead import AnomalyDetector
from loglead.enhancers import EventLogEnhancer
from loglead.loaders import HadoopLoader, LO2Loader


# TODO: Be able to change enhancers and item_list_col
class LogAnalyzer:
    def __init__(self):
        self._df = None
        self._sad = AnomalyDetector()

        self._model_to_func = {
            "lr": self.train_lr,
            "kmeans": self.train_kmeans,
            "dt": self.train_dt,
        }

    def load_lo2(self, dir_path):
        loader = LO2Loader(dir_path)
        loader.load()

        if loader.df is None:
            raise ValueError("No data loaded")

        self._df = loader.df

        # remove later
        enhancer = EventLogEnhancer(self._df)
        self._df = enhancer.words()

        self._df = self._df.with_columns(
            [(~pl.col("normal")).cast(bool).alias("anomaly")]
        )

    def load_hadoop(self, dir_path, labels_file_name=None):
        loader = HadoopLoader(
            filename=dir_path,
            filename_pattern="*.log",
            labels_file_name=labels_file_name,
        )

        loader.load()
        loader.preprocess()

        if loader.df is None:
            raise ValueError("No data loaded")

        self._df = loader.df.join(
            loader.df_seq.select(["seq_id", "normal"]), on="seq_id", how="left"
        )

        enhancer = EventLogEnhancer(self._df)
        self._df = enhancer.words()

        self._df = self._df.with_columns(
            [(~pl.col("normal")).cast(bool).alias("anomaly")]
        )

    def train_lr(self):
        self._sad.train_LR()
        return self._sad.predict()

    def train_kmeans(self):
        self._sad.train_KMeans()
        return self._sad.predict()

    def train_dt(self):
        self._sad.train_DT()
        return self._sad.predict()

    def train_split(self, item_list_col="e_words", test_frac=0.9):
        self._sad.item_list_col = item_list_col
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

        avg_scores = self._sad.storage.calculate_average_scores(score_type="accuracy")

        return (results, avg_scores)

    @property
    def df(self):
        return self._df
