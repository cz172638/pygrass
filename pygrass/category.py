# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 17:44:14 2012

@author: pietro
"""

import grass.lib.gis as libgis
import grass.lib.raster as libraster
import grass.lib.segment as libseg
from raster_type import TYPE as RTYPE
import ctypes
import numpy as np

#GET_ITH_CAT = {
#    'CELL' : libraster.Rast_get_ith_c_cat,
#    'FCELL': libraster.Rast_get_ith_f_cat,
#    'DCELL': libraster.Rast_get_ith_d_cat,
#}
#
#SET_CAT = {
#    'CELL' : libraster.Rast_set_c_cat,
#    'FCELL': libraster.Rast_set_f_cat,
#    'DCELL': libraster.Rast_set_d_cat,
#}




class Category(object):
    """
    I would like to add the following functions:

    Getting the umber of cats:
    Rast_number_of_cats() <- Important for ith access

    Getting and setting the title:
    Rast_get_cats_title()
    Rast_set_cats_title()

    Do not use these functions for category access:
    Rast_get_cat()
    and the specialized types for CELL, FCELL and DCELL.
    Since these functions are working on hidden static buffer.

    Use the ith-get methods:
    Rast_get_ith_c_cat()
    Rast_get_ith_f_cat()
    Rast_get_ith_d_cat()

    This can be implemented using an iterator too. So that the category object
    provides the [] access operator to the categories, returning a tuple
    (label, min, max).
    Using this, the category object must be aware of its raster map type.

    Set categories using:
    Rast_set_c_cat()
    Rast_set_f_cat()
    Rast_set_d_cat()

    Misc:
    Rast_sort_cats()
    Rast_copy_cats() <- This should be wrapped so that categories from an
    existing Python category class are copied.


    >>> import grass.lib.raster as libraster
    >>> import ctypes
    >>> import pygrass
    >>> land = pygrass.RasterRow('landcover_1m')
    >>> cats = pygrass.Category()
    >>> cats.read(land) # or with cats.read(land.name, land.mapset, land.mtype)
    >>> cats.labels()
    ['pond', 'forest', 'developed', 'bare', 'paved road', 'dirt road', 'vineyard', 'agriculture', 'wetland', 'bare ground path', 'grass']
    >>> min_cat = ctypes.c_void_p()
    >>> max_cat = ctypes.c_void_p()
    >>> libraster.Rast_get_ith_c_cat(ctypes.byref(cats.cats), 0, min_cat, max_cat)
    """
    def __init__(self, mtype = None):
        self.cats = libraster.Categories()
        libraster.Rast_init_cats("", ctypes.byref(self.cats))
        self._mtype = mtype
        self._gtype = None if mtype == None else RTYPE[mtype]['grass type']

    def _get_mtype(self):
        return self._mtype

    def _set_mtype(self, mtype):
        if mtype.upper() not in ('CELL', 'FCELL', 'DCELL'):
            #fatal(_("Raser type: {0} not supported".format(mtype) ) )
            raise ValueError(_("Raser type: {0} not supported".format(mtype) ))
        self._mtype = mtype
        self._gtype = RTYPE[self.mtype]['grass type']

    mtype = property(fget = _get_mtype, fset = _set_mtype)

    def _get_title(self):
        return libraster.Rast_get_cats_title(ctypes.byref(self.cats))

    def _set_title(self, newtitle):
        return libraster.Rast_set_cats_title(newtitle, ctypes.byref(self.cats))

    title = property(fget = _get_title, fset = _set_title)

    def __str__(self):
        return self.__repr__()

    def __list__(self):
        cats = []
        for cat in self.__iter__():
            cats.append(cat)
        return cats

    def __dict__(self):
        diz = dict()
        for cat in self.__iter__():
            label, min_cat, max_cat = cat
            diz[(min_cat, max_cat)] = label
        return diz

    def __repr__(self):
        cats = []
        for cat in self.__iter__():
            cats.append(repr(cat))
        return "[{0}]".format(',\n '.join(cats))

    def __len__(self):
        return libraster.Rast_number_of_cats(ctypes.byref(self.cats))

    def __getitem__(self, index):
        """Returns i-th description and i-th data range from the list of
        category descriptions with corresponding data ranges. end points of
        data interval.

        Rast_get_ith_cat(const struct Categories * 	pcats,
                         int 	i,
                         void * 	rast1,
                         void * 	rast2,
                         RASTER_MAP_TYPE 	data_type
                         )
        """
        return self.get_cat(index)


    def __iter__(self):
        return (self.__getitem__(i) for i in xrange(self.cats.ncats) )

    def get_cat(self, index):
        """Returns i-th description and i-th data range from the list of
        category descriptions with corresponding data ranges. end points of
        data interval.

        Rast_get_ith_cat(const struct Categories * 	pcats,
                         int 	i,
                         void * 	rast1,
                         void * 	rast2,
                         RASTER_MAP_TYPE 	data_type
                         )
        """
        if type(index) == str:
            try:
                index = self.labels().index(index)
            except ValueError:
                raise KeyError(index)
        min_cat = ctypes.pointer(RTYPE[self.mtype]['grass def']() )
        max_cat = ctypes.pointer(RTYPE[self.mtype]['grass def']() )
        lab = libraster.Rast_get_ith_cat(ctypes.byref(self.cats),
                                         index,
                                         ctypes.cast(min_cat, ctypes.c_void_p),
                                         ctypes.cast(max_cat, ctypes.c_void_p),
                                         self._gtype)
        # Manage C function Errors
        if lab == '': print(_("Error executing: Rast_get_ith_cat")); raise
        return lab, min_cat.contents.value, max_cat.contents.value

    def set_cat(self, label, min_cat, max_cat):
        """Adds the label for range min through max in category structure cats.

        int Rast_set_cat(const void * 	rast1,
                         const void * 	rast2,
                         const char * 	label,
                         struct Categories * 	pcats,
                         RASTER_MAP_TYPE 	data_type
                         )
        """
        min_cat = ctypes.pointer(RTYPE[self.mtype]['grass def'](min_cat) )
        max_cat = ctypes.pointer(RTYPE[self.mtype]['grass def'](max_cat) )
        err = libraster.Rast_set_cat(ctypes.cast(min_cat, ctypes.c_void_p),
                                     ctypes.cast(max_cat, ctypes.c_void_p),
                                     label,
                                     ctypes.byref(self.cats), self._gtype)
        # Manage C function Errors
        if err == 1: return None
        elif err == 0: print(_("Null value detected")); raise
        elif err == -1: print(_("Error executing: Rast_set_cat")); raise

    def __del__(self):
        libraster.Rast_free_cats(ctypes.byref(self.cats))

    def read(self, map, mapset = None, mtype = None):
        """Read categories from a raster map

        The category file for raster map name in mapset is read into the
        cats structure. If there is an error reading the category file,
        a diagnostic message is printed.

        int Rast_read_cats(const char * 	name,
                           const char * 	mapset,
                           struct Categories * 	pcats
                           )
        """
        if type(map) == str:
            mapname = map
            if mapset == None or mtype == None:
                raise TypeError(_('Mapset and maptype must be specify'))
        else:
            mapname = map.name
            mapset = map.mapset
            mtype = map.mtype

        self.mtype = mtype
        err = libraster.Rast_read_cats(mapname, mapset,
                                       ctypes.byref(self.cats))
        if err == -1: raise


    def write(self, map):
        """Writes the category file for the raster map name in the current
           mapset from the cats structure.

        void Rast_write_cats(const char * 	name,
                             struct Categories * 	cats
                             )
        """
        if type(map) == str:
            mapname = map
        else:
            mapname = map.name
        libraster.Rast_write_cats(mapname, ctypes.byref(self.cats))

    def copy(self, category):
        """Copy from another Category class"""
        libraster.Rast_copy_cats(ctypes.byref(self.cats),     # to
                                 ctypes.byref(category.cats)) # from

    def ncats(self):
        return self.__len__()

    def set_cats_fmt(self, fmt):
        pass

    def from_rules(self, filename):
        """Copy categories from a rules file"""
        pass

    def sort(self):
        libraster.Rast_sort_cats(ctypes.byref(self.cats))

    def get(self, value):
        """Return the category given a value"""
        pass

    def labels(self):
        labels = []
        for i in range(self.cats.ncats):
            labels.append(ctypes.cast(self.cats.labels[i],
                                      ctypes.c_char_p).value)
        return labels

    def rules(self):
        pass

