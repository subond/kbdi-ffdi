#########################
kbdiffdi.indices.FFDI
#########################


FFDI
*****
*class* **kbdiffdi.indices.FFDI()**  

An FFDI object is initialized without any parameters.  

examples
"""""""""""""

---------------------

initialize an FFDI object
::

   from kbdiffdi import indices  
   my_ffdi = indices.FFDI()


attributes
"""""""""""

-----------------------------

   KBDI: *kbdiffdi.feature.RasterCube*  
      Set to ``None`` on initialization by ``__init__()``. A RasterCube object that holds daily KBDI data  
   temp: *kbdiffdi.feature.RasterCube*  
      RasterCube object that holds temperature data  
   prcp: *kbdiffdi.feature.RasterCube*  
      RasterCube object that holds precipitation data  
   wind: *kbdiffdi.feature.RasterCube*  
      RasterCube object that holds wind data  
   rel_hum: *kbdiffdi.feature.RasterCube*  
      RasterCube object that holds relative humidity data  

methods
"""""""""

---------------------------------------

`fit <./api_ref/>`_ (initKBDI, initprcp, inittemp, initwind, initrelhum)  
   sets the FFDI object's attributes and returns the daily FFDI.  
