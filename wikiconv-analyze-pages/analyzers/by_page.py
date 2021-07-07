import enum
import os
import json
import argparse
from re import A
import numpy as np
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta, MO
from typing import Any, Counter, Dict, List, Mapping, Union
from .analyzer import Analyzer
from ..utils import file_utils
from ..utils.emotion_lexicon import initEmotionLexicon, countEmotionsOfText, Emotions, getEmotionName
import json
import random

class ByPage(Analyzer):
    lang = 'en'
    file = 'delme.json'

    userGenderDic = {}
    roles = set()
    counter = {}

    def __init__(self):
        self.configureArgs()

    @staticmethod
    def inizialize():
        ByPage.configureArgs()
        ByPage.counter = [ [] for x in range(0, 250) ]

    @staticmethod
    def configureArgs():
        parser = argparse.ArgumentParser(
            prog='by-gender',
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
        ByPage.lang = parsed_args.lang


    def monthDiff(self, a: datetime, b: datetime) -> int:
        return relativedelta(a,b).years * 12 + relativedelta(a,b).months

    def getMonth(self, obj: Any) -> str:
        return obj['timestamp'][0:7]

    def getDate(self, obj: Any) -> datetime:
        return datetime.strptime(obj['timestamp'], "%Y-%m-%dT%H:%M:%SZ")

    def filterId(self, sectionId: int) -> bool:
        return sectionId in [ 31520850, 31776448, 31866536, 33808342, 47378300, 47818503, 48911840, 49328465 ]

    def finalizeSection(self, sectionCounter: int, currentSectionObjs: List[Mapping[str, Any]], currentSectionId: int) -> None:
        if sectionCounter <= 0:
            return
        if currentSectionId <= 0:
            return
        if currentSectionId not in [ 31520850, 31776448, 31866536, 33808342, 47378300, 47818503, 48911840, 49328465 ]:
            return

        print(f"Doing {currentSectionObjs[0]['pageTitle']}")

        startOfTime = datetime.strptime("2000-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")


        for obj in currentSectionObjs:
            if obj['type'][0] == 'A' or obj['type'][0] == 'C':
                em = np.array([int(x) for x in obj['emotions'].split(',')[0:11] ])
                d = self.getDate(obj)
                iMont = self.monthDiff(d, startOfTime)

                x = ByPage.normalize(em)
                if x is not None:
                    ByPage.counter[iMont].append(ByPage.normalize(em))


    @staticmethod
    def normalize(x: np.ndarray) -> Union[np.ndarray, None]:
        a = x[0]
        if a > 0:
            x = x / a
            x[0] = a
            return x
        return None

    def finalize(self) -> None:
        for i in range(0, len(ByPage.counter)):
            ByPage.counter[i] = np.mean(ByPage.counter[i], axis=0).tolist() if len(ByPage.counter[i]) > 0 else [0] * 11

        with open(ByPage.file, 'w') as f:
            json.dump(ByPage.counter, f)


# if obj['type'] == 'ADDITION' or obj['type'] == 'CREATION':
# c = countEmotionsOfText(obj['cleanedContent'])
# minObj = {
#     'id': obj['id'],
#     'type': obj['type'],
#     'pageTitle': obj['pageTitle'],
#     'pageId': obj['pageId'],
#     'pageId': obj['pageId'],
#     'user': obj['user'] if 'user' in obj else None,
#     'timestamp': obj['timestamp'],
#     'pageNamespace': obj['pageNamespace'],
#     'emotions': f"{c[Emotions.ANY]},{c[Emotions.POSITIVE]},{c[Emotions.NEGATIVE]},{c[Emotions.ANGER]},{c[Emotions.ANTICIPATION]},{c[Emotions.DISGUST]},{c[Emotions.FEAR]},{c[Emotions.JOY]},{c[Emotions.SADNESS]},{c[Emotions.SURPRISE]},{c[Emotions.TRUST]},"
# }
# self.__file.write(f"{currentSectionId}\t{json.dumps(minObj)}\n")
