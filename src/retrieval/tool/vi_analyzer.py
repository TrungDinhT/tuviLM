from whoosh.analysis import Tokenizer, Token
from pyvi import ViTokenizer
from unidecode import unidecode
from whoosh.fields import Schema, TEXT, ID


class ViAnalyzer(Tokenizer):
    def __call__(self, value, **kwargs):
        text = value.strip().lower()
        seg_vi = ViTokenizer.tokenize(text)
        # seg_nf = ViTokenizer.tokenize(unidecode(text))
        # merged = (seg + " " + seg_nf).split()
        merged = (seg_vi + " " + text).split()
        t = Token()
        for i, w in enumerate(merged):
            t.original = w
            t.text = w
            t.boost = 1.0
            t.pos = i
            t.startchar = 0
            t.endchar = 0
            yield t


def get_schema():
    return Schema(
        id=ID(stored=True, unique=True),
        title=TEXT(stored=True, analyzer=ViAnalyzer()),
        content=TEXT(stored=True, analyzer=ViAnalyzer()),
        all=TEXT(stored=True, analyzer=ViAnalyzer())
    )
