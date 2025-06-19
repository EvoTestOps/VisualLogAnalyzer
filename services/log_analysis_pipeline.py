from services.loader import Loader
from services.enhancer import Enhancer
from services.log_analyzer import LogAnalyzer
from utils.data_filtering import filter_runs
from utils.run_level_analysis import aggregate_run_level


class LogAnalysisPipeline:
    def __init__(
        self,
        model_names,
        item_list_col,
        log_format,
        test_frac=0.9,
        directory_path=None,
        sequence_enhancement=False,
    ):

        self._directory_path = directory_path
        self._model_names = model_names
        self._item_list_col = item_list_col
        self._log_format = log_format
        self._sequence_enhancement = sequence_enhancement
        self._test_frac = test_frac

        self._df = None
        self._df_seq = None

        self._results = None

    def load(self):
        loader = Loader(
            self._directory_path,
            self._log_format,
        )
        loader.load()

        self._df = loader.df
        self._df_seq = loader.df_seq

    def enhance(self):
        enhancer = Enhancer(self._df, self._df_seq)
        if self._sequence_enhancement:
            enhancer.enhance_seq(self._item_list_col)
        else:
            enhancer.enhance_event(self._item_list_col)

        self._df = enhancer.df
        self._df_seq = enhancer._df_seq

    def analyze(self):
        analyzer = LogAnalyzer(self._df, self._df_seq, self._item_list_col)
        analyzer.train_split(self._test_frac, sequence=self._sequence_enhancement)

        self._results = analyzer.run_models(self._model_names)

    @property
    def results(self):
        return self._results


class ManualTrainTestPipeline:
    def __init__(
        self,
        model_names,
        item_list_col,
        log_format,
        sequence_enhancement=False,
        train_data_path=None,
        test_data_path=None,
        runs_to_include=None,
    ):

        self._model_names = model_names
        self._item_list_col = item_list_col
        self._log_format = log_format
        self._sequence_enhancement = sequence_enhancement

        self._train_data_path = train_data_path
        self._test_data_path = test_data_path
        self._runs_to_include = runs_to_include

        self._df_test = None
        self._df_train = None
        self._df_seq_test = None
        self._df_seq_train = None

        self._results = None

    def load(self):
        self._df_train, self._df_seq_train = self._load_test_train(
            self._train_data_path
        )
        self._df_test, self._df_seq_test = self._load_test_train(self._test_data_path)

        if self._runs_to_include is not None:
            self._df_test = filter_runs(self._df_test, self._runs_to_include)

    def _load_test_train(self, directory_path):
        loader = Loader(directory_path, self._log_format, self._runs_to_include)
        loader.load()

        return loader.df, loader.df_seq

    def enhance(self):
        self._df_test, self._df_seq_test = self._enhance_test_train(
            self._df_test, self._df_seq_test
        )
        self._df_train, self._df_seq_train = self._enhance_test_train(
            self._df_train, self._df_seq_train
        )

    def _enhance_test_train(self, df, df_seq):
        enhancer = Enhancer(df, df_seq)

        if self._sequence_enhancement:
            enhancer.enhance_seq(self._item_list_col)
        else:
            enhancer.enhance_event(self._item_list_col)

        return enhancer.df, enhancer.df_seq

    def analyze(self):
        analyzer = LogAnalyzer(item_list_col=self._item_list_col)
        if self._sequence_enhancement:
            analyzer.manual_train_split(self._df_seq_train, self._df_seq_test)
        else:
            analyzer.manual_train_split(self._df_train, self._df_test)

        self._results = analyzer.run_models(self._model_names)

    def aggregate_to_run_level(self):
        self._df_train = aggregate_run_level(self._df_train, self._item_list_col)
        self._df_test = aggregate_run_level(self._df_test, self._item_list_col)

    @property
    def results(self):
        return self._results
