import argparse
import re
import liwc
import numpy as np
from collections import Counter
from typing import Any, Callable, Generator, Iterable, Mapping, List, cast
from .analyzer import Analyzer


class MeanVarAnalyzer(Analyzer):
    __minPageLines = 100

    __liwcParser: Callable[[Any], Generator[Any, None, None]]
    __categoryNames: List[str]
    __pagesValues: Mapping[str, List[float]]
    __minPageLines: int = 0

    def __init__(self):
        self.__liwcParser, self.__categoryNames = liwc.load_token_parser('./LIWC2007_English080730.dic')
        self.__categoryNames = cast(List[str], self.__categoryNames)
        self.__pagesValues = {}

        for cat in self.__categoryNames:
            self.__pagesValues[cat] = cast(List[float], [])
        range(self.__minPageLines)

    def configureArgs(self):
        parser = argparse.ArgumentParser(
            prog='mean_var',
            description='Graph snapshot features extractor.',
        )
        parser.add_argument(
            '--min-page-lines',
            type=int,
            required=True,
            help='Analyzer module name.'
        )
        parsed_args, _ = parser.parse_known_args()
        self.__minPageLines = parsed_args.min_page_lines

    def filterId(self, sectionId: int) -> bool:
        return True

    def filterObj(self, obj: Mapping[str, Any]) -> bool:
        return obj["type"] != "DELETION" and obj["type"] != "MODIFICATION"

    def finalizeSection(self, sectionCounter: int, currentSectionObjs: List[Mapping[str, Any]], currentSectionId: int) -> None:
        if sectionCounter >= self.__minPageLines:
            self.__analyzePage(currentSectionObjs)

    def __analyzePage(self, pageObjs: List[Mapping[str, Any]]):
        pageCounter: 'Counter[str]' = Counter()
        totalNumberOfWords = 0
        for obj in pageObjs:
            totalNumberOfWords += self.__analyzeLine(obj["cleanedContent"], pageCounter)
        
        if totalNumberOfWords > 0:
            for cat in self.__categoryNames:
                self.__pagesValues[cat].append(pageCounter[cat] / totalNumberOfWords)

    def __analyzeLine(self, line: str, pageCounter: 'Counter[str]') -> int:
        words = list(self.__tokenize(line))
        pageCounter.update([category for w in words for category in self.__liwcParser(w)])
        return len(words)

    def __tokenize(self, text: str) -> Iterable[str]:
        for match in re.finditer(r'\w+', text, re.UNICODE):
            yield match.group(0)


    def finalize(self):
        with open("output/categories_mean_var.txt", "w") as f:
            with open("output/categories_mean_var_human.txt", "w") as f_human:
                for cat in self.__categoryNames:

                    mean = np.mean(self.__pagesValues[cat])
                    var = np.var(self.__pagesValues[cat])

                    f.write(f"{cat}\t{mean}\t{var}\n")
                    f_human.write(f"{cat:12}\t{mean:.6f}\t{var:.6f}\n")
                    print(f"{cat:12}\t{mean:.6f}\t{var:.7f}")




