from collections import Counter
import argparse
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple, Union
from .analyzer import Analyzer
from ..utils.emotion_lexicon import initEmotionLexicon, countEmotionsOfText, Emotions, getEmotionName
from ..utils.database import DatabaseService


class EmotionLexiconAnalyzerDb(Analyzer):

    db: DatabaseService
    year_month_cosi: List[str] = []
    lang = 'en'

    metricsOrder = [
        Emotions.ANY, Emotions.NEGATIVE, Emotions.POSITIVE,
        Emotions.ANGER, Emotions.ANTICIPATION, Emotions.DISGUST,
        Emotions.FEAR, Emotions.JOY, Emotions.SADNESS,
        Emotions.SURPRISE, Emotions.TRUST
    ]


    @staticmethod
    def inizialize():
        EmotionLexiconAnalyzerDb.db = DatabaseService(map(lambda x: getEmotionName(x), EmotionLexiconAnalyzerDb.metricsOrder))
        EmotionLexiconAnalyzerDb.db.dropTables([EmotionLexiconAnalyzerDb.lang])
        EmotionLexiconAnalyzerDb.db.createTable([EmotionLexiconAnalyzerDb.lang])

        EmotionLexiconAnalyzerDb.configureArgs()
        initEmotionLexicon(EmotionLexiconAnalyzerDb.lang)
        # EmotionLexiconAnalyzerDb.year_month_cosi = [f"{str(y).zfill(4)}-{str(m).zfill(2)}" for y in range(2000, 2021) for m in range(1, 13)]

    @staticmethod
    def configureArgs():
        parser = argparse.ArgumentParser(
            prog='emotion_analyzer',
            description='Graph snapshot features extractor.',
        )
        parser.add_argument(
            '--lang',
            type=str,
            required=False,
            default='en',
            help='Language.',
        )
        parsed_args, _ = parser.parse_known_args()
        EmotionLexiconAnalyzerDb.lang = parsed_args.lang

    def __init__(self):
        self.db = DatabaseService(map(lambda x: getEmotionName(x), EmotionLexiconAnalyzerDb.metricsOrder))


    def saveMonth(self, id: int, title: str, month: str, monthCounter: Counter, sectionCounter: Counter):
        monthTotal = monthCounter[Emotions.ANY]
        sectionTotal = sectionCounter[Emotions.ANY]

        if monthTotal == 0 or sectionTotal == 0:
            return

        metrics: List[Tuple[float, float, float, float]] = []
        for m in EmotionLexiconAnalyzerDb.metricsOrder:
            metrics.append((
                monthCounter[m], monthCounter[m] / monthTotal,
                sectionCounter[m], sectionCounter[m] / sectionTotal
            ))

        self.db.insertMetrics(
            EmotionLexiconAnalyzerDb.lang,
            id,
            title,
            month,
            metrics
        )

    def finalizeSection(self, lineCount: int, currentSectionObjs: List[Dict[str, Any]], currentSectionId: int) -> None:
        if lineCount <= 0:
            return

        title = currentSectionObjs[0]["pageTitle"]
        id = int(currentSectionObjs[0]["pageId"])

        monthCounter = Counter()
        sectionCounter = Counter()
        thisMonth = ''
        for obj in currentSectionObjs:
            if obj['type'] == 'ADDITION' or obj['type'] == 'CREATION':
                month = obj['timestamp'][:7]

                if month != thisMonth:
                    if thisMonth != '':
                        self.saveMonth(id, title, thisMonth, monthCounter, sectionCounter)

                    thisMonth = month
                    sectionCounter.update(monthCounter)
                    monthCounter = Counter()

                c = countEmotionsOfText(obj['cleanedContent'])
                monthCounter.update(c)

        sectionCounter.update(monthCounter)
        self.saveMonth(id, title, thisMonth, monthCounter, sectionCounter)


