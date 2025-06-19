import polars as pl
from loglead.loaders import LO2Loader, RawLoader


class Loader:
    def __init__(self, directory_path, log_format="lo2", runs_to_include=None):
        self._directory_path = directory_path
        self._log_format = log_format
        self._runs_to_include = runs_to_include
        self._df = None
        self._df_seq = None

    def load(self):
        if self._log_format == "lo2":
            self._load_lo2()
        elif self._log_format == "raw":
            self._load_raw()
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

    # Asumes format:
    # log_data_root/
    #   run1/
    #       example.log
    #       example-n.log
    #   ...
    #   run-n/
    #       example-z.log

    def _load_raw(self):
        loader = RawLoader(
            self._directory_path,
            filename_pattern="*.log",
            strip_full_data_path=self._directory_path,
        )
        df = loader.execute()

        if loader.df is None:
            raise ValueError(
                f"Error: No data loaded. Check your directory path ({self._directory_path}) and data format."
            )

        self._df = self._prepare_raw_data(df)

    def _prepare_raw_data(self, df):
        df = df.filter(pl.col("m_message").is_not_null())
        df = df.filter(~pl.col("m_message").str.contains("�"))

        df = df.with_columns(
            [
                pl.col("file_name").str.extract(r"^([^/]+)", 1).alias("run"),
                pl.col("file_name")
                .str.replace(r"^[^/]+/", "", literal=False)
                .alias("file_name"),
            ]
        )

        df = df.with_columns(
            [
                pl.concat_str([pl.col(("run")), pl.col("file_name")], separator="_")
                .str.replace(r"\.log$", "", literal=False)
                .alias("seq_id")
            ]
        )

        df = df.with_columns(
            [pl.col("seq_id").cum_count().over("seq_id").alias("line_number")]
        )

        df = df.drop("orig_file_name")

        return df

    # def filter_runs(self, runs: list[str], include=True):
    #     self._df = (
    #         self._df.filter(pl.col("run").is_in(runs))
    #         if include
    #         else self._df.filter(~pl.col("run").is_in(runs))
    #     )

    # def filter_files(self, file_seq_ids: list[str], include=True):
    #     self._df = (
    #         self._df.filter(pl.col("seq_id").is_in(file_seq_ids))
    #         if include
    #         else self._df.filter(~pl.col("seq_id").is_in(file_seq_ids))
    #     )

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, new_df):
        self._df = new_df

    @property
    def df_seq(self):
        return self._df_seq
