import datetime
import copy

import numpy as np

class STFeatureStack:

    def __init__(self):
        """
        attributes of an STFeatureStack:
        --------------------------------
        data: numpy ndarray
            a 3d array [timestep, row, col]
        datelist: list
            a list of python datetime objects
        projection: string
            well known text representation of projection
            (maybe this should just be the EPSG number)
        calendar: string
            the calendar the datetime.datetime objects reference
        sc: boolean
            spatially consistent
        tc: boolean
            temporally consistent
        start: python datetime
            the first datetime object in the datelist
        end: python datetime
            the last datetime object in the datelist
        mbr: list
            the minimum bounding rectange for the entire stack [ulx, uly, lrx, lry]
        mbrlist: list
            a list holding the minimum bounding rectange of the underly features at
            each timestep in the STFeatureStack
        origin: list
            the origin of the STFeatureStack. [ulx, uly, start]
        conclusion: list
            the conclusion of the STFeatureStack. [llx, lly, end]
        mbc: list
            the minimum bounding cube [[ulx, uly, start], [llx, lly, end]]
        """

        self.data = None
        self.datelist = None

        self.projection = None
        # (see http://cfconventions.org/Data/cf-conventions/cf-conventions-1.6/build/cf-conventions.html#time-coordinate) 
        self.calendar = None

        self.sc = None
        self.tc = None

        self.mbr = None
        self.mbrlist = None

        self.start = None 
        self.end = None 

        self.origin = None
        self.conclusion = None
 
        self.mbc = None

    def set_projection(self, new_projection):
        self.projection = new_projection

    def set_calendar(self, new_calendar):
        self.calendar = new_calendar

    def set_time_attributes(self, new_datelist):
        self.datelist = new_datelist
        self.set_timebounds()

    def set_timebounds(self):
        self.start = self.datelist[0]
        self.end = self.datelist[-1]

    def set_space_attributes(self, new_mbrlist):
        """
        sets all the STFeatureStack's spatial attributes

        parameters:
        ------------
        new_mbrlist: list
            a list holding the minimum bounding rectangles of the features
        
        returns:
        ----------
        None
        """
        new_mbrlist = np.array(new_mbrlist)
        if False in np.all(new_mbrlist == new_mbrlist[0,:], axis=0): # not space consistent
            self.sc = False
            ulx = np.min(new_mbrlist[:,0])
            uly = np.max(new_mbrlist[:,1])
            lrx = np.max(new_mbrlist[:,2])
            lry = np.min(new_mbrlist[:,3])
        else:
            ulx = new_mbrlist[0][0]
            uly = new_mbrlist[0][1]
            lrx = new_mbrlist[0][2]
            lry = new_mbrlist[0][3]
        self.mbr = [ulx, uly, lrx, lry]
        self.mbrlist = new_mbrlist

    def set_all_attributes(self, new_mbrlist, new_datelist):
        self.set_space_attributes(new_mbrlist)
        self.set_time_attributes(new_datelist)
        self.origin = [self.mbr[0], self.mbr[1], self.start]
        self.conclusion = [self.mbr[2], self.mbr[3], self.end]
        self.mbc = [self.origin, self.conclusion]

    def set_st_attributes(self):
        """
        assumes the mbr, mbrlist, and datelist have been set
        """
        self.origin = [self.mbr[0], self.mbr[1], self.start]
        self.conclusion = [self.mbr[2], self.mbr[3], self.end]
        self.mbc = [self.origin, self.conclusion]

    def append_date(self, new_feature):
        self.datelist.append(new_feature.date)
        self.set_timebounds()

    def append_mbr(self, new_feature):
        new_mbrlist = np.append(self.mbrlist, [new_feature.mbr], axis=0)
        self.set_space_attributes(new_mbrlist)

    def is_empty(self):
        if self.data is None and self.datelist is None and self.projection is None and self.calendar is None and self.origin is None and self.conclusion is None and self.mbc is None and self.mbr is None:
            return True
        else:
            return False

    def __str__(self):
        if self.data is None:
            return(str(type(self)) + " EMPTY")
        else:
            return(str(type(self)) + " "
                + "mbc: " + str(self.mbc) + " "
                + "shape: " + str(self.data.shape))

    def __repr__(self):
        if self.data is None:
            return(str(type(self)) + " EMPTY")
        else:
            return(str(type(self)) + " "
                + "mbc: " + str(self.mbc) + " "
                + "shape: " + str(self.data.shape))

class RasterStack(STFeatureStack):

    def __init__(self):
        super().__init__()

        self.x = None
        self.y = None

        self.cell_width = None
        self.cell_height = None

        #self.cell_widthlist = None
        #self.cell_heightlist = None
        # implement when I incorporate support for different raster resolutions
        # in the same RasterStack

        self.nlayers = None
        self.nsteps = None
        self.ncols = None
        self.nrows = None

        self.mbc = None

        #self.rc = None # resolution consistent
        # not in use yet
        # are the cell_widths, and cell_heights between slices the same?

    def create_sc_stack(self,
                        initdata,
                        initdatelist,
                        initprojection,
                        initcalendar,
                        initx,
                        inity,
                        initcellwidth,
                        initcellheight):
        """
        creates an STFeatureStack from the given input data (3d array).
        data must be space consistent in order to use this. It assumes all data
        is perfectly aligned in space (raster layers and their cells occupy the same space)
        If uncertain about the data, use create_stack_from_features()
        When the stack is sc, there isn't a need to define an mbrlist.

        parameters:
        ------------
        initdata: list or numpy ndarray
            the input data. Must be a 3d array
        initdatelist: list
            list of datetime.datetime objects
        initprojection: string
            projection
        initcalendar: string
            calendar
        initx: float or int
            the upper left x coordinate of the RasterStack
        inity: float or int
            the upper left x or y coordinate of the RasterStack
        initcellwidth: float or int
            the cell width
        initcellheight: float or int (must be negative!!)
            the cell height
        """
        self.set_data(initdata)

        self.sc = True
        #self.rc = True

        self.set_projection(initprojection)
        self.set_calendar(initcalendar)
        
        self.x = initx
        self.y = inity
        self.cell_width = initcellwidth
        self.cell_height = initcellheight

        self.mbr = [self.x, self.y, self.x + (self.ncols * self.cell_width) - self.cell_width, self.y + (self.nrows * self.cell_height) + abs(self.cell_height)]
        self.set_time_attributes(initdatelist)
        self.set_st_attributes()

    def set_data(self, new_data):
        self.data = np.array(new_data)
        self.nsteps = len(self.data)
        self.nlayers = len(self.data[0])
        self.nrows = len(self.data[0][0])
        self.ncols = len(self.data[0][0][0])


    def create_stack_from_features(self, STFeatures):
        """
        given a list of STFeatures, iterate through the list and build an STFeatureStack.

        parameters:
        ------------
        STFeatures: list
            a list of STFeature objects. The objects must be of the same type. For example,
            you can not pass in a list of STFeatures where some STFeatures are Raster objects
            and others are Vector objects
        returns:
        ---------
        None
        """
        t = 0
        sc = True # change to false if at any point NaN padding needs to happen
        self.projection = STFeatures[t].projection
        self.calendar = STFeatures[t].calendar
        self.cell_width = STFeatures[t].cell_width
        self.cell_height = STFeatures[t].cell_height
        mbrlist = []
        max_mbr = STFeatures[t].mbr
        datelist = []
        
        while t < len(STFeatures):
            if t > 0: # ensure that the next feature to be appended has the same projection and calendar
                if STFeatures[t].projection != self.projection or STFeatures[t].calendar != self.calendar:
                    # throw some exception
                    print("error: not the same projection or calendar")
                    self.clear() # set all attributes to None
                    return
            mbrlist.append(STFeatures[t].mbr)
            if max_mbr != STFeatures[t].mbr and sc != False: # spatially inconsistent if mbrs don't match
                sc = False
            if STFeatures[t].mbr[0] < max_mbr[0]:
                ulx = STFeatures[t].mbr[0]
                max_mbr[0] = ulx
            if STFeatures[t].mbr[1] > max_mbr[1]:
                uly = STFeatures[t].mbr[1]
                max_mbr[1] = uly
            if STFeatures[t].mbr[2] > max_mbr[2]:
                lrx = STFeatures[t].mbr[2]
                max_mbr[2] = lrx
            if STFeatures[t].mbr[3] < max_mbr[3]:
                lry = STFeatures[t].mbr[3]
                max_mbr[3] = lry
            datelist.append(STFeatures[t].date)
            t+=1
        # now that the spatial and temporal attributes have been gathered,
        # now set the attributes of the STFeatureStack.
        self.sc = sc
        self.mbr = max_mbr
        self.set_all_attributes(mbrlist, datelist)
        
        # and now that the max_mbr is known, append data and pad
        # if needed.
        if sc == False:
            new_data = self.__pad_data_to_mbr(STFeatures[0].data, STFeatures[0].cell_width, STFeatures[0].cell_height, STFeatures[0].mbr)
        else:
            new_data = np.array([STFeatures[0].data])
        # iterate throught the features and append data while padding the raster if needed
        t = 1
        while t < len(STFeatures):
            if sc == False: # if space inconsistent, pad the rasters to the max mbr
                padded_data = self.__pad_data_to_mbr(STFeatures[t].data, STFeatures[t].cell_width, STFeatures[t].cell_height, STFeatures[t].mbr)
                new_data = np.append(new_data, padded_data, axis=0) # append the padded data to the new data stack
            else:
                new_data = np.append(new_data, [STFeatures[t].data], axis=0) # add a dimension to the feature_data
            STFeatures[t] = None # destroy the object
            t+=1
        self.set_data(new_data)

    def append_STFeature(self, new_STFeature):
        """
        Appends a new STFeature Raster to the STFeatureStack

        parameters:
        ------------
        new_STFeature: Raster STFeature
            the STFeature object to be appended to the already initialized
            STFeatureStack
        returns:
        ---------
        None
        """
        if type(new_STFeature) != feature.Raster:
            print("error: cannot append a Vector STFeature to a Raster STFeature")
            return
        if self.is_empty():
            self.set_data(new_STFeature.data)
            self.set_all_attributes([new_STFeature.mbr], [new_STFeature.date])
        elif new_STFeature.projection != self.projection or new_STFeature.calendar != self.calendar:
            print("error: not the same projection or calendar")
            return
        elif new_STFeature.cell_width != self.cell_width or new_STFeature.cell_height != self.cell_height:
            print("error: feature does not have the same cell resolution as the stack")
            return
        else:
            self.__append_data(new_STFeature) # pads data if needed
            self.append_date(new_STFeature)
            self.append_mbr(new_STFeature)
            self.set_st_attributes()

    def __append_data(self, new_feature):
        """
        append the new_feature to the this STFeatureStack. Pad the stack data or the
        new_feature's data if neccessary.

        parameters:
        -----------
        new_feature: feature.Raster
            the Raster STFeature that will be appened to the STFeatureStack
        returns:
        ---------
        None
        """

        # check to see if this feature is all together smaller than or equal in extent to 
        # the underlying stack data. If so, only the feature being appended needs to be padded
        # otherwise, need to pad all data in the stack to the new mbr
        if new_feature.mbr[0] >= self.mbr[0] and new_feature.mbr[1] <= self.mbr[1] and new_feature.mbr[2]  <= self.mbr[2] and new_feature.mbr[3] >= self.mbr[3]:
            # pad feature data to the stack mbr
            new_data = self.__pad_data_to_mbr(new_feature.data, new_feature.cell_width, new_feature.cell_height, new_feature.mbr)
            new_data_stack = self.data
            # finally, append the new_feature's data
            new_data_stack = np.append(new_data_stack, new_data)
        else:
            new_data_stack = self.__pad_data_to_mbr(self.data[0], self.cell_width, self.cell_height, new_feature.mbr)
            # pad stack data to the new maximum mbr given the new_feature mbr and the stack's mbr
            t = 1
            while t < len(self.data):
                new_data = self.__pad_data_to_mbr(self.data[t], self.cell_width, self.cell_height, new_feature.mbr)
                new_data_stack = np.append(new_data_stack, new_data, axis=0)
                t+=1
            # finally, append the new_feature's data
            feature_data = self.__pad_data_to_mbr(new_feature.data, new_feature.cell_width, new_feature.cell_height, new_feature.mbr)
            new_data_stack = np.append(new_data_stack, feature_data, axis=0)
        # finish by setting the stack's data
        self.set_data(new_data_stack)

    def __pad_data_to_mbr(self, input_data, input_cell_width, input_cell_height, input_mbr):
        """
        When padding data, always pad to the maximum of the two input mbrs.
        """
        ulx = min(input_mbr[0], self.mbr[0])
        uly = max(input_mbr[1], self.mbr[1])
        lrx = max(input_mbr[2], self.mbr[2])
        lry = min(input_mbr[3], self.mbr[3])
        max_mbr = [ulx, uly, lrx, lry]

        target_nrows = int(abs((max_mbr[1] - max_mbr[3] + abs(input_cell_height)) / input_cell_height))
        target_ncols = int((max_mbr[2] - max_mbr[0] + input_cell_width) / input_cell_width)

        new_data = np.zeros((len(input_data), target_nrows, target_ncols))
        new_data.fill(np.nan)

        origin_row = int(abs((max_mbr[1] - input_mbr[1]) / input_cell_height))
        origin_col = int((input_mbr[0] - max_mbr[0]) / input_cell_width)
        new_data[:, origin_row: origin_row+len(input_data[0]), origin_col: origin_col+len(input_data[0][0])] = input_data
        return np.array([new_data])

    def clear(self):
        self.data = None
        self.datelist = None
        self.projection = None
        self.calendar = None
        self.sc = None
        self.tc = None
        self.mbr = None
        self.mbrlist = None
        self.start = None 
        self.end = None 
        self.origin = None
        self.conclusion = None
        self.mbc = None
        self.x = None
        self.y = None
        self.cell_width = None
        self.cell_height = None
        self.ncols = None
        self.nrows = None


class VectorStack(STFeatureStack):

    def __init__(self):
        super().__init__()

        self.geoms = None

    """
    methods for populating the RasterStack's attributes
    """

class STFeature:

    def __init__(self,
                 initdata,
                 initzinfo,
                 initdate,
                 initprojection = None,
                 initcalendar = "standard",
                 initdescription = None):
        """
        all data should be 3-dimensional.
        Its format will be: [timestep, row, column]
        
        So if its a timeseries for a single polygon or point
        there will only be one value for each timestep and thus 
        there will only be one row and one column for each timestep
        """

        self.data = initdata 
        self.z_info = initzinfo
        self.date = initdate

        self.projection = initprojection
        self.calendar = initcalendar

        self.description = initdescription

        self.mbr = None

    def set_data(self, new_data):
        self.data = new_data

    def set_z_info(self, new_z_info):
        self.z_info = new_z_info

    def set_date(self, new_date):
        self.date = new_date

    def set_projection(self, new_projection):
        self.projection = new_projection

    def set_calendar(self, new_calendar):
        self.calendar = new_calendar

    def set_description(self, new_description):
        self.description = new_description

    def get_index_at_z(self, z_value):
        idx = self.z_info[z_value]
        return idx

    def add_layer(self, new_raster):
        self.__append_data(new_raster)

    def duplicate_feature(self):
        return copy.deepcopy(self)

class Raster(STFeature):

    def __init__(self,
                 initdata,
                 initzinfo,
                 initdate,
                 initprojection,
                 initcalendar,
                 initdescription,
                 initx,
                 inity,
                 initcellwidth,
                 initcellheight):
        super().__init__(initdata,
                         initzinfo,
                         initdate,
                         initprojection,
                         initcalendar,
                         initdescription)
        self.x = initx
        self.y = inity

        # spatial coordinate info
        self.cell_width = initcellwidth
        self.cell_height = initcellheight
        
        self.nlayers = len(self.data)
        self.nrows = len(self.data[0]) # the number of pixels in the y direction
        self.ncols = len(self.data[0][0]) # the number of pixels in the x direction

        self.set_mbr()

    def set_mbr(self):
        self.mbr = [self.x, self.y, self.x + (self.ncols * self.cell_width) - self.cell_width, self.y + (self.nrows * self.cell_height) + abs(self.cell_height)]

    def set_data(self, new_data):
        self.data = new_data
        self.nlayers = len(self.data)
        self.nrows = len(self.data[0])
        self.ncols = len(self.data[0][0])

    def append_feature(self, new_feature):
        """
        appends the data of a new feature onto this feature.
        this is strict. In order for data from the new_feature to be
        appended to this feature, it must have the same projection, shape,
        calendar, date, mbr, cell size, ncols, nrows.
        """
        if self.equals(new_feature):
            new_data = np.append(self.data, new_feature.data, axis=0)
            self.set_data(new_data)
        else:
            print("error: features are not compatible")

    def append_data(self, new_data, new_z_info):
        if len(new_data[0]) == self.nrows and len(new_data[0][0]) == self.ncols:
            out = np.append(self.data, new_data, axis=0)
            self.z_info[new_z_info] = len(self.data)
            self.set_data(out)
        else:
            print("error: could not append data")

    def equals(self, other_feature):
        if self.mbr != other_feature.mbr or self.projection != other_feature.projection or self.calendar != other_feature.calendar or self.nrows != other_feature.nrows or self.ncols != other_feature.ncols or self.date != other_feature.date or self.cell_height != other_feature.cell_height or self.cell_width != other_feature.cell_width:
            return False
        else:
            return True

    def __str__(self):
        return(str(type(self)) + " "
           + "mbr: " + str(self.mbr) + " "
           + "shape: " + str(self.data.shape))

    def __repr__(self):
        return(str(type(self)) + " "
           + "mbr: " + str(self.mbr) + " "
           + "shape: " + str(self.data.shape))

class Vector(STFeature):

    def __init__(self,
                 initdata,
                 initzinfo,
                 initdate,
                 initprojection,
                 initcalendar,
                 initdescription,
                 initgeom):
        super().__init__(initdata,
                         initdate,
                         initprojection,
                         initcalendar,
                         initdescription)

        self.geom = initgeom

        self.set_mbr() # [ulx, uly, lrx, lry]

    def set_mbr(self):
        if type(self.geom["coordinates"]) != np.ndarray:
            self.geom["coordinates"] = np.array(self.geom["coordinates"])
        if self.geom["type"] == "Point":
            self.mbr = [self.geom["coordinates"][0], self.geom["coordinates"][1], self.geom["coordinates"][0], self.geom["coordinates"][1]] 
        elif self.geom["type"] == "LineString":
            self.mbr = [np.min(self.geom["coordinates"][:,0]), np.max(self.geom["coordinates"][:,1]), np.max(self.geom["coordinates"][:,0]), np.min(self.geom["coordinates"][:,1])]
        elif self.geom["type"] == "Polygon":
            self.mbr = [np.min(self.geom["coordinates"][:,:,0]), np.max(self.geom["coordinates"][:,:,1]), np.max(self.geom["coordinates"][:,:,0]), np.min(self.geom["coordinates"][:,:,1])]

    def __str__(self):
        return(str(type(self)) + " "
               + "geometry type: " + str(self.geom["type"]))

    def __repr__(self):
        return(str(type(self)) + " "
               + "geometry type: " + str(self.geom["type"]))