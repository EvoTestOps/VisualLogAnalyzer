import os
import polars as pl
from loglead.loaders import LO2Loader, RawLoader


class Loader:
    def __init__(self, directory_path, log_format="raw"):
        self._directory_path = directory_path
        self._log_format = log_format
        self._df = None

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

    # Asumes format:
    # log_data_root/
    #   run1/
    #       example.log
    #       example-n.log
    #   ...
    #   run-n/
    #       example-z.log

    def _load_raw(self):
        pattern = "*.log" if os.path.isdir(self._directory_path) else None
        loader = RawLoader(
            self._directory_path,
            filename_pattern=pattern,
            strip_full_data_path=self._directory_path,
        )
        df = loader.execute()

        if loader.df is None:
            raise ValueError(
                f"Error: No data loaded. Check your directory path ({self._directory_path}) and data format."
            )

        self._df = self._prepare_raw_data(df)

    def _prepare_raw_data(self, df):
        is_file = os.path.isfile(self._directory_path)
        if is_file:
            df = df.with_columns(pl.lit(str(self._directory_path)).alias("file_name"))
            df = df.with_columns(
                pl.lit(str(self._directory_path)).alias("orig_file_name")
            )

        df = df.filter(pl.col("m_message").is_not_null())
        df = df.filter(~pl.col("m_message").str.contains("�"))

        if is_file:
            df = df.with_columns(pl.col("file_name").alias("run"))
        else:
            df = df.with_columns(
                [
                    pl.col("file_name")
                    .str.strip_chars("/")
                    .str.extract(r"^([^/]+)", 1)
                    .alias("run"),
                    pl.col("file_name")
                    .str.strip_chars("/")
                    .str.replace(r"^[^/]+/", "", literal=False)
                    .alias("file_name"),
                ]
            )

        if is_file:
            df = df.with_columns(pl.col("file_name").alias("seq_id"))
        else:
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

        # df = df.drop("orig_file_name")

        return df

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, new_df):
        self._df = new_df
