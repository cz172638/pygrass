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

#CELL = np.int
#FCELL = np.float
#DCELL = np.double


## Define global variables to not exceed the 80 columns
ERR_CREATE = 'Error: You are try to creat a new map, but you are in a read mode'
ERR_R_ONLY = 'The map is open in read only mode, I can not write!'
ERR_W_ONLY = 'The map is open in read only mode, I can not read!'
WARN_OVERWRITE = "Raster map <{0}> already exists and will be overwritten"
INDXOUTRANGE = "The index (%d) is out of range, have you open the map?."
MTHD_NOT_SUP = '{0} Method not valid, use: {1}'
MODE_NOT_SUP = '{0} Mode not valid, use: {1}'

ROWTYPE = {
'CELL' : np.int,
'FCELL': np.float,
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


class Row(np.ndarray):
    """Row object: Inherits: "numpy array" [0]:
    * Internal private C-array as buffer allocated with Rast_allocate_buf
      using a void pointer
    * The numpy array uses the private C-array as buffer [1]
    * No copying of values are needed since Raster_get_row() and
      Rast_put_row() accept the internal buffer argument
    * Check for NULL values
    """
    pass
    #self.pbuf = c.cast(c.c_void_p(self.buffer), c.POINTER(c.c_float) )



def row_to_array(row, cols):
    """Transform a row into a numpy array"""
    buf = np.core.multiarray.int_asbuffer(
          c.addressof(row.contents), 8*cols)
    return np.frombuffer(buf, float)

class RasterAbstractBase(object):
    """Raster_abstract_base: The base class from which all sub-classes
    inherit. It does not implement any row or map access methods:
    * Implements raster metadata information access (Type, ...)
    * Implements an open method that will be overwritten by the sub-classes
    * Implements the close method that might be overwritten by sub-classes
      (should work for simple row access)
    * Implements get and set region methods
    * Implements color, history and category handling
    * Renaming, deletion, ...

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


    def _get_name(self):
        """Private method to return the Raster name"""
        return self._name

    def _set_name(self, newname):
        """Private method to change the Raster name"""
        if self.exist():
            self.rename(newname)
        self._name = newname

    name = property(fget = _get_name, fset = _set_name)

    def __unicode__(self):
        return "{name}@{mapset}".format(name = self.name, mapset = self.mapset)

    def __str__(self):
        """Return the string of the object"""
        return self.__unicode__()

    def __len__(self):
        return self._rows

    def __getitem__(self, key):
        """Return the row of Raster object, slice allowed."""
        if isinstance( key, slice ) :
            #Get the start, stop, and step from the slice
            return [self.get_row(ii) for ii in xrange(*key.indices(len(self)))]
        elif isinstance( key, int ) :
            if key < 0 : #Handle negative indices
                key += self._rows
            if key >= self._rows:
                fatal(INDXOUTRANGE.format(key))
                raise IndexError
            return self.get_row(key)
        else:
            fatal("Invalid argument type.")

    def __iter__(self):
        """Return a constructor of the class"""
        return ( self.__getitem__(irow) for irow in xrange(self._rows) )

    def __del__(self):
        #TODO: implement
        self.remove()


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
            warning(_("The map is open, closing the map"))
            self.close()
        if self.exist():
            libgis.G_rename(c.c_char_p(self.mtype.lower()),
                            c.c_char_p(self.name),
                            c.c_char_p(newname))
        else:
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

class RasterRow(RasterAbstractBase):
    """Raster_row_access": Inherits: "Raster_abstract_base" and implements
    the default row access of the Rast library.
        * Implements row access using row id
        * The get_row() method must accept a Row object as argument that will
          be used for value storage, so no new buffer will be allocated
        * Implements sequential writing of rows
        * Implements indexed value read only access using the [row][col] operator
        * Implements the [row] read method that returns a new Row object
        * Writing is limited using the put_row() method which accepts a Row as argument
        * No mathematical operation like __add__ and stuff for the Raster
          object (only for rows), since r.mapcalc is more sophisticated and
          faster
    """
    def __init__(self, name, mode = 'r', *args, **kargs):
        self.mode = mode
        super(RasterRow, self).__init__(name, *args, **kargs)

        #self.row = Row()

    # mode = "r", method = "row",
    def __getitem__(self, row):
        """Private method that return the row using:

            * the read mode and
            * `row` method

        call the `Rast_get_row` function."""
        libraster.Rast_get_row(self._fd, self._pbuf, row, self._type)
        #import pdb; pdb.set_trace()
        buf = np.core.multiarray.int_asbuffer( c.addressof(self._pbuf.contents),
                                               8*self._cols)
        self.row = Row( (self._cols, ), buffer = buf)
        return self.row

    def write_row(self, pbuf):
        """Private method to write the row sequentially:

            * the write mode and
            * `row` method

        call the `Rast_put_row` function."""
        self._pbuf = pbuf
        libraster.Rast_put_row(self._fd, self._pbuf, self._type)
        return None



    def open(self, mode = '', mtype = '', overwrite = False):
        """Open the raster if exist or created a new one.

        Parameters
        ------------

        mode: string
            Specify if the map will be open with read, write, read & write
            'r', 'w'
        type: string
            If a new map is open, specify the type of the map:
                `CELL`
                `FCELL`
                `DCELL`


        if the map already exist, automatically check the type and set:
            * self.mtype

        Set all the privite, attributes:
            * self._fd;
            * self._type
            * self._ptype
            * self._rows and self._cols
        """
        # check input parameters and overwrite attributes
        if mode != '':
            self.mode = mode
        if mtype != '':
                self.mtype = mtype.upper()
                self._type = RAST_TYPE[self.mtype]
                self._ptype = POINTER_TYPE[self._type]
        if overwrite != '':
            self.overwrite = overwrite
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
        # read rows and cols from the active region
        self._rows = libraster.Rast_window_rows()
        self._cols = libraster.Rast_window_cols()


class RasterRowIO(RasterAbstractBase):
    """Raster_row_cache_access": The same as "Raster_row_access" but uses
    the ROWIO library for cached row access
    """
    def get_row(self):
        """Private method that return the row using:

            * the read mode and
            * `rowcache` method

        not implemented yet!"""
        pass

    def write_row(self):
        """Private method that return the row using:

            * the read mode and
            * `rowcache` method

        not implemented yet!"""
        pass



class RasterSegment(RasterAbstractBase):
    """Raster_segment_access": Inherits "Raster_abstract_base" and uses the
    segment library for cached randomly reading and writing access.
        * Implements the [row][col] operator for read and write access using
          segement_get() and segment_put() functions internally
        * Implements row read and write access with the [row] operator using
          segment_get_row() segment_put_row() internally
        * Implements the get_row() and put_row() method  using
          segment_get_row() segment_put_row() internally
        * Implements the flush_segment() method
        * Implements the copying of raster maps to segments and vice verse
        * Overwrites the open and close methods
        * No mathematical operation like __add__ and stuff for the Raster
          object (only for rows), since r.mapcalc is more sophisticated and
          faster
    """
    def __init__(self, srows = 64, scols = 64, maxmem = 100):
        self.srows = srows
        self.scols = scols
        self.maxmem = maxmem

    def map2segment(self):
        pass

    def segment2map(self):
        pass

    def get_row(self):
        """Private method that return the row using:
           the `segment` method

        not implemented yet!"""
        pass

    def write_row(self):
        """Private method that write the row using:
           the `segment` method

        not implemented yet!"""
        pass


class RasterNumpy(RasterAbstractBase):
    """Raster_cached_narray": Inherits "Raster_abstract_base" and
    "numpy.memmap". Its purpose is to allow numpy narray like access to
    raster maps without loading the map into the main memory.
    * Behaves like a numpy array and supports all kind of mathematical
      operations: __add__, ...
    * Overrides the open and close methods
    * Be aware of the 2Gig file size limit
    """

    def get_row(self):
        """Private method that return the row using:
           the `array` method

        not implemented yet!"""
        pass

    def write_row(self):
        """Private method that write the row using:
           the `array` method

        not implemented yet!"""
        pass


if __name__ == "__main__":
    import doctest
    doctest.testmod()