import copy
import math
import datetime

import numpy as np

from kbdiffdi.features import feature

np.warnings.filterwarnings('ignore')

class FFDI(object):
    
    def __init__(self):
        self.KBDI = None
        self.prcp = None
        self.temp =  None
        self.wind = None
        self.rel_hum = None
        
    
    def fit(self, initKBDI, initprcp, inittemp, initwind, initrelhum):
        self.KBDI = initKBDI
        self.prcp = initprcp
        self.temp = inittemp
        self.wind = initwind
        self.rel_hum = initrelhum

        x = self.calculate_sig_rain_event()
        x_lim = self.calc_x_lim()
        DF = self.griffith_drought_factor(x, x_lim)
        FFDI = self.forest_fire_danger_index(DF)
        return FFDI, DF


    def calculate_sig_rain_event(self):
        """
        See Finkele et al. 2006 and Lucas 2010 for a detailed explanation. Basically, in order to calculate
        the drought factor, a calculation of "significant rainfall events" during the past
        20 days needs to be calculated. A rainfall event is defined as a set of consecutive days
        each with rainfall above 2 mm. the rainfall event amount P (not be confused with daily precip)
        is the sum of the rainfall within the event. A rainfall event can be a single rain day.

        Event age N (not to be confused with days since last rain) is defined as the number of
        days since the day with the largest daily rainfall amount within the rain event.

        Precip data should be in millimeters
        """
        #daysagolist = []
        #rainsumlist = []
        n = 0
        window = 20 # to look at the past 20 days. (20 including the current day. So there will only be a 19 days ago max. today is zero days ago. there is a total of 20 days analyzed though)
        x_3d_arr = None
        while n < len(self.prcp.data):
            if n < window:
                prev_rain_cube = np.array(self.prcp.data[:n+1]) # use all available past data, because there hasn't been 20 days of data yet
            else:
                prev_rain_cube = np.array(self.prcp.data[n+1-window:n+1]) # to get the last 20 days # disgusting off by one... :(
            # now that there is a datastructure holding the previous 20 days of rain data,
            # iterate through the prevRainCube, and update the sigEvent data to hold
            # the relevant information for the significant rain event in the past 20 days
            prev_rain_cube = np.where(prev_rain_cube < 2, 0, prev_rain_cube) # rain events need to have more than 2 mm of precipitation
            days_ago = np.zeros(shape=(len(prev_rain_cube), len(prev_rain_cube[0]), len(prev_rain_cube[0][0]), len(prev_rain_cube[0][0][0])))
            rain_sum = np.zeros(shape=(len(prev_rain_cube), len(prev_rain_cube[0]), len(prev_rain_cube[0][0]), len(prev_rain_cube[0][0][0])))
            running_total = np.zeros(shape=(len(self.prcp.data[0][0]), len(self.prcp.data[0][0][0])))
            cur_max = np.zeros(shape=(len(self.prcp.data[0][0]), len(self.prcp.data[0][0][0])))
            cur_max_idx = np.zeros(shape=(len(self.prcp.data[0][0]), len(self.prcp.data[0][0][0])))
            for layer in range(len(prev_rain_cube)):
                running_total = running_total + prev_rain_cube[layer]
                rain_sum[layer] = np.where(prev_rain_cube[layer] == 0, 0, rain_sum[layer])
                days_ago[layer] = np.where(prev_rain_cube[layer] == 0, len(prev_rain_cube)-layer-1, days_ago[layer])

                # first day of 20
                if layer == 0 and layer != len(prev_rain_cube)-1:
                    # a consecutive event, start the tallying

                    running_total = np.where((prev_rain_cube[layer] != 0) & (prev_rain_cube[layer+1] != 0), prev_rain_cube[layer], running_total)
                    cur_max_idx = np.where((prev_rain_cube[layer] != 0) & (prev_rain_cube[layer+1] !=0), layer, cur_max_idx) 
                    cur_max = np.where((prev_rain_cube[layer] != 0) & (prev_rain_cube[layer+1] !=0), prev_rain_cube[layer], cur_max)

                    # a single rain event.

                    rain_sum[layer] = np.where((prev_rain_cube[layer] != 0) & (prev_rain_cube[layer+1] == 0), running_total, rain_sum[layer])
                    days_ago[layer] = np.where((prev_rain_cube[layer] != 0) & (prev_rain_cube[layer+1] == 0), len(prev_rain_cube)-layer-1, days_ago[layer])
                    running_total = np.where((prev_rain_cube[layer] != 0) & (prev_rain_cube[layer+1] == 0), 0, running_total)


                # day in the middle
                if layer > 0 and layer < len(prev_rain_cube)-1:
                    # a single rain day.

                    cur_max_idx = np.where((prev_rain_cube[layer] != 0) & (prev_rain_cube[layer+1] == 0) & (prev_rain_cube[layer] > cur_max), layer, cur_max_idx)
                    cur_max = np.where((prev_rain_cube[layer] != 0) & (prev_rain_cube[layer+1] == 0) & (prev_rain_cube[layer] > cur_max), prev_rain_cube[layer], cur_max)
                    rain_sum[layer] = np.where((prev_rain_cube[layer] != 0) & (prev_rain_cube[layer+1] == 0), running_total, rain_sum[layer])
                    days_ago[layer] = np.where((prev_rain_cube[layer] != 0) & (prev_rain_cube[layer+1] == 0), len(prev_rain_cube) - cur_max_idx-1,days_ago[layer])
                    running_total = np.where((prev_rain_cube[layer] != 0) & (prev_rain_cube[layer+1] == 0), 0, running_total)
                    cur_max = np.where((prev_rain_cube[layer] != 0) & (prev_rain_cube[layer+1] == 0), 0, cur_max)


                    # consecutive and ongoing

                    cur_max_idx = np.where((prev_rain_cube[layer] != 0) & (prev_rain_cube[layer+1] != 0) & (prev_rain_cube[layer] > cur_max), layer, cur_max_idx)
                    cur_max = np.where((prev_rain_cube[layer] != 0) & (prev_rain_cube[layer+1] != 0) & (prev_rain_cube[layer] > cur_max), prev_rain_cube[layer], cur_max)
                    rain_sum[layer] = np.where((prev_rain_cube[layer] != 0) & (prev_rain_cube[layer+1] != 0), np.nan, rain_sum[layer])
                    days_ago[layer] = np.where((prev_rain_cube[layer] != 0) & (prev_rain_cube[layer+1] != 0), np.nan, days_ago[layer])

                if layer == len(prev_rain_cube)-1:
                    cur_max_idx = np.where((prev_rain_cube[layer] != 0) & (prev_rain_cube[layer] > cur_max), layer, cur_max_idx)
                    cur_max = np.where((prev_rain_cube[layer] != 0) & (prev_rain_cube[layer] > cur_max), prev_rain_cube[layer], cur_max)
                    rain_sum[layer] = running_total
                    days_ago[layer] = np.where(prev_rain_cube[layer] != 0,len(prev_rain_cube)-cur_max_idx-1,days_ago[layer]) #np.ones(shape=(len(daysAgo[0]),len(daysAgo[0][0]))) * len(prevRainCube)-curMaxIdx-1

            #daysagolist.append(daysAgo)
            #rainsumlist.append(rainSum)
            x = self.calc_x(days_ago, rain_sum)
            if x_3d_arr is None:
                x_3d_arr = np.array([x])
            else:
                x_3d_arr = np.append(x_3d_arr, [x], axis=0)
            n+=1
        out = copy.deepcopy(self.prcp)
        out.data = x_3d_arr #out.set_data(x_3d_arr)
        return out


    def calc_x(self, N, P): # P is rain sum from the significant events method
        """
        This follows the process of calculating x values for finding the "most significant rain" event.
        See Holgate et al. (2017), and Finkele et al. (2006)
        """
        data = np.ones(shape=(len(N),len(N[0]),len(N[0][0]),len(N[0][0][0])))
        data = np.where((N >= 1) & (P > 2), np.power(N, 1.3) / (np.power(N, 1.3) + (P - 2)), data)
        data = np.where((N == 0) & (P > 2), np.power(0.8, 1.3) / (np.power(0.8, 1.3) + (P - 2)), data)
        data = np.where((P <= 2), 1, data)
        data = np.amin(data, axis=0) # now minimize x. These are the values that go in for x in griffith's drought factor equation
        return data

    def calc_x_lim(self):
        """
        "In operational use it was found that the above algorithm tended to increase the drought factor
        too quickly in prolonged dry periods following a significant rain event. This tendancy has been
        ameliorated in the Bureau's operational calculations, by substituting x with the minimum of
        the two quantities, namely the previously calculated x, and the limiting function Xlim" Finkele et al. 2006
        """
        out = np.where(self.KBDI.data < 20, 1 / (1 + 0.1135 * self.KBDI.data), 75 / (270.525 - 1.267 * self.KBDI.data))
        x_lim_arr = copy.deepcopy(self.KBDI)
        x_lim_arr.data = out #x_lim_arr.set_data(out)
        return x_lim_arr

    
    def griffith_drought_factor(self, x_arr, x_lim_arr):
        """
        This is equation 3 from Griffiths 1999. if calculates drought factor more accurately
        and closer to McArthurs original paper than Noble et al.'s equation.

        Parameters:
        -----------
        I : ndarry
            Keetch Byram Drought Index
        xArr: ndarray
            the resulting x values after minimizing the x function.
        xLimArr: ndarray
            the resulting x values from the x limiting function.
        """
        # so set x to an array that contains the minimum of the x value calculated using the x function
        # and the x value calculated using the x limiting function.
        x = np.where(x_arr.data < x_lim_arr.data, x_arr.data, x_lim_arr.data) 
        x_term = (41*x**2 + x) / (40*x**2 + x + 1)
        other_term = 10.5 * (1 - np.power(math.e, -(self.KBDI.data + 30) / 40.))
        full_term = other_term * x_term
        data = np.minimum(full_term, 10) # now because 10.5 from above allows for values above, take the minimum of the fullterm and 10. (values can't exceed 10)
        drought_factor = copy.deepcopy(self.KBDI)
        drought_factor.data = data #drought_factor.set_data(data)
        return drought_factor

    def forest_fire_danger_index(self, drought_factor):
        """
        Calculate Forest Fire Danger Index using Noble et al. equation for Mark 5.

        Parameters:
        -----------
        droughtFactor: STCube
            drought factor calculated from Noble et al. equation
        maxTemp: STCube
            daily maximum temperature in C
        windSpeed: STCube
            daily average wind velocity at 10m in km/hr
        relHumidity: STCube
            daily relative humidity in %

        Returns:
        --------
        out: STCube
            Daily forest fire danger.
        """
        drought = np.multiply(0.987, np.log(drought_factor.data))
        humidity = np.multiply(0.0345, self.rel_hum.data)
        temp = np.multiply(0.0338, self.temp.data)
        wind = np.multiply(0.0234, self.wind.data)

        data = 2*np.power(math.e, (-0.45 + drought - humidity + temp + wind))
        out = copy.deepcopy(self.temp)
        out.data = data #out.set_data(data)
        return out