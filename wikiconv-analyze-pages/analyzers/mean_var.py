import re
import liwc
import numpy as np
from collections import Counter
from typing import Iterable, Mapping, List

liwcParser, category_names = liwc.load_token_parser('./LIWC2007_English080730.dic')
pagesValues = {}
for cat in category_names:
    pagesValues[cat] = []


def printResult():
    with open("categories_mean_var.txt", "w") as f:
        with open("categories_mean_var_human.txt", "w") as f_human:
            for cat in category_names:
                mean = np.mean(pagesValues[cat])
                var = np.var(pagesValues[cat])
                f.write(f"{cat}\t{mean}\t{var}\n")
                f_human.write(f"{cat:12}\t{mean:.6f}\t{var:.6f}\n")
                print(f"{cat:12}\t{mean:.6f}\t{var:.7f}")

def finalizePage(pageName: str, pageCounter : int, currentPageObjs: List[Mapping]):
    if pageCounter >= 100:
        analyzePage(pageName, currentPageObjs)

def analyzePage(pageName: str, pageObjs: List[Mapping]):
    pageCounter = Counter()
    totalNumberOfWords = 0
    for obj in pageObjs:
        totalNumberOfWords += analyzeLine(obj["cleanedContent"], pageCounter)
    
    if totalNumberOfWords > 0:
        for cat in category_names:
            pagesValues[cat].append(pageCounter[cat] / totalNumberOfWords)

def analyzeLine(line: str, pageCounter: Counter) -> int:
    words = list(tokenize(line))
    pageCounter.update([category for w in words for category in liwcParser(w)])
    return len(words)

def tokenize(text: str):
    for match in re.finditer(r'\w+', text, re.UNICODE):
        yield match.group(0)