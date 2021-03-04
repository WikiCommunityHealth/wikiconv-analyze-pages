from typing import Callable, List, Mapping
from .mean_var import MeanVarAnalyzer
from .analyzer import Analyzer

def __getAnalyzers() -> Mapping[str, Callable[[], Analyzer]]:
    return {
        "mean-var": lambda : MeanVarAnalyzer(),
        "pippo": lambda : Analyzer()
    }

def getAnalyzersNames() -> List[str]:
    return [x for x in __getAnalyzers()]

def getAnalyzer(name: str) -> Analyzer:
    return __getAnalyzers()[name]()