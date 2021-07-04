# %% imports and const
from typing import Any, Dict, List, Tuple, Union, cast
import json
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt

emotionColor: List[Tuple[str, str]] = [
    ('gray', 'dimgray'),
    ('green', 'darkgreen'),
    ('black', 'black'),
    ('red', 'darkred'),
    ('cyan', 'teal'),
    ('olive', 'darkolivegreen'),
    ('purple', 'indigo'),
    ('yellow', 'gold'),
    ('blue', 'darkblue'),
    ('orange', 'darkorange'),
    ('navy', 'midnightblue')
]

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
dataUserCa = {}
dataUserIt = {}
dataUserEs = {}
dataReplyCa = {}
dataReplyIt = {}
dataReplyEs = {}

with open(f'../json/ca-gender.json') as f:
    dataUserCa = json.load(f)
with open(f'../json/it-user.json') as f:
    dataUserIt = json.load(f)
with open(f'../json/es-user.json') as f:
    dataUserEs = json.load(f)

with open(f'../json/ca-reply.json') as f:
    dataReplyCa = json.load(f)
with open(f'../json/it-reply.json') as f:
    dataReplyIt = json.load(f)
with open(f'../json/es-reply.json') as f:
    dataReplyEs = json.load(f)

users = [ (dataUserEs, "Spanish"), (dataUserIt, "Italian"), (dataUserCa, "Catalan")]
reply = [ (dataReplyEs, "Spanish"), (dataReplyIt, "Italian"), (dataReplyCa, "Catalan")]

print("All loaded")

# %% genders
ax = plt.subplot(111)
x = [ name[e] for e in ems ]
xAx = np.arange(len(x))

fig, axs = plt.subplots(1, 3, figsize=(17,4))
fig.suptitle("Percentage of emotions by user gender for different emotions.")
plt.setp(axs, xticks=xAx, xticklabels=x)

for i, data in  enumerate(reply):

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

for i, data in  enumerate(users):

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

# %% over time
def plotLinesAndBars(
    ax,
    lines,
    bars: List[float],
    emotions: List[int]
):

    x = list(range(0, max(len(line) for line in lines)))
    for line, e in zip(lines, ems):
        ax.plot(x, line, 'k-', label=name[e], color=emotionColor[e][0])
    ax.legend()

    axTwin = ax.twinx()
    ax.patch.set_visible(False)
    axTwin.patch.set_visible(True)
    ax.set_zorder(axTwin.get_zorder() + 1)
    axTwin.bar(x, bars, 0.5, color='gainsboro', label='Volumes' )
    axTwin.set_ylim(0, max(bars) / 1)
    axTwin.set_ylabel('Number of actions')

    # plt.gcf().autofmt_xdate()
    # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    # plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    # plt.savefig('../charts/userem.png', bbox_inches='tight')


def plottaLang(ax, lang, dataset, xField):
    lines = [ np.array([ x['mean'][e] for x in dataset['all'][xField][:150] ]) for e in ems ]
    lines = [ (line - np.mean(line)) / np.var(line) for line in lines ]
    bars = [ x['n'] for x in dataset['all'][xField][:150] ]

    ax.title.set_text(lang)
    ax.get_yaxis().set_visible(False)
    plotLinesAndBars(ax, lines, bars, ems)


def plot4(reply: bool, xField, title):
    f = plt.figure(figsize=(15, 7))
    fig, axs = plt.subplots(2, 2, figsize=(20,10))
    plottaLang(axs[0][0], 'English', dataReplyEs if reply else dataUserEs, xField)
    plottaLang(axs[0][1], 'Spanish', dataReplyEs if reply else dataUserEs, xField)
    plottaLang(axs[1][0], 'Italian', dataReplyIt if reply else dataUserIt, xField)
    plottaLang(axs[1][1], 'Catalan', dataReplyCa if reply else dataUserCa, xField)
    fig.suptitle(title)
    plt.show()

# %% users emotion
# plot4(False, 'monthStart', 'User emotion written monthStart')
plot4(False, 'monthEnd', 'User emotion written monthEnd')

# plot4(True, 'monthStart', 'User emotion recived monthStart')
# plot4(True, 'monthEnd', 'User emotion recived monthEnd')


# %% shihs
# %% shihs
# def plotta(dataLines: Dict[str, Dict[str, Any]], emotionsToPlot: List[str], vols: Dict[str, Any], useLifeMonth:bool = True):

#     f = plt.figure(figsize=(40, len(data) * 10))
#     for i, em in enumerate(emotionsToPlot):
#         ax = f.add_subplot(len(ems), 1, i + 1)
#         ax.title.set_text(em)

#         emIndex = emotionNumber[em]

#         for lineName in dataLines:
#             ys = []
#             if useLifeMonth:
#                 ys = [dataLines[lineName]["lifeMonths"][m] for m in lifeMonths]
#             else:
#                 ys = [dataLines[lineName]["months"][m.strftime('%Y-%m')] for m in months]
#             ax.plot(
#                 months[:-10],
#                 list(map(lambda m: m[emIndex], ys))[:-10],
#                 'k-', color=linecolor[lineName][0], label=lineName
#             )

#         axTwin = plt.twinx()
#         ax.patch.set_visible(False)
#         axTwin.patch.set_visible(True)
#         ax.set_zorder(axTwin.get_zorder() + 1)
#         barYs = []
#         if useLifeMonth:
#             barYs = [vols["lifeMonths"][m] for m in lifeMonths]
#         else:
#             barYs = [vols["months"][m.strftime('%Y-%m')] for m in months]
#         barYs = list(map(lambda m: m[emIndex], barYs))
#         axTwin.bar(
#             cast(List, months)[:-10],
#             barYs[:-10],
#             15, color='gainsboro', label='Volumes'
#         )
#         axTwin.set_ylim(0, max(barYs) / 1)
#         axTwin.set_ylabel('Volumes')

#     plt.gcf().autofmt_xdate()
#     plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
#     plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=6))
#     # plt.show()
#     plt.savefig('../charts/userem.png', bbox_inches='tight')
#     plt.close()

# %%
