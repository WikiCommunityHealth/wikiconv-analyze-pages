# %%
import argparse
import re
import liwc
import datetime
import random
import numpy as np
from collections import Counter
from typing import Iterable, Mapping, List
import matplotlib.pyplot as plt


monthsCounters = {}


minPageLines = 100
emotion = ""

for year in range(2000, 2022):
    for month in range(1, 13):
        monthsCounters[f"{year}-{str(month).zfill(2)}"] = [0, Counter()]

heights = []
labels = []

for months in monthsCounters:
    [tot, conter] = monthsCounters[months]
    labels.append(months)
    heights.append(random.choice(range(1, 10)))

y_pos = range(len(labels))

f, ax = plt.subplots(figsize=(100,20)) # set the size that you'd like (width, height)
plt.bar(y_pos, heights)
plt.xticks(y_pos, labels, rotation=90)

plt.show()
# %%
