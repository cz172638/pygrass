# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 13:22:38 2012

@author: pietro
"""
import ctypes
import grass.lib.rowio as librowio
import grass.lib.raster as librast
from raster_type import TYPE as RTYPE
from raster_type import RTYPE_STR


"""
int getmaprow(int fd, void *buf, int row, int len)
{
   Rast_get_d_row(fd, (DCELL *) buf, row);
   return 1;
}

import ctypes
import grass.lib.gis as libgis
import grass.lib.raster as libraster
import grass.lib.segment as libseg
import pygrass

RTYPE_STR = {libraster.CELL_TYPE : 'CELL',
             libraster.FCELL_TYPE: 'FCELL',
             libraster.DCELL_TYPE: 'DCELL'}

elev = pygrass.RasterRowIO('elevation')
elev._rows = libraster.Rast_window_rows()
elev._cols = libraster.Rast_window_cols()
elev.exist()
elev._fd = libraster.Rast_open_old( elev.name, elev.mapset )
elev._gtype = libraster.Rast_get_map_type ( elev._fd )
elev.mtype = RTYPE_STR[elev._gtype]
elev.rowio.open(elev._fd, elev.rows, elev.cols, elev.mtype)
elev.open()
"""

CMPFUNC = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p,
                           ctypes.c_int, ctypes.c_int)

def getmaprow_CELL(fd, buf, row, l):
    librast.Rast_get_f_row( fd, ctypes.cast(buf, librast.FCELL), row)
    return 0

def getmaprow_FCELL(fd, buf, row, l):
    librast.Rast_get_f_row( fd, ctypes.cast(buf, librast.FCELL), row)
    return 0

def getmaprow_DCELL(fd, buf, row, l):
    librast.Rast_get_f_row( fd, ctypes.cast(buf, librast.FCELL), row)
    return 0

get_row = {
    'CELL'  : CMPFUNC(getmaprow_CELL),
    'FCELL' : CMPFUNC(getmaprow_FCELL),
    'DCELL' : CMPFUNC(getmaprow_DCELL),
}

class RowIO(object):
    """
    The file descriptor fd must be open for reading.
    int in = Rast_open_old(in_name, "");

    Rowio_setup(&r, fd, rows, buflen,
			getrow, NULL);

    R	      pointer to ROWIO structure
    fd	      file descriptor
    nrows	number of rows
    getrow	get row function

    execute_filter(&r, out, &filter[n], cell);
    Rowio_get(r, row)

    Rowio_release(&r);
	}
    """
    def __init__(self):
        self.crowio = librowio.ROWIO()
        self.fd = None
        self.rows = None
        self.cols = None
        self.mtype = None

    def open(self, fd, rows, cols, mtype):
        self.fd = fd
        self.rows = rows
        self.cols = cols
        self.mtype = mtype
        librowio.Rowio_setup(ctypes.byref(self.crowio), self.fd,
                             self.rows,
                             ctypes.sizeof(RTYPE[mtype]['grass def'] * cols),
                             get_row[self.mtype],
                             None)

    def release(self):
        librowio.release(ctypes.byref(self.crowio))
        self.fd = None
        self.rows = None
        self.cols = None
        self.mtype = None


    def get(self, row_index, buf):
        self.crowio.buf = ctypes.cast(buf.p, ctypes.c_void_p)
        librowio.Rowio_get(ctypes.byref(self.crowio), row_index)