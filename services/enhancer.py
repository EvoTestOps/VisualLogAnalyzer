from loglead.enhancers import EventLogEnhancer, SequenceEnhancer


class Enhancer:
    def __init__(self, df=None, df_seq=None):
        self._df = df
        self._df_seq = df_seq

        self._event_enhancer = None
        self._sequence_enhancer = None

        # in the future should probably be handled through validators
        self._event_cols = [
            "e_event_drain_id",
            "e_event_spell_id",
            "e_event_tip_id",
            "e_event_pliplom_id",
            "e_event_iplom_id",
            "e_event_brain_id",
        ]

    def enhance_event(self, item_list_col="e_words"):
        enhancer = EventLogEnhancer(self._df)

        self._df = enhancer.normalize()

        if item_list_col == "e_words":
            self._df = enhancer.words()
        elif item_list_col == "e_trigrams":
            self._df = enhancer.trigrams()
        elif item_list_col == "e_event_drain_id":
            self._df = enhancer.parse_drain()
        elif item_list_col == "e_event_tip_id":
            self._df = enhancer.parse_tip()
        elif item_list_col == "e_event_brain_id":
            self._df = enhancer.parse_brain()
        elif item_list_col == "e_event_spell_id":
            self._df = enhancer.parse_spell()
        elif item_list_col == "e_event_pliplom_id":
            self._df = enhancer.parse_pliplom()
        elif item_list_col == "e_event_iplom_id":
            self._df = enhancer.parse_iplom()
        elif item_list_col in ["e_chars_len", "e_lines_len", "e_words_len"]:
            self._df = enhancer.length()
        else:
            raise ValueError(f"Unsupported enhance: {item_list_col}")

        return self._df

    def enhance_seq(self, item_list_col):
        self._sequence_enhancer = SequenceEnhancer(self._df, self._df_seq)

        if item_list_col in self._event_cols:
            self._check_prerequisites(item_list_col)
            self._df_seq = self._sequence_enhancer.events(item_list_col)
        elif item_list_col in ["e_words", "e_trigrams"]:
            self._check_prerequisites(item_list_col)
            self._df_seq = self._sequence_enhancer.tokens(token=item_list_col)
        else:
            raise ValueError(f"Unsupported sequence enhancer: {item_list_col}")

        return self._df_seq

    def _check_prerequisites(self, item_list_col):
        if self._df.get_column(item_list_col, default=None) is None:
            self.enhance_event(item_list_col)
            self._sequence_enhancer.df = self._df

    @property
    def df(self):
        return self._df

    @property
    def df_seq(self):
        return self._df_seq
