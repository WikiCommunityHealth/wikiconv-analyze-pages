import re
from enum import Enum
from typing import Counter, Iterator

class Emotions(Enum):
    ANGER = 1 << 0
    ANTICIPATION = 1 << 1
    DISGUST = 1 << 2
    FEAR = 1 << 3
    JOY = 1 << 4
    NEGATIVE = 1 << 5
    POSITIVE = 1 << 6
    SADNESS = 1 << 7
    SURPRISE = 1 << 8
    TRUST = 1 << 9
    ANY = 1 << 10
    def __int__(self):
        return self.value

path = './assets/NRC-Emotion-Lexicon-Wordlevel-v0.92.txt'
dic = {}

def getEmotionName(emotion: Emotions) -> str:
    if emotion == Emotions.ANGER:
        return "anger"
    if emotion == Emotions.ANTICIPATION:
        return "anticipation"
    if emotion == Emotions.DISGUST:
        return "disgust"
    if emotion == Emotions.FEAR:
        return "fear"
    if emotion == Emotions.JOY:
        return "joy"
    if emotion == Emotions.NEGATIVE:
        return "negative"
    if emotion == Emotions.POSITIVE:
        return "positive"
    if emotion == Emotions.SADNESS:
        return "sadness"
    if emotion == Emotions.SURPRISE:
        return "surprise"
    if emotion == Emotions.TRUST:
        return "trust"
    if emotion == Emotions.ANY:
        return "analized words"
    return "unknown"

def init():
    with open(path) as file:
        lines = [l for l in file]
        for i in range(0, len(lines), 10):
            wordLine = [l for l in lines[i:i + 10]]
            term = wordLine[0].split('\t')[0]
            bitmap = 1 << 10
            for j in range(10):
                bitmap += int(wordLine[j].split('\t')[2][0]) << j
            dic[term] = bitmap

def tokenize(text: str) -> Iterator[str]:
    for match in re.finditer(r'\w+', text, re.UNICODE):
        yield match.group(0)

def isWordOfEmotion(word: str, emotion: Emotions) -> bool:
    if word in dic:
        return (dic[word] & emotion.value) != 0
    return False

def getEmotionsOfWord(word: str) -> Iterator[Emotions]:
    if word not in dic:
        return []
    d = dic[word]
    for e in Emotions:
        if d & e.value != 0:
            yield e

def countEmotionsOfWords(words: Iterator[str]) -> Counter[Emotions]:
    c = Counter()
    for w in words:
        c.update(getEmotionsOfWord(w))
    return c

def countEmotionsOfText(text: str) -> Counter[Emotions]:
    return countEmotionsOfWords(tokenize(text))