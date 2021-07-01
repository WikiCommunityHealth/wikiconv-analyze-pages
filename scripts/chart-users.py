# %% init
from typing import Any, Dict, List, Tuple, cast
import json
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import datetime as dt
months = [dt.datetime.strptime(f"{y}-{str(m).zfill(2)}", '%Y-%m').date() for y in range(2000, 2021) for m in  range(1, 13)]
lifeMonths = list(map(lambda x: str(x), range(0, ((2021 - 2000) * 12))))
emToPlot = ["positive", "negative", "anger", "fear", "joy", "sadness"]

emotionColor: Dict[str, Tuple[str, str]] = {
    "global": ('black', 'black'),
    "positive": ('green', 'darkgreen'),
    "negative": ('gray', 'dimgray'),
    "anger": ('red', 'darkred'),
    "anticipation": ('cyan', 'teal'),
    "disgust": ('olive', 'darkolivegreen'),
    "fear": ('navy', 'midnightblue'),
    "joy": ('yellow', 'gold'),
    "sadness": ('blue', 'darkblue'),
    "surprise": ('orange', 'darkorange'),
    "trust": ('purple', 'indigo')
}
linecolor: Dict[str, Tuple[str, str]] = {
    "unknown": ('black', 'grey'),
    "female": ('red', 'darkred'),
    "male": ('cyan', 'teal'),
    "users": ('black', 'grey'),
    "autoconfirmed": ('red', 'darkred'),
    "confirmed": ('cyan', 'teal'),
}
emotionName: Dict[int, str] = {
    0: "global",
    1: "positive",
    2: "negative",
    3: "anger",
    4: "anticipation",
    5: "disgust",
    6: "fear",
    7: "joy",
    8: "sadness",
    9: "surprise",
    10: "trust",
}

emotionNumber: Dict[str, int] = {
    "global": 0,
    "positive": 1,
    "negative": 2,
    "anger": 3,
    "anticipation": 4,
    "disgust": 5,
    "fear": 6,
    "joy": 7,
    "sadness": 8,
    "surprise": 9,
    "trust": 10,
}

# %% load data
lang = 'it'
with open(f'../assets/user-emotions/{lang}.json') as f:
    data = json.load(f)
normalizedData = data["normalized"]
assData = data["assolute"]
print("File loaded")

# %% plot fn
def plotta(dataLines: Dict[str, Dict[str, Any]], emotionsToPlot: List[str], vols: Dict[str, Any], useLifeMonth:bool = True):

    f = plt.figure(figsize=(40, len(data) * 10))
    for i, em in enumerate(emotionsToPlot):
        ax = f.add_subplot(len(emToPlot), 1, i + 1)
        ax.title.set_text(em)

        emIndex = emotionNumber[em]

        for lineName in dataLines:
            ys = []
            if useLifeMonth:
                ys = [dataLines[lineName]["lifeMonths"][m] for m in lifeMonths]
            else:
                ys = [dataLines[lineName]["months"][m.strftime('%Y-%m')] for m in months]
            ax.plot(
                months[:-10],
                list(map(lambda m: m[emIndex], ys))[:-10],
                'k-', color=linecolor[lineName][0], label=lineName
            )

        axTwin = plt.twinx()
        ax.patch.set_visible(False)
        axTwin.patch.set_visible(True)
        ax.set_zorder(axTwin.get_zorder() + 1)
        barYs = []
        if useLifeMonth:
            barYs = [vols["lifeMonths"][m] for m in lifeMonths]
        else:
            barYs = [vols["months"][m.strftime('%Y-%m')] for m in months]
        barYs = list(map(lambda m: m[emIndex], barYs))
        axTwin.bar(
            cast(List, months)[:-10],
            barYs[:-10],
            15, color='gainsboro', label='Volumes'
        )
        axTwin.set_ylim(0, max(barYs) / 1)
        axTwin.set_ylabel('Volumes')

    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    # plt.show()
    plt.savefig('../charts/userem.png', bbox_inches='tight')
    plt.close()

# %% gender
dataLines = {
    "male": normalizedData['genders']['male'],
    "female": normalizedData['genders']['female'],
    "unknown": normalizedData['genders']['unknown'],
}
plotta(dataLines, emToPlot, assData['all'])

# %% roles
dataLines = {
    "users": normalizedData['roles']['*'],
    "autoconfirmed": normalizedData['roles']['autoconfirmed\n'],
    "confirmed": normalizedData['roles']['confirmed'],
}
plotta(dataLines, emToPlot, assData['all'])
# %%
