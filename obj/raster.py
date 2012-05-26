# -*- coding: utf-8 -*-
"""
Created on Fri May 25 12:56:33 2012

@author: pietro
"""

import ctypes as c
import grass.lib.gis as libgis
import grass.lib.raster as libraster
from region import Region
#import grass.script as grass
#import grass.temporal as tgis
#import numpy as np

NOT_IMPL_STR = 'Mode: {0}, Method: {1}, not implemented yet!'
ERROR_MODE_METHD = 'Error: Mode: {0}, Method: {1}, not supported!'
INDXOUTRANGE = "The index (%d) is out of range, have you open the map?."

class Raster():
    """Return a raster object
    
    Examples
    ==========
    
    ::
        
        # import the raster function
        >>> import obj
        # instantiate a Raster
        >>> dtm = obj.Raster('dtm')
        # open the raster in read mode 'r'
        >>> dtm.open()
        # get access
        >>> for row in dtm[:5]: print(row[:3])
        [718.0910034179688, 717.8709716796875, 717.551025390625]
        [718.0910034179688, 717.8709716796875, 717.551025390625]
        [718.0910034179688, 717.8709716796875, 717.551025390625]
        [718.0910034179688, 717.8709716796875, 717.551025390625]
        [718.0910034179688, 717.8709716796875, 717.551025390625]
        >>> dtm[5][:3]
        [718.051025390625, 717.7310180664062, 717.4210205078125]
        >>> dtm.close()
    """
    ## Private dictionary to convert type string into RASTER_TYPE.
    _rast_type = {'CELL' : libraster.CELL_TYPE,
                   'FCELL': libraster.FCELL_TYPE,
                   'DCELL': libraster.DCELL_TYPE}
    ## Private dictionary to convert RASTER_TYPE into type string.
    _rtype_str = {libraster.CELL_TYPE : 'CELL',
                   libraster.FCELL_TYPE: 'FCELL',
                   libraster.DCELL_TYPE: 'DCELL'}
   ## Private dictionary to convert RASTER_TYPE into ctypes pointer
    _poiter_type = {libraster.CELL_TYPE : c.POINTER(c.c_int),
                   libraster.FCELL_TYPE: c.POINTER(c.c_float),
                   libraster.DCELL_TYPE: c.POINTER(c.c_double)}
    
    def __init__(self, name, mapset = "", mode = "r", method = "row", 
                 type = "CELL"):
        """The constructor need at least the name of the map
        *optional* fields are:
            
            * `mapset`: to specify the mapset
            * `mode`: could be: `r`, `w`, `rw`, see: open methods for more 
            details
            * `method`: could be: `row`, `rowcache`, `segment`, `array`, 
            see: open methods for more details
            * `type`: for new maps you could specify the type."""
        self.name = name
        self.mapset = mapset
        self.type = type
        self.mode = mode
        self.method = method
        self.region = Region()
        #self.get_row = None
        
        ## Private attribute `_type` is the RASTER_TYPE of the map
        self._type = self._rast_type[self.type]
        ## Private attribute `_type` is the ctypes pointer
        self._ptype = c.POINTER(c.c_float)
        ## Private attribute `_fd` that return the file descriptor of the map
        self._fd = None
        ## Private attribute `_buf` that return the file descriptor of the map
        self._buf = None
        self._pbuf = None
        
    
    def _r_row(self, row):
        """Private method that return the row using:
            
            * the read mode and 
            * `row` method
            
        call the `Rast_get_row` function."""
        libraster.Rast_get_row(self._fd, self._pbuf, row, self._type)
        return self._pbuf
        
    def _w_row(self, row):
        """Private method to write the row using:
            
            * the write mode and 
            * `row` method
            
        call the `Rast_put_row` function."""
        libraster.Rast_put_row(self._fd, self._pbuf, row, self._type)
        return self._pbuf
    
    def _r_rowcache(self):
        """Private method that return the row using:
            
            * the read mode and 
            * `rowcache` method
            
        not implemented yet!"""
        pass
    
    def _w_rowcache(self):
        """Private method that return the row using:
            
            * the read mode and 
            * `rowcache` method
            
        not implemented yet!"""
        pass
    
    def _rw_segment(self):
        """Private method that return the row using:
            
            * the read and write mode and 
            * `segment` method
            
        not implemented yet!"""
        pass
    
    def _rw_array(self):
        """Private method that return the row using:
            
            * the read and write mode and 
            * `array` method
            
        not implemented yet!"""
        pass
    
    def __unicode__(self):
        return "{name}@{mapset}".format(name = self.name, mapset = self.mapset)
        
    def __str__(self):
        """Return the string of the object"""
        return self.__unicode__()
        
    def __len__(self):
        return libraster.Rast_window_rows()
        
    def __getitem__(self, key):
        """Return the row of Raster object, slice allowed."""
        if isinstance( key, slice ) :
            #Get the start, stop, and step from the slice
            return [self.getrow(ii) for ii in xrange(*key.indices(len(self)))]
        elif isinstance( key, int ) :
            if key < 0 : #Handle negative indices
                key += self.region.rows
            if key >= self.region.rows:
                raise IndexError(INDXOUTRANGE.format(key))
            return self.getrow(key)
        else:
            raise TypeError("Invalid argument type.")
        
    def __iter__(self):
        """Return a constructor of the class"""
        for irow in range(self.region.rows):
            yield self.__getitem__(irow)
        

        
    @property
    def exist(self):
        """Return True if the map already exist, and 
        set the mapset if were not set.
        
        call the C function `G_find_raster`."""
        self.mapset = libgis.G_find_raster(self.name, self.mapset)
        if self.mapset:
            return True
        else:
            return False
            
    def set_item(self):
        """Function to determ how to access to the item comply with 
        `mode` and `method`
        """
        if self.mode == 'r':
            if self.method == 'row':
                self.getrow = self._r_row
            elif self.method == 'rowcache':
                print(NOT_IMPL_STR.format(self.mode, self.method))
                self.getrow = self._r_rowcache
        elif self.mode == 'w':
            if self.method == 'row':
                print(NOT_IMPL_STR.format(self.mode, self.method))
                self.getrow = self._w_row
            elif self.method == 'rowcache':
                print(NOT_IMPL_STR.format(self.mode, self.method))
                self.getrow = self._w_rowcache
        elif self.mode == 'rw':
            if self.method == 'row':
                print(NOT_IMPL_STR.format(self.mode, self.method))
                self.getrow = self._rw_segment
            elif self.method == 'rowcache':
                print(NOT_IMPL_STR.format(self.mode, self.method))
                self.getrow = self._rw_array
        else:
            print(ERROR_MODE_METHD.format(self.mode, self.method))
            raise
    
    def open(self, mode = '', method = '', type = ''):
        """Open the raster if exist or created a new one.
        """
        #ToDO: add more documentation 
        if mode != '': self.mode = mode
        if method != '': self.method = method
        if self.exist:
            self._fd = libraster.Rast_open_old ( self.name, self.mapset )
            self._type = libraster.Rast_get_map_type ( self._fd )
            self._ptype = self._poiter_type[self._type]
            self.type = self._rtype_str[self._type]
        else:
            # Create a new map
            if type != '': 
                self._type = self._rast_type[type]
                self._ptype = self._poiter_type[self._type]
                self.type = type
            self._fd = libraster.Rast_open_new( self.name, self._type )
        self._buf = libraster.Rast_allocate_buf ( self._type )
        self._pbuf = c.cast(c.c_void_p(self._buf), self._ptype)
        self.set_item()
        self.set_from_rast()


    def close(self):
        """Close the map"""
        libgis.G_free(self._buf)
        libraster.Rast_close(self._fd)
        
    def set_from_rast(self, rastname='', mapset=''):
        """Set the region that will use from a map, if rastername and mapset 
        is not specify, use itself.
        
        call C function `Rast_get_cellhd`"""
        self.region = Region()
        if rastname == '': 
            rastname = self.name
        if mapset == '': 
            mapset = self.mapset

        libraster.Rast_get_cellhd(rastname, mapset, 
                                  c.byref(self.region._region))

if __name__ == "__main__":
    import doctest
    doctest.testmod()