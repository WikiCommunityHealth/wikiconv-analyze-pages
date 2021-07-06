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

class ByGender(Analyzer):
    lang = 'en'
    file = 'delme.json'

    userGenderDic = {}
    roles = set()
    counter = {}

    @staticmethod
    def getEmptySectionCounter():
        return {
            "all": [],
            "month": [ [] for x in range(0, 250) ],
            "monthStart": [ [] for x in range(0, 250) ],
            # "monthEnd": [ [] for x in range(0, 250) ],
        }

    @staticmethod
    def getEmptyCounter():
        # c = {
        #     'all': ByGender.getEmptySectionCounter(),
        #     'male': ByGender.getEmptySectionCounter(),
        #     'female': ByGender.getEmptySectionCounter(),
        #     'unknown': ByGender.getEmptySectionCounter(),
        #     'autopatrolled': ByGender.getEmptySectionCounter(),
        #     'rollbacker': ByGender.getEmptySectionCounter(),
        #     'sysop': ByGender.getEmptySectionCounter(),
        # }
        c = {
            # 'all': ByGender.getEmptySectionCounter(),
            'dropoff': ByGender.getEmptySectionCounter(),
            'dropoff-1Y': ByGender.getEmptySectionCounter(),
            'dropoff-2Y': ByGender.getEmptySectionCounter(),
            '2Y': ByGender.getEmptySectionCounter(),
            '1Y': ByGender.getEmptySectionCounter(),
            '10': ByGender.getEmptySectionCounter(),
            '100': ByGender.getEmptySectionCounter(),
            '1000': ByGender.getEmptySectionCounter(),
            '10000': ByGender.getEmptySectionCounter(),
        }
        return c

    @staticmethod
    def loadGenderDic():
        infoFromCsv = {}
        with open(f'./assets/genders/genders-{ByGender.lang}.tsv') as f:
            for l in f:
                info = l.strip('\n').split('\t')
                if info[1] == 'NOT FOUND':
                    continue
                g = 'U'
                if info[2] == 'male':
                    g = 'M'
                elif info[2] == 'female':
                    g = 'F'

                infoFromCsv[int(info[0])] = (g, int(info[3]))

        ByGender.roles = set()
        c = Counter()
        ByGender.userGenderDic = {}
        with open(f'./assets/roles/{ByGender.lang}.tsv') as f:
            for l in f:
                info = l.strip('\n').split('\t')
                id = int(info[0])
                currRoles = info[4].split(',')
                ByGender.userGenderDic[id] = {
                    "gender": infoFromCsv[id][0] if id in infoFromCsv else 'U',
                    "editCount": infoFromCsv[id][1] if id in infoFromCsv else None,
                    "isBot": info[2] == 'True',
                    "lasteEdit": datetime.strptime(info[3], "%Y-%m-%dT%H:%M:%SZ") if info[3] != 'None' else None,
                    "roles": currRoles
                }
                c.update(currRoles)
                for r in currRoles:
                    ByGender.roles.add(r)
        print("User dic loaded")
        print(c)

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

        userInfo = None
        if currentSectionId in ByGender.userGenderDic:
            userInfo =  ByGender.userGenderDic[int(currentSectionId)]
            if userInfo["isBot"]:
                return

        firstDate = self.getDate(currentSectionObjs[0])
        lastDate = self.getDate(currentSectionObjs[-1])
        mDiff = self.monthDiff(
            self.getDate(currentSectionObjs[-1]),
            firstDate
        ) + 1

        startOfTime = datetime.strptime("2000-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
        endOfTime = datetime.strptime("2020-04-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
        offSetMonths = self.monthDiff(firstDate, startOfTime)
        notEditingFor = self.monthDiff(endOfTime, lastDate)

        userEmotions = np.array([0] * 11)
        monthsEmotions = [ np.array([0] * 11) for x in range(0, mDiff + 1) ]
        monthsEmotionsI = [ np.array([0] * 11) for x in range(0, mDiff + 1) ]

        for obj in currentSectionObjs:
            if obj['type'][0] == 'A' or obj['type'][0] == 'C':
                em = [int(x) for x in obj['emotions'].split(',')[0:11] ]
                d = self.getDate(obj)
                nMonth = self.monthDiff(d, firstDate)
                iMont = self.monthDiff(d, startOfTime) - offSetMonths
                userEmotions += em
                monthsEmotions[nMonth] += em
                monthsEmotionsI[iMont] += em

        # ByGender.addToSection('all', userEmotions, monthsEmotions, monthsEmotionsI, mDiff, offSetMonths)

        if userInfo is not None:
            # # GENDER
            # g =  userInfo['gender']
            # if g == 'M':
            #     ByGender.addToSection('male', userEmotions, monthsEmotions, monthsEmotionsI, mDiff, offSetMonths)
            # elif g == 'F':
            #     ByGender.addToSection('female', userEmotions, monthsEmotions, monthsEmotionsI, mDiff, offSetMonths)
            # else:
            #     ByGender.addToSection('unknown', userEmotions, monthsEmotions, monthsEmotionsI, mDiff, offSetMonths)

            # # ROLES
            # if 'autopatrolled' in userInfo['roles'] or 'autoreviewer' in userInfo['roles']:
            #     ByGender.addToSection('autopatrolled', userEmotions, monthsEmotions, monthsEmotionsI, mDiff, offSetMonths)
            # if 'rollbacker' in userInfo['roles']:
            #     ByGender.addToSection('rollbacker', userEmotions, monthsEmotions, monthsEmotionsI, mDiff, offSetMonths)
            # if 'sysop' in userInfo['roles']:
            #     ByGender.addToSection('sysop', userEmotions, monthsEmotions, monthsEmotionsI, mDiff, offSetMonths)

            # EDIT COUNT
            editCount =  userInfo['editCount']
            if editCount is None:
                editCount = sectionCounter
            if editCount >= 10:
                ByGender.addToSection('10', userEmotions, monthsEmotions, monthsEmotionsI, mDiff, offSetMonths)

                if notEditingFor >= 12:
                    ByGender.addToSection('dropoff', userEmotions, monthsEmotions, monthsEmotionsI, mDiff, offSetMonths)
                    if mDiff > 12:
                        ByGender.addToSection('dropoff-1Y', userEmotions, monthsEmotions, monthsEmotionsI, mDiff, offSetMonths)
                    if mDiff > 24:
                        ByGender.addToSection('dropoff-2Y', userEmotions, monthsEmotions, monthsEmotionsI, mDiff, offSetMonths)

                if mDiff > 12:
                    ByGender.addToSection('1Y', userEmotions, monthsEmotions, monthsEmotionsI, mDiff, offSetMonths)
                if mDiff > 24:
                    ByGender.addToSection('2Y', userEmotions, monthsEmotions, monthsEmotionsI, mDiff, offSetMonths)


            if editCount >= 100:
                ByGender.addToSection('100', userEmotions, monthsEmotions, monthsEmotionsI, mDiff, offSetMonths)
            if editCount >= 1000:
                ByGender.addToSection('1000', userEmotions, monthsEmotions, monthsEmotionsI, mDiff, offSetMonths)
            if editCount >= 10000:
                ByGender.addToSection('10000', userEmotions, monthsEmotions, monthsEmotionsI, mDiff, offSetMonths)


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
                    # ByGender.counter[section]["monthEnd"][( - mDiff) + i].append(toAppend)

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
                # "monthEnd": [ self.getMeanVarList(x) for x in ByGender.counter[section]["monthEnd"] ][::-1],
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
