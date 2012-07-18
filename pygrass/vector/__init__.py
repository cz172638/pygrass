# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 08:51:53 2012

@author: pietro
"""
import ctypes
import grass.lib.vector as libvect
from vector_type import VTYPE
import geometry as geo


#=============================================
# VECTOR
#=============================================

class Vector(object):
    def __init__(self, name, mapset = ''):
        self.name = name
        self.mapset = mapset
        self._Map_info = libvect.Map_info()
        self.mapinfo = ctypes.byref(self._Map_info)
        self._spatial_index = libvect.spatial_index()
        self.topology = False
        self.overwrite = False


    def numberof(self, vtype):
        """
        >>> rail = Vector('railroads')
        >>> rail.open()
        >>> rail.numberof('line')
        10831
        """
        return libvect.Vect_get_num_primitives(self.mapinfo,
                                               VTYPE[vtype])

    def get_line(self, line_id):
        """Return a Line object given a line number

        >>> rail.get_line(10)
        Line(id = 10)

        """
        return geo.Line(mapinfo = self.mapinfo, line_id = line_id)


    def lines(self):
        """Return a generator of Line obj

        >>> for line in rail.lines()
        ...     print line.length()
        """
        for line_id in self.numberof('line'):
            yield self.get_line(line_id)



    def open(self, mode = 'r', layer = '0', topology = None, overwrite = None):
        self.topology = topology if topology != None else self.topology
        if self.topology:
            libvect.Vect_set_open_level(2)
        self.overwrite = overwrite if overwrite != None else self.overwrite
        if mode == 'r':
            openvect = libvect.Vect_open_old2(self.mapinfo, self.name,
                               self.mapset, layer)
            if openvect == 1:
                topology = False
            elif openvect == 2:
                topology = True
            else:
                raise
        elif mode == 'w':
            openvect = libvect.Vect_open_new(self.mapinfo,
                                             self.name, libvect.WITHOUT_Z)
            if openvect == -1: raise

    def close(self):
        pass

    def bbox(self):
        """Vect_get_map_box
        """
        pass
