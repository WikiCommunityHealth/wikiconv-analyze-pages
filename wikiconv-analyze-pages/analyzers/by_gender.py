import enum
import os
import json
import argparse
from re import A
import numpy as np
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta, MO
from typing import Any, Dict, List, Mapping, Union
from .analyzer import Analyzer
from ..utils import file_utils
from ..utils.emotion_lexicon import initEmotionLexicon, countEmotionsOfText, Emotions, getEmotionName
import json

class ByGender(Analyzer):
    lang = 'en'
    file = 'delme.json'

    userGenderDic = {}
    counter = {}

    @staticmethod
    def getEmptySectionCounter():
        return {
            "all": [],
            "month": [ [] for x in range(0, 250) ],
            "monthStart": [ [] for x in range(0, 250) ],
            "monthEnd": [ [] for x in range(0, 250) ],
        }

    @staticmethod
    def getEmptyCounter():
        c = {
            'all': ByGender.getEmptySectionCounter(),
            'male': ByGender.getEmptySectionCounter(),
            'female': ByGender.getEmptySectionCounter(),
            'unknown': ByGender.getEmptySectionCounter(),
        }
        return c
        # c["gender"] = {
        #     "M": ByGender.getEmptySectionCounter(),
        #     "F": ByGender.getEmptySectionCounter(),
        #     "U":ByGender.getEmptySectionCounter()
        # }

    @staticmethod
    def loadGenderDic():
        ByGender.userGenderDic = {}
        with open(f'./assets/genders/genders-{ByGender.lang}.tsv') as f:
            for l in f:
                info = l.strip('\n').split('\t')
                g = 'U'
                if info[2] == 'male':
                    g = 'M'
                elif info[2] == 'female':
                    g = 'F'
                ByGender.userGenderDic[int(info[0])] = g

    def __init__(self):
        self.configureArgs()

    @staticmethod
    def inizialize():
        ByGender.counter = ByGender.getEmptyCounter()
        ByGender.configureArgs()
        ByGender.loadGenderDic()

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
        parser.add_argument(
            '--json',
            type=str,
            required=True,
        )
        parsed_args, _ = parser.parse_known_args()
        ByGender.lang = parsed_args.lang
        ByGender.file = parsed_args.json


    def monthDiff(self, a: datetime, b: datetime) -> int:
        return relativedelta(a,b).years * 12 + relativedelta(a,b).months

    def getMonth(self, obj: Any) -> str:
        return obj['timestamp'][0:7]

    def getDate(self, obj: Any) -> datetime:
        return datetime.strptime(obj['timestamp'], "%Y-%m-%dT%H:%M:%SZ")

    def finalizeSection(self, sectionCounter: int, currentSectionObjs: List[Mapping[str, Any]], currentSectionId: int) -> None:
        if sectionCounter <= 0:
            return
        if currentSectionId <= 0:
            return

        # if len(ByGender.counter["all"]) > 2:
            # return



        firstDate = self.getDate(currentSectionObjs[0])
        mDiff = self.monthDiff(
            self.getDate(currentSectionObjs[-1]),
            firstDate
        ) + 1

        startOfTime = datetime.strptime("2000-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
        offSetMonths = self.monthDiff(firstDate, startOfTime)

        userEmotions = np.array([0] * 11)
        monthsEmotions = [np.array([0] * 11)] * mDiff
        monthsEmotionsI = [np.array([0] * 11)] * (mDiff + 1)

        # if currentSectionId in ByGender.userGenderDic:
        #     # print(ByGender.userGenderDic[currentSectionId])
        #     if (currentSectionObjs[-1]['timestamp'] > "2020-03-01T00:00:00Z"):
        #         print(currentSectionObjs[-1]['timestamp'])

        for obj in currentSectionObjs:
            if obj['type'][0] == 'A' or obj['type'][0] == 'C':
                em = [int(x) for x in obj['emotions'].split(',')[0:11] ]
                d = self.getDate(obj)
                nMonth = self.monthDiff(d, firstDate)
                iMont = self.monthDiff(d, startOfTime) - offSetMonths
                userEmotions += em
                monthsEmotions[nMonth] += em
                monthsEmotionsI[iMont] += em

        ByGender.addToSection('all', userEmotions, monthsEmotions, monthsEmotionsI, mDiff, offSetMonths)

        if currentSectionId in ByGender.userGenderDic:
            g =  ByGender.userGenderDic[currentSectionId]
            if g == 'M':
                ByGender.addToSection('male', userEmotions, monthsEmotions, monthsEmotionsI, mDiff, offSetMonths)
            elif g == 'F':
                ByGender.addToSection('female', userEmotions, monthsEmotions, monthsEmotionsI, mDiff, offSetMonths)
            else:
                ByGender.addToSection('unknown', userEmotions, monthsEmotions, monthsEmotionsI, mDiff, offSetMonths)



    @staticmethod
    def addToSection(
        section: str,
        userEmotions: np.ndarray,
        monthsEmotions: List[np.ndarray],
        monthsEmotionsI: List[np.ndarray],
        mDiff: int,
        offSetMonths: int
    ):
        x = ByGender.normalize(userEmotions)
        if x is not None:
            ByGender.counter[section]["all"].append(ByGender.normalize(userEmotions))
            for i, em in enumerate(monthsEmotions):
                toAppend = ByGender.normalize(em)
                if toAppend is not None:
                    ByGender.counter[section]["monthStart"][i].append(toAppend)
                    ByGender.counter[section]["monthEnd"][mDiff - 1 - i].append(toAppend)

            for i, em in enumerate(monthsEmotionsI):
                toAppend = ByGender.normalize(em)
                if toAppend is not None:
                    ByGender.counter[section]["month"][i + offSetMonths].append(toAppend)

    @staticmethod
    def normalize(x: np.ndarray) -> Union[np.ndarray, None]:
        a = x[0]
        if a > 0:
            x = x / a
            x[0] = a
            return x
        return None


    def getMeanVarList(self, x):
        l = len(x)
        return {
            "mean": np.mean(x, axis=0).tolist() if l > 0 else [0] * 11,
            "var": np.var(x, axis=0).tolist() if l > 0 else [0] * 11,
            "n": l,
            "tot": sum(n[0] for n in x)
        }

    def finalize(self) -> None:
        res = {}
        for section in ByGender.counter:
            res[section] = {
                "all": self.getMeanVarList(ByGender.counter[section]["all"]),
                "monthStart": [ self.getMeanVarList(x) for x in ByGender.counter[section]["monthStart"] ],
                "monthEnd": [ self.getMeanVarList(x) for x in ByGender.counter[section]["monthEnd"] ],
                "month": [ self.getMeanVarList(x) for x in ByGender.counter[section]["month"] ]
            }

        with open(ByGender.file, 'w') as f:
            json.dump(res, f)


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
