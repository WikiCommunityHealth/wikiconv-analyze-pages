from typing import Callable, Dict, List, Mapping, Type
from .mean_var import MeanVarAnalyzer
from .reply_to import ReplyToAnalyzer
from .emotion_lexicon import EmotionLexiconAnalyzer
from .emotion_lexicon_db import EmotionLexiconAnalyzerDb
from .item_word_cloud import ItemWordCloud
from .month_word_cloud import MonthWordCloud
from .minify import Minify
from .analyzer import Analyzer

def __getAnalyzers() -> Dict[str, Type[Analyzer]]:
    return {
        "mean-var": MeanVarAnalyzer,
        "reply-to": ReplyToAnalyzer,
        "emotion-lexicon": EmotionLexiconAnalyzer,
        "emotion-lexicon-db": EmotionLexiconAnalyzerDb,
        "item-word-cloud": ItemWordCloud,
        "month-word-cloud": MonthWordCloud,
        "minify": Minify
    }

def getAnalyzersNames() -> List[str]:
    return [x for x in __getAnalyzers()]

def getAnalyzer(name: str) -> Analyzer:
    return __getAnalyzers()[name]()
    
def getAnalyzerClass(name: str) -> Type[Analyzer]:
    return __getAnalyzers()[name]