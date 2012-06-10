# -*- coding: utf-8 -*-
"""
Created on Fri Jun  8 18:46:34 2012

@author: pietro
"""
import grass.lib.raster as raster
import ctypes
import numpy as np

class Row(np.ndarray):
    """Row object: is a subclass of the: "numpy.ndarray":
        * Internal private C-array as buffer allocated with Rast_allocate_buf
          using a void pointer
        * The numpy array uses the private C-array as buffer [1]
        * No copying of values are needed since Raster_get_row() and
          Rast_put_row() accept the internal buffer argument
        * Check for NULL values
    """
    def __new__(cls, cols, grass_type):

        if grass_type == raster.CELL_TYPE:
            obj = np.ndarray.__new__(cls, cols, dtype=np.int32)
            obj.p = obj.ctypes.data_as(ctypes.POINTER(ctypes.c_long))
        if grass_type == raster.FCELL_TYPE:
            obj = np.ndarray.__new__(cls, cols, dtype=np.float32)
            obj.p = obj.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        if grass_type == raster.DCELL_TYPE:
            obj = np.ndarray.__new__(cls, cols, dtype=np.float64)
            obj.p = obj.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

        obj.cols = cols
        obj.grass_type = grass_type

        return obj



"""
ncols = raster.Rast_window_cols()
nrows = raster.Rast_window_rows()

# New row to be used as buffer
row = Row(ncols, raster.CELL_TYPE)
# Print the pointer type to the numpy array
print row.p

fd = raster.Rast_open_old("elev", "")
for i in xrange(nrows):
    raster.Rast_get_row(fd, row.p, i, row.grass_type)
    print row

raster.Rast_close(fd)
"""