from services.loader import Loader
from services.enhancer import Enhancer
from services.log_analyzer import LogAnalyzer


class LogAnalysisPipeline:
    def __init__(
        self,
        model_names,
        item_list_col,
        log_format,
        test_frac=0.9,
        directory_path=None,
        labels_file_name=None,
        sequence_enhancement=False,
        manual_split=False,
        train_data_path=None,
        test_data_path=None,
    ):

        self._directory_path = directory_path
        self._model_names = model_names
        self._item_list_col = item_list_col
        self._log_format = log_format
        self._labels_file_name = labels_file_name
        self._sequence_enhancement = sequence_enhancement
        self._test_frac = test_frac

        self._manual_split = manual_split
        self._train_data_path = train_data_path
        self._test_data_path = test_data_path

        self._df = None
        self._df_seq = None

        self._df_test = None
        self._df_train = None
        self._df_seq_test = None
        self._df_seq_train = None

        self._results = None

    def load(self):
        if self._manual_split:
            self._df_train, self._df_seq_train = self._load_test_train(
                self._train_data_path
            )
            self._df_test, self._df_seq_test = self._load_test_train(
                self._test_data_path
            )
            # might need to change to work with other datasets
            self._df_test = self._df_test.drop(["normal", "anomaly"])
            self._df_seq_test = self._df_seq_test.drop(["normal", "anomaly"])

        else:
            loader = Loader(
                self._directory_path, self._log_format, self._labels_file_name
            )
            loader.load()

            self._df = loader.df
            self._df_seq = loader.df_seq

    def _load_test_train(self, directory_path):
        loader = Loader(directory_path, self._log_format, self._labels_file_name)
        loader.load()

        return loader.df, loader.df_seq

    def enhance(self):
        if self._manual_split:
            self._df_test, self._df_seq_test = self._enhance_test_train(
                self._df_test, self._df_seq_test
            )
            self._df_train, self._df_seq_train = self._enhance_test_train(
                self._df_train, self._df_seq_train
            )
        else:
            enhancer = Enhancer(self._df, self._df_seq)
            if self._sequence_enhancement:
                enhancer.enhance_seq(self._item_list_col)
            else:
                enhancer.enhance_event(self._item_list_col)

            self._df = enhancer.df
            self._df_seq = enhancer._df_seq

    def _enhance_test_train(self, df, df_seq):
        enhancer = Enhancer(df, df_seq)

        if self._sequence_enhancement:
            enhancer.enhance_seq(self._item_list_col)
        else:
            enhancer.enhance_event(self._item_list_col)

        return enhancer.df, enhancer.df_seq

    def analyze(self):
        if self._manual_split:
            analyzer = LogAnalyzer(item_list_col=self._item_list_col)
            if self._sequence_enhancement:
                analyzer.manual_train_split(self._df_seq_train, self._df_seq_test)
            else:
                analyzer.manual_train_split(self._df_train, self._df_test)

            self._results = analyzer.run_models(self._model_names)
        else:
            analyzer = LogAnalyzer(self._df, self._df_seq, self._item_list_col)
            analyzer.train_split(self._test_frac, sequence=self._sequence_enhancement)

            self._results = analyzer.run_models(self._model_names)

    @property
    def results(self):
        return self._results
