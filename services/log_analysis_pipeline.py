from services.loader import Loader
from services.enhancer import Enhancer
from services.log_analyzer import LogAnalyzer


class LogAnalysisPipeline:
    def __init__(
        self,
        directory_path,
        model_names,
        item_list_col,
        test_frac,
        log_format,
        labels_file_name=None,
        sequence_enhancement=False,
    ):

        self._directory_path = directory_path
        self._model_names = model_names
        self._item_list_col = item_list_col
        self._log_format = log_format
        self._labels_file_name = labels_file_name
        self._sequence_enhancement = sequence_enhancement
        self._test_frac = test_frac

        self._df = None
        self._df_seq = None

        self._results = None

    def load(self):
        loader = Loader(self._directory_path, self._log_format, self._labels_file_name)
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
