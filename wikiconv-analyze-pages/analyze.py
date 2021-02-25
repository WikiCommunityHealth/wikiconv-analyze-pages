
import json
from typing import Iterable, Mapping, List
from . import file_utils
import numpy as np





def analyze(files: Iterable[list], analyzer):
    currentPageId = -1
    currentPageCounter = 0
    currentPageObjs = []

    analyzer.init()

    for inputFile in files:
        i = 0
        print(f"Analyzing {inputFile}...")

        for line in file_utils.open_text_file(str(inputFile)):

            i += 1
            if i % 10000 == 0:
                print(i)
                break
            
            # GET LINE
            [pageId, timestamp, obj] = line.split("\t")
            pageId = int(pageId)

            # ON CHANGE PAGE
            if pageId != currentPageId:
                analyzer.finalizePage(currentPageCounter, currentPageObjs, currentPageId)
                currentPageId = pageId
                currentPageCounter = 0
                currentPageObjs = []


            # FILTER LINE
            if not analyzer.filterId(pageId):
                continue
            obj = json.loads(obj)
            if not analyzer.filterObj(obj):
                continue
            
            currentPageObjs.append(obj)
            currentPageCounter += 1
            
        print(f"Done Analyzing {inputFile}.")
    
    analyzer.printResult()
