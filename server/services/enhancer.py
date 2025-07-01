from loglead.enhancers import EventLogEnhancer
import polars as pl
from server.regex_masks.myllari import MYLLARI
from server.regex_masks.myllari_extended import MYLLARI_EXTENDED
from server.regex_masks.drain_loglead import DRAIN_LOGLEAD
from server.regex_masks.drain_orig import DRAIN_ORIG


class Enhancer:
    def __init__(self, df):
        self._df = df

    def enhance_event(self, item_list_col="e_words", mask_type=None) -> pl.DataFrame:
        enhancer = EventLogEnhancer(self._df)

        regex_mask = self._get_regex_mask(mask_type)
        if regex_mask:
            self._df = enhancer.normalize(regex_mask)

        field = "e_message_normalized" if regex_mask else "m_message"

        if item_list_col == "e_words":
            self._df = enhancer.words(field)
        elif item_list_col == "e_trigrams":
            self._df = enhancer.trigrams(field)
        elif item_list_col == "e_event_drain_id":
            self._df = enhancer.parse_drain(field)
        elif item_list_col == "e_event_tip_id":
            self._df = enhancer.parse_tip(field)
        elif item_list_col == "e_event_brain_id":
            self._df = enhancer.parse_brain(field)
        elif item_list_col == "e_event_pliplom_id":
            self._df = enhancer.words(field)
            self._df = enhancer.parse_pliplom(field)
        elif item_list_col == "e_event_iplom_id":
            self._df = enhancer.parse_iplom(field)
        else:
            raise ValueError(f"Unsupported enhance: {item_list_col}")

        return self._df

    def _get_regex_mask(self, mask_type):
        masks_map = {
            "myllari": MYLLARI,
            "myllari_extended": MYLLARI_EXTENDED,
            "drain_loglead": DRAIN_LOGLEAD,
            "drain_orig": DRAIN_ORIG,
        }
        return masks_map.get(mask_type, None)

    @property
    def df(self):
        return self._df
