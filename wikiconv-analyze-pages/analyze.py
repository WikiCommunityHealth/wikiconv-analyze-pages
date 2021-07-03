import json
import os
from pathlib import Path
from .utils.timestamp import printTimestamp
from typing import Any, List, Mapping, Tuple
from .utils import file_utils
from .analyzers import Analyzer
import concurrent.futures
from .analyzers import getAnalyzer, getAnalyzerClass


analysisCompleted = False

def analyze(files: List[Path], analyzerName: str, parallel = False, max_workers=4):
    printTimestamp("Inizializing")
    getAnalyzerClass(analyzerName).inizialize()

    filesAndIndex = enumerate(files)
    if parallel:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            iterator = executor.map(lambda f: analyzeFileListSync([f], analyzerName), filesAndIndex)
            list(iterator)
    else:
        analyzeFileListSync(filesAndIndex, analyzerName)

    printTimestamp("Finalizing")
    getAnalyzerClass(analyzerName).finalizeAll()

    printTimestamp("All done")

def analyzeFileListSync(filesAndIndex, analyzerName: str):
    global analysisCompleted
    analyzer = getAnalyzer(analyzerName)
    for i, inputFile in filesAndIndex:
        if analysisCompleted:
            return
        printTimestamp(f"Starting {os.path.basename(inputFile)}")
        analyzeFile(inputFile, i, analyzer)
        printTimestamp(f"Completed {os.path.basename(inputFile)}")
    analyzer.finalize()

def analyzeFile(inputFile: Path, index: int, analyzer: Analyzer):
    global analysisCompleted

    analyzer.fileStart(index, os.path.basename(inputFile))
    currentSectionId = -1
    currentSectionCounter = 0
    currentSectionObjs: List[Mapping[str, Any]] = []


    file = file_utils.open_text_file(str(inputFile))
    for line in file:
        # GET LINE
        [sortingFields, obj] = line.split("\t")

        # analyzer.finalizeSection(1, [json.loads(obj)], int(sortingFields.split(' ')[0]))
        # continue

        sectionId = -2
        try: 
            sectionId = int(sortingFields.split(' ')[0])
        except:
            print(f"Couldn't parse id, using -2, for {sortingFields}")


        # ON CHANGE PAGE
        if sectionId != currentSectionId:
            completed = analyzer.finalizeSection(currentSectionCounter, currentSectionObjs, currentSectionId)
            currentSectionId = sectionId
            currentSectionCounter = 0
            currentSectionObjs.clear()
            currentSectionObjs = []

            if completed == True or analysisCompleted == True:
                analysisCompleted = True
                printTimestamp(f"Analysis completed without reading all files")
                return

        # FILTER LINE
        if not analyzer.filterId(sectionId):
            continue
        obj = json.loads(obj)
        if not analyzer.filterObj(obj):
            continue
        
        currentSectionObjs.append(obj)
        currentSectionCounter += 1

    file.close()
    if len(currentSectionObjs) > 0:
        analyzer.finalizeSection(currentSectionCounter, currentSectionObjs, currentSectionId)
