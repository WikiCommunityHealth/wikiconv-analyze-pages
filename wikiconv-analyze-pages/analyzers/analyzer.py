from pathlib import Path
from typing import Any, List, Mapping
from abc import ABC, abstractmethod
class Analyzer(ABC):

    @abstractmethod
    def __init__(self):
        pass

    def configureArgs(self):
        return

    def filterId(self, sectionId: int) -> bool:
        return True

    def filterObj(self, obj: Mapping[str, Any]) -> bool:
        return True

    def finalizeSection(
        self,
        sectionCounter: int,
        currentSectionObjs: List[Mapping[str, Any]],
        currentSectionId: int
        ) -> None:
        return

    def printResult(self) -> None:
        return

    def fileEnd(self) -> None:
        return
