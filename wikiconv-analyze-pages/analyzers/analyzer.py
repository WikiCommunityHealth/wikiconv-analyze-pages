from typing import Any, List, Mapping
from abc import ABC, abstractmethod
class Analyzer(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def configureArgs(self):
        pass

    @abstractmethod
    def filterId(self, sectionId: int) -> bool:
        pass

    @abstractmethod
    def filterObj(self, obj: Mapping[str, Any]) -> bool:
        pass

    @abstractmethod
    def finalizeSection(
        self,
        sectionCounter: int,
        currentSectionObjs: List[Mapping[str, Any]],
        currentSectionId: int
        ) -> None:
        pass

    @abstractmethod
    def printResult(self) -> None:
        pass
