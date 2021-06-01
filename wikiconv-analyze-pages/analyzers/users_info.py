import argparse
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple, cast
from .analyzer import Analyzer
from threading import Lock
import json

class UserInfo(Analyzer):
    outputFile: Path = Path()
    genderFile: Path = Path()
    usersGenderAndRoles: Dict[int, Tuple[str, List]] = {} # Female: True, Male: False
    data = {}
    dataLock = Lock()

    @staticmethod
    def inizialize():
        UserInfo.configureArgs()
        gensersSet: Set[str] = set()
        rolesSet: Set[str] = set()
        with open(UserInfo.genderFile) as f:
            for l in f:
                info = l.split('\t')
                userId = int(info[0])
                gender = info[2]
                roles = info[5].split(',')
                UserInfo.usersGenderAndRoles[userId] = (gender, roles)
                gensersSet.add(gender)
                for r in roles:
                    rolesSet.add(r)

        data = {}
        data["roles"] = {}
        data["genders"] = {}
        data["all"] = UserInfo.getEmptyDataElement()
        for r in rolesSet:
            data["roles"][r] = UserInfo.getEmptyDataElement()
        for g in gensersSet:
            data["genders"][g] = UserInfo.getEmptyDataElement()
        UserInfo.data = data

    @staticmethod
    def getEmptyDataElement() -> Dict[str, Any]:
        return {
            "all": [0] * 11,
            "lifeMonths": {x: [0]*11 for x in range(0, ((2021 - 2000) * 12))},
            "months": {f"{y}-{str(m).zfill(2)}": [0]*11 for y in range(2000, 2021) for m in  range(1, 13)}
        }

    @staticmethod
    def configureArgs():
        parser = argparse.ArgumentParser(
            prog='emotion_analyzer',
            description='Graph snapshot features extractor.',
        )
        parser.add_argument(
            '--output-file',
            type=Path,
            required=True,
            help='JSON data file.',
        )
        parser.add_argument(
            '--gender-file',
            type=Path,
            required=True,
            help='TSV gender file.',
        )
        parsed_args, _ = parser.parse_known_args()
        UserInfo.outputFile = parsed_args.output_file
        UserInfo.genderFile = parsed_args.gender_file

    def __init__(self):
        super().__init__()


    def finalizeSection(self, sectionCounter: int, currentSectionObjs: List[Dict[str, Any]], currentSectionId: int) -> None:
        if sectionCounter <= 0:
            return

        firstMotn = currentSectionObjs[0]['timestamp'][:7]

        print(currentSectionId)

        if currentSectionId in UserInfo.usersGenderAndRoles:
            userId = currentSectionId
            for obj in currentSectionObjs:
                (gender, roles) = UserInfo.usersGenderAndRoles[userId]
                month = obj['timestamp'][:7]
                lifeMonth = self.monthDiff(firstMotn, month)
                listEmotions = list(map(lambda x: int(x), cast(str, obj['emotions']).split(',')[:-1]))

                with UserInfo.dataLock:
                    self.addToDataElemet(UserInfo.data['all'], month, lifeMonth, listEmotions)
                    self.addToDataElemet(UserInfo.data['genders'][gender], month, lifeMonth, listEmotions)
                    for r in roles:
                        self.addToDataElemet(UserInfo.data['roles'][r], month, lifeMonth, listEmotions)


    def addToDataElemet(self, dataElemet: Dict[str, Any], month: str, lifeMonth: int, listEmotions: List[int]):
        dataElemet['all'] = self.sumList(dataElemet['all'], listEmotions)
        dataElemet['lifeMonths'][lifeMonth] = self.sumList(dataElemet['lifeMonths'][lifeMonth], listEmotions)
        dataElemet['months'][month] = self.sumList(dataElemet['months'][month], listEmotions)


    def sumList(self, l1: List[int], l2: List[int]) -> List[int]:
        return [a+b for a, b in zip(l1, l2)]

    @staticmethod
    def normalizeList(l: List[int]) -> List[float]:
        tot = l[0]
        if tot == 0:
            return [0] * len(l)
        return [x / tot for x in l]

    @staticmethod
    def normalizeElement(el: Dict[str, Any]) -> Dict[str, Any]:
        res = {}
        res["all"] = UserInfo.normalizeList(el["all"])

        res["lifeMonths"] = {}
        for k in el["lifeMonths"]:
            res["lifeMonths"][k] = UserInfo.normalizeList(el["lifeMonths"][k])

        res["months"] = {}
        for k in el["months"]:
            res["months"][k] = UserInfo.normalizeList(el["months"][k])

        return res

    @staticmethod
    def normalizeData(el: Dict[str, Any]) -> Dict[str, Any]:
        res = {}
        res["all"] = UserInfo.normalizeElement(el["all"])

        res["genders"] = {}
        for g in el["genders"]:
            res["genders"][g] = UserInfo.normalizeElement(el["genders"][g])

        res["roles"] = {}
        for r in el["roles"]:
            res["roles"][r] = UserInfo.normalizeElement(el["roles"][r])

        return res

    def monthDiff(self, date1: str, date2: str) -> int:
        return ((int(date2[:4]) - int(date1[:4])) * 12) + (int(date2[-2:]) - int(date1[-2:]))

    @staticmethod
    def finalizeAll():
        normalized = UserInfo.normalizeData(UserInfo.data)
        res = {
            "assolute": UserInfo.data,
            "normalized": normalized
        }

        with open(UserInfo.outputFile, 'w') as outfile:
            json.dump(res, outfile)
