import argparse
import numpy as np
from collections import Counter
from typing import Any, Callable, Dict, Generator, Iterable, Mapping, List, cast
from ..utils.emotion_lexicon import initEmotionLexicon, countEmotionsOfText, Emotions, getEmotionName
from .analyzer import Analyzer
import json
import matplotlib.pyplot as plt
from pathlib import Path

class MeanVarAnalyzer(Analyzer):

    __sectionsEmotionsCount: Dict[Emotions, List[float]]
    __sectionsEmotionsCountByMonth: Dict[str, Dict[Emotions, List[float]]]
    lang = 'en'
    outFile: Path = Path('out.json')

    @staticmethod
    def inizialize():
        MeanVarAnalyzer.configureArgs()

        MeanVarAnalyzer.__sectionsEmotionsCount = {}
        for e in Emotions:
            MeanVarAnalyzer.__sectionsEmotionsCount[e] = []

        MeanVarAnalyzer.__sectionsEmotionsCountByMonth = {}
        for year in range(2000, 2021):
            for month in range(1, 13):
                monthCounters: Dict[Emotions, List[float]] = {}
                for e in Emotions:
                    monthCounters[e] = []
                MeanVarAnalyzer.__sectionsEmotionsCountByMonth[f'{year}-{month:02}'] = monthCounters

        initEmotionLexicon(MeanVarAnalyzer.lang)

    @staticmethod
    def configureArgs():
        parser = argparse.ArgumentParser(
            prog='emotion_analyzer',
            description='Graph snapshot features extractor.',
        )
        parser.add_argument(
            '--output-file',
            metavar='OUTPUT_FILE',
            type=Path,
            required=True,
        )
        parser.add_argument(
            '--lang',
            type=str,
            required=False,
            default='en',
            help='Language.',
        )
        parsed_args, _ = parser.parse_known_args()
        MeanVarAnalyzer.lang = parsed_args.lang
        MeanVarAnalyzer.outFile = parsed_args.output_file


    def filterObj(self, obj: Mapping[str, Any]) -> bool:
        return obj["type"] != "DELETION" and obj["type"] != "MODIFICATION"

    def finalizeSection(self, lineCount: int, currentSectionObjs: List[Mapping[str, Any]], currentSectionId: int) -> None:
        if lineCount <= 0:
            return

        pageCounter: Counter[Emotions] = Counter()
        thisMonthCounter: Counter[Emotions] = Counter()
        thisMonth = ''

        for obj in currentSectionObjs:
            month = obj['timestamp'][:7]
            if month != thisMonth:
                if thisMonth != '':
                    self.saveEmotionCounter(MeanVarAnalyzer.__sectionsEmotionsCountByMonth[thisMonth], thisMonthCounter)
                thisMonth = month
                pageCounter.update(thisMonthCounter)
                thisMonthCounter = Counter()

            c: Counter[Emotions] = countEmotionsOfText(obj['cleanedContent'])
            thisMonthCounter.update(c)
        

        self.saveEmotionCounter(MeanVarAnalyzer.__sectionsEmotionsCountByMonth[thisMonth], thisMonthCounter)
        pageCounter.update(thisMonthCounter)

        self.saveEmotionCounter(MeanVarAnalyzer.__sectionsEmotionsCount, pageCounter)

    def saveEmotionCounter(self, dictToUpdate: Dict[Emotions, List[float]], c: 'Counter[Emotions]'):
        analyzedWords = c[Emotions.ANY]
        if analyzedWords > 0:
            for e in Emotions:
                dictToUpdate[e].append(c[e] / analyzedWords)



    @staticmethod
    def finalizeAll():
        res = MeanVarAnalyzer.meanVarFromEmotionCounter(MeanVarAnalyzer.__sectionsEmotionsCount)

        resMonth: Dict[str, Dict[str, Dict[str, float]]] = {}
        for month in MeanVarAnalyzer.__sectionsEmotionsCountByMonth:
            resMonth[month] = MeanVarAnalyzer.meanVarFromEmotionCounter(MeanVarAnalyzer.__sectionsEmotionsCountByMonth[month])

        with open(MeanVarAnalyzer.outFile, 'w') as f:
            json.dump({
                'ALL': res,
                'months': resMonth
            }, f, cls=EnumEncoder, indent=4)

        MeanVarAnalyzer.drawCharts(resMonth)

    @staticmethod
    def meanVarFromEmotionCounter(c: Dict[Emotions, List[float]]) -> Dict[str, Dict[str, float]]:
        res: Dict[str, Dict[str, float]] = {}
        for e in Emotions:
                if len(c[e]) > 0:
                    res[getEmotionName(e)] = {
                        'mean': float(np.mean(c[e])),
                        'var': float(np.var(c[e])),
                        'len': len(c[e])
                    }
                else:
                    res[getEmotionName(e)] = {
                        'mean': 0,
                        'var': 0,
                        'len': 0
                    }
        return res

    @staticmethod
    def drawCharts(d: Dict[str, Dict[str, Dict[str, float]]]):
        x: List[str] = [month for month in d]
        y = [d[month][getEmotionName(Emotions.ANGER)]['mean'] for month in d]

        plt.plot(x, y)
        plt.savefig(f'ch.png')

class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        print(obj)
        if isinstance(obj, Emotions):
            return getEmotionName(obj)
        return json.JSONEncoder.default(self, obj)