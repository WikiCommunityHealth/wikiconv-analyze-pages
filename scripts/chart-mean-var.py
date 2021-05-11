# %% load
from typing import Any, Callable, Dict, Generator, Iterable, Mapping, List, Tuple, Union, cast
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



# %% base
months = [dt.datetime.strptime(month, '%Y-%m').date() for month in data]
disturbo = np.array([((x - (len(months) / 2)) / (len(months) / 2))**2 for x in range(0, len(months))])
ys: Dict[str, np.ndarray] = {}
varss: Dict[str, np.ndarray] = {}
vol: Dict[str, np.ndarray] = {}
for e in em:
    ys[e] = np.array([data[month][e]['mean'] for month in data])
    varss[e] = (np.array([data[month][e]['var'] for month in data]) / 2)
    vol[e] = np.array([data[month][e]['len'] for month in data])
vol['global'] = np.array([ sum([data[month][e]['len'] for e in data[month]]) for month in data])

# Trim
if True:
    months = months[102:-8]
    for e in ys:
        ys[e] = ys[e][102:-8]
    for e in varss:
        varss[e] = varss[e][102:-8]
    for e in vol:
        vol[e] = vol[e][102:-8]
# plotta(months, ys, vol=vol, showOnly='anger')
print("Done")


# %% mean
means: Dict[str, np.number] = {}
for e in em:
    means[e] = np.mean(ys[e])
globalMean = np.mean([means[m] for m in means])
means['global'] = globalMean
# plt.figure(figsize=(100,10))
# plt.plot(months, mean)
# plt.show()
# plt.close()
toPlotMeans: Dict[str, np.ndarray] = {}
for e in means:
    toPlotMeans[e] = np.array([means[e]] * len(months))
# print("Medie")
# plotta(months, toPlotMeans)

distanzaDallaMedia: Dict[str, np.ndarray] = {}
for e in em:
    distanzaDallaMedia[e] = ys[e] - means[e]

mediaDistanzaDallaMedia = []
for i in range(0, len(months)):
    mediaDistanzaDallaMedia.append(np.mean([distanzaDallaMedia[e][i] for e in distanzaDallaMedia]))
distanzaDallaMedia['global'] = np.array(mediaDistanzaDallaMedia)
# print("Distanza dalla media")
# plotta(months, distanzaDallaMedia)
# plotta(months, ys)

print("Res")
ilRisultato = {}
for e in em:
    ilRisultato[e] = distanzaDallaMedia[e] - mediaDistanzaDallaMedia
ilRisultato['global'] = mediaDistanzaDallaMedia

plotta(months, ilRisultato, varss, vol=vol, showOnly=[None] + em)
print("Done")

# %%
