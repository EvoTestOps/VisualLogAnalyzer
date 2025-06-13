import polars as pl
from loglead.loaders import HadoopLoader, LO2Loader


class Loader:
    def __init__(self, directory_path, log_format="lo2", labels_file_name=None):
        self._directory_path = directory_path
        self._log_format = log_format
        self._labels_file_name = labels_file_name
        self._df = None
        self._df_seq = None

    def load(self):
        if self._log_format == "lo2":
            self._load_lo2()
        elif self._log_format == "hadoop":
            self._load_hadoop()
        else:
            raise ValueError(f"Unsupported log format: {self._log_format}")

    def _load_lo2(self):
        loader = LO2Loader(self._directory_path)

        loader.load()
        loader.preprocess()

        if loader.df is None:
            raise ValueError(
                f"Error: No data loaded. Check your directory path ({self._directory_path}) and data format."
            )

        self._df = loader.df
        self._df_seq = loader.df_seq

    # Fix this makes no sense
    def _load_hadoop(self):
        loader = HadoopLoader(
            filename=self._directory_path,
            filename_pattern="*.log",
            labels_file_name=self._labels_file_name,
        )

        loader.load()
        loader.preprocess()

        if loader.df is None:
            raise ValueError("No data loaded")

        # Do we need these??
        self._df = loader.df.join(
            loader.df_seq.select(["seq_id", "normal"]), on="seq_id", how="left"
        )

        self._df = self._cast_normal_to_anomaly()
        self._df_seq = loader.df_seq

    def _cast_normal_to_anomaly(self):
        return self._df.with_columns([(~pl.col("normal")).cast(bool).alias("anomaly")])

    @property
    def df(self):
        return self._df

    @property
    def df_seq(self):
        return self._df_seq
