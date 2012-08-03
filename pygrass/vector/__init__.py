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

_NUMOF = {"areas":libvect.Vect_get_num_areas,
          "dblinks":libvect.Vect_get_num_dblinks,
          "faces":libvect.Vect_get_num_faces,
          "holes":libvect.Vect_get_num_holes,
          "islands":libvect.Vect_get_num_islands,
          "kernels":libvect.Vect_get_num_kernels,
          "line_points":libvect.Vect_get_num_line_points,
          "lines":libvect.Vect_get_num_lines,
          "nodes":libvect.Vect_get_num_nodes,
          "updated_lines":libvect.Vect_get_num_updated_lines,
          "updated_nodes":libvect.Vect_get_num_updated_nodes,
          "volumes":libvect.Vect_get_num_volumes}

_GEOOBJ = {"areas":geo.Area,
           "dblinks":None,
           "faces":None,
           "holes":None,
           "islands":Isle,
           "kernels":None,
           "line_points":None,
           "lines":Border,
           "nodes":Node,
           "volumes":None}

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


    def num_primitive_of(self, primitive):
        """
        primitive are:
            * "boundary",
            * "centroid",
            * "face",
            * "kernel",
            * "line",
            * "point"

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

        """
        return libvect.Vect_get_num_primitives(self.c_mapinfo,
                                               VTYPE[primitive])

    def number_of(self, vtype):
        """
        vtype in ["areas", "dblinks", "faces", "holes", "islands", "kernels",
                  "line_points", "lines", "nodes", "update_lines",
                  "update_nodes", "volumes"]
        """
        if vtype in _NUMOF.keys():
            return _NUMOF[vtype](self.c_mapinfo)
        else:
            keys = "', '".join(_NUMOF.keys())
            raise ValueError("vtype not supported, use one of: '%s'" % keys)

    def viter(vtype):
        if vtype in _GEOOBJ.keys():
            if _GEOOBJ[vtype] is not None:
                return (_GEOOBJ[vtype](vid=indx, c_mapinfo=self.c_mapinfo)
                        for indx in xrange(self.number_of(vtype)))
        else:
            keys = "', '".join(_GEOOBJ.keys())
            raise ValueError("vtype not supported, use one of: '%s'" % keys)


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
