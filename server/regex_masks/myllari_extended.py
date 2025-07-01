MYLLARI_EXTENDED = [
    ("${start}<QUOTED_ALPHANUMERIC>${end}", r"(?P<start>[^A-Za-z0-9-_]|^)'[a-zA-Z0-9-_]{16,}'(?P<end>[^A-Za-z0-9-_]|$)"),
    ("${start}<DATE>${end}", r"(?P<start>[^0-9/]|^)\d{2}/\d{2}/\d{4}(?P<end>[^0-9/]|$)"),
    ("${start}<DATE>${end}", r"(?P<start>[^0-9-]|^)\d{4}-\d{2}-\d{2}(?P<end>[^0-9-]|$)"),
    ("${start}<DATE_XX>${end}", r"(?P<start>[^A-Za-z0-9_]|^)DATE_\d{2}(?P<end>[^A-Za-z0-9_]|$)"),
    ("${start}<DATE>${end}", r"(?P<start>[^A-Za-z]|^)\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun), \d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b(?P<end>[^A-Za-z]|$)"),
    ("${start}<TIME>${end}", r"(?P<start>[^0-9:]|^)\d{2}:\d{2}:\d{2},\d{3}(?P<end>[^0-9:]|$)"),  #New pattern for HH:MM:SS,MMM format
    ("${start}<TIME>${end}", r"(?P<start>[^0-9:.]|^)\d{2}:\d{2}(?::\d{2}(?:\.\d{3})?)?(?P<end>[^0-9:.]|$)"),
    ("${start}<TIME>${end}", r"(?P<start>[^0-9:]|^)\d{2}:\d{2}(?P<end>[^0-9:]|$)"),
    ("${start}<DATETIME>${end}", r"(?P<start>[^0-9.]|^)\d{1,2}\.\d{1,2}\.\d{4} \d{1,2}\.\d{1,2}\.\d{2}(?P<end>[^0-9.]|$)"),
    ("${start}<VERSION>${end}", r"(?P<start>[^0-9.]|^)\d{1,5}(?:\.\d{1,3}){1,4}(?P<end>[^0-9.]|$)"),
    ("${start}<URL>${end}", r"(?P<start>[^A-Za-z0-9:/]|^)(https?://[^\s]+)(?P<end>[^A-Za-z0-9:/]|$)"),
    ("${start}<DATE>${end}", r"(?P<start>[^A-Za-z]|^)\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{2}| \d) \d{4}\b(?P<end>[^A-Za-z]|$)"),
    ("${start}<TXID>${end}", r"(?P<start>[^0-9A-Fa-f-]|^)\d{4}-[0-9A-Fa-f]{16}(?P<end>[^0-9A-Fa-f-]|$)"),
    ("${start}<FILEPATH>${end}", r"(?P<start>[^A-Za-z0-9:\\]|^)[A-Za-z]:\\(?:[^\\\n]+\\)*[^\\\n]+(?P<end>[^A-Za-z0-9:\\]|$)"),
    ("${start}<APIKEY>${end}", r"(?P<start>[^A-Za-z0-9\"]|^)\"x-apikey\":\s\"[^\"]+\"(?P<end>[^A-Za-z0-9\"]|$)"),
    ("${start}<TIMEMS>${end}", r"(?P<start>[^0-9ms]|^)\b\d+\s+ms\b(?P<end>[^0-9ms]|$)"),
    ("${start}<SECONDS>${end}", r"(?P<start>[^0-9s-]|^)-?\d{1,4}s(?P<end>[^0-9s-]|$)"),
    ("${start}<HEXBLOCKS>${end}", r"(?P<start>[^0-9A-Fa-f-]|^)(?:[0-9A-Fa-f]{4,}-)+[0-9A-Fa-f]{4,}(?P<end>[^0-9A-Fa-f-]|$)"),
    ("${start}<HEX>${end}", r"(?P<start>[^0-9A-Fa-f]|^)0x[0-9A-Fa-f]+(?P<end>[^0-9A-Fa-f]|$)"),
    ("${start}<HEX>${end}", r"(?P<start>[^0-9A-Fa-f]|^)([0-9A-Fa-f]{6,})(?P<end>[^0-9A-Fa-f]|$)"),
    ("${start}<LARGEINT>${end}", r"(?P<start>[^0-9]|^)\d{4,}(?P<end>[^0-9]|$)"),
    ("${start}<IP>${end}", r"(?P<start>[^A-Za-z0-9]|^)(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?P<end>[^A-Za-z0-9]|$)"), #New
    ("${start}<NUM>${end}", r"(?P<start>[^A-Za-z0-9]|^)([\-\+]?[1-9]\d+)(?P<end>[^A-Za-z0-9]|$)") #New
]
