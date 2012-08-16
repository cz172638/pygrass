# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 08:51:53 2012

@author: pietro
"""
import ctypes
import datetime
import grass.lib.vector as libvect
from vector_type import VTYPE, GV_TYPE
import geometry as geo
import sys
import os
# modify the python path to load "env" and "errors"
vectorpath = os.path.dirname(os.path.abspath(__file__))
sys.path.append(vectorpath)
sys.path.append("%s/.." % vectorpath)
import env
from errors import GrassError, OpenError
from basic import Bbox
from table import DBlinks


_MAPTYPE = {libvect.GV_FORMAT_NATIVE: "native",
            libvect.GV_FORMAT_OGR: "OGR",
            libvect.GV_FORMAT_OGR_DIRECT: "OGR",
            libvect.GV_FORMAT_POSTGIS: "PostGIS"}

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

class Info(object):
    """Basic vector info.
    To get access to the vector info the map must be opened. ::

        >>> municip = Info('boundary_municp', 'PERMANENT')
        >>> municip.open()

    Then it is possible to read and write the following map attributes: ::

        >>> municip.organization
        'NC OneMap'
        >>> municip.person
        'helena'
        >>> municip.title
        'North Carolina municipality boundaries (polygon map)'
        >>> municip.map_date
        datetime.datetime(2006, 11, 7, 0, 1, 27)
        >>> municip.date
        ''
        >>> municip.scale
        1
        >>> municip.comment
        ''
        >>> municip.comment = "One useful comment!"
        >>> municip.comment
        'One useful comment!'
        >>> municip.zone
        0
        >>> municip.proj
        99

    There are some read only attributes: ::

        >>> municip.full_name
        'boundary_municp@PERMANENT'
        >>> municip.proj_name
        'Lambert Conformal Conic'
        >>> municip.maptype
        'native'

    And some basic methods: ::

        >>> municip.is_3D()
        False
        >>> municip.exist()
        True
        >>> municip.is_open()
        True
        >>> municip.close()

    """
    def __init__(self, name, mapset=''):
        # Set map name and mapset
        self._name = name
        self.mapset = mapset
        self.c_mapinfo = ctypes.pointer(libvect.Map_info())
        self._topo_level = 1
        self._class_name = 'Vector'
        self.overwrite = False
        self.date_fmt =  '%a %b  %d %H:%M:%S %Y'

    def _get_name(self):
        if self.exist() and self.is_open():
            return libvect.Vect_get_name(self.c_mapinfo)
        else:
            return self._name

    def _set_name(self, newname):
        self.rename(newname)

    name = property(fget=_get_name, fset=_set_name)

#    @property
#    def mapset(self):
#        return libvect.Vect_get_mapset(self.c_mapinfo)

    def _get_organization(self):
        return libvect.Vect_get_organization(self.c_mapinfo)

    def _set_organization(self, org):
        libvect.Vect_get_organization(self.c_mapinfo, ctypes.c_char_p(org))

    organization = property(fget=_get_organization, fset=_set_organization)

    def _get_date(self):
        return libvect.Vect_get_date(self.c_mapinfo)

    def _set_date(self, date):
        return libvect.Vect_set_date(self.c_mapinfo, ctypes.c_char_p(date))

    date = property(fget=_get_date, fset=_set_date)

    def _get_person(self):
        return libvect.Vect_get_person(self.c_mapinfo)

    def _set_person(self, person):
        libvect.Vect_set_person(self.c_mapinfo, ctypes.c_char_p(person))

    person = property(fget=_get_person, fset=_set_person)

    def _get_title(self):
        return libvect.Vect_get_map_name(self.c_mapinfo)

    def _set_title(self, title):
        libvect.Vect_set_map_name(self.c_mapinfo, ctypes.c_char_p(title))

    title = property(fget=_get_title, fset=_set_title)

    def _get_map_date(self):
        date_str = libvect.Vect_get_map_date(self.c_mapinfo)
        return datetime.datetime.strptime(date_str, self.date_fmt)

    def _set_map_date(self, datetimeobj):
        date_str = datetimeobj.strftime(self.date_fmt)
        libvect.Vect_set_map_date(self.c_mapinfo, ctypes.c_char_p(map_date))

    map_date = property(fget=_get_map_date, fset=_set_map_date)

    def _get_scale(self):
        return libvect.Vect_get_scale(self.c_mapinfo)

    def _set_scale(self, scale):
        return libvect.Vect_set_scale(self.c_mapinfo, ctypes.c_int(scale))

    scale = property(fget=_get_scale, fset=_set_scale)

    def _get_comment(self):
        return libvect.Vect_get_comment(self.c_mapinfo)

    def _set_comment(self, comm):
        return libvect.Vect_set_comment(self.c_mapinfo, ctypes.c_char_p(comm))

    comment = property(fget=_get_comment, fset=_set_comment)

    def _get_zone(self):
        return libvect.Vect_get_zone(self.c_mapinfo)

    def _set_zone(self, zone):
        return libvect.Vect_set_zone(self.c_mapinfo, ctypes.c_int(zone))

    zone = property(fget=_get_zone, fset=_set_zone)

    def _get_proj(self):
        return libvect.Vect_get_proj(self.c_mapinfo)

    def _set_proj(self, proj):
        libvect.Vect_set_proj(self.c_mapinfo, ctypes.c_int(proj))

    proj = property(fget=_get_proj, fset=_set_proj)

    def _get_thresh(self):
        return libvect.Vect_get_thresh(self.c_mapinfo)

    def _set_thresh(self, thresh):
        return libvect.Vect_set_thresh(self.c_mapinfo, ctypes.c_double(thresh))

    thresh = property(fget=_get_thresh, fset=_set_thresh)

    @property
    def full_name(self):
        return libvect.Vect_get_full_name(self.c_mapinfo)

    @property
    def maptype(self):
        return _MAPTYPE[libvect.Vect_maptype(self.c_mapinfo)]

    @property
    def proj_name(self):
        return libvect.Vect_get_proj_name(self.c_mapinfo)

    def _write_header(self):
        libvect.Vect_write_header(self.c_mapinfo)

    def rename(self, newname):
        """Rename the map"""
        if self.exist():
            env.rename(self.name, newname, 'vect')
        self._name = newname

    def is_3D(self):
        return bool(libvect.Vect_is_3d(self.c_mapinfo))

    def exist(self):
        if self._name:
            self.mapset = env.get_mapset_vector(self._name, self.mapset)
        else:
            return False
        if self.mapset:
            return True
        else:
            return False

    def is_open(self):
        return bool(self.c_mapinfo.contents.open)

    def open(self, mode='r', layer='0', overwrite=None):
        """::

            >>> mun = Vector('boundary_municp_sqlite')
            >>> mun.open()
            >>> mun.is_open()
            True
            >>> mun.close()

        ..
        """
        if libvect.Vect_set_open_level(self._topo_level) != 0:
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
        # initialize the dblinks object
        self.dblinks = DBlinks(self.c_mapinfo)
        # check the C function result.
        if openvect != self._topo_level:
            str_err = "Not able to open the map, C function return %d."
            raise OpenError(str_err % openvect)

    def close(self):
        if self.is_open():
            if libvect.Vect_close(self.c_mapinfo) != 0:
                str_err = 'Error when trying to close the map with Vect_close'
                raise GrassError(str_err)


#=============================================
# VECTOR
#=============================================

class Vector(Info):
    """ ::

        >>> from pygrass.vector import Vector
        >>> municip = Vector('boundary_municp_sqlite')
        >>> municip.is_open()
        False
        >>> municip.mapset
        ''
        >>> municip.exist()
        True
        >>> municip.mapset
        'user1'
        >>> municip.overwrite
        False

    ..
    """
    def __init__(self, name, mapset=''):
        # Set map name and mapset
        super(Vector, self).__init__(name, mapset)
        self._topo_level = 1
        self._class_name = 'Vector'
        self.overwrite = False
        self.dblinks = None

    def __repr__(self):
        if self.exist():
            return "%s(%r, %r)" % (self._class_name, self.name, self.mapset)
        else:
            return "%s(%r)" % (self._class_name, self.name)

    def __iter__(self):
        """::

            >>> mun = Vector('boundary_municp_sqlite')
            >>> mun.open()
            >>> features = [feature for feature in mun]
            >>> features[:3]
            [Boundary(v_id=None), Boundary(v_id=None), Boundary(v_id=None)]
            >>> mun.close()

        ..
        """
        #return (self.read(f_id) for f_id in xrange(self.num_of_features()))
        return self

    def next(self):
        """::

            >>> mun = Vector('boundary_municp_sqlite')
            >>> mun.open()
            >>> mun.next()
            Boundary(v_id=None)
            >>> mun.next()
            Boundary(v_id=None)
            >>> mun.close()

        ..
        """
        v_id = self.c_mapinfo.contents.next_line
        v_id = v_id if v_id != 0 else None
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

    def bbox(self):
        """Return the BBox of the vecor map
        """
        bbox = Bbox()
        libvect.Vect_get_map_box(self.c_mapinfo, bbox.c_bbox)
        return bbox

    def write(self, geo_obj):
        """::

            >>> mun = Vector('boundary_municp_sqlite')         #doctest: +SKIP
            >>> mun.open(mode='rw')            #doctest: +SKIP
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
            >>> mun.close()                                    #doctest: +SKIP

        ..
        """
        result = libvect.Vect_write_line(self.c_mapinfo, geo_obj.gtype,
                                         geo_obj.c_points, geo_obj.c_cats)
        if result == -1:
            raise GrassError("Not able to write the vector feature.")
        if self._topo_level == 2:
            # return new feature id (on level 2)
            geo_obj.id = result
        else:
            # return offset into file where the feature starts (on level 1)
            geo_obj.offset = result


#=============================================
# VECTOR WITH TOPOLOGY
#=============================================

class VectTopo(Vector):
    def __init__(self, name, mapset=''):
        super(VectTopo, self).__init__(name, mapset)
        self._topo_level = 2
        self._class_name = 'VectTopo'

    def __len__(self):
        return libvect.Vect_get_num_lines(self.c_mapinfo)

    def __getitem__(self, key):
        """::

            >>> mun = VectTopo('boundary_municp_sqlite')
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

    def num_primitive_of(self, primitive):
        """primitive are:
            * "boundary",
            * "centroid",
            * "face",
            * "kernel",
            * "line",
            * "point" ::

            >>> rail = VectTopo('rail')
            >>> rail.open()
            >>> rail.num_primitive_of('line')
            10837
            >>> municip = VectTopo('boundary_municp_sqlite')
            >>> municip.open()
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

            >>> municip = VectTopo('boundary_municp_sqlite')
            >>> municip.open()
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
            >>> municip = VectTopo('boundary_municp_sqlite')
            >>> municip.open()
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
            >>> municip.close()

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

            >>> mun = VectTopo('boundary_municp_sqlite')
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

            >>> mun = VectTopo('boundary_municp_sqlite')
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

    def rewrite(self, geo_obj):
        result = libvect.Vect_rewrite_line(self.c_mapinfo,
                                           geo_obj.id, geo_obj.gtype,
                                           geo_obj.c_points,
                                           geo_obj.c_cats)
        # return offset into file where the feature starts
        geo_obj.offset = result

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