# %% imports and const
from typing import Dict, List, Tuple, Union, cast
import json
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt

emotionColor: Dict[str, Tuple[str, str]] = {
    "global": ('black', 'black'),
    "anger": ('red', 'darkred'),
    "anticipation": ('cyan', 'teal'),
    "disgust": ('olive', 'darkolivegreen'),
    "fear": ('navy', 'midnightblue'),
    "joy": ('yellow', 'gold'),
    "negative": ('gray', 'dimgray'),
    "positive": ('green', 'darkgreen'),
    "sadness": ('blue', 'darkblue'),
    "surprise": ('orange', 'darkorange'),
    "trust": ('purple', 'indigo')
}

name: List[str] = [
    "any",
    "Positive",
    "negative",
    "Anger",
    "Anticipation",
    "Disgust",
    "Fear",
    "Joy",
    "Sadness",
    "Surprise",
    "Trust"
]


ANY = 0
POSITIVE = 1
NEGATIVE = 2
ANGER = 3
ANTICIPATION = 4
DISGUST = 5
FEAR = 6
JOY = 7
SADNESS = 8
SURPRISE = 9
TRUST = 10

ems = [POSITIVE, NEGATIVE, FEAR, ANGER, JOY, SADNESS]

# %% import data
dataCa = {}
with open(f'../json/ca-gender.json') as f:
    dataCa = json.load(f)
print("Ca loaded")

dataIt = {}
with open(f'../json/it-gender.json') as f:
    dataIt = json.load(f)
print("It loaded")

dataEs = {}
with open(f'../json/es-gender.json') as f:
    dataEs = json.load(f)
print("Es loaded")

# %% genders
ax = plt.subplot(111)
x = [ name[e] for e in ems ]
xAx = np.arange(len(x))

fig, axs = plt.subplots(1, 3, figsize=(17,4))
fig.suptitle("Percentage of emotions by user gender for different emotions.")
plt.setp(axs, xticks=xAx, xticklabels=x)

for i, data in  enumerate([
    # (dataEs, "Spanish"),
    # (dataIt, "Italian"),
    (dataCa, "Catalan"),
]):

    unknown = [ data[0]["all"]["all"]["mean"][e] for e in ems ]
    male = [ data[0]["male"]["all"]["mean"][e] for e in ems ]
    female = [ data[0]["female"]["all"]["mean"][e] for e in ems ]

    axs[i].set(xlabel=data[1], ylabel='Percentage of emotions')
    axs[i].bar(xAx - 0.3, unknown, 0.3, label = 'Unknown', color=['tab:gray'], hatch="//", edgecolor='black')
    axs[i].bar(xAx, female, 0.3, label = 'Female', color=['tab:red'], hatch="xx", edgecolor='black')
    axs[i].bar(xAx + 0.3, male, 0.3, label = 'Male', color=['tab:blue'], hatch="++", edgecolor='black')

for ax in axs.flat:
    ax.label_outer()
plt.legend()
# plt.show()
fig.savefig("ciao.jpg")
# %% roles
ax = plt.subplot(111)
x = [ name[e] for e in ems ]
xAx = np.arange(len(x))

fig, axs = plt.subplots(1, 3, figsize=(17,4))
fig.suptitle("Percentage of emotions by user gender for different emotions.")
plt.setp(axs, xticks=xAx, xticklabels=x)

for i, data in  enumerate([
    # (dataEs, "Spanish"),
    (dataCa, "Catalan"),
    (dataIt, "Italian"),
    (dataCa, "Catalan"),
]):

    all = [ data[0]["all"]["all"]["mean"][e] for e in ems ]
    autopatrolled = [ data[0]["autopatrolled"]["all"]["mean"][e] for e in ems ]
    sysop = [ data[0]["sysop"]["all"]["mean"][e] for e in ems ]

    axs[i].set(xlabel=data[1], ylabel='Percentage of emotions')
    axs[i].bar(xAx - 0.3, all, 0.3, label = 'All', hatch="//", edgecolor='black')
    axs[i].bar(xAx, sysop, 0.3, label = 'Admin', hatch="xx", edgecolor='black')
    axs[i].bar(xAx + 0.3, autopatrolled, 0.3, label = 'Autopatrolled', hatch="++", edgecolor='black')

for ax in axs.flat:
    ax.label_outer()
plt.legend()
# plt.show()
fig.savefig("ciao.jpg")
# %%
