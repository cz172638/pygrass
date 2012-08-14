# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 08:51:53 2012

@author: pietro
"""
import ctypes
import grass.lib.vector as libvect
from vector_type import VTYPE, GV_TYPE
import geometry as geo
from basic import Bbox
from table import DBlinks

import sys
import os

vectorpath = os.path.dirname(os.path.abspath(__file__))
sys.path.append(vectorpath)
sys.path.append("%s/.." % vectorpath)
import env


class GrassError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class OpenError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


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

                 # 0    1         2       3           4           5
feature_label = [None, 'point', 'line', 'boundary', 'centroid', 'face',
                 # 6        7        8
                 'kernel', 'area', 'volume']


#=============================================
# VECTOR
#=============================================

class Vector(object):
    """ ::

        >>> from pygrass.vector import Vector
        >>> municip = Vector('boundary_municp_sqlite')
        >>> municip.isopen()
        False
        >>> municip.mapset
        ''
        >>> municip.exist()
        True
        >>> municip.mapset
        'user1'
        >>> municip.topology
        False
        >>> municip.overwrite
        False

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

    def __iter__(self):
        """::

            >>> mun = Vector('boundary_municp_sqlite')
            >>> mun.open()
            >>> features = [feature for feature in mun]
            >>> features[:3]
            [Boundary(v_id=1), Boundary(v_id=2), Boundary(v_id=3)]
            >>> mun.close()

        ..
        """
        #return (self.read(f_id) for f_id in xrange(self.num_of_features()))
        return self

    def __len__(self):
        return libvect.Vect_get_num_lines(self.c_mapinfo)

    def __getitem__(self, key):
        """::

            >>> mun = Vector('boundary_municp_sqlite')
            >>> mun.open()
            >>> mun[:3]
            [Boundary(v_id=1), Boundary(v_id=2), Boundary(v_id=3)]
            >>> mun.close()

        ..
        """
        if isinstance(key, slice):
            #import pdb; pdb.set_trace()
            #Get the start, stop, and step from the slice
            return [self.read(indx + 1)
                    for indx in xrange(*key.indices(len(self)))]
        elif isinstance(key, int):
            self.read(key)
        else:
            raise ValueError("Invalid argument type: %r." % key)

    def __repr__(self):
        if self.exist():
            return "Vector(%r, %r)" % (self.name, self.mapset)
        else:
            return "Vector(%r)" % self.name

    def next(self):
        """::

            >>> mun = Vector('boundary_municp_sqlite')
            >>> mun.open()
            >>> mun.next()
            Boundary(v_id=1)
            >>> mun.next()
            Boundary(v_id=2)
            >>> mun.close()

        ..
        """
        v_id = self.c_mapinfo.contents.next_line
        c_points = ctypes.pointer(libvect.line_pnts())
        c_cats = ctypes.pointer(libvect.line_cats())
        ftype = libvect.Vect_read_next_line(self.c_mapinfo, c_points, c_cats)
        if ftype == -2:
            raise StopIteration()
        if ftype == -1:
            raise
        #if  GV_TYPE[ftype]['obj'] is not None:
        return GV_TYPE[ftype]['obj'](v_id=v_id,
                                     c_mapinfo=self.c_mapinfo,
                                     c_points=c_points,
                                     c_cats=c_cats)

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
            10837
            >>> municip = Vector('boundary_municp_sqlite')
            >>> municip.open(topology=True)
            >>> municip.num_primitive_of('line')
            0
            >>> municip.num_primitive_of('centroid')
            3579
            >>> municip.num_primitive_of('boundary')
            5128
            >>> rail.close()
            >>> municip.close()

        ..
        """
        return libvect.Vect_get_num_primitives(self.c_mapinfo,
                                               VTYPE[primitive])

    def number_of(self, vtype):
        """
        vtype in ["areas", "dblinks", "faces", "holes", "islands", "kernels",
                  "line_points", "lines", "nodes", "update_lines",
                  "update_nodes", "volumes"]

            >>> municip = Vector('boundary_municp_sqlite')
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
            'areas', 'dblinks', 'faces', 'holes', 'islands', 'kernels',
            'line_points', 'lines', 'nodes', 'updated_lines', 'updated_nodes',
            'volumes'
            >>> municip.close()


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
            >>> municip = Vector('boundary_municp_sqlite')
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
            >>> munico.close()

        ..
        """
        if vtype in _GEOOBJ.keys():
            if _GEOOBJ[vtype] is not None:
                return (_GEOOBJ[vtype](v_id=indx, c_mapinfo=self.c_mapinfo)
                        for indx in xrange(1, self.number_of(vtype) + 1))
        else:
            keys = "', '".join(sorted(_GEOOBJ.keys()))
            raise ValueError("vtype not supported, use one of: '%s'" % keys)

    def rewind(self):
        """Rewind vector map to cause reads to start at beginning. ::

            >>> mun = Vector('boundary_municp_sqlite')
            >>> mun.open()
            >>> mun.next()
            Boundary(v_id=1)
            >>> mun.next()
            Boundary(v_id=2)
            >>> mun.next()
            Boundary(v_id=3)
            >>> mun.rewind()
            >>> mun.next()
            Boundary(v_id=1)
            >>> mun.close()

        ..
        """
        libvect.Vect_rewind(self.c_mapinfo)

    def read(self, feature_id):
        """Return a geometry object given the feature id. ::

            >>> mun = Vector('boundary_municp_sqlite')
            >>> mun.open()
            >>> feature1 = mun.read(0)                     #doctest: +ELLIPSIS
            Traceback (most recent call last):
                ...
            ValueError: The index must be >0, 0 given.
            >>> feature1 = mun.read(1)
            >>> feature1
            Boundary(v_id=1)
            >>> feature1.length()
            1415.3348048582038
            >>> mun.read(-1)
            Centoid(649102.382010, 15945.714502)
            >>> len(mun)
            8707
            >>> mun.read(8707)
            Centoid(649102.382010, 15945.714502)
            >>> mun.read(8708)                             #doctest: +ELLIPSIS
            Traceback (most recent call last):
              ...
            IndexError: Index out of range
            >>> mun.close()

        ..
        """
        if feature_id < 0:  # Handle negative indices
                feature_id += self.__len__() + 1
        if feature_id >= (self.__len__() + 1):
            raise IndexError('Index out of range')
        if feature_id > 0:
            c_points = ctypes.pointer(libvect.line_pnts())
            c_cats = ctypes.pointer(libvect.line_cats())
            ftype = libvect.Vect_read_line(self.c_mapinfo, c_points,
                                           c_cats, feature_id)
            if  GV_TYPE[ftype]['obj'] is not None:
                return GV_TYPE[ftype]['obj'](v_id=feature_id,
                                             c_mapinfo=self.c_mapinfo,
                                             c_points=c_points,
                                             c_cats=c_cats)
        else:
            raise ValueError('The index must be >0, %r given.' % feature_id)

    def write(self, geo_obj):
        """::

            >>> mun = Vector('boundary_municp_sqlite')         #doctest: +SKIP
            >>> mun.open(mode='rw', topology=False)            #doctest: +SKIP
            >>> feature1 = mun.read(1)                         #doctest: +SKIP
            >>> feature1                                       #doctest: +SKIP
            Boundary(v_id=1)
            >>> feature1[:3]             #doctest: +SKIP +NORMALIZE_WHITESPACE
            [Point(463718.874987, 310970.844494),
             Point(463707.405987, 310989.499494),
             Point(463714.593986, 311084.281494)]
            >>> from geometry import Point                     #doctest: +SKIP
            >>> feature1.insert(1, Point(463713.000000, 310980.000000)) #doctest: +SKIP
            >>> feature1[:4]                   #doctest: +SKIP +NORMALIZE_WHITESPACE
            [Point(463718.874987, 310970.844494),
             Point(463713.000000, 310980.000000),
             Point(463707.405987, 310989.499494),
             Point(463714.593986, 311084.281494)]
            >>> mun.write(feature1)                            #doctest: +SKIP
            >>> feature1                                       #doctest: +SKIP
            Boundary(v_id=8708)
            >>> mun.close()

        ..
        """
        result = libvect.Vect_write_line(self.c_mapinfo, geo_obj.gtype,
                                         geo_obj.c_points, geo_obj.c_cats)
        if result == -1:
            raise GrassError("Not able to write the vector feature.")
        if self.topology:
            # return new feature id (on level 2)
            geo_obj.id = result
        else:
            # return offset into file where the feature starts (on level 1)
            geo_obj.offset = result

    def rewrite(self, geo_obj):
        if self.topology:
            result = libvect.Vect_rewrite_line(self.c_mapinfo,
                                               geo_obj.id, geo_obj.gtype,
                                               geo_obj.c_points,
                                               geo_obj.c_cats)
            # return offset into file where the feature starts
            geo_obj.offset = result
        else:
            raise OpenError("the vector map must be open with topology.")

    def delete(self, feature_id):
        if libvect.Vect_rewrite_line(self.c_mapinfo, feature_id) == -1:
            raise GrassError("C funtion: Vect_rewrite_line.")

    def restore(self, geo_obj):
        if hasattr(geo_obj, 'offset'):
            if libvect.Vect_restore_line(self.c_mapinfo, geo_obj.id,
                                         geo_obj.offset) == -1:
                raise GrassError("C funtion: Vect_restore_line.")
        else:
            raise ValueError("The value have not an offset attribute.")

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
        """::

            >>> mun = Vector('boundary_municp_sqlite')
            >>> mun.open()
            >>> mun.topology
            False
            >>> mun.is_open()
            True
            >>> mun.close()

        ..
        """
        # update topology attribute
        self.topology = topology if topology is not None else self.topology
        # et level consistency with topology
        level = 2 if self.topology else 1
        if libvect.Vect_set_open_level(level) != 0:
            raise OpenError("Invalid access level.")
        # update the overwrite attribute
        self.overwrite = overwrite if overwrite is not None else self.overwrite
        # check if the mode is valid
        if mode not in ('r', 'rw', 'w'):
            raise ValueError("Mode not supported. Use one of: 'r', 'rw', 'w'.")
        # check if the map exist
        if self.exist() and mode == 'r':
            openvect = libvect.Vect_open_old2(self.c_mapinfo, self.name,
                                              self.mapset, layer)
        # If it is opened in write mode
        if mode == 'w':
            openvect = libvect.Vect_open_new(self.c_mapinfo, self.name,
                                             libvect.WITHOUT_Z)
        elif mode == 'rw':
            openvect = libvect.Vect_open_update2(self.c_mapinfo, self.name,
                                                 self.mapset, layer)
        # check the C function result.
        if openvect == 1:
            self.topology = False
        elif openvect == 2:
            self.topology = True
        else:
            raise OpenError("Not able to open the map, something wrong.")
        # initialize the dblinks object
        self.dblinks = DBlinks(self.c_mapinfo)

    def close(self):
        if libvect.Vect_close(self.c_mapinfo) != 0:
            str_err = 'Error when trying to close the map with Vect_close'
            raise GrassError(str_err)

    def bbox(self):
        """Return the BBox of the vecor map
        """
        bbox = Bbox()
        libvect.Vect_get_map_box(self.c_mapinfo, bbox.c_bbox)
        return bbox