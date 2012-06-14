# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 18:02:27 2012

@author: pietro
"""
import grass.lib.gis as libgis
import grass.lib.raster as libraster
import grass.lib.segment as libseg
from raster_type import TYPE as RTYPE
import ctypes
import numpy as np



class CSeg(ctypes.Structure):
    """
    """
    _fields_ = [("x", ctypes.c_int),
                ("y", ctypes.c_int)]



class Segment(object):
    def __init__(self, srows = 64, scols = 64, maxmem = 100):
        self.srows = srows
        self.scols = scols
        self.maxmem = maxmem
        self.cseg = libseg.SEGMENT()

    @property
    def rows(self):
        return libraster.Rast_window_rows()

    @property
    def cols(self):
        return libraster.Rast_window_cols()

    @property
    def nseg(self):
        rows = self.rows
        cols = self.cols
        return ( ( rows + self.srows - 1 ) / self.srows ) * \
               ( ( cols + self.scols - 1 ) / self.scols )

    @property
    def segments_in_mem(self):
        if self.maxmem > 0 and self.maxmem < 100:
            seg_in_mem = ( self.maxmem * self.nseg ) / 100
        else:
            seg_in_mem = 4 * ( self.rows / self.srows + \
                               self.cols / self.scols + 2 )
        if seg_in_mem == 0: seg_in_mem = 1
        return seg_in_mem

    def open(self, mapobj):
        """
        """
        self.val = RTYPE[mapobj.mtype]['grass def']()
        size = ctypes.sizeof( RTYPE[mapobj.mtype]['ctypes'] )
        file_name = libgis.G_tempfile()
        #import pdb; pdb.set_trace()
        libseg.segment_open(ctypes.byref(self.cseg), file_name,
                                         self.rows, self.cols,
                                         self.srows, self.scols,
                                         size,
                                         self.nseg)

#        file_name = libgis.G_tempfile()
#        mapobj.temp_file = file(file_name, 'w')
#        #import pdb; pdb.set_trace()
#        libseg.segment_format(mapobj.temp_file.fileno(), self.rows, self.cols,
#                                 self.srows, self.scols, size)
#        # TODO: why should I close and then re-open it?
#        mapobj.temp_file.close()
#        mapobj.temp_file = open(file_name, 'w')
#        libseg.segment_init(ctypes.byref(self.cseg), mapobj.temp_file.fileno(),
#                            self.segments_in_mem )


    def get_row(self, row, buf):
        """Private method that return the row using:
           the `segment` method"""
        libseg.segment_get_row(ctypes.byref(self.cseg), buf.p, row)
        return buf


    def write_row(self, row, buf):
        """Private method that write the row using:
           the `segment` method!"""
        libseg.segment_put_row(ctypes.byref(self.cseg), buf.p, row)

    def get_point(self, row, col):
        """
        """
        libseg.segment_get(ctypes.byref(self.cseg),
                           ctypes.byref(self.val), row, col)
        return self.val.value

    def write_point(self, row, col):
        #import pdb; pdb.set_trace()
        libseg.segment_put(ctypes.byref(self.cseg),
                           ctypes.byref(self.val), row, col)

    def get_seg_number(self, row, col):
        """row/segment_info->srows * segment_info->ncols / segment_info->scols +
           col/segment_info->scols;
        """
        return row/self.srows * self.cols / self.scols + col / self.scols

    def get_seg(self, seg_number):
        return self.cseg.scb[seg_number]


    def write_seg(self, seg_number):
        pass


    def flush(self):
        pass


    def close(self):
        pass