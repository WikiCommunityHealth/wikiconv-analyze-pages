import os
import json
import argparse
from pathlib import Path
from typing import Any, List, Mapping
from .analyzer import Analyzer
from ..utils import file_utils
from ..utils.emotion_lexicon import initEmotionLexicon, countEmotionsOfText, Emotions, getEmotionName

class Minify(Analyzer):
    __file = None
    output_dir_path: str = '.'
    __outputCounter = 0
    __compression = None
    lang = 'en'

    def __init__(self):
        self.configureArgs()

    @staticmethod
    def inizialize():
        Minify.configureArgs()
        initEmotionLexicon(Minify.lang)

    @staticmethod
    def configureArgs():
        parser = argparse.ArgumentParser(
            prog='minify',
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
            '--output-compression',
            choices={None, '7z', 'bz2', 'gz'},
            required=False,
            default=None,
            help='Output compression format [default: no compression].',
        )
        parser.add_argument(
            '--lang',
            type=str,
            required=False,
            default='en',
            help='Language.',
        )
        parsed_args, _ = parser.parse_known_args()
        Minify.output_dir_path = parsed_args.output_dir_path
        Minify.__compression = parsed_args.output_compression
        Minify.lang = parsed_args.lang


    def finalizeSection(self, sectionCounter: int, currentSectionObjs: List[Mapping[str, Any]], currentSectionId: int) -> None:
        if sectionCounter <= 0:
            return
        
        if self.__file is not None:
            for obj in currentSectionObjs:
                if obj['type'] == 'ADDITION' or obj['type'] == 'CREATION':
                    c = countEmotionsOfText(obj['cleanedContent'])
                    minObj = {
                        'id': obj['id'],
                        'type': obj['type'],
                        'pageTitle': obj['pageTitle'],
                        'pageId': obj['pageId'],
                        'pageId': obj['pageId'],
                        'user': obj['user'] if 'user' in obj else None,
                        'timestamp': obj['timestamp'],
                        'pageNamespace': obj['pageNamespace'],
                        'emotions': f"{c[Emotions.ANY]},{c[Emotions.POSITIVE]},{c[Emotions.NEGATIVE]},{c[Emotions.ANGER]},{c[Emotions.ANTICIPATION]},{c[Emotions.DISGUST]},{c[Emotions.FEAR]},{c[Emotions.JOY]},{c[Emotions.SADNESS]},{c[Emotions.SURPRISE]},{c[Emotions.TRUST]},"
                    }
                    self.__file.write(f"{currentSectionId}\t{json.dumps(minObj)}\n")

    def fileStart(self, number: int, filename: str) -> None:
        if self.__file is not None:
            self.__file.close()
        newFilename = str(Path(self.output_dir_path) / (f"min-{os.path.splitext(filename)[0]}"))
        self.__file = file_utils.output_writer(path=newFilename, compression=self.__compression)
        self.__outputCounter += 1

    def finalize(self) -> None:
        if self.__file is not None:
            self.__file.close()