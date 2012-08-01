# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 10:46:25 2012

@author: pietro

"""
#import grass.lib.gis as libgis
#libgis.G_gisinit('')
import ctypes
import grass.lib.vector as libvect
#from vector_type import VTYPE
import numpy as np
import re
from collections import Iterable
from basic import Ilist, Bbox

WKT = {  # 'POINT\(\s*([+-]*\d+\.*\d*)+\s*\)'
       'POINT\((.*)\)': 'point',
       'LINESTRING\((.*)\)': 'line'}


def read_WKT(string):
    """Read the string and return a geometry object

    WKT:
    POINT(0 0)
    LINESTRING(0 0,1 1,1 2)
    POLYGON((0 0,4 0,4 4,0 4,0 0),(1 1, 2 1, 2 2, 1 2,1 1))
    MULTIPOINT(0 0,1 2)
    MULTILINESTRING((0 0,1 1,1 2),(2 3,3 2,5 4))
    MULTIPOLYGON(((0 0,4 0,4 4,0 4,0 0),(1 1,2 1,2 2,1 2,1 1)), ((-1 -1,-1 -2,-2 -2,-2 -1,-1 -1)))
    GEOMETRYCOLLECTION(POINT(2 3),LINESTRING(2 3,3 4))


    EWKT:
    POINT(0 0 0) -- XYZ
    SRID=32632;POINT(0 0) -- XY with SRID
    POINTM(0 0 0) -- XYM
    POINT(0 0 0 0) -- XYZM
    SRID=4326;MULTIPOINTM(0 0 0,1 2 1) -- XYM with SRID
    MULTILINESTRING((0 0 0,1 1 0,1 2 1),(2 3 1,3 2 1,5 4 1))
    POLYGON((0 0 0,4 0 0,4 4 0,0 4 0,0 0 0),(1 1 0,2 1 0,2 2 0,1 2 0,1 1 0))
    MULTIPOLYGON(((0 0 0,4 0 0,4 4 0,0 4 0,0 0 0),(1 1 0,2 1 0,2 2 0,1 2 0,1 1 0)),((-1 -1 0,-1 -2 0,-2 -2 0,-2 -1 0,-1 -1 0)))
    GEOMETRYCOLLECTIONM( POINTM(2 3 9), LINESTRINGM(2 3 4, 3 4 5) )
    MULTICURVE( (0 0, 5 5), CIRCULARSTRING(4 0, 4 4, 8 4) )
    POLYHEDRALSURFACE( ((0 0 0, 0 0 1, 0 1 1, 0 1 0, 0 0 0)), ((0 0 0, 0 1 0, 1 1 0, 1 0 0, 0 0 0)), ((0 0 0, 1 0 0, 1 0 1, 0 0 1, 0
    0 0)), ((1 1 0, 1 1 1, 1 0 1, 1 0 0, 1 1 0)), ((0 1 0, 0 1 1, 1 1 1, 1 1 0, 0 1 0)), ((0 0 1, 1 0 1, 1 1 1, 0 1 1, 0 0 1)) )
    TRIANGLE ((0 0, 0 9, 9 0, 0 0))
    TIN( ((0 0 0, 0 0 1, 0 1 0, 0 0 0)), ((0 0 0, 0 1 0, 1 1 0, 0 0 0)) )

    """
    for regexp, obj in WKT.items():
        if re.match(regexp, string):
            geo = 10
            return obj(geo)


def read_WKB(buff):
    """Read the binary buffer and return a geometry object"""
    pass


#=============================================
# GEOMETRY
#=============================================


def get_xyz(pnt):
    """Return a tuple with: x, y, z. ::

        >>> pnt = Point(0, 0)
        >>> get_xyz(pnt)
        (0.0, 0.0, 0.0)
        >>> get_xyz((1, 1))
        (1, 1, 0.0)
        >>> get_xyz((1, 1, 2))
        (1, 1, 2)
        >>> get_xyz((1, 1, 2, 2))                          #doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        ValueError: The the format of the point is not supported: (1, 1, 2, 2)
    """
    if isinstance(pnt, Point):
        if pnt.is2D:
            x, y = pnt.x, pnt.y
            z = 0.
        else:
            x, y, z = pnt.x, pnt.y, pnt.z
    else:
        if len(pnt) == 2:
            x, y = pnt
            z = 0.
        elif len(pnt) == 3:
            x, y, z = pnt
        else:
            str_error = "The the format of the point is not supported: {0!r}"
            raise ValueError(str_error.format(pnt))
    return x, y, z


class Point(object):
    """

    ::

        >>> pnt = Point(0, 0)
        >>> pnt.x
        0.0
        >>> pnt.y
        0.0
        >>> pnt.z
        >>> pnt.is2D
        True
        >>> pnt.coords()
        (0.0, 0.0)
        >>> pnt.z = 0
        >>> pnt.is2D
        False
        >>> pnt
        Point(0.000000, 0.000000, 0.000000)
        >>> print pnt
        POINT(0.000000, 0.000000, 0.000000)
    """
    def __init__(self, x, y, z=None, is2D=True):
        self.c_px = ctypes.pointer(ctypes.c_double())
        self.c_py = ctypes.pointer(ctypes.c_double())
        self.c_pz = ctypes.pointer(ctypes.c_double())
        self.is2D = is2D

        self.x = x
        self.y = y
        self.z = z

        # geometry type
        self.gtype = 'point'

    def _get_x(self):
        return self.c_px.contents.value

    def _set_x(self, value):
        self.c_px.contents.value = value

    x = property(fget=_get_x, fset=_set_x)

    def _get_y(self):
        return self.c_py.contents.value

    def _set_y(self, value):
        self.c_py.contents.value = value

    y = property(fget=_get_y, fset=_set_y)

    def _get_z(self):
        if self.is2D:
            return None
        return self.c_pz.contents.value

    def _set_z(self, value):
        if value is None:
            self.is2D = True
            self.c_pz.contents.value = 0
        else:
            self.c_pz.contents.value = value
            self.is2D = False

    z = property(fget=_get_z, fset=_set_z)

    def __str__(self):
        return self.get_wkt()

    def __repr__(self):
        return "Point(%s)" % ', '.join(['%f' % coord
                                        for coord in self.coords()])

    def __eq__(self, pnt):
        if isinstance(pnt, Point):
            return pnt.coords() == self.coords()

        return Point(*pnt).coords() == self.coords()

    def coords(self):
        """Return a tuple with the point coordinates.
        ::

            >>> pnt = Point(0, 0)
            >>> pnt.coords()
            (0.0, 0.0)

        If the point is 2D return a x, y tuple.
        """
        if self.is2D:
            return self.x, self.y
        else:
            return self.x, self.y, self.z

    def get_wkt(self):
        """Return a "well know text" (WKT) geometry string. ::

            >>> pnt = Point(0, 0)
            >>> pnt.get_wkt()
            'POINT(0.000000, 0.000000)'

        .. warning::

            Only ``POINT`` (2/3D) are supported, ``POINTM`` and ``POINT`` with:
            ``XYZM`` are not supported yet.
        """
        return "POINT(%s)" % ', '.join(['%f' % coord
                                        for coord in self.coords()])

    def get_wkb(self):
        """Return a "well know binary" (WKB) geometry buffer"""
        pass

    def distance(self, pnt):
        """Calculate distance of 2 points, using the Vect_points_distance
        C function, If one of the point have z == None, return the 2D distance.
        ::

            >>> pnt0 = Point(0, 0, 0)
            >>> pnt1 = Point(1, 0)
            >>> pnt0.distance(pnt1)
            1.0
            >>> pnt1.z = 1
            >>> pnt1
            Point(1.000000, 0.000000, 1.000000)
            >>> pnt0.distance(pnt1)
            1.4142135623730951

        The distance method require a :class:Point or a tuple with
        the coordinates.
        """
        if self.is2D or pnt.is2D:
            return libvect.Vect_points_distance(self.x, self.y, 0,
                                                pnt.x, pnt.y, 0, 0)
        else:
            return libvect.Vect_points_distance(self.x, self.y, self.z,
                                                pnt.x, pnt.y, pnt.z, 1)

    def buffer(self, dist=None, dist_x=None, dist_y=None, angle=0,
               round_=True, tol=0.1):
        """Return an Area object using the ``Vect_point_buffer2`` C function.
        Creates buffer around the point (px, py).
        """
        print "Not implemented yet"
        raise
        if dist is not None:
            dist_x = dist
            dist_y = dist
        area = Area()
        libvect.Vect_point_buffer2(self.x, self.y,
                                   dist_x, dist_y,
                                   angle, int(round_), tol,
                                   area.c_points)
        return area


class Line(object):
    """Instantiate a new Line with a list of tuple, or with a list of Point. ::

        >>> line = Line([(0, 0), (1, 1), (2, 0), (1, -1)])
        >>> line                               #doctest: +NORMALIZE_WHITESPACE
        Line([Point(0.000000, 0.000000),
              Point(1.000000, 1.000000),
              Point(2.000000, 0.000000),
              Point(1.000000, -1.000000)])

    ..
    """
    def __init__(self, points=None, c_mapinfo=None, lineid=None, field=None,
                 is2D=True):
        self.c_points = libvect.Vect_new_line_struct()
        self.c_mapinfo = c_mapinfo
        self.lineid = lineid
        self.field = field
        if points is not None:
            for pnt in points:
                self.append(pnt)

        self.is2D = is2D
        # geometry type
        self.gtype = 'line'

    def __getitem__(self, key):
        """Get line point of given index,  slice allowed. ::

            >>> line = Line([(0, 0), (1, 1), (2, 2), (3, 3)])
            >>> line[1]
            Point(1.000000, 1.000000)
            >>> line[-1]
            Point(3.000000, 3.000000)
            >>> line[:2]
            [Point(0.000000, 0.000000), Point(1.000000, 1.000000)]
        """
        #TODO:
        # line[0].x = 10 is not working
        #pnt.c_px = ctypes.pointer(self.c_points.contents.x[indx])
        # pnt.c_px = ctypes.cast(id(self.c_points.contents.x[indx]),
        # ctypes.POINTER(ctypes.c_double))
        if isinstance(key, slice):
            #import pdb; pdb.set_trace()
            #Get the start, stop, and step from the slice
            return [Point(self.c_points.contents.x[indx],
                          self.c_points.contents.y[indx],
                    None if self.is2D else self.c_points.contents.z[indx])
                    for indx in xrange(*key.indices(len(self)))]
        elif isinstance(key, int):
            if key < 0:  # Handle negative indices
                key += self.c_points.contents.n_points
            if key >= self.c_points.contents.n_points:
                raise IndexError('Index out of range')
            return Point(self.c_points.contents.x[key],
                         self.c_points.contents.y[key],
                         None if self.is2D else self.c_points.contents.z[key])
        else:
            raise ValueError("Invalid argument type: %r." % key)

    def __setitem__(self, indx, pnt):
        """Change the coordinate of point. ::

            >>> line = Line([(0, 0), (1, 1)])
            >>> line[0] = (2, 2)
            >>> line
            Line([Point(2.000000, 2.000000), Point(1.000000, 1.000000)])
        """
        x, y, z = get_xyz(pnt)
        self.c_points.contents.x[indx] = x
        self.c_points.contents.y[indx] = y
        self.c_points.contents.z[indx] = z

    def __iter__(self):
        """Return a Point generator of the Line"""
        return (self.__getitem__(i) for i in range(self.__len__()))

    def __len__(self):
        """Return the number of points

        int 	Vect_get_num_line_points (const struct line_pnts *Points)
        Get number of line points."""
        return self.c_points.contents.n_points

    def __str__(self):
        return self.get_wkt()

    def __repr__(self):
        return "Line([%s])" % ', '.join([repr(pnt) for pnt in self.__iter__()])

#    def __del__(self):
# """Frees all memory associated with a line_pnts structure, including the
# structure itself.
#        void 	Vect_destroy_line_struct (struct line_pnts *p)
#        """
#        libvect.Vect_destroy_line_struct(ctypes.byref(self.c_points))

    def get_pnt(self, distance, angle=0, slope=0):
        """Return a Point object on line in the specified distance, using the
        `Vect_point_on_line` C function.
        Raise a ValueError If the distance exceed the Line length. ::

            >>> line = Line([(0, 0), (1, 1)])
            >>> line.get_pnt(5)                           #doctest: +ELLIPSIS
            Traceback (most recent call last):
                ...
            ValueError: The distance exceed the lenght of the line, that is: 1.414214
            >>> line.get_pnt(1)
            Point(0.707107, 0.707107)
        """
        # instantiate an empty Point object
        maxdist = self.length()
        if distance > maxdist:
            str_err = "The distance exceed the lenght of the line, that is: %f"
            raise ValueError(str_err % maxdist)
        pnt = Point(0, 0, -9999)
        libvect.Vect_point_on_line(self.c_points, distance,
                                   pnt.c_px, pnt.c_py, pnt.c_pz,
                                   angle, slope)
        pnt.is2D = self.is2D
        return pnt

    def append(self, pnt):
        """Appends one point to the end of a line, using the
        ``Vect_append_point`` C function. ::

            >>> line = Line()
            >>> line.append((10, 100))
            >>> line
            Line([Point(10.000000, 100.000000)])
            >>> line.append((20, 200))
            >>> line
            Line([Point(10.000000, 100.000000), Point(20.000000, 200.000000)])

        Like python list.
        """
        x, y, z = get_xyz(pnt)
        libvect.Vect_append_point(self.c_points, x, y, z)

    def bbox(self):
        """Return the bounding box of the line, using ``Vect_line_box``
        C function. ::

            >>> line = Line([(0, 0), (0, 1), (2, 1), (2, 0)])
            >>> bbox = line.bbox()
            >>> bbox.north
            1.0
            >>> bbox.south
            0.0
            >>> bbox.east
            2.0
            >>> bbox.west
            0.0
            >>> bbox.top
            0.0
            >>> bbox.bottom
            0.0

        It is possible to access to the C struct of the object with:
        ``bbox.c_bbox``
        """
        bbox = Bbox()
        libvect.Vect_line_box(self.c_points, bbox.c_bbox)
        return bbox

    def extend(self, line, forward=True):
        """Appends points to the end of a line.

        It is possible to extend a line, give a list of points, or directly
        with a line_pnts struct.

        If forward is True the line is extend forward otherwise is extend
        backward. The method use the `Vect_append_points` C function. ::

            >>> line = Line([(0, 0), (1, 1)])
            >>> line.extend( Line([(2, 2), (3, 3)]) )
            >>> line                           #doctest: +NORMALIZE_WHITESPACE
            Line([Point(0.000000, 0.000000),
                  Point(1.000000, 1.000000),
                  Point(2.000000, 2.000000),
                  Point(3.000000, 3.000000)])

        Like python list, it is possible to extend a line, with another line
        or with a list of points.
        """
        # set direction
        if forward:
            direction = libvect.GV_FORWARD
        else:
            direction = libvect.GV_BACKWARD
        # check if is a Line object
        if isinstance(line, Line):
            c_points = line.c_points
        else:
            # instantiate a Line object
            lin = Line()
            for pnt in line:
                # add the points to the line
                lin.append(pnt)
            c_points = lin.c_points

        libvect.Vect_append_points(self.c_points, c_points, direction)

    def insert(self, indx, pnt):
        """Insert new point at index position and move all old points at
        that position and above up, using ``Vect_line_insert_point``
        C function. ::

            >>> line = Line([(0, 0), (1, 1)])
            >>> line.insert(0, Point(1.000000, -1.000000) )
            >>> line                           #doctest: +NORMALIZE_WHITESPACE
            Line([Point(1.000000, -1.000000),
                  Point(0.000000, 0.000000),
                  Point(1.000000, 1.000000)])

        ..
        """
        if indx < 0:  # Handle negative indices
            indx += self.c_points.contents.n_points
        if indx >= self.c_points.contents.n_points:
            raise IndexError('Index out of range')
        x, y, z = get_xyz(pnt)
        libvect.Vect_line_insert_point(self.c_points, indx, x, y, z)

    def length(self):
        """Calculate line length, 3D-length in case of 3D vector line, using
        `Vect_line_length` C function.  ::

            >>> line = Line([(0, 0), (1, 1), (0, 1)])
            >>> line.length()
            2.414213562373095

        ..
        """
        return libvect.Vect_line_length(self.c_points)

    def length_geodesic(self):
        """Calculate line length, usig `Vect_line_geodesic_length` C function.
        ::

            >>> line = Line([(0, 0), (1, 1), (0, 1)])
            >>> line.length_geodesic()
            2.414213562373095

        ..
        """
        return libvect.Vect_line_geodesic_length(self.c_points)

    def distance(self, pnt):
        """Return a tuple with:

            * the closest point on the line,
            * the distance between these two points,
            * distance of point from segment beginning
            * distance of point from line

        The distance is compute using the ``Vect_line_distance`` C function.
        """
        # instantite outputs
        cx = ctypes.c_double(0)
        cy = ctypes.c_double(0)
        cz = ctypes.c_double(-9999)
        dist = ctypes.c_double(0)
        sp_dist = ctypes.c_double(0)
        lp_dist = ctypes.c_double(0)

        libvect.Vect_line_distance(self.c_points,
                                   pnt.x, pnt.y, pnt.z, 0 if self.is2D else 1,
                                   ctypes.byref(cx), ctypes.byref(cy),
                                   ctypes.byref(cz), ctypes.byref(dist),
                                   ctypes.byref(sp_dist),
                                   ctypes.byref(lp_dist))
        # instantiate the Point class
        point = Point(cx.value, cy.value, cz.value)
        point.is2D = self.is2D
        return point, dist, sp_dist, lp_dist

    def get_first_cat(self):
        """Fetches FIRST category number for given vector line and field, using
        the ``Vect_get_line_cat`` C function.
        """
        libvect.Vect_get_line_cat(self.map, self.lineid, self.field)
        pass

    def pop(self, indx):
        """Return the point in the index position and remove from the Line. ::

            >>> line = Line([(0, 0), (1, 1), (2, 2)])
            >>> midle_pnt = line.pop(1)
            >>> midle_pnt
            Point(1.000000, 1.000000)
            >>> line
            Line([Point(0.000000, 0.000000), Point(2.000000, 2.000000)])

        ..
        """
        if indx < 0:  # Handle negative indices
            indx += self.c_points.contents.n_points
        if indx >= self.c_points.contents.n_points:
            raise IndexError('Index out of range')
        pnt = self.__getitem__(indx)
        libvect.Vect_line_delete_point(self.c_points, indx)
        return pnt

    def delete(self, indx):
        """Remove the point in the index position. ::

            >>> line = Line([(0, 0), (1, 1), (2, 2)])
            >>> line.delete(-1)
            >>> line
            Line([Point(0.000000, 0.000000), Point(1.000000, 1.000000)])

        ..
        """
        if indx < 0:  # Handle negative indices
            indx += self.c_points.contents.n_points
        if indx >= self.c_points.contents.n_points:
            raise IndexError('Index out of range')
        libvect.Vect_line_delete_point(self.c_points, indx)

    def prune(self):
        """Remove duplicate points, i.e. zero length segments, using
        `Vect_line_prune` C function. ::

            >>> line = Line([(0, 0), (1, 1), (1, 1), (2, 2)])
            >>> line.prune()
            >>> line                           #doctest: +NORMALIZE_WHITESPACE
            Line([Point(0.000000, 0.000000),
                  Point(1.000000, 1.000000),
                  Point(2.000000, 2.000000)])

        ..
        """
        libvect.Vect_line_prune(self.c_points)

    def prune_thresh(self, threshold):
        """Remove points in threshold, using the ``Vect_line_prune_thresh``
        C funtion."""
        libvect.Vect_line_prune(self.c_points, threshold)

    def remove(self, pnt):
        """Delete point at given index and move all points above down, using
        `Vect_line_delete_point` C function. ::

            >>> line = Line([(0, 0), (1, 1), (2, 2)])
            >>> line.remove((2, 2))
            >>> line[-1]
            Point(1.000000, 1.000000)

        ..
        """
        for indx, point in enumerate(self.__iter__()):
            if pnt == point:
                libvect.Vect_line_delete_point(self.c_points, indx)
                return
        raise ValueError('list.remove(x): x not in list')

    def reverse(self):
        """Reverse the order of vertices, using `Vect_line_reverse`
        C function. ::

            >>> line = Line([(0, 0), (1, 1), (2, 2)])
            >>> line.reverse()
            >>> line                           #doctest: +NORMALIZE_WHITESPACE
            Line([Point(2.000000, 2.000000),
                  Point(1.000000, 1.000000),
                  Point(0.000000, 0.000000)])

        ..
        """
        libvect.Vect_line_reverse(self.c_points)

    def segment(self, start, end):
        """Create line segment. using the ``Vect_line_segment`` C function."""
        line = Line()
        libvect.Vect_line_segment(self.c_points, start, end, line.c_points)
        return line

    def tolist(self):
        """Return a list of tuple. ::

            >>> line = Line([(0, 0), (1, 1), (2, 0), (1, -1)])
            >>> line.tolist()
            [(0.0, 0.0), (1.0, 1.0), (2.0, 0.0), (1.0, -1.0)]

        .. dummmy
        """
        return [pnt.coords() for pnt in self.__iter__()]

    def toarray(self):
        """Return an array of coordinates. ::

            >>> line = Line([(0, 0), (1, 1), (2, 0), (1, -1)])
            >>> line.toarray()                 #doctest: +NORMALIZE_WHITESPACE
            array([[ 0.,  0.],
                   [ 1.,  1.],
                   [ 2.,  0.],
                   [ 1., -1.]])

        ..
        """
        return np.array(self.tolist())

    def get_wkt(self):
        """Return a Well Known Text string of the line. ::

            >>> line = Line([(0, 0), (1, 1), (1, 2)])
            >>> line.get_wkt()
            'LINESTRING(0.000000 0.000000, 1.000000 1.000000, 1.000000 2.000000)'

        ..
        """
        return "LINESTRING(%s)" % ', '.join([
               ' '.join(['%f' % coord for coord in pnt.coords()])
               for pnt in self.__iter__()])

    def from_wkt(self, wkt):
        """Read a WKT string. ::

            >>> line = Line()
            >>> line.from_wkt("LINESTRING(0 0,1 1,1 2)")
            >>> line                           #doctest: +NORMALIZE_WHITESPACE
            Line([Point(0.000000, 0.000000),
                  Point(1.000000, 1.000000),
                  Point(1.000000, 2.000000)])

        ..
        """
        match = re.match('LINESTRING\((.*)\)', wkt)
        if match:
            self.reset()
            for coord in match.groups()[0].strip().split(','):
                self.append(tuple([float(e) for e in coord.split(' ')]))
        else:
            return None

    def get_wkb(self):
        pass

    def buffer(self, dist=None, dist_x=None, dist_y=None,
               angle=0, round_=True, tol=0.1):
        """Return the buffer area around the line, using the
        ``Vect_line_buffer2`` C function.

        .. warning::
            Not implemented yet.
        """
        if dist is not None:
            dist_x = dist
            dist_y = dist
        area = Area()
        libvect.Vect_line_buffer2(self.c_points,
                                  dist_x, dist_y,
                                  angle, int(round_), tol,
                                  area.boundary.c_points,
                                  area.isles.c_points,
                                  area.num_isles)
        return area

    def reset(self):
        """Reset line, using `Vect_reset_line` C function. ::

            >>> line = Line([(0, 0), (1, 1), (2, 0), (1, -1)])
            >>> len(line)
            4
            >>> line.reset()
            >>> len(line)
            0
            >>> line
            Line([])

        ..
        """
        libvect.Vect_reset_line(self.c_points)



class Boundary(object):
    """
    ['Vect_get_area_boundaries',
     'Vect_get_isle_boundaries',]
    """
    def __init__(self, area_id, c_mapinfo, lines=None, left=None, right=None):
        self.area_id = area_id
        self.c_mapinfo = c_mapinfo
        self.ilist = Ilist()
        self.lines = lines
        if len(lines) != len(left) or len(lines) != len(right):
            str_err = "Left and right must have the same length of lines"
            raise ValueError(str_err)
        self.left = Ilist()
        self.right = right
        # geometry type
        self.gtype = 'boundary'

    def boundaries(self):
        """Returna Ilist object with the line id"""
        bounds = Ilist()
        libvect.Vect_get_area_boundaries(self.c_mapinfo, self.area_id,
                                         bounds.c_ilist)
        return bounds


class Centroid(Point):
    """
    ['Vect_attach_centroids',
     'Vect_find_poly_centroid',
     'Vect_get_area_centroid',
     'Vect_get_centroid_area']
    """
    def __init__(self):
        # geometry type
        self.gtype = 'centroid'


class Isle(object):
    """
    ['Vect_attach_isle',
     'Vect_attach_isles',
     'Vect_find_island',
     'Vect_get_area_isle',
     'Vect_get_area_num_isles',
     'Vect_get_isle_area',
     'Vect_get_isle_boundaries',
     'Vect_get_isle_box',
     'Vect_get_isle_points',
     'Vect_get_isle_points_geos',
     'Vect_get_num_islands',
     'Vect_get_point_in_poly_isl',
     'Vect_isle_alive',
     'Vect_point_in_island',
     'Vect_select_isles_by_box']
    """
    def __init__(self, isle_id, c_mapinfo):
        self.isle_id = isle_id
        self.c_mapinfo = c_mapinfo
        #self.area_id = area_id

    def __repr__(self):
        return "Isle(%d, %d)" % (self.isle_id)

    def boundaries(self):
        ilist = Ilist()
        libvect.Vect_get_isle_boundaries(self.c_mapinfo, self.isle_id,
                                         ilist.c_ilist)
        return ilist

    def bbox(self):
        bbox = Bbox()
        libvect.Vect_get_isle_box(self.c_mapinfo, self.isle_id, bbox.c_bbox)
        return bbox

    def points(self):
        """Return a Line object with the outer ring points"""
        line = Line()
        libvect.Vect_get_isle_points(self.c_mapinfo, line.c_points)
        return line

    def points_geos(self):
        """Return a Line object with the outer ring points
        """
        line = Line()
        libvect.Vect_get_isle_points_geos(self.c_mapinfo, line.c_points)
        return line

    def area_id(self):
        """Returns area id for isle."""
        return libvect.Vect_get_isle_area(self.c_mapinfo, self.isle_id)

    def alive(self):
        """Check if isle is alive or dead (topology required)"""
        return bool(libvect.Vect_isle_alive(self.c_mapinfo, self.isle_id))

    def contain_pnt(self, pnt):
        """Check if point is in area."""
        bbox = self.bbox()
        return bool(libvect.Vect_point_in_island(pnt.x, pnt.y,
                                                 self.c_mapinfo, self.isle_id,
                                                 bbox.c_bbox.contents))

class Isles(object):
    def __init__(self, c_mapinfo, area_id):
        self.c_mapinfo = c_mapinfo
        self.area_id = area_id
        self._isles_id = self.get_isles_id()
        self._isles = self.get_isles()


    def __len__(self):
        return libvect.Vect_get_area_num_isles(self.c_mapinfo, self.area_id)

    def __repr__(self):
        return "Isles(%r)" % self._isles

    def __getitem__(self, key):
        return self._isles[key]

    def get_isles_id(self):
        return [libvect.Vect_get_area_isle(self.c_mapinfo, i)
                for i in range(self.__len__())]

    def get_isles(self):
        return [Isle(isle_id, self.c_mapinfo, self.area_id)
                for isle_id in self._isles_id]



class Area(object):
    """
     'Vect_build_line_area',
     'Vect_find_area',
     'Vect_get_area_box',
     'Vect_get_area_points_geos',
     'Vect_get_centroid_area',

     'Vect_get_isle_area',
     'Vect_get_line_areas',
     'Vect_get_num_areas',
     'Vect_get_point_in_area',
     'Vect_isle_find_area',
     'Vect_point_in_area',
     'Vect_point_in_area_outer_ring',

     'Vect_read_area_geos',
     'Vect_remove_small_areas',
     'Vect_select_areas_by_box',
     'Vect_select_areas_by_polygon']
    """

    def __init__(self, area_id=None, c_mapinfo=None,
                 boundary=None, centroid=None, isles=[]):
        self.area_id = area_id
        self.c_mapinfo = c_mapinfo
        self.boundary = self.get_boundary()
        self.centroid = centroid
        self.isles = Ilist()
        # geometry type
        self.gtype = 'area'

    def init_from_id(self, area_id=None):
        """Return an Area object"""
        if area_id is None and self.area_id is None:
            raise ValueError("You need to give or set the area_id")
        self.area_id = area_id if area_id is not None else self.area_id
        # get boundary
        self.get_boundary()
        # get isles
        self.get_isles()
        pass

    def boundary(self):
        """Return a Line object with the outer ring"""
        line = Line()
        libvect.Vect_get_area_points(self.c_mapinfo, self.area_id,
                                     line.c_points)
        return line

    def centroid(self):
        centroid_id = libvect.Vect_get_area_centroid(self.c_mapinfo,
                                                     self.area_id)
        return Centroid(self.c_mapinfo, centroid)

    def num_isles(self):
        return libvect.Vect_get_area_num_isles(self.c_mapinfo, self.area_id)


    def get_isles(self):
        """Instantiate the boundary attribute reading area_id"""
        return Isles(self.c_mapinfo, self.area_id)
#        num_isles = libvect.Vect_get_area_num_isles(self.c_mapinfo,
#                                                    self.area_id,)
#        isles = [libvect.Vect_get_area_isle(self.c_mapinfo, i)
#                 for i in range(num_isles)]
#
#        libvect.Vect_get_isle_boundaries(self.c_mapinfo, isle_id,
#                                         self.boundary.c_ilist)

    def area(self):
        """Returns area of area without areas of isles.
        double Vect_get_area_area (const struct Map_info *Map, int area)

        """
        pass

    def alive(self):
        """Check if area is alive or dead (level 2 required)

        Parameters :
        Map	pointer to Map_info structure
        area	area id

        Returns:
        1 area alive
        0 area is dead

        int Vect_area_alive(const struct Map_info *Map, int area)
        """
        pass

    def bbox(self):
        """
        Vect_get_area_box
        """
        pass

    def buffer(self):
        """Creates buffer around area.

        Parameters:
        Map	vector map
        area	area id
        da	distance along major axis
        db	distance along minor axis
        dalpha	angle between 0x and major axis
        round	make corners round
        caps	add caps at line ends
        tol	maximum distance between theoretical arc and output segments
        [out]	oPoints	output polygon outer border (ccw order)
        [out]	inner_count	number of holes
        [out]	iPoints	array of output polygon's holes (cw order)

        void Vect_area_buffer2(const struct Map_info * Map,
                               int 	area,
                               double 	da,
                               double 	db,
                               double 	dalpha,
                               int 	round,
                               int 	caps,
                               double 	tol,
                               struct line_pnts ** 	oPoints,
                               struct line_pnts *** 	iPoints,
                               int * 	inner_count)
        """
        pass

    def boundaries(self):
        """Creates list of boundaries for given area.

        int Vect_get_area_boundaries(const struct Map_info *Map,
                                     int area, struct ilist *List)
        """

    def cats(self):
        """Get area categories.
        int Vect_get_area_cats (const struct Map_info *Map,
                                int area, struct line_cats *Cats)
        """
        pass

    def get_first_cat(self):
        """Find FIRST category of given field and area.

        int Vect_get_area_cat(const struct Map_info *Map, int area, int field)
        """
        pass

    def contain_pnt(self):
        """Check if point is in area.
        int Vect_point_in_area(double x, double y,
                               const struct Map_info *Map,
                               int area, struct bound_box box)
        """
        pass

    def centroid(self):
        """Returns centroid id for given area.

        int Vect_get_area_centroid(const struct Map_info *Map, int area)
        """
        pass

    def perimeter(self):
        """Calculate area perimeter.

        double Vect_area_perimeter (const struct line_pnts *Points)

        """

    def points(self):
        """Returns polygon array of points (outer ring) of given area.
        int 	Vect_get_area_points (const struct Map_info *Map,
                                   int area, struct line_pnts *BPoints)
        """
        pass

    def isles_boundary(self):
        """Creates list of boundaries for given isle.

        int Vect_get_isle_boundaries (const struct Map_info *Map,
                                      int isle, struct ilist *List)
        """

    def isles_points(self):
        """Returns polygon array of points for given isle.
        int 	Vect_get_isle_points(const struct Map_info *Map,
                                    int isle, struct line_pnts *BPoints)
        """
        pass

    def num_isles(self):
        """Returns number of isles for given area.

        int Vect_get_area_num_isles (const struct Map_info *Map, int area)
        """
        pass

    def isle_id(self):
        """Returns isle id for area.

        int Vect_get_area_isle (const struct Map_info *Map, int area, int isle)
        """
        pass

    def id_area(self):
        """Returns area id for isle.

        int 	Vect_get_isle_area (const struct Map_info *Map, int isle)
        """
        pass