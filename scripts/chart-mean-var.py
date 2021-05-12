# %% load
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

em: List[str] = [
    "anger",
    "anticipation",
    "disgust",
    "fear",
    "joy",
    "negative",
    "positive",
    "sadness",
    "surprise",
    "trust",
]
showAll: List[Union[str, None]] = cast(List[Union[str, None]], [None]) + cast(List[Union[str, None]], em)

with open('../out.json') as f:
    data = json.load(f)['months']
print("File loaded")


# %% load fn
def plotta( months,
            ys: Dict[str, np.ndarray],
            varss: Union[Dict[str, np.ndarray], None] = None,
            vol: Union[Dict[str, np.ndarray], None] = None,
            showOnly: List[Union[str, None]] = [None]
        ):
    f = plt.figure(figsize=(100, len(showOnly) * 15))

    for i, emotion in enumerate(showOnly):
        ax = f.add_subplot(len(showOnly), 1, i + 1)
        ax.title.set_text(emotion if emotion is not None else 'All')

        for e in ys:
            if emotion is None or emotion == e:
                ax.plot(months, ys[e], 'k-', color=emotionColor[e][0], label=e)
                if varss is not None and e != 'global' and emotion is not None:
                    ax.fill_between(months, ys[e]-varss[e], ys[e]+varss[e], color=emotionColor[e][1])
        ax.legend()

        if vol is not None:
            axTwin = plt.twinx()
            ax.patch.set_visible(False)
            axTwin.patch.set_visible(True)
            ax.set_zorder(axTwin.get_zorder() + 1)

            if emotion is None:
                axTwin.bar(months, vol['global'], 15, color='gainsboro', label='Volumes')
            else:
                axTwin.bar(months, vol['global'] - vol[emotion], 15, color='gainsboro', label='Volumes')
                axTwin.bar(months, vol[emotion], 15, color=emotionColor[emotion][0], label='Specific')
            axTwin.set_ylim(0, max(vol['global']) / 40)
            axTwin.set_ylabel('Volumes')

    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.show()
    # plt.savefig(f'pippo.jpeg')
    plt.close()
print("Fn loaded")



# %% calculate stuff
months = [dt.datetime.strptime(month, '%Y-%m').date() for month in data]
disturbo = np.array([((x - (len(months) / 2)) / (len(months) / 2))**2 for x in range(0, len(months))])
ys: Dict[str, np.ndarray] = {}
varss: Dict[str, np.ndarray] = {}
vol: Dict[str, np.ndarray] = {}
means: Dict[str, np.number] = {}
standardScore: Dict[str, np.ndarray] = {}
meanOverVar: Dict[str, np.ndarray] = {}
for e in em:
    ys[e] = np.array([data[month][e]['mean'] for month in data])
    varss[e] = (np.array([data[month][e]['var'] for month in data]) / 2)
    vol[e] = np.array([data[month][e]['len'] for month in data])
    means[e] = np.mean(ys[e])
    standardScore[e] = (ys[e] - means[e]) / np.var(ys[e])
    meanOverVar[e] = np.divide(ys[e], varss[e], out=np.zeros_like(ys[e]), where=varss[e]!=0)

vol['global'] = np.array([ sum([data[month][e]['len'] for e in data[month]]) for month in data])
means['global'] = np.mean([means[m] for m in means])

def trimArr(a):
    return a[102:-8]
def trimArrDict(d):
    for e in d:
        d[e] = d[e][102:-8]
# Trim
if True:
    months = trimArr(months)
    trimArrDict(ys)
    trimArrDict(varss)
    trimArrDict(vol)
    trimArrDict(standardScore)
    trimArrDict(meanOverVar)
    # trimArrDict(distanzaDallaMedia)
    # trimArrDict(toPlotMeans)
    # mediaDistanzaDallaMedia = trimArr(mediaDistanzaDallaMedia)
print("Done")

# %% basic charts
print("Raw data")
plotta(months, ys, varss, vol=vol, showOnly=showAll)
# plotta(months, meanOverVar, vol=vol, showOnly=showAll)
# plotta(months, meanOverVar, vol=vol, showOnly=showAll)
print("Std score")
# plotta(months, standardScore, vol=vol)


# %% Means lines to plot
toPlotMeans: Dict[str, np.ndarray] = {}
for e in means:
    toPlotMeans[e] = np.array([means[e]] * len(months))
print("Medie")
plotta(months, toPlotMeans)

# %% Distance from avg line
distanzaDallaMedia: Dict[str, np.ndarray] = {}
for e in em:
    distanzaDallaMedia[e] = ys[e] - means[e]
# Avg distance from avg line
mediaDistanzaDallaMedia = []
for i in range(0, len(months)):
    mediaDistanzaDallaMedia.append(np.mean([distanzaDallaMedia[e][i] for e in distanzaDallaMedia]))
distanzaDallaMedia['global'] = np.array(mediaDistanzaDallaMedia)

print("Distanza dalla media")
plotta(months, distanzaDallaMedia)


# %% res
ilRisultato: Dict[str, np.ndarray] = {}
for e in em:
    ilRisultato[e] = distanzaDallaMedia[e] - mediaDistanzaDallaMedia
ilRisultato['global'] = np.array(mediaDistanzaDallaMedia)
print("Res")
plotta(months, ilRisultato, varss, vol=vol, showOnly=showAll)

# %% red std score
resStdScore: Dict[str, np.ndarray] = {}
for e in em:
    resStdScore[e] = (ilRisultato[e] - np.mean(ilRisultato[e])) / np.var(ilRisultato[e])
plotta(months, resStdScore, vol=vol)

# %%
