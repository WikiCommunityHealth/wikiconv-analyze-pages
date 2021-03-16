from collections import Counter
import argparse
import glob
from io import TextIOWrapper
from pathlib import Path
from typing import Any, Dict, Iterable, List, TextIO, Union
from .analyzer import Analyzer
from .. import file_utils
from ..utils.emotion_lexicon import initEmotionLexicon, countEmotionsOfText, Emotions, getEmotionName
from ..utils import csv_writer

class EmotionLexiconAnalyzer(Analyzer):
    __file_all_int: Union[TextIOWrapper, TextIO, None] = None
    __file_all_float: Union[TextIOWrapper, TextIO, None] = None
    __file_by_emotions: Dict[Emotions, Union[TextIOWrapper, TextIO, None]] = {}

    year_month_cosi: List[str] = []
    outputPath: Path = Path()
    compression = None
    lang = 'en'

    emotionPrintOrder = [
        Emotions.ANY, Emotions.NEGATIVE, Emotions.POSITIVE,
        Emotions.ANGER, Emotions.ANTICIPATION, Emotions.DISGUST,
        Emotions.FEAR, Emotions.JOY, Emotions.SADNESS,
        Emotions.SURPRISE, Emotions.TRUST
        ]


    @staticmethod
    def inizialize():
        EmotionLexiconAnalyzer.configureArgs()
        initEmotionLexicon(EmotionLexiconAnalyzer.lang)
        #EmotionLexiconAnalyzer.year_month_cosi = [f"{str(y).zfill(4)}-{str(m).zfill(2)}" for y in range(2000, 2021) for m in range(1, 13)]
        EmotionLexiconAnalyzer.year_month_cosi = [f"{str(y).zfill(4)}" for y in range(2000, 2021)]


    @staticmethod
    def configureArgs():
        parser = argparse.ArgumentParser(
            prog='emotion_analyzer',
            description='Graph snapshot features extractor.',
        )
        parser.add_argument(
            '--output-dir-path',
            metavar='OUTPUT_DIR',
            type=Path,
            required=True,
            help='XML output directory.',
        )
        parser.add_argument(
            '--lang',
            type=str,
            required=False,
            default='en',
            help='Language.',
        )
        parser.add_argument(
            '--output-compression',
            choices={None, '7z', 'bz2', 'gz'},
            required=False,
            default=None,
            help='Output compression format [default: no compression].',
        )
        parsed_args, _ = parser.parse_known_args()
        EmotionLexiconAnalyzer.outputPath = parsed_args.output_dir_path
        EmotionLexiconAnalyzer.compression = parsed_args.output_compression
        EmotionLexiconAnalyzer.lang = parsed_args.lang

    @staticmethod
    def finalizeAll():
        file_utils.create_path(EmotionLexiconAnalyzer.outputPath / "results")

        csv_writer.joinCSVs(
            filesPattern=str(EmotionLexiconAnalyzer.outputPath / "page-emotion-lexicon-*.csv"),
            headers=["Page name", "Months"] + [getEmotionName(e) for e in EmotionLexiconAnalyzer.emotionPrintOrder],
            outputFile=str(EmotionLexiconAnalyzer.outputPath / "results/page-emotion-lexicon.csv"),
            compression=EmotionLexiconAnalyzer.compression
        )
        csv_writer.joinCSVs(
            filesPattern=str(EmotionLexiconAnalyzer.outputPath / "page-emotion-lexicon-percentage-*.csv"),
            headers=["Page name", "Months"] + [getEmotionName(e) for e in EmotionLexiconAnalyzer.emotionPrintOrder],
            outputFile=str(EmotionLexiconAnalyzer.outputPath / "results/page-emotion-lexicon-percentage.csv"),
            compression=EmotionLexiconAnalyzer.compression
        )
        for e in EmotionLexiconAnalyzer.emotionPrintOrder:
            csv_writer.joinCSVs(
                filesPattern=str(EmotionLexiconAnalyzer.outputPath / f"page-emotion-lexicon-{getEmotionName(e)}-*.csv"),
                headers=["Page name"] + EmotionLexiconAnalyzer.year_month_cosi,
                outputFile=str(EmotionLexiconAnalyzer.outputPath / f"results/page-emotion-lexicon-{getEmotionName(e)}.csv"),
                compression=EmotionLexiconAnalyzer.compression
            )


    def __init__(self):
        pass

    def finalizeSection(self, sectionCounter: int, currentSectionObjs: List[Dict[str, Any]], currentSectionId: int) -> None:
        if sectionCounter <= 0:
            return

        monthCounters: Dict[str, 'Counter[Emotions]'] = {}
        for m in EmotionLexiconAnalyzer.year_month_cosi:
            monthCounters[m] = Counter()

        for obj in currentSectionObjs:
            if obj['type'] == 'ADDITION' or obj['type'] == 'CREATION':
                month = obj['timestamp'][:4]
                c = countEmotionsOfText(obj['cleanedContent'])
                monthCounters[month].update(c)

        emotionsData: Dict[Emotions, List[int]] = {}
        emotionsDataPercentage: Dict[Emotions, List[float]] = {}
        for e in EmotionLexiconAnalyzer.emotionPrintOrder:
            emotionsData[e] = []
            emotionsDataPercentage[e] = []

        for m in EmotionLexiconAnalyzer.year_month_cosi:
            monthCounter = monthCounters[m]
            allCounter = monthCounters[m].get(Emotions.ANY, 0)
            for e in EmotionLexiconAnalyzer.emotionPrintOrder:
                monthValue = monthCounter.get(e, 0)
                emotionsData[e].append(monthValue)
                if e == Emotions.ANY:
                    emotionsDataPercentage[e].append(monthValue)
                else:
                    emotionsDataPercentage[e].append(monthValue / allCounter if allCounter > 0 else 0)
        
        title = currentSectionObjs[0]["pageTitle"]
        csv_writer.writelineMultiValueNumber(
            file=self.__file_all_int,
            preValues=[title, "2000-01|2020-12"],
            multiValues=[emotionsData[e] for e in EmotionLexiconAnalyzer.emotionPrintOrder]
        )
        csv_writer.writelineMultiValueNumber(
            file=self.__file_all_float,
            preValues=[title, "2000-01|2020-12"],
            multiValues=[emotionsDataPercentage[e] for e in EmotionLexiconAnalyzer.emotionPrintOrder]
        )
        for e in EmotionLexiconAnalyzer.emotionPrintOrder:
            csv_writer.writelineNumber(
                file=self.__file_by_emotions[e],
                values=[title] + emotionsData[e]
            )

        # line = currentSectionObjs[0]["pageTitle"]
        # line += f",{len(currentSectionObjs)},{lineAnalyzed}"
        # for e in EmotionLexiconAnalyzer.emotionPrintOrder:
        #     line += f",{globalCounter.get(e, 0)}"

        # self.__file.write(f"{line}\n")

    def fileStart(self, number: int) -> None:
        self.closeFiles()

        newFilenameInt = str(EmotionLexiconAnalyzer.outputPath / (f"page-emotion-lexicon-{str(number).zfill(4)}.csv"))
        self.__file_all_int = file_utils.output_writer(path=newFilenameInt, compression=EmotionLexiconAnalyzer.compression)

        newFilenameFloat = str(EmotionLexiconAnalyzer.outputPath / (f"page-emotion-lexicon-percentage-{str(number).zfill(4)}.csv"))
        self.__file_all_float = file_utils.output_writer(path=newFilenameFloat, compression=EmotionLexiconAnalyzer.compression)

        for e in EmotionLexiconAnalyzer.emotionPrintOrder:
            newFilenameEmotion = str(EmotionLexiconAnalyzer.outputPath / (f"page-emotion-lexicon-{getEmotionName(e)}-{str(number).zfill(4)}.csv"))
            self.__file_by_emotions[e] = file_utils.output_writer(path=newFilenameEmotion, compression=EmotionLexiconAnalyzer.compression)

    def closeFiles(self) -> None:
        if self.__file_all_int is not None:
            self.__file_all_int.close()

        if self.__file_all_float is not None:
            self.__file_all_float.close()

        for k in self.__file_by_emotions:
            self.__file_by_emotions[k].close()

    def finalize(self) -> None:
        self.closeFiles()

