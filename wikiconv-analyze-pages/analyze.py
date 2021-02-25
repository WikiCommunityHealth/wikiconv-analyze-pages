
import json
from typing import Iterable, Mapping, List
from . import file_utils
import numpy as np





def analyze(files: Iterable[list], analyzer):
    currentPageId = -1
    currentPageCounter = 0
    currentPageObjs = []

    analyzer.init()

    i = 0
    for inputFile in files:
        print(f"Analyzing {inputFile}...")

        for line in file_utils.open_text_file(str(inputFile)):
            
            # GET LINE
            [pageId, timestamp, obj] = line.split("\t")
            obj = json.loads(obj)

            # FILTER LINE
            if not filterLines(obj):
                continue

            # ON CHANGE PAGE
            if pageId != currentPageId:
                analyzer.finalizePage(obj["pageTitle"], currentPageCounter, currentPageObjs)
                currentPageId = pageId
                currentPageCounter = 0
                currentPageObjs = []
            
            currentPageObjs.append(obj)
            currentPageCounter += 1

            i += 1
            if i % 100000 == 0:
                print(i)
            
        print(f"Done Analyzing {inputFile}.")
    
    analyzer.printResult()
    


def filterLines(obj: Mapping) -> bool:
    return obj["type"] != "DELETION" and obj["type"] != "MODIFICATION"


