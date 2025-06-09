import polars as pl
from loglead import AnomalyDetector, enhancers
from loglead.enhancers import EventLogEnhancer
from loglead.loaders import HadoopLoader, LO2Loader


class LogAnalyzer:
    def __init__(self):
        self._df = None
        self._df_seq = None
        self._item_list_col = None

        self._sad = AnomalyDetector()

        self._model_to_func = {
            "lr": self._train_lr,
            "kmeans": self._train_kmeans,
            "dt": self._train_dt,
        }

    def load(self, dir_path, log_format="lo2", labels_file_name=None):
        if log_format == "lo2":
            self._load_lo2(dir_path)
        elif log_format == "hadoop":
            self._load_hadoop(dir_path, labels_file_name)
        else:
            raise ValueError(f"Unsupported log format: {log_format}")

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

    def _cast_normal_to_anomaly(self):
        return self._df.with_columns([(~pl.col("normal")).cast(bool).alias("anomaly")])

    def _load_lo2(self, dir_path):
        loader = LO2Loader(dir_path)

        loader.load()
        loader.preprocess()

        if loader.df is None:
            raise ValueError("No data loaded")

        self._df = loader.df
        self._df_seq = loader.df_seq

    def _load_hadoop(self, dir_path, labels_file_name=None):
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

        self._df = self._cast_normal_to_anomaly()
        self._df_seq = loader.df_seq

    def _train_lr(self):
        self._sad.train_LR()
        return self._sad.predict()

    def _train_kmeans(self):
        self._sad.train_KMeans()
        return self._sad.predict()

    def _train_dt(self):
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

    @property
    def item_list_col(self):
        return self._item_list_col
