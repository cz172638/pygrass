# -*- coding: utf-8 -*-
"""
Created on Fri May 25 12:56:33 2012

@author: pietro
"""

import ctypes
from grass.script import fatal, warning#, message
from grass.script import core as grasscore
#from grass.script import core
#import grass.lib as grasslib
import grass.lib.gis as libgis
import grass.lib.raster as libraster
import grass.lib.segment as libseg
import grass.lib.rowio as librowio
from raster_type import TYPE as RTYPE
from raster_type import RTYPE_STR
from region import Region
from category import Category
import env
from buffer import Buffer
from segment import Segment
from rowio import RowIO
import numpy as np

#import grass.script as grass
#import grass.temporal as tgis
#import numpy as np

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



def clean_map_name(name):
    name.strip()
    for char in ' @#^?°,;%&/':
        name = name.replace(char, '')
    return name


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
    """

    def __init__(self, name, mapset = "",
                 mtype = "CELL", overwrite = False):
        """The constructor need at least the name of the map
        *optional* fields are:

            * `mapset`: to specify the mapset
            * `mtype`: for new maps you could specify the type:
                - CELL;
                - FCELL;
                - DCELL."""
        self.mapset = mapset
        self.mtype = mtype.upper()
        self.overwrite = overwrite
        #self.region = Region()
        self.cats = Category()

        self._name = name
        ## Private attribute `_type` is the RASTER_TYPE of the map
        self._mtype = mtype
        ## Private attribute `_fd` that return the file descriptor of the map
        self._fd = None
        ## Private attribute `_rows` that return the number of rows
        # in active window, When the class is instanced is empty and it is set
        # when you open the file, using Rast_window_rows()
        self._rows = None
        ## Private attribute `_cols` that return the number of rows
        # in active window, When the class is instanced is empty and it is set
        # when you open the file, using Rast_window_cols()
        self._cols = None

    def _get_mtype(self):
        return self._mtype

    def _set_mtype(self, mtype):
        if mtype.upper() not in ('CELL', 'FCELL', 'DCELL'):
            #fatal(_("Raser type: {0} not supported".format(mtype) ) )
            raise ValueError(_("Raster type: {0} not supported (\"CELL\",\"FCELL\",\"DCELL\")".format(mtype) ))
        self._mtype = mtype
        self._gtype = RTYPE[self.mtype]['grass type']

    mtype = property(fget = _get_mtype, fset = _set_mtype)

    def _get_mode(self):
        return self._mode

    def _set_mode(self, mode):
        if mode.upper() not in ('R', 'W'):
            raise ValueError(_("Mode type: {0} not supported (\"r\", \"w\")".format(mode) ))
        self._mode = mode
    
    mode = property(fget = _get_mode, fset = _set_mode)
    
    def _get_overwrite(self):
        return self._overwrite

    def _set_overwrite(self, overwrite):
        if overwrite not in (True, False):
            raise ValueError(_("Overwrite type: {0} not supported (True/False)".format(overwrite) ))
        self._overwrite = overwrite
    
    overwrite = property(fget = _get_overwrite, fset = _set_overwrite)
    
    def _get_name(self):
        """Private method to return the Raster name"""
        return self._name

    def _set_name(self, newname):
        """Private method to change the Raster name"""
        #import pdb; pdb.set_trace()
        cleanname = clean_map_name(newname)
        if self.exist():
            self.rename(cleanname)
        self._name = cleanname

    name = property(fget = _get_name, fset = _set_name)

    def _get_rows(self):
        """Private method to return the Raster name"""
        return self._rows

    def _set_unchangeable(self, new):
        """Private method to change the Raster name"""
        warning(_("Unchaneable attribute"))

    rows = property(fget = _get_rows, fset = _set_unchangeable)

    def _get_cols(self):
        """Private method to return the Raster name"""
        return self._cols

    cols = property(fget = _get_cols, fset = _set_unchangeable)

    def _get_range(self):
        if self.mtype == 'CELL':
            maprange = libraster.Range()
            libraster.Rast_read_range(self.name, self.mapset,
                                      ctypes.byref(maprange))
            self._min = libgis.CELL()
            self._max = libgis.CELL()
        else:
            maprange = libraster.FPRange()
            libraster.Rast_read_fp_range(self.name, self.mapset,
                                         ctypes.byref(maprange))
            self._min = libgis.DCELL()
            self._max = libgis.DCELL()
        libraster.Rast_get_fp_range_min_max(ctypes.byref(maprange),
                                            ctypes.byref(self._min),
                                            ctypes.byref(self._max))
        return self._min.value, self._max.value

    range = property(fget = _get_range, fset = _set_unchangeable)

    def _get_cats_title(self):
        return self.cats.title

    def _set_cats_title(self, newtitle):
        self.cats.title = newtitle

    cats_title = property(fget = _get_cats_title, fset = _set_cats_title)

    def __unicode__(self):
        return self.name_mapset()

    def __str__(self):
        """Return the string of the object"""
        return self.__unicode__()

    def __len__(self):
        return self._rows

    def __getitem__(self, key):
        """Return the row of Raster object, slice allowed."""
        if isinstance( key, slice ) :
            #import pdb; pdb.set_trace()
            #Get the start, stop, and step from the slice
            return (self.get_row(ii) for ii in xrange(*key.indices(len(self))))
        elif isinstance( key, tuple ) :
            x, y = key
            return self.get(x, y)
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


    def exist(self):
        """Return True if the map already exist, and
        set the mapset if were not set.

        call the C function `G_find_raster`."""
        if self.name:
            self.mapset = env.get_mapset(self.name, self.mapset)
        else:
            return False
        if self.mapset:
            return True
        else:
            return False

    def isopen(self):
        """Return True if the map is open False otherwise"""
        return True if self._fd != None and self._fd >= 0 else False

    def close(self):
        """Close the map"""
        if self.isopen():
            libraster.Rast_close(self._fd)
            # update rows and cols attributes
            self._rows = None
            self._cols = None
            self._fd = None
        else:
            warning(_("The map is already close!"))

    def remove(self):
        """Remove the map"""
        if self.isopen():
            self.close()
        grasscore.run_command('g.remove', rast = self.name)


    def name_mapset(self, name = None, mapset = None):
        if name == None: name = self.name
        if mapset == None:
            self.exist()
            mapset = self.mapset

        if mapset:
            return "{name}@{mapset}".format(name = name, mapset = mapset)
        else:
            return name

    def rename(self, newname):
        """Rename the map"""
        if self.exist():
            env.rename(self.name, newname, 'rast')
        self._name = newname


    def set_from_rast(self, rastname='', mapset=''):
        """Set the region that will use from a map, if rastername and mapset
        is not specify, use itself.

        call C function `Rast_get_cellhd`"""
        if self.isopen():
            fatal("You cannot change the region if map is open")
            raise
        region = Region()
        if rastname == '':
            rastname = self.name
        if mapset == '':
            mapset = self.mapset

        libraster.Rast_get_cellhd(rastname, mapset,
                                  ctypes.byref(region._region))
        # update rows and cols attributes
        self._rows = libraster.Rast_window_rows()
        self._cols = libraster.Rast_window_cols()


    def has_cats(self):
        """Return True if the raster map has categories"""
        if self.exist():
            self.cats.read(self)
            if len(self.cats) != 0:
                return True
        return False

    def num_cats(self):
        """Return the number of categories"""
        return len(self.cats)

    def copy_cats(self, raster):
        """Copy categories from another raster map object"""
        self.cats.copy(raster.cats)

    def sort_cats(self):
        """Sort categories order by range"""
        self.cats.sort()

    def read_cats(self):
        """Read category from the raster map file"""
        self.cats.read(self)

    def write_cats(self):
        """Write category to the raster map file"""
        self.cats.write(self)

    def read_cats_rules(self, filename, sep = ':'):
        """Read category from the raster map file"""
        self.cats.read_rules(filename, sep)

    def write_cats_rules(self, filename, sep = ':'):
        """Write category to the raster map file"""
        self.cats.write_rules(filename, sep)

    def get_cats(self):
        """Return a category object"""
        cat = Category()
        cat.read(self)
        return cat

    def set_cats(self, category):
        """The internal categories are copied from this object."""
        self.cats.copy(category)

    def get_cat(self, label):
        """Return a category given an index or a label"""
        return self.cats[label]

    def set_cat(self, label, min_cat, max_cat = None, index = None):
        """Set or update a category"""
        self.cats.set_cat( index, (label, min_cat, max_cat) )

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


    # mode = "r", method = "row",
    def get_row(self, row, row_buffer = None):
        """Private method that return the row using the read mode
        call the `Rast_get_row` C function.
        """
        if row_buffer == None: row_buffer = Buffer((self._cols,), self.mtype)
        libraster.Rast_get_row(self._fd, row_buffer.p, row, self._gtype)
        return row_buffer

    def put_row(self, row):
        """Private method to write the row sequentially.
        """
        libraster.Rast_put_row(self._fd, row.p, self._gtype)
        return None


    def open(self, mode = 'r', mtype = 'CELL', overwrite = False):
        """Open the raster if exist or created a new one.

        Parameters
        ------------

        mode: string
            Specify if the map will be open with read or write mode ('r', 'w')
        type: string
            If a new map is open, specify the type of the map(`CELL`, `FCELL`,
            `DCELL`)
        overwrite: Boolean
            Use this flag to set the overwrite mode of existing raster maps


        if the map already exist, automatically check the type and set:
            * self.mtype

        Set all the privite, attributes:
            * self._fd;
            * self._gtype
            * self._rows and self._cols
        """
        self.mode = mode
        self.mtype = mtype
        self.overwrite = overwrite
        
        # check if exist and instantiate all the private attributes
        if self.exist():
            if self.mode == 'r':
                # the map exist, read mode
                self._fd = libraster.Rast_open_old( self.name, self.mapset )
                self._gtype = libraster.Rast_get_map_type ( self._fd )
                self.mtype = RTYPE_STR[self._gtype]
            elif self.overwrite:
                if self._gtype == None:
                    fatal(_("Raster type not defined"))
                #TODO: may be we should remove the warning.
                warning(_(WARN_OVERWRITE.format(self)))
                self._fd = libraster.Rast_open_new( self.name, self._gtype )
            else:
                fatal(_("Raster map <{0}> already exists".format(self) ) )
        else:
            # Create a new map
            if self.mode == 'r':
                # check if we are in read mode
                raise KeyError( _(ERR_CREATE) )
            self._fd = libraster.Rast_open_new( self.name, self._gtype )
        # read rows and cols from the active region
        self._rows = libraster.Rast_window_rows()
        self._cols = libraster.Rast_window_cols()


class RasterRowIO(RasterRow):
    """Raster_row_cache_access": The same as "Raster_row_access" but uses
    the ROWIO library for cached row access
    """
    def __init__(self, name, *args, **kargs):
        self.rowio = RowIO()
        super(RasterRowIO, self).__init__(name, *args, **kargs)

    def open(self, mode = 'r', mtype = 'CELL', overwrite = False):
        super(RasterRowIO, self).open(mode, mtype, overwrite)
        self.rowio.open(self._fd, self.rows, self.cols, self.mtype)

    def close(self):
        if self.isopen():
            self.rowio.release()
            libraster.Rast_close(self._fd)
            # update rows and cols attributes
            self._rows = None
            self._cols = None
            self._fd = None
        else:
            warning(_("The map is already close!"))

    def get_row(self, row, row_buffer = None):
        """Private method that return the row using:

            * the read mode and
            * `rowcache` method

        not implemented yet!"""
        if row_buffer == None: row_buffer = Buffer((self._cols,), self.mtype)
        rowio_buf = librowio.Rowio_get(ctypes.byref(self.rowio.crowio), row)
        ctypes.memmove(row_buffer.p, rowio_buf, self.rowio.row_size )
        return row_buffer





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
    def __init__(self, name, srows = 64, scols = 64, maxmem = 100,
                 *args, **kargs):
        self.segment = Segment(srows, scols, maxmem)
        super(RasterSegment, self).__init__(name, *args, **kargs)

    def _get_mode(self):
        return self._mode

    def _set_mode(self, mode):
        if mode.upper() not in ('R', 'W', 'RW'):
            raise ValueError(_("Mode type: {0} not supported (\"r\", \"w\",\"rw\")".format(mode) ))
        self._mode = mode
    
    mode = property(fget = _get_mode, fset = _set_mode)
    
    def __setitem__(self, key, row):
        """Return the row of Raster object, slice allowed."""
        if isinstance( key, slice ) :
            #Get the start, stop, and step from the slice
            return [self.put_row(ii, row) for ii in xrange(*key.indices(len(self)))]
        elif isinstance( key, tuple ) :
            x, y = key
            return self.put(x, y, row)
        elif isinstance( key, int ) :
            if key < 0 : #Handle negative indices
                key += self._rows
            if key >= self._rows:
                fatal(INDXOUTRANGE.format(key))
                raise IndexError
            return self.put_row(key, row)
        else:
            fatal("Invalid argument type.")

    def map2segment(self):
        """Transform an existing map to segment file.
        """
        if self.isopen():
            row_buffer = Buffer((self._cols), self.mtype)
            for row in xrange(self._rows):
                libraster.Rast_get_row(self._fd, row_buffer.p, row, self._gtype)
                libseg.segment_put_row(ctypes.byref(self.segment.cseg),
                                       row_buffer.p, row)

    def segment2map(self):
        """Transform the segment file to a map.
        """
        if self.isopen():
            row_buffer = Buffer((self._cols), self.mtype)
            for row in xrange(self._rows):
                libseg.segment_get_row(ctypes.byref(self.segment.cseg),
                                       row_buffer.p, row)
                libraster.Rast_put_row(self._fd, row_buffer.p, self._gtype)

    def get_row(self, row, row_buffer = None):
        """Return the row using the `segment.get_row` method

        Parameters
        ------------

        row: integer
            Specify the row number;
        row_buffer: Buffer object, optional
            Specify the Buffer object that will be instantiate.
        """
        if row_buffer == None: row_buffer = Buffer((self._cols), self.mtype)
        libseg.segment_get_row(ctypes.byref(self.segment.cseg), row_buffer.p, row)
        return row_buffer

    def put_row(self, row, row_buffer):
        """Write the row using the `segment.put_row` method

        Parameters
        ------------

        row: integer
            Specify the row number;
        row_buffer: Buffer object
            Specify the Buffer object that will be write to the map.
        """
        libseg.segment_put_row(ctypes.byref(self.segment.cseg),
                               row_buffer.p, row)

    def get(self, row, col):
        """Return the map value using the `segment.get` method

        Parameters
        ------------

        row: integer
            Specify the row number;
        col: integer
            Specify the column number.
        """
        libseg.segment_get(ctypes.byref(self.segment.cseg),
                           ctypes.byref(self.segment.val), row, col)
        return self.segment.val.value

    def put(self, row, col, val):
        """Write the value to the map using the `segment.put` method

        Parameters
        ------------

        row: integer
            Specify the row number;
        col: integer
            Specify the column number.
        val: value
            Specify the value that will be write to the map cell.
        """
        self.segment.val.value = val
        libseg.segment_put(ctypes.byref(self.segment.cseg),
                           ctypes.byref(self.segment.val), row, col)
        
    def open(self, mode = 'r', mtype = 'DCELL', overwrite = False):
        """Open the map, if the map already exist: determine the map type
        and copy the map to the segment files;
        else, open a new segment map.

        Parameters
        ------------

        mode: string, optional
            Specify if the map will be open with read, write or read/write mode ('r', 'w', 'rw')
        mtype: string, optional
            Specify the map type, valid only for new maps: CELL, FCELL, DCELL;
        overwrite: Boolean, optional
            Use this flag to set the overwrite mode of existing raster maps
        """
        # read rows and cols from the active region
        self._rows = libraster.Rast_window_rows()
        self._cols = libraster.Rast_window_cols()
        
        self.overwrite = overwrite
        self.mode = mode
        self.mtype = mtype
        
        if self.exist():
            if (self.mode == "w" or self.mode == "rw") and self.overwrite == False:
                fatal(_("Raster map <{0}> already exists. Use overwrite flag to overwrite".format(self) ) )
                
            # We copy the raster map content into the segments
            if self.mode == "rw" or self.mode == "r":
                self._fd = libraster.Rast_open_old( self.name, self.mapset )
                self._gtype = libraster.Rast_get_map_type ( self._fd )
                self.mtype = RTYPE_STR[self._gtype]
                # initialize the segment, I need to determine the mtype of the map
                # before to open the segment
                self.segment.open(self)
                self.map2segment()
                self.segment.flush()
            
                if self.mode == "rw":
                    warning(_(WARN_OVERWRITE.format(self)))
                    # Close the file descriptor and open it as new again
                    libraster.Rast_close(self._fd)
                    self._fd = libraster.Rast_open_new( self.name, self._gtype )
            # Here we simply overwrite the existing map without content copying
            elif self.mode == "w":
                warning(_(WARN_OVERWRITE.format(self)))
                self._gtype = RTYPE[self.mtype]['grass type']
                self.segment.open(self)
                self._fd = libraster.Rast_open_new( self.name, self._gtype )
        else:
            if self.mode == "r":
                fatal(_("Raster map <{0}> does not exists".format(self) ) )
                
            self._gtype = RTYPE[self.mtype]['grass type']
            self.segment.open(self)
            self._fd = libraster.Rast_open_new( self.name, self._gtype )

    def close(self, rm_temp_files = True):
        """Close the map, copy the segment files to the map.

        Parameters
        ------------

        rm_temp_files: bool
            If True all the segments file will be removed.
        """
        if self.isopen():
            if self.mode == "w" or self.mode == "rw":
                self.segment.flush()
                self.segment2map()
            if rm_temp_files:
                self.segment.close()
            else:
                self.segment.release()
            libraster.Rast_close(self._fd)
            # update rows and cols attributes
            self._rows = None
            self._cols = None
            self._fd = None
        else:
            warning(_("The map is already close!"))



FLAGS = {1 : {'b' : 'i', 'i' : 'i',  'u':'i'},
         2 : {'b' : 'i', 'i' : 'i',  'u':'i'},
         4 : {'f' : 'f', 'i' : 'i',  'b':'i', 'u':'i'},
         8 : {'f' : 'd'},}


class RasterNumpy(np.memmap, RasterAbstractBase):
    """Raster_cached_narray": Inherits "Raster_abstract_base" and
    "numpy.memmap". Its purpose is to allow numpy narray like access to
    raster maps without loading the map into the main memory.
    * Behaves like a numpy array and supports all kind of mathematical
      operations: __add__, ...
    * Overrides the open and close methods
    * Be aware of the 2Gig file size limit

    >>> import pygrass
    >>> elev = pygrass.RasterNumpy('elevation')
    >>> elev.open()
    >>> elev[:5, :3]
    RasterNumpy([[ 141.99613953,  141.27848816,  141.37904358],
       [ 142.90461731,  142.39450073,  142.68611145],
       [ 143.81854248,  143.54707336,  143.83972168],
       [ 144.56524658,  144.58493042,  144.86477661],
       [ 144.99488831,  145.22894287,  145.57142639]], dtype=float32)
    >>> el = elev < 144
    >>> el[:5, :3]
    RasterNumpy([[ True,  True,  True],
       [ True,  True,  True],
       [ True,  True,  True],
       [False, False, False],
       [False, False, False]], dtype=bool)
    >>> el._write('new', overwrite = True)

    """
    def __new__(cls, name,  mapset = "", mtype='CELL', mode = 'r+',
                overwrite = False):
        reg = Region()
        shape = (reg.rows, reg.cols)
        mapset = libgis.G_find_raster(name, mapset)
        gtype = None
        if mapset:
            # map exist, set the map type
            gtype = libraster.Rast_map_type (name, mapset)
            mtype = RTYPE_STR[ gtype ]
        filename = grasscore.tempfile()
        obj = np.memmap.__new__(cls, filename = filename,
                                dtype = RTYPE[mtype]['numpy'],
                                mode = mode,
                                shape = shape)
        obj.mtype = mtype.upper()
        obj.gtype = gtype if gtype else RTYPE[mtype]['grass type']
        obj._rows = reg.rows
        obj._cols = reg.cols
        obj.filename = filename
        obj._name = name
        obj.mapset = mapset
        obj.reg = reg
        obj.overwrite = overwrite
        return obj

    def __array_finalize__(self, obj):
        if hasattr(obj, '_mmap'):
            self._mmap = obj._mmap
            self.filename = grasscore.tempfile()
            self.offset = obj.offset
            self.mode = obj.mode
            self._rows = obj._rows
            self._cols = obj._cols
            self._name = obj._name
            self.mapset = obj.mapset
            self.reg = obj.reg
            self.overwrite = obj.overwrite
            self.mtype = obj.mtype
            self._fd = obj._fd
        else:
            self._mmap = None

    def _get_mode(self):
        return self._mode

    def _set_mode(self, mode):
        if mode.upper() not in ('R', 'W', "R+", "W+"):
            raise ValueError(_("Mode type: {0} not supported (\"r\", \"w\",\"r+\", \"w+\")".format(mode) ))
        self._mode = mode
    
    mode = property(fget = _get_mode, fset = _set_mode)
    
    def __array_wrap__(self, out_arr, context=None):
        """See:
        http://docs.scipy.org/doc/numpy/user/basics.subclassing.html#array-wrap-for-ufuncs"""
        if out_arr.dtype.kind in 'bui':
            # there is not support for boolean maps, so convert into integer
            out_arr = out_arr.astype(np.int32)
            out_arr.mtype = 'CELL'
        #out_arr.p = out_arr.ctypes.data_as(out_arr.pointer_type)
        return np.ndarray.__array_wrap__(self, out_arr, context)

    def __init__(self, name, *args, **kargs):
        ## Private attribute `_fd` that return the file descriptor of the map
        self._fd = None

    def _get_flags(self, size, kind):
        if FLAGS.has_key(size):
            if FLAGS[size].has_key(kind):
                return size, FLAGS[size][kind]
            else:
                raise ValueError(_('Invalid type {0}'.forma(kind)))
        else:
            raise ValueError(_('Invalid size {0}'.format(size)))

    def _read(self):
        """!Read raster map into array

        @return 0 on success
        @return non-zero code on failure
        """
        print "start export"
        self.null = None
        
        size, kind = self._get_flags(self.dtype.itemsize, self.dtype.kind)
        kind = 'f' if kind == 'd' else kind
        ret = grasscore.run_command('r.out.bin', flags = kind,
                                     input = self._name, output = self.filename,
                                     bytes = size, null = self.null,
                                     quiet = True)
        print "end export"
        return ret

    def _write(self):
        """
        r.in.bin input=/home/pietro/docdat/phd/thesis/gis/north_carolina/user1/.tmp/eraclito/14325.0 output=new title='' bytes=1,anull='' --verbose --overwrite north=228500.0 south=215000.0 east=645000.0 west=630000.0 rows=1350 cols=1500

        """
        size, kind = self._get_flags(self.dtype.itemsize, self.dtype.kind)
        #print size, kind
        if kind == 'i':
            kind = None
            size = 4
        else: kind
        size = None if kind == 'f' else size
        
        # To be set in the future
        self.title = None
        self.null = None
        
        if self.overwrite == True and (self.mode == "w" or self.mode == "w+"):
            print "start import"
            ret = grasscore.run_command('r.in.bin', flags = kind,
                                         input = self.filename, output = self._name,
                                         title = self.title, bytes = size,
                                         anull = self.null, overwrite = self.overwrite,
                                         verbose = True,
                                         north = self.reg.north,
                                         south = self.reg.south,
                                         east  = self.reg.east,
                                         west  = self.reg.west,
                                         rows  = self.reg.rows,
                                         cols  = self.reg.cols)
            print "end import"
            return ret

    def open(self, mtype = '', null = None):
        """Open the map, if the map already exist: determine the map type
        and copy the map to the segment files;
        else, open a new segment map.

        Parameters
        ------------

        mtype: string, optional
            Specify the map type, valid only for new maps: CELL, FCELL, DCELL;
        """
        
        self.null = null
        # rows and cols already set in __new__
        if self.exist():
            self._read()
        else:
            if mtype: self.mtype = mtype
            self._gtype = RTYPE[self.mtype]['grass type']
        # set _fd, because this attribute is used to check
        # if the map is open or not
        self._fd = 1

    def close(self):
        self._write()
        np.memmap._close(self)
        grasscore.try_remove(self.filename)
        self._fd = None


def random_map_only_columns(mapname, mtype, overwrite = True, factor = 100):
    region = Region()
    random_map = RasterRow(mapname, mtype, overwrite = overwrite)
    row_buf = Buffer((region.cols, ), mtype,
                         buffer = (np.random.random(region.cols,)*factor).data )
    random_map.open(mode = 'w')
    for _ in xrange(region.rows):
        random_map.put_row(row_buf)
    random_map.close()
    return random_map

def random_map(mapname, mtype, overwrite = True, factor = 100):
    region = Region()
    random_map = RasterRow(mapname, mtype, overwrite = overwrite)
    random_map.open(mode = 'w')
    for _ in xrange(region.rows):
        row_buf = Buffer((region.cols, ), mtype,
                         buffer = (np.random.random(region.cols,)*factor).data )
        random_map.put_row(row_buf)
    random_map.close()
    return random_map


if __name__ == "__main__":
    import doctest
    doctest.testmod()