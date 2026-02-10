import string
import logging
from faker import Faker

logger = logging.getLogger(__name__)

class DataHelper:

    def __init__(self, seed: int | None = None):
        
        self.langs = {
            "basic_latinh": ["en_US"],
            "accented": ["vi_VN", "fr_FR", "de_DE", "es_ES", "pt_BR", "it_IT", "pl_PL", "cs_CZ"],
            "non_latinh": ["ja_JP", "ko_KR", "zh_CN", "ru_RU", "ar_SA"]
        }

        self.chars = {
            "ascii_letter": string.ascii_letters,
            "digit": string.digits,
            "punctuation_no_at": string.punctuation.replace("@", ""),
            "punctuation": string.punctuation,
            "symbol": "©®™§¶†‡•€£¥∞±≠",
            "math": "+-=*/√^∞∫≈≠≤≥∀∂∃∅∇∈∉∋∏∑−∕∗∘√∝∞∠∧∨∩∪∫∬∭∮",
            "emoji": "😀🚀🔥✅❌🌟💯🐱‍👤",
            "control": "".join(chr(i) for i in range(0, 32)),
            "whitespace": " \t\n\r\u00A0\u200B",
        }

        all_locales = [lang for group in self.langs.values() for lang in group]
        self.faker = Faker(all_locales)
        if seed is None:
            import time
            seed = int(time.time())
        self.seed = seed
        self.faker.seed_instance(seed)