import os
import csv
import datetime

import numpy as np
# from osgeo import gdal
# from osgeo import ogr
# from osgeo import osr

from kbdiffdi.utilities import conversion
from kbdiffdi.features import feature

def load_csv(filename):
    """
    Parameters:
    ------------
    filename: str
        the full path and filename of the input csv

    Returns:
    --------
    rain: KBDI_FFDI.feature.RasterStack
        daily precipitation data in millimeters
    temp: KBDI_FFDI.feature.RasterStack
        daily temperature data in celsius
    relhum: KBDI_FFDI.feature.RasterStack
        daily relative humidity data in percent
    wind: KBDI_FFDI.feature.RasterStack
        daily wind speed data in kilometers per hour:
        NOTE: it expects to read wind data in meters per second from the
          input csv. The wind values are converted to kilometers per hour
    """
    indata = np.loadtxt(filename, dtype=str, delimiter=",")
    datelist = []
    out_rainfall = indata[1:,2].astype(float).reshape(-1,1,1,1)
    out_temp = indata[1:,3].astype(float).reshape(-1,1,1,1)
    out_rel_hum = indata[1:,4].astype(float).reshape(-1,1,1,1)
    out_wind = indata[1:,5].astype(float).reshape(-1,1,1,1)
    for row in indata[1:]:
        datelist.append(datetime.datetime(year=int(row[1][:4]),month=int(row[1][4:6]),day=int(row[1][6:]))) # append the datetime ob
    # create the featureStacks
    rain = feature.RasterStack()
    rain.create_sc_stack(out_rainfall, datelist, None, "standard", 0, 0, 1, -1)
    temp = feature.RasterStack()
    temp.create_sc_stack(out_temp, datelist, None, "standard", 0, 0, 1, -1)
    relhum = feature.RasterStack()
    relhum.create_sc_stack(out_rel_hum, datelist, None, "standard", 0, 0, 1, -1)
    wind = feature.RasterStack()
    wind.create_sc_stack(out_wind, datelist, None, "standard", 0, 0, 1, -1)
    conversion.mpers_to_kmperh(wind)
    return rain, temp, relhum, wind

def write_kbdi(inputfilename, outputfilename, KBDIobject):
    kbdi = KBDIobject.data.flatten()
    with open(inputfilename, "r") as inputcsv:
        with open(outputfilename, "w", newline="") as outputcsv:
            reader = csv.reader(inputcsv, delimiter=",")
            writer = csv.writer(outputcsv, delimiter=",")
            index = 0
            firstRow = True
            for row in reader:
                if firstRow:
                    firstRow = False
                    row.extend(["KBDI"])
                else:
                    row.extend([kbdi[index]])
                    index+=1
                writer.writerow(row)

def write_csv(inputfilename, outputfilename, KBDIobject=None, FFDIobject=None, DFobject=None):
    if KBDIobject:
        kbdi = KBDIobject.data.flatten()
    if FFDIobject:
        ffdi = FFDIobject.data.flatten()
    if DFobject:
        df = DFobject.data.flatten()
    with open(inputfilename, "r") as inputcsv:
        with open(outputfilename, "w", newline="") as outputcsv:
            reader = csv.reader(inputcsv, delimiter=",")
            writer = csv.writer(outputcsv, delimiter=",")
            index = 0
            firstRow = True
            for row in reader:
                if firstRow:
                    firstRow = False
                    row.extend(["KBDI", "DF", "FFDI"])
                else:
                    row.extend([kbdi[index],df[index],ffdi[index]])
                    index+=1
                writer.writerow(row)
                    