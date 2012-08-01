# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 08:51:53 2012

@author: pietro
"""
import ctypes
import grass.lib.vector as libvect
import grass.lib.gis as libgis
from vector_type import VTYPE
import geometry as geo
from basic import Bbox


#=============================================
# VECTOR
#=============================================

class Vector(object):
    def __init__(self, name, mapset = ''):
        #
        # Set map name and mapset
        #
        self.name = name
        self.mapset = mapset
        self.c_mapinfo = ctypes.pointer(libvect.Map_info())
        self._spatial_index = libvect.spatial_index()
        self.topology = False
        self.overwrite = False


    def number_of(self, vtype):
        """
        >>> rail = Vector('rail')
        >>> rail.open()
        >>> rail.number_of('line')
        10831
        >>> municip = Vector('boundary_municp')
        >>> municip.open(topology=True)
        >>> municip.number_of('line')
        0
        >>> municip.number_of('centroid')
        3579
        >>> municip.number_of('boundary')
        5128

        """
        return libvect.Vect_get_num_primitives(self.c_mapinfo,
                                               VTYPE[vtype])

    def get_line(self, line_id):
        """Return a Line object given a line number

        >>> rail.get_line(10)
        Line(id = 10)

        """
        return geo.Line(c_mapinfo = self.c_mapinfo, line_id = line_id)


    def lines(self):
        """Return a generator of Line obj

        >>> for line in rail.lines()
        ...     print line.length()
        """
        for line_id in self.number_of('line'):
            yield self.get_line(line_id)

    def exist():
        pass

    def isopen():
        pass

    def open(self, mode='r', layer='0', topology=None, overwrite=None):
        self.topology = topology if topology is not None else self.topology
        if self.topology:
            libvect.Vect_set_open_level(2)
        self.overwrite = overwrite if overwrite is not None else self.overwrite
        if mode == 'r':
            openvect = libvect.Vect_open_old2(self.c_mapinfo, self.name,
                               self.mapset, layer)
            if openvect == 1:
                topology = False
            elif openvect == 2:
                topology = True
            else:
                raise
        elif mode == 'w':
            if libvect.Vect_open_new(self.c_mapinfo,
                                     self.name, libvect.WITHOUT_Z) == -1:
                raise  # TODO raise error, somwthing went wrong in GRASS

    def close(self):
        pass

    def bbox(self):
        """Return the BBox of the vecor map
        """
        bbox = Bbox()
        libvect.Vect_get_map_box(self.c_mapinfo, bbox.c_bbox)
        return bbox
