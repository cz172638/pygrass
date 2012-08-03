# -*- coding: utf-8 -*-
"""
Created on Tue Jul 31 13:06:20 2012

@author: pietro
"""
import ctypes
import grass.lib.vector as libvect
from collections import Iterable



class Bbox(object):
    def __init__(self):
        self.c_bbox = ctypes.pointer(libvect.bound_box())

    def _get_n(self):
        return self.c_bbox.contents.N

    def _set_n(self, value):
        self.c_bbox.contents.N = value

    north = property(fget=_get_n, fset=_set_n)

    def _get_s(self):
        return self.c_bbox.contents.S

    def _set_s(self, value):
        self.c_bbox.contents.S = value

    south = property(fget=_get_s, fset=_set_s)

    def _get_e(self):
        return self.c_bbox.contents.E

    def _set_e(self, value):
        self.c_bbox.contents.E = value

    east = property(fget=_get_e, fset=_set_e)

    def _get_w(self):
        return self.c_bbox.contents.W

    def _set_w(self, value):
        self.c_bbox.contents.W = value

    west = property(fget=_get_w, fset=_set_w)

    def _get_t(self):
        return self.c_bbox.contents.T

    def _set_t(self, value):
        self.c_bbox.contents.T = value

    top = property(fget=_get_t, fset=_set_t)

    def _get_b(self):
        return self.c_bbox.contents.B

    def _set_b(self, value):
        self.c_bbox.contents.B = value

    bottom = property(fget=_get_b, fset=_set_b)



class Ilist(object):
    def __init__(self, integer_list=None):
        self.c_ilist = libvect.Vect_new_list()
        if integer_list is not None:
            self.extend(integer_list)

    def __getitem__(self, key):
        if isinstance(key, slice):
            #import pdb; pdb.set_trace()
            #Get the start, stop, and step from the slice
            return [self.c_ilist.contents.value[indx]
                    for indx in xrange(*key.indices(len(self)))]
        elif isinstance(key, int):
            if key < 0:  # Handle negative indices
                key += self.c_ilist.contents.n_values
            if key >= self.c_ilist.contents.n_values:
                raise IndexError('Index out of range')
            return self.c_ilist.contents.value[key]
        else:
            raise ValueError("Invalid argument type: %r." % key)

    def __setitem__(self, key, value):
        if self.contins(value):
            raise ValueError('Integer already in the list')
        self.c_ilist.contents.value[key] = int(value)

    def __len__(self):
        return self.c_ilist.contents.n_values

    def __iter__(self):
        return [self.c_ilist.contents.value[i] for i in xrange(self.__len__())]

    def __repr__(self):
        return "Ilist(%r)" % repr(self.__iter__())

    def append(self, value):
        """Append an integer to the list"""
        if libvect.Vect_list_append(self.c_ilist, value):
            raise  # TODO

    def reset(self):
        """Reset the list"""
        libvect.Vect_reset_list(self.c_ilist)

    def extend(self, ilist):
        """Extend the list with anothe Ilist object or
        with a list of integers"""
        if isinstance(ilist, Ilist):
            libvect.Vect_list_append_list(self.c_ilist, ilist.ilist)
        else:
            for i in ilist:
                self.append(i)

    def remove(self, value):
        """Remove a value from a list"""
        if isinstance(value, int):
            libvect.Vect_list_delete(self.c_ilist, value)
        elif isinstance(value, Ilist):
            libvect.Vect_list_delete_list(self.c_ilist, value.ilist)
        elif isinstance(value, Iterable):
            for i in value:
                libvect.Vect_list_delete(self.c_ilist, int(i))
        else:
            raise ValueError('Value: %r, is not supported' % value)

    def contins(self, value):
        """Check if value is in the list"""
        return bool(libvect.Vect_val_in_list(self.c_ilist, value))

class Cats(object):
    """
    ['Vect_cidx_get_num_cats_by_index',
     'Vect_cidx_get_num_unique_cats_by_index',
     'Vect_copy_table_by_cats',
     'Vect_destroy_cats_struct',
     'Vect_reset_cats',
     'dig_alloc_cats',
     'line_cats',
     'struct_line_cats']
    """
    def __init__(self, c_mapinfo, area_id):
        self.c_mapinfo = c_mapinfo
        self.area_id = area_id
        self.c_cats =  libvect.Vect_new_cats_struct()
        self.get_cats()

    def get_cats(self):
        """Get area categories.
        int Vect_get_area_cats (const struct Map_info *Map,
                                int area, struct line_cats *Cats)
        """
        libvect.Vect_get_area_cats(self.c_mapinfo, self.area_id, self.c_cats)

    def reset(self):
        libvect.Vect_reset_cats(self.c_cats)

