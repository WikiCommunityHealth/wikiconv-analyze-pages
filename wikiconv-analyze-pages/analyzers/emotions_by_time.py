import argparse
import re
import liwc
import datetime
import numpy as np
from collections import Counter
from typing import Iterable, Mapping, List
from ..utils import types
import matplotlib.pyplot as plt


liwcParser, category_names = liwc.load_token_parser('./LIWC2007_English080730.dic')
monthsCounters = {}


minPageLines = 100
emotion = ""

def configureArgs():
    global minPageLines
    global emotion

    parser = argparse.ArgumentParser(
        prog='mean_var',
        description='Graph snapshot features extractor.',
    )
    parser.add_argument(
        '--min-page-lines',
        type=int,
        required=False,
        default=250,
        help='Analyzer module name.'
    )
    parser.add_argument(
        '--emotion', '-e',
        type=str,
        required=True,
        help='Analyzer module name.'
    )
    parsed_args, _ = parser.parse_known_args()

    minPageLines = parsed_args.min_page_lines
    emotion = parsed_args.emotion
    if emotion not in category_names:
        print(f"Emotion {emotion} not found")
        exit(0)

def init():
    for year in range(2000, 2022):
        for month in range(1, 13):
            monthsCounters[f"{year}-{str(month).zfill(2)}"] = [0, Counter()]

def finalize():
    heights = []
    labels = []

    for months in monthsCounters:
        [tot, conter] = monthsCounters[months]
        labels.append(months)
        if tot != 0:
            heights.append(conter[emotion] / tot)
        else:
            heights.append(0 if tot <= 0 else conter[emotion] / tot)

    y_pos = range(len(labels))
    f, ax = plt.subplots(figsize=(100,20)) # set the size that you'd like (width, height)
    plt.bar(y_pos, heights)
    plt.xticks(y_pos, labels, rotation=90)
    plt.savefig(f'output/emotion-by-time-{emotion}.png')

    for months in monthsCounters:
        [tot, conter] = monthsCounters[months]
        print(f"{months}\t{tot}\n")
        for em in category_names:
            print(f"{em}\t{conter[em]}\t{0 if tot <= 0 else conter[emotion] / tot}\n")
            print("\n")

def finalizePage(pageCounter : int, currentPageObjs: List[Mapping], pageId):
    if pageCounter > 0:
        analyzePage(currentPageObjs, pageId)

def filterId(pageId: int) -> bool:
    return True
    return pageId == 1197298

def filterObj(obj: Mapping) -> bool:
    return obj["type"] != "DELETION" and obj["type"] != "MODIFICATION" and obj["type"] != "RESTORATION"

def analyzePage(pageObjs: List[Mapping], pageId):
    for raw_obj in pageObjs:
        obj = types.cast_json(raw_obj)
        monthstr = obj["timestamp"].strftime("%Y-%m")

        words = list(tokenize(obj["cleanedContent"]))
        monthsCounters[monthstr][1].update([category for w in words for category in liwcParser(w)])
        monthsCounters[monthstr][0] += len(words)

    return


def tokenize(text: str):
    for match in re.finditer(r'\w+', text, re.UNICODE):
        yield match.group(0)