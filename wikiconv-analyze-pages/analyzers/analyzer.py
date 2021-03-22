from pathlib import Path
from typing import Any, List, Mapping, Union
from abc import ABC, abstractmethod
class Analyzer(ABC):

    @staticmethod
    def inizialize():
        pass

    @staticmethod
    def finalizeAll():
        pass

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
        ) -> Union[None, bool]:
        return

    def finalize(self) -> None:
        return

    def fileStart(self, number: int) -> None:
        return
