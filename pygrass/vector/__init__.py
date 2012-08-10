# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 08:51:53 2012

@author: pietro
"""
import ctypes
import grass.lib.vector as libvect
from vector_type import VTYPE
import geometry as geo
from basic import Bbox
from table import DBlinks

import sys
import os

vectorpath = os.path.dirname(os.path.abspath(__file__))
sys.path.append(vectorpath)
sys.path.append("%s/.." % vectorpath)
import env

_NUMOF = {"areas": libvect.Vect_get_num_areas,
          "dblinks": libvect.Vect_get_num_dblinks,
          "faces": libvect.Vect_get_num_faces,
          "holes": libvect.Vect_get_num_holes,
          "islands": libvect.Vect_get_num_islands,
          "kernels": libvect.Vect_get_num_kernels,
          "line_points": libvect.Vect_get_num_line_points,
          "lines": libvect.Vect_get_num_lines,
          "nodes": libvect.Vect_get_num_nodes,
          "updated_lines": libvect.Vect_get_num_updated_lines,
          "updated_nodes": libvect.Vect_get_num_updated_nodes,
          "volumes": libvect.Vect_get_num_volumes}

_GEOOBJ = {"areas": geo.Area,
           "dblinks": None,
           "faces": None,
           "holes": None,
           "islands": geo.Isle,
           "kernels": None,
           "line_points": None,
           "lines": geo.Boundary,
           "nodes": geo.Node,
           "volumes": None}

#=============================================
# VECTOR
#=============================================

class Vector(object):
    """
    ::

        >>> from pygrass.vector import Vector
        >>> municip = Vector('boundary_municp')
        >>> municip.isopen()
        False
        >>> municip.mapset
        ''
        >>> municip.exist()
        True
        >>> municip.mapset
        'user1'

    ..
    """


    def __init__(self, name, mapset=''):
        # Set map name and mapset
        self.name = name
        self.mapset = mapset
        self.c_mapinfo = ctypes.pointer(libvect.Map_info())
        self._spatial_index = libvect.spatial_index()
        self.topology = False
        self.overwrite = False
        self.dblinks = None

    def __repr__(self):
        if self.exist():
            return "Vector(%r, %r)" % (self.name, self.mapset)
        else:
            return "Vector(%r)" % self.name

    def num_primitive_of(self, primitive):
        """primitive are:
            * "boundary",
            * "centroid",
            * "face",
            * "kernel",
            * "line",
            * "point" ::

            >>> rail = Vector('rail')
            >>> rail.open()
            >>> rail.num_primitive_of('line')
            10831
            >>> municip = Vector('boundary_municp')
            >>> municip.open(topology=True)
            >>> municip.num_primitive_of('line')
            0
            >>> municip.num_primitive_of('centroid')
            3579
            >>> municip.num_primitive_of('boundary')
            5128

        ..
        """
        return libvect.Vect_get_num_primitives(self.c_mapinfo,
                                               VTYPE[primitive])

    def number_of(self, vtype):
        """
        vtype in ["areas", "dblinks", "faces", "holes", "islands", "kernels",
                  "line_points", "lines", "nodes", "update_lines",
                  "update_nodes", "volumes"]

            >>> municip = Vector('boundary_municp')
            >>> municip.open(topology=True)
            >>> municip.number_of("areas")
            3579
            >>> municip.number_of("islands")
            2629
            >>> municip.number_of("holes")
            0
            >>> municip.number_of("lines")
            8707
            >>> municip.number_of("nodes")
            4178
            >>> municip.number_of("pizza")
            ...                     # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
            Traceback (most recent call last):
                ...
            ValueError: vtype not supported, use one of:
            'updated_nodes', 'lines', 'dblinks', 'areas', 'kernels',
            'holes', 'updated_lines', 'volumes', 'faces', 'islands',
            'nodes', 'line_points'

        ..
        """
        if vtype in _NUMOF.keys():
            return _NUMOF[vtype](self.c_mapinfo)
        else:
            keys = "', '".join(sorted(_NUMOF.keys()))
            raise ValueError("vtype not supported, use one of: '%s'" % keys)

    def viter(self, vtype):
        """Return an iterator of vector features

        ::
            >>> municip = v.Vector('boundary_municp')
            >>> municip.open(topology=True)
            >>> big = [area for area in municip.viter('areas')
            ...        if area.alive() and area.area >= 10000]
            >>> big[:3]
            [Area(1), Area(2), Area(3)]


        to sort the result in a efficient way, use: ::

            >>> from operator import methodcaller as method
            >>> big.sort(key = method('area'), reverse = True)  # sort the list
            >>> for area in big[:3]:
            ...     print area, area.area()
            Area(3102) 697521857.848
            Area(2682) 320224369.66
            Area(2552) 298356117.948

        ..
        """
        if vtype in _GEOOBJ.keys():
            if _GEOOBJ[vtype] is not None:
                return (_GEOOBJ[vtype](vid=indx, c_mapinfo=self.c_mapinfo)
                        for indx in xrange(1, self.number_of(vtype) + 1))
        else:
            keys = "', '".join(sorted(_GEOOBJ.keys()))
            raise ValueError("vtype not supported, use one of: '%s'" % keys)


    def exist(self):
        if self.name:
            self.mapset = env.get_mapset_vector(self.name, self.mapset)
        else:
            return False
        if self.mapset:
            return True
        else:
            return False

    def isopen(self):
        return bool(self.c_mapinfo.contents.open)

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
        self.dblinks = DBlinks(self.c_mapinfo)

    def close(self):
        pass

    def bbox(self):
        """Return the BBox of the vecor map
        """
        bbox = Bbox()
        libvect.Vect_get_map_box(self.c_mapinfo, bbox.c_bbox)
        return bbox