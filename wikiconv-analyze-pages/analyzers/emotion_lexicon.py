from collections import Counter
import argparse
import glob
from pathlib import Path
from typing import Any, Dict, List
from .analyzer import Analyzer
from .. import file_utils
from ..utils.emotion_lexicon import initEmotionLexicon, countEmotionsOfText, Emotions, getEmotionName

class EmotionLexiconAnalyzer(Analyzer):
    __file = None
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
        files = glob.glob(str(EmotionLexiconAnalyzer.outputPath / "page-emotion-lexicon-*.csv"))

        newFilename = str(EmotionLexiconAnalyzer.outputPath / ("page-emotion-lexicon.csv"))
        outFile = file_utils.output_writer(path=newFilename, compression=EmotionLexiconAnalyzer.compression)

        header = "Page name,Total wikiconv lines, wikiconv lines analyzed"
        for e in EmotionLexiconAnalyzer.emotionPrintOrder:
            header += f",{getEmotionName(e)}"
        outFile.write(f"{header}\n")
        
        for f in files:
            with open(f) as infile:
                for line in infile:
                    outFile.write(line)

        outFile.close()


    def __init__(self):
        pass

    def finalizeSection(self, sectionCounter: int, currentSectionObjs: List[Dict[str, Any]], currentSectionId: int) -> None:
        if sectionCounter <= 0:
            return

        lineAnalyzed = 0
        c = Counter()
        for obj in currentSectionObjs:
            if obj['type'] == 'ADDITION' or obj['type'] == 'CREATION':
                countEmotionsOfText(obj['cleanedContent'], c)
                # c.update(countEmotionsOfText(obj['cleanedContent']))
                lineAnalyzed += 1

        line = currentSectionObjs[0]["pageTitle"]
        line += f",{len(currentSectionObjs)},{lineAnalyzed}"
        for e in EmotionLexiconAnalyzer.emotionPrintOrder:
            line += f",{c.get(e, 0)}"

        self.__file.write(f"{line}\n")

    def fileStart(self, number: int) -> None:
        if self.__file is not None:
            self.__file.close()
        newFilename = str(EmotionLexiconAnalyzer.outputPath / (f"page-emotion-lexicon-{str(number).zfill(4)}.csv"))
        self.__file = file_utils.output_writer(path=newFilename, compression=EmotionLexiconAnalyzer.compression)

    def finalize(self) -> None:
        if self.__file is not None:
            self.__file.close()
