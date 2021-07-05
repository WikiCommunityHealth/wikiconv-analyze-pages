# %% imports and const
from typing import Any, Dict, List, Tuple, Union, cast
import json
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt

# %% shish
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
    "Negative",
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


months = []
for y in range(2000, 2021):
    for m in range(1, 13):
        months.append(f"{y}-{m:02d}")

months = [dt.datetime.strptime(month, '%Y-%m').date() for month in months]

# %% import data
dataUserCa = {}
dataUserIt = {}
dataUserEs = {}
dataUserEn = {}
dataReplyCa = {}
dataReplyIt = {}
dataReplyEs = {}
dataReplyEn = {}

with open(f'../json/ca-user.json') as f:
    dataUserCa = json.load(f)
with open(f'../json/it-user.json') as f:
    dataUserIt = json.load(f)
with open(f'../json/es-user.json') as f:
    dataUserEs = json.load(f)
with open(f'../json/en-user.json') as f:
    dataUserEn = json.load(f)

with open(f'../json/ca-reply.json') as f:
    dataReplyCa = json.load(f)
with open(f'../json/it-reply.json') as f:
    dataReplyIt = json.load(f)
with open(f'../json/es-reply.json') as f:
    dataReplyEs = json.load(f)
with open(f'../json/en-reply.json') as f:
    dataReplyEn = json.load(f)

users = [ (dataUserEn, "English"), (dataUserEs, "Spanish"), (dataUserIt, "Italian"), (dataUserCa, "Catalan")]
reply = [ (dataReplyEn, "English"), (dataReplyEs, "Spanish"), (dataReplyIt, "Italian"), (dataReplyCa, "Catalan")]

print("All loaded")

# %% genders
ax = plt.subplot(111)
x = [ name[e] for e in ems ]
xAx = np.arange(len(x))

fig, axs = plt.subplots(1, 4, figsize=(17,4))
# fig.suptitle("Percentage of emotions by user gender for different emotions.")
plt.setp(axs, xticks=xAx, xticklabels=x)

for i, data in  enumerate(users):

    unknown = [ data[0]["all"]["all"]["mean"][e] for e in ems ]
    male = [ data[0]["male"]["all"]["mean"][e] for e in ems ]
    female = [ data[0]["female"]["all"]["mean"][e] for e in ems ]

    axs[i].set(xlabel=data[1], ylabel='Percentage of emotions')
    axs[i].bar(xAx - 0.3, unknown, 0.3, label = 'All', color=['tab:gray'], hatch="//", edgecolor='black')
    axs[i].bar(xAx, female, 0.3, label = 'Female', color=['tab:red'], hatch="xx", edgecolor='black')
    axs[i].bar(xAx + 0.3, male, 0.3, label = 'Male', color=['tab:blue'], hatch="++", edgecolor='black')

for ax in axs.flat:
    ax.label_outer()
plt.legend()
# plt.show()
plt.tight_layout()
fig.savefig("emgender.jpg")


# %% roles
fig, axs = plt.subplots(1, 4, figsize=(17,4))
# fig.suptitle("Percentage of emotions by user gender for different emotions.")
plt.setp(axs, xticks=xAx, xticklabels=x)

for i, data in  enumerate(users):

    unknown = [ data[0]["all"]["all"]["mean"][e] for e in ems ]
    male = [ data[0]["autopatrolled"]["all"]["mean"][e] for e in ems ]
    female = [ data[0]["sysop"]["all"]["mean"][e] for e in ems ]

    axs[i].set(xlabel=data[1], ylabel='Percentage of emotions')
    axs[i].bar(xAx - 0.3, unknown, 0.3, label = 'All', hatch="//", edgecolor='black')
    axs[i].bar(xAx, female, 0.3, label = 'Autop Patrolled', hatch="xx", edgecolor='black')
    axs[i].bar(xAx + 0.3, male, 0.3, label = 'Admins', hatch="++", edgecolor='black')

for ax in axs.flat:
    ax.label_outer()
plt.legend()
# plt.show()
plt.tight_layout()
fig.savefig("emroles.jpg")

# %% over time
def plotLinesAndBars(
    ax,
    lines,
    bars: List[float],
    hideLabel = False,
    emotions = ems
):
    x = list(range(0, max(len(line) for line in lines)))
    for line, e in zip(lines, emotions):
        ax.plot(x, line, 'k-', label=name[e], color=emotionColor[e][0])
    ax.legend(loc='upper center')
    ax.set_xlabel('Month from first activity')

    axTwin = ax.twinx()
    ax.patch.set_visible(False)
    axTwin.patch.set_visible(True)
    ax.set_zorder(axTwin.get_zorder() + 1)
    axTwin.bar(x, bars, 0.5, color='gainsboro', label='Volumes' )
    axTwin.set_ylim(0, max(bars) / 1)
    if not hideLabel:
        axTwin.set_ylabel('Number of active users')

    # plt.gcf().autofmt_xdate()
    # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    # plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    # plt.savefig('../charts/userem.png', bbox_inches='tight')


def plottaLang(ax, title, dataset, xField, role='all', hideLabel = False):
    lines = [ np.array([ x['mean'][e] for x in dataset[role][xField][:150] ]) for e in ems ]
    lines = [ (line - np.mean(line)) / np.var(line) for line in lines ]
    bars = [ x['n'] for x in dataset[role][xField][:150] ]

    ax.title.set_text(title)
    ax.get_yaxis().set_visible(False)
    plotLinesAndBars(ax, lines, bars, hideLabel)

def gender(reply: bool, xField, title, file='gtime.jpg'):
    f = plt.figure(figsize=(15, 7))
    fig, axs = plt.subplots(1, 3, figsize=(15,4))
    dataset = dataReplyEs if reply else dataUserEs

    for i, e in enumerate([POSITIVE, NEGATIVE, SADNESS]):
        l1 = np.array([ x['mean'][e] for x in dataset['all'][xField][1:150] ])
        axs[i].plot(
            range(1, 150),
            (l1 - np.mean(l1)) / np.var(l1), '-.',
            label='All', color='black'
        )
        l1 = np.array([ x['mean'][e] for x in dataset['female'][xField][1:150] ])
        axs[i].plot(
            range(1, 150),
            (l1 - np.mean(l1)) / np.var(l1),
            label='Female', color='tab:red'
        )
        l2 = np.array([ x['mean'][e] for x in dataset['male'][xField][1:150] ])
        axs[i].plot(
            range(1, 150),
            (l2 - np.mean(l2)) / np.var(l2), '--',
            label='Male', color='tab:blue'
        )
        axs[i].title.set_text(name[e])
        axs[i].legend()
        axs[i].set_xlabel('Months from first activity')
        axs[i].get_yaxis().set_visible(False)
    plt.tight_layout()
    plt.savefig(file)


def roles(reply: bool, xField, title, file='rtime.jpg'):
    f = plt.figure(figsize=(15, 7))
    fig, axs = plt.subplots(1, 2, figsize=(15,4))
    dataset = dataReplyEs if reply else dataUserEs

    for i, e in enumerate([POSITIVE, NEGATIVE]):
        l1 = np.array([ x['mean'][e] for x in dataset['all'][xField][1:140] ])
        axs[i].plot(
            range(1, 140),
            (l1 - np.mean(l1)) / np.var(l1), '-.',
            label='All'
        )
        l2 = np.array([ x['mean'][e] for x in dataset['autopatrolled'][xField][1:140] ])
        axs[i].plot(
            range(1, 140),
            (l2 - np.mean(l2)) / np.var(l2), '--',
            label='Auto Patrolled'
        )
        l1 = np.array([ x['mean'][e] for x in dataset['sysop'][xField][1:140] ])
        axs[i].plot(
            range(1, 140),
            (l1 - np.mean(l1)) / np.var(l1),
            label='Admin'
        )
        axs[i].title.set_text(name[e])
        axs[i].legend()


    # fig.suptitle(title)
    plt.tight_layout()
    plt.savefig(file)



def plot4(reply: bool, xField, title, name='unamed.jpg'):
    f = plt.figure(figsize=(15, 7))
    fig, axs = plt.subplots(2, 2, figsize=(15,8))
    d = dataReplyEn if reply else dataUserEn
    plottaLang(axs[0][0], 'English', d, xField, 'all', True)
    plottaLang(axs[0][1], 'Spanish', d, xField, 'all')
    plottaLang(axs[1][0], 'Italian', d, xField, 'all', True)
    plottaLang(axs[1][1], 'Catalan', d, xField, 'all')
    for ax in axs.flat:
        ax.label_outer()
    fig.suptitle(title)
    plt.tight_layout()
    plt.savefig(name)

# %% users emotion
# plot4(False, 'monthStart', 'Emotions expressed by users from their first action', 'mstartuser.jpg')
# plot4(True, 'monthStart', 'Emotions received by users from their first action', 'mstartreply.jpg')
plot4(False, 'month', 'User emotion written monthEnd')

# gender(False, 'monthStart', 'La locura')
# roles(False, 'monthStart', 'La locura')

# plot4(True, 'monthStart', 'User emotion recived monthStart')
# plot4(True, 'monthEnd', 'User emotion recived monthEnd')


# %% shihs
# %% emotions by all
fig, ax = plt.subplots(1, 2, figsize=(13,5), gridspec_kw={'width_ratios': [1, 2]})

for i, ee in enumerate([ems[:2], ems[2:]]):
    en = [ dataUserEn["all"]["all"]["mean"][e] for e in ee ]
    es = [ dataUserEs["all"]["all"]["mean"][e] for e in ee ]
    it = [ dataUserIt["all"]["all"]["mean"][e] for e in ee ]
    ca = [ dataUserCa["all"]["all"]["mean"][e] for e in ee ]

    xAx = np.arange(len(ee))
    ax[i].title.set_text('Sentiments' if i == 0 else 'Emotions')
    plt.setp(ax[i], xticks=xAx, xticklabels=[ name[e] for e in ee])
    ax[i].bar(xAx - 0.3, en, 0.2, label = 'English', color=['tab:blue'], hatch="x", edgecolor='black')
    ax[i].bar(xAx - 0.1, es, 0.2, label = 'Spanish', color=['tab:orange'], hatch="+", edgecolor='black')
    ax[i].bar(xAx + 0.1, it, 0.2, label = 'Italian', color=['tab:green'], hatch="/", edgecolor='black')
    ax[i].bar(xAx + 0.3, ca, 0.2, label = 'Catalan', color=['tab:red'], hatch="-", edgecolor='black')
    ax[i].set_ylabel('Percentage')
    if i == 0:
        ax[i].legend()

fig.savefig("emlang.jpg")


# %%
