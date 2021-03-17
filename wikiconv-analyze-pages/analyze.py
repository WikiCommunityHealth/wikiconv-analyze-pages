import json
import os
from pathlib import Path
from .utils.timestamp import printTimestamp
from typing import Any, List, Mapping, Tuple
from . import file_utils
from .analyzers import Analyzer
import concurrent.futures
from .analyzers import getAnalyzer, getAnalyzerClass

def analyze(files: List[Path], analyzerName: str, parallel = False, max_workers=4):
    printTimestamp(Path('.'), "Inizializing")
    getAnalyzerClass(analyzerName).inizialize()

    filesAndIndex = enumerate(files)
    if parallel:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            iterator = executor.map(lambda f: analyzeFileListSync([f], analyzerName), filesAndIndex)
            list(iterator)
    else:
        analyzeFileListSync(filesAndIndex, analyzerName)

    printTimestamp(Path('.'), "Finalizing")
    getAnalyzerClass(analyzerName).finalizeAll()

    printTimestamp(Path('.'), "All done")

def analyzeFileListSync(filesAndIndex, analyzerName: str):
    analyzer = getAnalyzer(analyzerName)
    for i, inputFile in filesAndIndex:
        printTimestamp(Path('.'), f"Starting {os.path.basename(inputFile)}")
        analyzeFile(inputFile, i, analyzer)
        printTimestamp(Path('.'), f"Completed {os.path.basename(inputFile)}")
    analyzer.finalize()

def analyzeFile(inputFile: Path, index: int, analyzer: Analyzer):

    analyzer.fileStart(index)
    currentSectionId = -1
    currentSectionCounter = 0
    currentSectionObjs: List[Mapping[str, Any]] = []


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
