# -*- coding: utf-8 -*-
"""
Created on Fri May 25 12:56:33 2012

@author: pietro
"""

import ctypes as c
from grass.script import fatal, warning#, message
from grass.script import core
import grass.lib as grasslib
import grass.lib.gis as libgis
import grass.lib.raster as libraster
from region import Region

#import grass.script as grass
#import grass.temporal as tgis
import numpy as np


## Define global variables to not exceed the 80 columns
ERR_CREATE = 'Error: You are try to creat a new map, but you are in a read mode'
ERR_R_ONLY = 'The map is open in read only mode, I can not write!'
ERR_W_ONLY = 'The map is open in read only mode, I can not read!'
WARN_OVERWRITE = "Raster map <{0}> already exists and will be overwritten"
INDXOUTRANGE = "The index (%d) is out of range, have you open the map?."
MTHD_NOT_SUP = '{0} Method not valid, use: {1}'
MODE_NOT_SUP = '{0} Mode not valid, use: {1}'

ROWTYPE = {
'CELL' : int,
'FCELL': float,
'DCELL': np.double}

## Private dictionary to convert type string into RASTER_TYPE.
RAST_TYPE = {'CELL' : libraster.CELL_TYPE,
               'FCELL': libraster.FCELL_TYPE,
               'DCELL': libraster.DCELL_TYPE}
## Private dictionary to convert RASTER_TYPE into type string.
RTYPE_STR = {libraster.CELL_TYPE : 'CELL',
               libraster.FCELL_TYPE: 'FCELL',
               libraster.DCELL_TYPE: 'DCELL'}
## Private dictionary to convert RASTER_TYPE into ctypes pointer
POINTER_TYPE = {libraster.CELL_TYPE : c.POINTER(c.c_int),
               libraster.FCELL_TYPE: c.POINTER(c.c_float),
               libraster.DCELL_TYPE: c.POINTER(c.c_double)}


class Row():
    def __init__(self, buf, cols):
        self.buf = buf
        self.cols = cols

    def __iter__(self):
        return (x for x in xrange(self.cols))

    def to_array(self):
        """Transform a row into a numpy array"""
        buf = np.core.multiarray.int_asbuffer(c.addressof(self.buf.contents),
                                              8*self.cols)
        return np.frombuffer(buf, float)

    def __add__(self, addend):
        if (isinstance(addend, int) or isinstance(addend, float) ):
            return Row([self.buf[i] + addend for i in xrange(self.cols)],
                        self.cols )

    def __getitem__(self, key):
        return self.buf[key]


def row_to_array(row, cols):
    """Transform a row into a numpy array"""
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

    def __init__(self, name, mapset = "",
                 mode = "r", method = "row",
                 mtype = "CELL", overwrite = False):
        """The constructor need at least the name of the map
        *optional* fields are:

            * `mapset`: to specify the mapset
            * `mode`: could be: `r`, `w`, `rw`, see: open methods for more
            details
            * `method`: could be: `row`, `rowcache`, `segment`, `array`,
            see: open methods for more details
            * `type`: for new maps you could specify the type."""
        self.mapset = mapset
        self.mtype = mtype.upper()
        self.mode = mode
        self.method = method
        self.overwrite = overwrite
        #self.region = Region()

        self._name = name
        ## Private attribute `_type` is the RASTER_TYPE of the map
        self._type = RAST_TYPE[self.mtype]
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
        self.mslice = False

    def _get_name(self):
        """Private method to return the Raster name"""
        return self._name

    def _set_name(self, newname):
        """Private method to change the Raster name"""
        if self.exist():
            self.rename(newname)
        self._name = newname

    name = property(fget = _get_name, fset = _set_name)


    def _r_row(self, row):
        """Private method that return the row using:

            * the read mode and
            * `row` method

        call the `Rast_get_row` function."""
        libraster.Rast_get_row(self._fd, self._pbuf, row, self._type)
        return self._pbuf

    def _w_row(self, pbuf):
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

    def __del__(self):
        #TODO: implement
        self.remove()

    def __add__(self, addend):
        import pdb; pdb.set_trace()
        if isinstance( addend, Raster ):
            # do with C function
            pass
        else:
            # do with C function
            pass


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
        """Return the las row, if try to set new a new value
        raise a fatal error"""
        if value != None:
            fatal(ERR_R_ONLY)
        return self._buf

    def _writeonly(self, key):
        """Return the last row"""
        return self._buf

    def set_item_method(self):
        """Function to determ how to access to the item comply with
        `mode` and `method`
        """
        mode_method = {
        # READ MODE
        'r' : {
               'row'      : {'get' : self._r_row, 'set' : self._readonly},
               'rowcache' : {'get' : self._r_rowcache, 'set' : self._readonly},
              },
        # WRITE MODE
        'w' : {
               'row'      : {'get' : self._writeonly, 'set' : self._w_row},
               'rowcache' : {'get' : self._writeonly, 'set' : self._w_rowcache},
              },
        # READ & WRITE MODE
        'rw': {
               'segment'  : {'get' : self._r_segment, 'set' : self._w_segment},
               'array'    : {'get' : self._r_array, 'set' : self._w_array},
              },
        }
        if mode_method.has_key(self.mode):
            if mode_method[self.mode].has_key(self.method):
                self.getrow = mode_method[self.mode][self.method]['get']
                if self.mode == 'w':
                    self.writerow = mode_method[self.mode][self.method]['set']
                else:
                    self.__setitem__ = mode_method[self.mode][self.method]['set']
            else:
                raise KeyError(_(MTHD_NOT_SUP.format(self.method,
                                 ','.join(mode_method[self.mode].keys() ) ) ) )
        else:
            raise KeyError(_(MODE_NOT_SUP.format(self.method,
                            ','.join( mode_method.keys() ) ) ) )

        if self.mslice:
            self.__getitem__ = self._getitem_slice
        else:
            self.__getitem__ = self.getrow


    def open(self, mode = '', method = '', mtype = '', mslice = True,
             overwrite = False):
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
            * self.mtype
            * self.mslice

        Set all the privite, attributes:
            * self._fd;
            * self._type
            * self._ptype
            * self._rows and self._cols
        """
        # check input parameters and overwrite attributes
        if mode != '':
            self.mode = mode
        if method != '':
            self.method = method
        if mtype != '':
                self.mtype = mtype.upper()
                self._type = RAST_TYPE[self.mtype]
                self._ptype = POINTER_TYPE[self._type]
        if mslice != '':
            self.mslice = mslice
        if overwrite != '':
            self.overwrite = overwrite
        self.overwrite
        # check if exist and instantiate all the privite attributes
        if self.exist():
            if self.mode == 'r':
                # the map exist, read mode
                self._fd = libraster.Rast_open_old ( self.name, self.mapset )
                self._type = libraster.Rast_get_map_type ( self._fd )
                self._ptype = POINTER_TYPE[self._type]
                self.mtype = RTYPE_STR[self._type]
            elif self.overwrite:
                #TODO: may be we should remove the warning.
                warning(_(WARN_OVERWRITE.format(self)))
                self._fd = libraster.Rast_open_new( self.name, self._type )
            else:
                fatal(_("Raster map <{0}> already exists".format(self) ) )
        else:
            # Create a new map
            if self.mode == 'r':
                # check if we are in read mode
                raise KeyError( _(ERR_CREATE) )
            self._fd = libraster.Rast_open_new( self.name, self._type )
        self._buf = libraster.Rast_allocate_buf ( self._type )
        self._pbuf = c.cast(c.c_void_p(self._buf), self._ptype)
        self.set_item_method()
        # read rows and cols from the active region
        self._rows = libraster.Rast_window_rows()
        self._cols = libraster.Rast_window_cols()



    def close(self):
        """Close the map"""
        if self.isopen():
            libgis.G_free(self._buf)
            libraster.Rast_close(self._fd)
            # update rows and cols attributes
            self._rows = None
            self._cols = None
        else:
            warning(_("The map is already close!"))

    def remove(self):
        """Remove the map"""
        if self.isopen():
            self.close()
        libgis.G_remove(self.mtype.lower(),
                        self.name)

    def rename(self, newname):
        """Rename the map"""
        if self.isopen():
                warning(_("The map is open, close before rename"))
                return
        if self.exist():
                libgis.G_rename(c.c_char_p(self.mtype.lower()),
                                c.c_char_p(self.name),
                                c.c_char_p(newname))
        self._name = newname


    def set_from_rast(self, rastname='', mapset=''):
        """Set the region that will use from a map, if rastername and mapset
        is not specify, use itself.

        call C function `Rast_get_cellhd`"""
        if self.isopen:
            fatal("You cannot change the region if map is open")
            raise
        region = Region()
        if rastname == '':
            rastname = self.name
        if mapset == '':
            mapset = self.mapset

        libraster.Rast_get_cellhd(rastname, mapset,
                                  c.byref(region._region))
        # update rows and cols attributes
        self._rows = libraster.Rast_window_rows()
        self._cols = libraster.Rast_window_cols()

if __name__ == "__main__":
    import doctest
    doctest.testmod()