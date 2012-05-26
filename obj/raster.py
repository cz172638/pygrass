# -*- coding: utf-8 -*-
"""
Created on Fri May 25 12:56:33 2012

@author: pietro
"""

import ctypes as c
from grass.script import fatal, warning, message
import grass.lib.gis as libgis
import grass.lib.raster as libraster
from region import Region

#import grass.script as grass
#import grass.temporal as tgis
import numpy as np

NOT_IMPL_STR = 'Mode: {0}, Method: {1}, not implemented yet!'
ERR_MODE_METHD = 'Error: Mode: {0}, Method: {1}, not supported!'
ERR_CREATE ='Error: You are try to creat a new map, but you are in a read mode'
ERR_R_ONLY = 'The map is open in read only mode, I can not write!'
ERR_W_ONLY = 'The map is open in read only mode, I can not read!'
INDXOUTRANGE = "The index (%d) is out of range, have you open the map?."

ROWTYPE = {
'CELL' : int,
'FCELL': float,
'DCELL': np.double}

def row_to_array(row, cols):
    buf = np.core.multiarray.int_asbuffer(
          c.addressof(row.contents), 8*cols) 
    return np.frombuffer(buf, float)

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
        self.type = type.upper()
        self.mode = mode
        self.method = method
        #self.region = Region()
        
        ## Private attribute `_type` is the RASTER_TYPE of the map
        self._type = self._rast_type[self.type]
        ## Private attribute `_type` is the ctypes pointer
        self._ptype = c.POINTER(c.c_float)
        ## Private attribute `_fd` that return the file descriptor of the map
        self._fd = None
        ## Private attribute `_buf` that return the buffer of the map
        self._buf = None
        ## Private attribute `_pbuf` that return the pointer to the buffer
        self._pbuf = None
        ## Private attribute `_rows` that return the number of rows 
        # in active window, When the class is instanced is empty and it is set
        # when you open the file, using Rast_window_rows()
        self._rows = None
        ## Private attribute `_cols` that return the number of rows 
        # in active window, When the class is instanced is empty and it is set
        # when you open the file, using Rast_window_cols()
        self._cols = None
        self._slice = False
    
    def _r_row(self, row):
        """Private method that return the row using:
            
            * the read mode and 
            * `row` method
            
        call the `Rast_get_row` function."""
        libraster.Rast_get_row(self._fd, self._pbuf, row, self._type)
        return self._pbuf
        
    def _w_row(self, row, pbuf):
        """Private method to write the row sequentially:
            
            * the write mode and 
            * `row` method
            
        call the `Rast_put_row` function."""
        self._pbuf = pbuf
        libraster.Rast_put_row(self._fd, self._pbuf, self._type)
        return None
    
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
    
    def _r_segment(self):
        """Private method that return the row using:
           the `segment` method
            
        not implemented yet!"""
        pass
    
    def _w_segment(self):
        """Private method that write the row using:
           the `segment` method
            
        not implemented yet!"""
        pass
    
    def _r_array(self):
        """Private method that return the row using:
           the `array` method
            
        not implemented yet!"""
        pass
    
    def _w_array(self):
        """Private method that write the row using:
           the `array` method
            
        not implemented yet!"""
        pass
    
    def __unicode__(self):
        return "{name}@{mapset}".format(name = self.name, mapset = self.mapset)
        
    def __str__(self):
        """Return the string of the object"""
        return self.__unicode__()
        
    def __len__(self):
        return self._rows
        
    def _getitem_slice(self, key):
        """Return the row of Raster object, slice allowed."""
        if isinstance( key, slice ) :
            #Get the start, stop, and step from the slice
            return [self.getrow(ii) for ii in xrange(*key.indices(len(self)))]
        elif isinstance( key, int ) :
            if key < 0 : #Handle negative indices
                key += self._rows
            if key >= self._rows:
                fatal(INDXOUTRANGE.format(key))
                raise IndexError
            return self.getrow(key)
        else:
            fatal("Invalid argument type.")
        
    def __iter__(self):
        """Return a constructor of the class"""
        return ( self.__getitem__(irow) for irow in xrange(self._rows) )
        

    def exist(self):
        """Return True if the map already exist, and 
        set the mapset if were not set.
        
        call the C function `G_find_raster`."""
        self.mapset = libgis.G_find_raster(self.name, self.mapset)
        if self.mapset:
            return True
        else:
            return False
            
    def isopen(self):
        """Return True if the map is open False otherwise"""
        return True if self._fd != None else False
        
    def _readonly(self, key, value):
        import pdb; pdb.set_trace()
        #if value != None:
        #    fatal(ERR_R_ONLY)
        return self._buf
        
    def _writeonly(self, key):
        import pdb; pdb.set_trace()
        #if value != None:
        #    fatal(ERR_W_ONLY)
        return self._buf

            
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
            #self.__setitem__ = self._readonly
            
            # check if the slice support is required
            if self._slice: 
                self.__getitem__ = self._getitem_slice
            else:
                self.__getitem__ = self.getrow
        elif self.mode == 'w':
            if self.method == 'row':
                warning(NOT_IMPL_STR.format(self.mode, self.method))
                self.__setitem__ = self._w_row
            elif self.method == 'rowcache':
                warning(NOT_IMPL_STR.format(self.mode, self.method))
                self.__setitem__ = self._w_rowcache
            self.__getitem__ = self._writeonly
        elif self.mode == 'rw':
            if self.method == 'segment':
                warning(NOT_IMPL_STR.format(self.mode, self.method))
                self.getrow = self._r_segment
                self.__setitem__ = self._w_segment
            elif self.method == 'array':
                warning(NOT_IMPL_STR.format(self.mode, self.method))
                self.getrow = self._r_array
                self.__setitem__ = self._w_array
                # check if the slice support is required
            if self._slice: 
                self.__getitem__ = self._getitem_slice
            else:
                self.__getitem__ = self.getrow
        else:
            fatal(ERR_MODE_METHD.format(self.mode, self.method))
            raise

    
    
    def open(self, mode = '', method = '', type = '', _slice = ''):
        """Open the raster if exist or created a new one.
        
        Parameters
        ------------
        
        mode: string
            Specify if the map will be open with read, write, read & write
            'r', 'w', 'rw'
        method: string
            Specify if you want to use:
                `row`: Access to the map row by row
                `rowcache`: Access to the map using the rowcache
                `segment`: Access to the map using the segmentation library
                `array`: Access to the map using numpy
        type: string
            If a new map is open, specify the type of the map:
                `CELL`
                `FCELL`
                `DCELL`
        

        if the map already exist, automatically check the type and set:
            * self.type
        
        Set all the privite, attributes:
            * self._fd;
            * self._type
            * self._ptype
            * self._slice
            * self._rows and self._cols
        """
        # check input parameters and overwrite attributes
        if mode != '': 
            self.mode = mode
        if method != '': 
            self.method = method
        if _slice != '': 
            self._slice = _slice
        # check if exist and instantiate all the privite attributes
        if self.exist():
            # the map exist
            self._fd = libraster.Rast_open_old ( self.name, self.mapset )
            self._type = libraster.Rast_get_map_type ( self._fd )
            self._ptype = self._poiter_type[self._type]
            self.type = self._rtype_str[self._type]
        else:
            # Create a new map
            if mode == 'r':
                fatal(ERR_CREATE)
                raise KeyError
            if type != '':
                self.type = type.upper()
                self._type = self._rast_type[self.type]
                self._ptype = self._poiter_type[self._type]
                
            #import pdb; pdb.set_trace()
            self._fd = libraster.Rast_open_new( self.name, self._type )
        self._buf = libraster.Rast_allocate_buf ( self._type )
        self._pbuf = c.cast(c.c_void_p(self._buf), self._ptype)
        self.set_item()
        # read rows and cols from the active region
        self._rows = libraster.Rast_window_rows()
        self._cols = libraster.Rast_window_cols()



    def close(self):
        """Close the map"""
        libgis.G_free(self._buf)
        libraster.Rast_close(self._fd)
        # update rows and cols attributes
        self._rows = None
        self._cols = None
        self._row = None
    
        
        
    def set_from_rast(self, rastname='', mapset=''):
        """Set the region that will use from a map, if rastername and mapset 
        is not specify, use itself.
        
        call C function `Rast_get_cellhd`"""
        if self.isopen:
            fatal("You cannot change the region if map is open")
            raise
        self.region = Region()
        if rastname == '': 
            rastname = self.name
        if mapset == '': 
            mapset = self.mapset

        libraster.Rast_get_cellhd(rastname, mapset, 
                                  c.byref(self.region._region))
        # update rows and cols attributes
        self._rows = libraster.Rast_window_rows()
        self._cols = libraster.Rast_window_cols()

if __name__ == "__main__":
    import doctest
    doctest.testmod()