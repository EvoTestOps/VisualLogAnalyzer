import polars as pl
from server.analysis.loader import Loader
from server.analysis.enhancer import Enhancer
from server.analysis.log_analyzer import LogAnalyzer
from .utils.data_filtering import filter_runs, filter_files
from .utils.run_level_analysis import aggregate_run_level
from .utils.file_level_analysis import (
    aggregate_file_level,
    aggregate_file_level_with_file_names,
)


class ManualTrainTestPipeline:
    def __init__(
        self,
        model_names,
        item_list_col,
        vectorizer,
        log_format="raw",
        train_data_path=None,
        test_data_path=None,
        runs_to_include=None,
        runs_to_include_train=None,
        files_to_include=None,
        files_to_include_train=None,
        mask_type=None,
    ):

        self._model_names = model_names
        self._item_list_col = item_list_col
        self._log_format = log_format

        self._train_data_path = train_data_path
        self._test_data_path = test_data_path

        self._runs_to_include = runs_to_include
        self._runs_to_include_train = runs_to_include_train

        self._files_to_include = files_to_include
        self._files_to_include_train = files_to_include_train

        self._mask_type = mask_type
        self._vectorizer = vectorizer

        self._df_test = None
        self._df_train = None

        self._results = None

    def load(self):
        self._df_train = self._load_test_train(self._train_data_path)
        self._df_test = self._load_test_train(self._test_data_path)

        if self._runs_to_include is not None:
            self._df_test = filter_runs(self._df_test, self._runs_to_include)
        elif self._files_to_include is not None:
            self._df_test = filter_files(self._df_test, self._files_to_include)

        if self._runs_to_include_train is not None:
            self._df_train = filter_runs(self._df_train, self._runs_to_include_train)
        elif self._files_to_include_train is not None:
            self._df_train = filter_files(self._df_train, self._files_to_include_train)

    def _load_test_train(self, directory_path):
        loader = Loader(directory_path, self._log_format)
        loader.load()

        return loader.df

    def enhance(self):
        self._df_test = self._enhance_test_train(self._df_test)
        self._df_train = self._enhance_test_train(self._df_train)

    def _enhance_test_train(self, df):
        enhancer = Enhancer(df)
        enhancer.enhance_event(self._item_list_col, self._mask_type)

        return enhancer.df

    def analyze(self):
        analyzer = LogAnalyzer(item_list_col=self._item_list_col)
        analyzer.manual_train_split(self._df_train, self._df_test, self._vectorizer)

        self._results = analyzer.run_models(self._model_names)

    def _analyze_grouped_by_file(
        self, df_train, df_test, common_file_names: list[str]
    ) -> pl.DataFrame:
        if not common_file_names or len(common_file_names) == 0:
            raise ValueError("No common file names found. Try changing settings.")

        analyzer = LogAnalyzer(item_list_col=self._item_list_col)

        results = []
        for file_name in common_file_names:
            train_subset = df_train.filter(pl.col("file_name") == file_name)
            test_subset = df_test.filter(pl.col("file_name") == file_name)

            analyzer.manual_train_split(train_subset, test_subset, self._vectorizer)
            results.append(analyzer.run_models(self._model_names))

        return pl.concat(results, how="vertical")

    def analyze_file_group_by_filenames(self):
        self._df_train = aggregate_file_level_with_file_names(
            self._df_train, self._item_list_col
        )
        self._df_test = aggregate_file_level_with_file_names(
            self._df_test, self._item_list_col
        )

        self._results = self._analyze_grouped_by_file(
            self._df_train,
            self._df_test,
            common_file_names=self._get_common_file_names(),
        )

    def analyze_line_group_by_filenames(self):
        self._results = self._analyze_grouped_by_file(
            self._df_train,
            self._df_test,
            common_file_names=self._get_common_file_names(),
        )

    def aggregate_to_run_level(self):
        self._df_train = aggregate_run_level(self._df_train, self._item_list_col)
        self._df_test = aggregate_run_level(self._df_test, self._item_list_col)

    def aggregate_to_file_level(self):
        self._df_train = aggregate_file_level(self._df_train, self._item_list_col)
        self._df_test = aggregate_file_level(self._df_test, self._item_list_col)

    def _get_common_file_names(self) -> list[str]:
        if self._df_train is None or self._df_test is None:
            raise ValueError("Train and/or test data was not initialized")

        return (
            self._df_train.select("file_name")
            .unique()
            .join(
                self._df_test.select("file_name").unique(), on="file_name", how="inner"
            )
            .to_series()
            .to_list()
        )

    @property
    def results(self):
        return self._results
