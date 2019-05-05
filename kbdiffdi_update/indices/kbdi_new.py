import math
import datetime

import numpy as np

def load_csv(filename):
    """
    Parameters:
    ------------
    filename: str
        the full path and filename of the input csv
    """
    indata = np.loadtxt(filename, dtype=str, delimiter=",")
    datelist = []
    out_rainfall = indata[1:,2].astype(float)
    out_temp = indata[1:,3].astype(float)
    out_relhum = indata[1:,4].astype(float)
    out_wind = indata[1:,5].astype(float)
    for row in indata[1:]:
        datelist.append(datetime.datetime(year=int(row[1][:4]),month=int(row[1][4:6]),day=int(row[1][6:]))) # append the datetime ob
    out_wind = mpers_to_kmperh(out_wind)
    return datelist, out_rainfall, out_temp, out_relhum, out_wind

def mpers_to_kmperh(data):
    return data*3.6

def calculate_net_rainfall(prcp_data):
    threshold = 5.08 # 0.20 * 25.4 # convert inches to mm. NOTE: some literature uses 5 mm instead of 5.08

    net_rainfall = np.zeros((len(prcp_data)))
    running_total = 0
    already_subtracted = False
    
    n = 0 
    while n < len(prcp_data):

        # when encountering a day without rain, reset
        if prcp_data[n] == 0: 
            net_rainfall[n] = 0
            running_total = 0
            already_subtracted = False
        
        # today's rain is greater than zero, consecutive rainfall, and threshold was already subtracted
        elif already_subtracted == True: 
            net_rainfall[n] = prcp_data[n]
        
        # consecutive rainfall, threshold is met, and haven't subtracted yet
        elif running_total + prcp_data[n] > threshold: 
            net_rainfall[n] = running_total + prcp_data[n] - threshold
            already_subtracted = True

        # consecutive rainfall, threshold is not met, haven't subtracted yet
        else: 
            net_rainfall[n] = 0
            running_total += prcp_data[n]

        n+=1
    return net_rainfall


def calculate_ET(prev_KBDI, prev_temp, mean_annual_rainfall):
    """
    Calculates the ET based on equation 17 in appendix A from Keetch and Byram 1968.
    (The typographical error is accounted for)

    Parameters:
    ------------
    prev_KBDI: ndarray shape=(1,1,m,n)
        KBDI yesterday (in metric equivalents)
    dailyTemp: ndarray shape=(1,m,n)
        the daily temperature (in celsius)

    Returns:
    ---------
        ET: ndarray shape=(1,m,n)
            daily evapotranspiration
    """
    numerator = (203.2 - prev_KBDI) * (0.968 * np.exp(0.0875 * prev_temp + 1.5552) - 8.30)
    denominator = 1 + 10.88 * np.exp(-0.001736 * mean_annual_rainfall)
    ET = 0.001 * (numerator / denominator)
    return ET

def calculate_KBDI(temp, mean_annual_rainfall, net_rainfall, first_kbdi):
    kb_cube = np.zeros((len(temp)))

    prev_kbdi = first_kbdi

    n = 0
    while n < len(temp):
        # today's ET requires yesterday's KBDI, yesterday's temp, and mean annual rainfall. 
        ET = calculate_ET(prev_kbdi, temp[n], mean_annual_rainfall) 
        # KBDI for today is calculated based on yesterday's KBDI, ET, and yesterday's effective prcp (net rainfall)  
        KBDI = prev_kbdi + ET - net_rainfall[n]  # output is a 2d array
        if KBDI < 0: # KBDI values can't be negative
            KBDI = 0
        
        kb_cube[n] = KBDI # set kb_cube to today's KBDI, this then becomes yesterday's KBDI at the next iteration 
        prev_kbdi = KBDI # prev_KBDI.set_data(KBDI)
        n+=1
    return kb_cube

def calculate_mean_annual(data, datetimes):
    yearly_total = 0
    yearly_sums = []
    n = 0
    cur_year = datetimes[n].year
    while n < len(datetimes):
        if datetimes[n].year != cur_year:
            yearly_sums.append(yearly_total)
            
            cur_year = datetimes[n].year
            yearly_total = data[n]
        else:
            yearly_total += data[n]
        n+=1
    # include the last year, only if it is a full year
    if datetimes[n-1].month == 12 and dates[n-1].day == 31: 
        yearly_sums.append(yearly_total)
    annual_mean = np.mean(yearly_sums)
    return annual_mean