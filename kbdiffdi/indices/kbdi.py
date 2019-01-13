import copy
import math
import datetime

import numpy as np

from kbdiffdi.features import feature

class KBDI(object):
    
    def __init__(self):        
        # main data
        self.temp = None # a feature.RasterCube or feature.Vector (data is a 3d array)
        self.prcp = None # a feature.RasterCube or feature.Vector (data is a 3d array)
        
        # first values for initializing the KBDI calculation
        self.first_KBDI = None # 2d array of data
        
        # additional data that is calculated further down the pipeline
        self.net_rainfall = None # 2d array (raster)
        self.mean_annual_rainfall = None # a 2d array (raster)


    def set_temp(self, newtemp):
        self.temp = newtemp

    def set_prcp(self, newprcp):
        self.prcp = newprcp

    def set_first_drought_index(self, newfirstdroughtindex):
        # initialize first drought index to match the shape of the input data
        # its date is the day before the date of the first actual value in the dataset
        d_index = feature.RasterStack()
        d_index.create_sc_stack(newfirstdroughtindex,
                                           [self.temp.datelist[0] - datetime.timedelta(days=1)],
                                           None,
                                           "standard",
                                           0,
                                           0,
                                           1,
                                           -1)
        self.first_KBDI = d_index

    def get_first_KBDI(self):
        return self.first_KBDI

    def set_mean_annual_rainfall(self, amount):
        self.mean_annual_rainfall = amount

    def get_mean_annual_rainfall(self):
        return self.mean_annual_rainfall

    def fit(self, inittemp, initprcp, initmeanannualrainfall=None, initdroughtindex=np.array([[[[0]]]])):
        self.set_temp(inittemp)
        self.set_prcp(initprcp)
        self.set_first_drought_index(initdroughtindex)
        self.set_mean_annual_rainfall(initmeanannualrainfall)
        return self.calculate_KBDI()

    def cut_first_slice(self): # cut the first slice of the temp and prcp data. Only initialize with the 1st KBDI
        self.temp.setdata(self.temp.data[1:])
        self.temp.datelist = self.temp.datelist[1:]
        self.prcp.setdata(self.prcp.data[1:])
        self.prcp.datelist = self.prcp.datelist[1:]
    

    def calculate_net_rainfall(self):
        threshold = 5.08 # 0.20 * 25.4 # convert inches to mm. NOTE: some literature uses 5 mm instead of 5.08

        #out = Bob.STCube(self.prcp.y,self.prcp.x,self.prcp.h,self.prcp.w,self.prcp.s,self.prcp.d)
        net_rainfall = np.zeros(shape=(len(self.prcp.data), len(self.prcp.data[0]), len(self.prcp.data[0][0]), len(self.prcp.data[0][0][0]))) # netRainfall

        #variables for the calculation
        daily_prcp = self.prcp.data # the precipitation data
        running_total = np.zeros(shape=(1, len(self.prcp.data[0]), len(self.prcp.data[0][0]))) # a running total for continuous rain days
        consec = np.zeros(shape=(len(self.prcp.data[0]), len(self.prcp.data[0][0])), dtype=bool) # which cells see consecutive rainfall?
        already_subtracted = np.zeros(shape=(len(self.prcp.data[0]), len(self.prcp.data[0][0])), dtype=bool) # has the 0.20 threshold been met and 0.20 subtracted?

        n=0
        while n < len(daily_prcp):
            running_total += daily_prcp[n]
            # if dailyPrcp[n] == 0: 
            net_rainfall[n] = np.where(daily_prcp[n] == 0, 0, net_rainfall[n])
            running_total = np.where(daily_prcp[n] == 0, 0, running_total)
            already_subtracted = np.where(daily_prcp[n] == 0, False, already_subtracted)

            if n > 0:
                # if dailyPrcp[n] > 0 and dailyPrcp[n-1] > 0
                consec = np.where((daily_prcp[n] > 0) & (daily_prcp[n-1] > 0), True, False)

            #if dailyPrcp[n] > 0 and consec and alreadySubtracted:
            net_rainfall[n] = np.where((daily_prcp[n] > 0) & (consec == True) and (already_subtracted == True), daily_prcp[n], net_rainfall[n])
            running_total = np.where((daily_prcp[n] > 0) & (consec == True) and (already_subtracted == True), 0, running_total)

            #if dailyPrcp[n] > 0.20 and consec and not alreadySubtracted:
            net_rainfall[n] = np.where((daily_prcp[n] > threshold) & (consec == True) & (already_subtracted == False), running_total - threshold, net_rainfall[n])
            already_subtracted = np.where((daily_prcp[n] > threshold) & (consec == True) & (already_subtracted == False), True, already_subtracted)
            running_total = np.where((daily_prcp[n] > threshold) & (consec == True) & (already_subtracted == False), 0, running_total)

            # if dailyPrcp[n] > 0.20 and not consec:
            net_rainfall[n] = np.where((daily_prcp[n] > threshold) & (consec == False), daily_prcp[n] - threshold, net_rainfall[n])
            already_subtracted = np.where((daily_prcp[n] > threshold) & (consec == False), True, already_subtracted)
            running_total = np.where((daily_prcp[n] > threshold) & (consec == False), 0, running_total)

            # if dailyPrcp[n] < 0.20 and not consec:
            net_rainfall[n] = np.where((daily_prcp[n] < threshold) & (consec == False), 0, net_rainfall[n])

            #if dailyPrcp[n] < 0.20 and consec and runningTotal <= 0.20 and not alreadySubtracted:
            net_rainfall[n] = np.where((daily_prcp[n] < threshold) & (consec == True) & (running_total <= threshold) & (already_subtracted == False), 0, net_rainfall[n])

            #if dailyPrcp[n] < 0.20 and consec and runningTotal > 0.20:
            net_rainfall[n] = np.where((daily_prcp[n] < threshold) & (consec == True) & (running_total > threshold), running_total - threshold, net_rainfall[n])
            already_subtracted = np.where((daily_prcp[n] < threshold) & (consec == True) & (running_total > threshold), True, already_subtracted)
            running_total = np.where((daily_prcp[n] < threshold) & (consec == True) & (running_total > threshold), 0, running_total)
            n+=1
        net_rain = feature.RasterStack()
        net_rain.create_sc_stack(net_rainfall,
                                self.prcp.datelist,
                                None,
                                "standard",
                                0,
                                0,
                                1,
                                -1) 
        self.net_rainfall = net_rain
    

    def get_net_rainfall(self):
        return self.net_rainfall
    

    # calculate mean annual rainfall for each cell using the KBDI prcp STCube and set the meanAnnualRainfall Raster.
    def calculate_mean_annual_rainfall(self):
        """
        Calculates a mean annual rainfall value for each cell in the input data.
        It is assumed that the data is daily data without missing values and starts on January 1st.

        Parameters:
        -----------
        none

        Returns:
        ---------
        out: ndarray
            A 2d array holding a mean annual rainfall value for 
            every cell in the input prcp data
        """
        raindata = copy.deepcopy(self.prcp.data)
        dates = self.prcp.datelist
        running_total = 0
        yearly_sums = None
        n = 0
        cur_year = dates[n].year
        while n < len(dates):
            if dates[n].year != cur_year: # we've hit a new year. 1. store the running total in the yearlySums and restart the running total
                if yearly_sums is None:
                    yearly_sums = np.array([running_total])
                else:
                    yearly_sums = np.append(yearly_sums, [running_total], axis=0)
                cur_year = dates[n].year
                running_total = self.prcp.data[n]
            else:
                running_total += self.prcp.data[n]
            n+=1
        # make sure to include the last year of data. The while condition doesn't    
        if dates[n-1].month == 12 and dates[n-1] == 31: 
            yearly_sums = np.append(yearly_sums, [running_total], axis=0)
        annual_mean = np.mean(yearly_sums, axis=0)
        mean_rain = feature.Raster(np.array([annual_mean]),
                                    {0: 0},
                                   datetime.datetime(1976, 7, 4),
                                   None,
                                   "standard",
                                   "mean annual rainfall",
                                   0,
                                   0,
                                   1,
                                   -1)
        self.mean_annual_rainfall = mean_rain

    
    def calculate_ET(self, prev_KBDI, prev_temp):
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
        numerator = (203.2 - prev_KBDI.data) * (0.968 * np.exp(0.0875 * prev_temp + 1.5552) - 8.30)
        denominator = 1 + 10.88 * np.exp(-0.001736 * self.get_mean_annual_rainfall().data)
        ET = 0.001 * (numerator / denominator)
        return ET


    def calculate_KBDI(self):
        """
        prcp must be in mm
        temp must be in C
        
        Parameters:
        ------------
        initialDroughtIndex: float or int
            the initial value to set the first drought index
            
        Returns:
        ---------
        out: STCube
            data structure holding KBDI values
        """
        if self.mean_annual_rainfall is None: # set the mean annual rainfall if not set yet
            self.calculate_mean_annual_rainfall()
        #self.cutFirstSlice() # to clip the first layer from the temp and prcp data. 
        self.calculate_net_rainfall()  
        #netRainfall[0], temp[0], prcp[0]. netRainfall[0] is the first day, self.firstKBDI is yesterday's KBDI
        
        kb_cube = np.ones(shape=(len(self.temp.data), len(self.temp.data[0]), len(self.temp.data[0][0]), len(self.temp.data[0][0][0])))

        prev_KBDI = self.get_first_KBDI()
        
        n = 0
        while n < len(self.temp.data):
            # today's ET requires yesterday's KBDI, yesterday's temp, and mean annual rainfall. 
            ET = self.calculate_ET(prev_KBDI, self.temp.data[n]) 
            # KBDI for today is calculated based on yesterday's KBDI, ET, and yesterday's effective prcp (net rainfall)  
            KBDI = prev_KBDI.data + ET - self.net_rainfall.data[n]  # output is a 2d array
            KBDI = np.where(KBDI < 0, 0, KBDI) # KBDI values can't be negative
            kb_cube[n] = KBDI # set kb_cube to today's KBDI, this then becomes yesterday's KBDI at the next iteration 
            prev_KBDI.data = KBDI # prev_KBDI.set_data(KBDI)
            n+=1
        out_kbdi = feature.RasterStack()
        out_kbdi.create_sc_stack(kb_cube,
                                      self.temp.datelist,
                                      None,
                                      "standard",
                                      0,
                                      0,
                                      1,
                                      -1)
        return out_kbdi