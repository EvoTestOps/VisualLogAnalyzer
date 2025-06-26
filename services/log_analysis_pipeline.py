from services.loader import Loader
from services.enhancer import Enhancer
from services.log_analyzer import LogAnalyzer
from utils.data_filtering import filter_runs, filter_files
from utils.run_level_analysis import aggregate_run_level
from utils.file_level_analysis import aggregate_file_level


class ManualTrainTestPipeline:
    def __init__(
        self,
        model_names,
        item_list_col,
        log_format,
        train_data_path=None,
        test_data_path=None,
        runs_to_include=None,
        files_to_include=None,
        mask_type=None,
    ):

        self._model_names = model_names
        self._item_list_col = item_list_col
        self._log_format = log_format

        self._train_data_path = train_data_path
        self._test_data_path = test_data_path
        self._runs_to_include = runs_to_include
        self._files_to_include = files_to_include

        self._mask_type = mask_type

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

    def _load_test_train(self, directory_path):
        loader = Loader(directory_path, self._log_format, self._runs_to_include)
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
        analyzer.manual_train_split(self._df_train, self._df_test)

        self._results = analyzer.run_models(self._model_names)

    def aggregate_to_run_level(self):
        self._df_train = aggregate_run_level(self._df_train, self._item_list_col)
        self._df_test = aggregate_run_level(self._df_test, self._item_list_col)

    def aggregate_to_file_level(self):
        self._df_train = aggregate_file_level(self._df_train, self._item_list_col)
        self._df_test = aggregate_file_level(self._df_test, self._item_list_col)

    @property
    def results(self):
        return self._results
