import json
from pathlib import Path
from typing import Any, List, Mapping
from . import file_utils
from .analyzers import Analyzer

def analyze(files: List[Path], analyzer: Analyzer):
    currentSectionId = -1
    currentSectionCounter = 0
    currentSectionObjs: List[Mapping[str, Any]] = []

    for inputFile in files:
        print(f"Analyzing {inputFile}...")
        analyzer.fileStart()

        for line in file_utils.open_text_file(str(inputFile)):
            # GET LINE
            [sortingFields, obj] = line.split("\t")
            sectionId = int(sortingFields.split(' ')[0])
            # obj = line
            # sectionId = 1

            # ON CHANGE PAGE
            if sectionId != currentSectionId:
                analyzer.finalizeSection(currentSectionCounter, currentSectionObjs, currentSectionId)
                currentSectionId = sectionId
                currentSectionCounter = 0
                currentSectionObjs = []


            # FILTER LINE
            if not analyzer.filterId(sectionId):
                continue
            obj = json.loads(obj)
            if not analyzer.filterObj(obj):
                continue
            
            currentSectionObjs.append(obj)
            currentSectionCounter += 1

        analyzer.finalizeSection(currentSectionCounter, currentSectionObjs, currentSectionId)
        print(f"Done Analyzing {inputFile}.")
    
    analyzer.finalize()
