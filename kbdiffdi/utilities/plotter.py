import datetime
import os

import numpy as np
import matplotlib.pyplot as plt

def timeseries(input_feature, start=None, end=None, save_fig_dir=None):
    if start is None:
        start = input_feature.datelist[0]
    if end is None or end == input_feature.datelist[-1]:
        y = input_feature.datelist[input_feature.datelist.index(start):]
        x = input_feature.data[input_feature.datelist.index(start):].flatten()
    else:
        y = input_feature.datelist[input_feature.datelist.index(start):input_feature.datelist.index(end)+1]
        x = input_feature.data[input_feature.datelist.index(start):input_feature.datelist.index(end)+1].flatten()
    plt.figure(figsize=(20, 8))
    plt.xlabel("Date")
    plt.grid(True)
    plt.plot(y, x)
    plt.show()


def map(input_feature, datetime, save_fig_dir=None):
    if isinstance(input_feature, feature.RasterCube) == False:
        print("error: must be a feature.RasterCube")