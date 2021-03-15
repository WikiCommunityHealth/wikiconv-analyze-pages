from typing import Callable, Dict, List, Mapping, Type
from .mean_var import MeanVarAnalyzer
from .reply_to import ReplyToAnalyzer
from .emotion_lexicon import EmotionLexiconAnalyzer
from .analyzer import Analyzer

def __getAnalyzers() -> Dict[str, Type[Analyzer]]:
    return {
        "mean-var": MeanVarAnalyzer,
        "reply-to": ReplyToAnalyzer,
        "emotion-lexicon": EmotionLexiconAnalyzer
    }

def getAnalyzersNames() -> List[str]:
    return [x for x in __getAnalyzers()]

def getAnalyzer(name: str) -> Analyzer:
    return __getAnalyzers()[name]()
    
def getAnalyzerClass(name: str) -> Type[Analyzer]:
    return __getAnalyzers()[name]