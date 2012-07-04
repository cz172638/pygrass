# -*- coding: utf-8 -*-
"""
Created on Fri May 25 12:57:10 2012

@author: pietro
"""
import ctypes as c
import grass.lib.gis as libgis

import grass.script as grass
#import grass.temporal as tgis
#import numpy as np


class Region():
    def __init__(self):
        self._region = libgis.Cell_head()
        libgis.G_get_set_window(c.byref(self._region))


    def _set_param(self, key, value):
        grass.run_command('g.region', **{key : value})

    #----------LIMITS----------
    def _get_n(self): return self._region.north
    def _set_n(self, value): self._set_param('n', value)
    north = property(fget=_get_n, fset=_set_n)

    def _get_s(self): return self._region.south
    def _set_s(self, value): self._set_param('s', value)
    south = property(fget=_get_s, fset=_set_s)

    def _get_e(self): return self._region.east
    def _set_e(self, value): self._set_param('e', value)
    east = property(fget=_get_e, fset=_set_e)

    def _get_w(self): return self._region.west
    def _set_w(self, value): self._set_param('w', value)
    west = property(fget=_get_w, fset=_set_w)

    def _get_t(self): return self._region.top
    def _set_t(self, value): self._set_param('t', value)
    top = property(fget=_get_t, fset=_set_t)

    def _get_b(self): return self._region.bottom
    def _set_b(self, value): self._set_param('b', value)
    bottom = property(fget=_get_b, fset=_set_b)

    #----------RESOLUTION----------
    def _get_rows(self): return self._region.rows
    def _set_rows(self, value): return self._set_param('rows', value)
    rows = property(fget=_get_rows, fset=_set_rows)

    def _get_cols(self): return self._region.cols
    def _set_cols(self, value): return self._set_param('cols', value)
    cols = property(fget=_get_cols, fset=_set_cols)

    def _get_nsres(self): return self._region.ns_res
    def _set_nsres(self, value): self._set_param('nsres', value)
    nsres = property(fget=_get_nsres, fset=_set_nsres)

    def _get_ewres(self): return self._region.ew_res
    def _set_ewres(self, value): self._set_param('ewres', value)
    ewres = property(fget=_get_ewres, fset=_set_ewres)

    def _get_tbres(self): return self._region.tb_res
    def _set_tbres(self, value): self._set_param('tbres', value)
    tbres = property(fget=_get_tbres, fset=_set_tbres)

    #----------MAGIC METHODS----------
    def __unicode__(self):
        return grass.pipe_command("g.region", flags="p").communicate()[0]

    def __str__(self):
        return self.__unicode__()

    #----------METHODS----------
    def zoom(self, raster_name):
        """Shrink region until it meets non-NULL data from this raster map:"""
        self._set_param('zoom', str(raster_name))

    def align(self, raster_name):
        """Adjust region cells to cleanly align with this raster map"""
        self._set_param('align', str(raster_name))

    def res(self, value):
        """Adjust region cells to cleanly align with this raster map"""
        self._set_param('res', float(value))

    def res3(self, value):
        """Adjust region cells to cleanly align with this raster map"""
        self._set_param('res3', float(value))

    def save(self, path):
        """Adjust region cells to cleanly align with this raster map"""
        self._set_param('save', path)
