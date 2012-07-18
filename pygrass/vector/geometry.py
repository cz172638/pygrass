# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 10:46:25 2012

@author: pietro
"""

import ctypes
import grass.lib.vector as libvect
from vector_type import VTYPE


def read_WKT(string):
    """Read the string and return a geometry object"""
    pass

def read_WKB(buff):
    """Read the binary buffer and return a geometry object"""
    pass

#=============================================
# GEOMETRY
#=============================================

class Point(object):
    """

     'Vect_get_num_line_points',
     'Vect_get_point_in_area',
     'Vect_get_point_in_poly',
     'Vect_get_point_in_poly_isl',

     '',
     'Vect_point_in_area',
     'Vect_point_in_area_outer_ring',
     'Vect_point_in_box',
     'Vect_point_in_island',
     'Vect_point_in_poly',
     'Vect_point_on_line',
     'Vect_points_distance']
    """
    def __init__(self, x, y, z = None):
        self.cx = ctypes.c_double(x)
        self.cy = ctypes.c_double(y)
        self.cz = ctypes.c_double(z) if z else None
        # geometry type
        self.gtype = 'point'

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Point(%g, %g, %g)" % (self.cx.value, self.cy.value,
                                      self.cz.value if self.cz != None else None)

    def __del__(self):
        pass

    def wkt(self):
        """Return a "well know text" (WKT) geometry string"""
        pass

    def wkb(self):
        """Return a "well know binary" (WKB) geometry buffer"""
        pass

    def distance(self, pnt):
        """Calculate distance of 2 points.
        double Vect_points_distance (double x1, double y1, double z1, double x2, double y2, double z2, int with_z)

        """
        pass

    def buffer(self, dist):
        """Vect_point_buffer2
        """
        pass



class Line(object):
    """
    ['Vect__intersect_line_with_poly',
     'Vect_break_lines',
     'Vect_break_lines_list',
     'Vect_build_line_area',
     'Vect_check_line_breaks',
     'Vect_check_line_breaks_list',
     'Vect_copy_map_lines',
     'Vect_copy_map_lines_field',
     'Vect_delete_line',
     'Vect_destroy_line_struct',
     'Vect_find_line',
     'Vect_find_line_list',
     'Vect_get_line_areas',
     'Vect_get_line_box',
     'Vect_get_line_cat',
     'Vect_get_line_nodes',
     'Vect_get_line_offset',
     'Vect_get_line_type',
     'Vect_get_next_line_id',
     'Vect_get_node_line',
     'Vect_get_node_line_angle',
     'Vect_get_node_n_lines',
     'Vect_get_num_line_points',
     'Vect_get_num_lines',
     'Vect_get_num_updated_lines',
     'Vect_get_updated_line',
     'Vect_get_updated_line_offset',
     'Vect_line_alive',
     'Vect_line_box',
     'Vect_line_buffer',
     'Vect_line_buffer2',
     'Vect_line_check_duplicate',
     'Vect_line_check_intersection',
     'Vect_line_delete_point',
     'Vect_line_distance',
     'Vect_line_geodesic_length',
     'Vect_line_get_intersections',
     'Vect_line_get_point',
     'Vect_line_insert_point',
     'Vect_line_intersection',
     'Vect_line_length',
     'Vect_line_parallel',
     'Vect_line_parallel2',
     'Vect_line_prune',
     'Vect_line_prune_thresh',
     'Vect_line_reverse',
     'Vect_line_segment',
     'Vect_line_to_geos',
     'Vect_merge_lines',
     'Vect_net_get_line_cost',
     'Vect_new_line_struct',
     'Vect_point_on_line',
     'Vect_read_line',
     'Vect_read_line_geos',
     'Vect_read_next_line',
     'Vect_reset_line',
     'Vect_restore_line',
     'Vect_rewrite_line',
     'Vect_select_lines_by_box',
     'Vect_select_lines_by_polygon',
     'Vect_sfa_check_line_type',
     'Vect_sfa_get_line_type',
     'Vect_sfa_is_line_closed',
     'Vect_sfa_is_line_simple',
     'Vect_sfa_line_astext',
     'Vect_sfa_line_dimension',
     'Vect_sfa_line_geometry_type',
     'Vect_snap_lines',
     'Vect_snap_lines_list',
     'Vect_write_line']

struct line_pnts * 	Vect_new_line_struct ()
 	Creates and initializes a line_pnts structure.


int 	Vect_copy_pnts_to_xyz (const struct line_pnts *Points, double *x, double *y, double *z, int *n)
 	Copy points from line structure to array.

    """
    def __init__(self):
        # geometry type
        self.gtype = 'line'

    def __getitem__(self, indx):
        """Get line point of given index.
        int 	Vect_line_get_point (const struct line_pnts *Points, int index, double *x, double *y, double *z)
        """
        pass

    def __iter__(self):
        return (self.__getitem__(i) for i in range(self.__len__()))

    def __len__(self):
        """Return the number of points

        int 	Vect_get_num_line_points (const struct line_pnts *Points)
        Get number of line points."""

    def __str__(self):
        pass

    def __repr__(self):
        pass

    def __del__(self):
        """Frees all memory associated with a line_pnts structure, including the structure itself.
        void 	Vect_destroy_line_struct (struct line_pnts *p)
        """
        pass

    def copy_xyz(self):
        """Copy points from array to line_pnts structure.
        int 	Vect_copy_xyz_to_pnts (struct line_pnts *Points, const double *x, const double *y, const double *z, int n)

        """
        pass

    def contain_pnt(self, pnt):
        """Find point on line in the specified distance.
        int 	Vect_point_on_line (const struct line_pnts *Points, double distance, double *x, double *y, double *z, double *angle, double *slope)
        """
        pass

    def append(self, pnt):
        """Appends one point to the end of a line.
        int 	Vect_append_point (struct line_pnts *Points, double x, double y, double z)
        """
        pass

    def bbox(self):
        """Get bounding box of line.
        void 	Vect_line_box (const struct line_pnts *Points, struct bound_box *Box)
        """
        pass

    def extend(self, pnts):
        """Appends points to the end of a line.

        int 	Vect_append_points (struct line_pnts *Points, const struct line_pnts *APoints, int direction)

        """
        pass

    def insert(self, indx, pnt):
        """Insert new point at index position and move all old points at that position and above up.
        int 	Vect_line_insert_point (struct line_pnts *Points, int index, double x, double y, double z)
        """
        pass

    def length(self):
        """Calculate line length, 3D-length in case of 3D vector line.
        double 	Vect_line_length (const struct line_pnts *Points)
 	   """
        pass

    def length_geodesic(self):
        """Calculate line length.
        double 	Vect_line_geodesic_length (const struct line_pnts *Points)
        """
        pass

    def line_distance(self):
        """Calculate line distance.
        int 	Vect_line_distance (const struct line_pnts *points, double ux, double uy, double uz, int with_z, double *px, double *py, double *pz, double *dist, double *spdist, double *lpdist)
        """
        pass

    def get_first_cat(self):
        """Fetches FIRST category number for given vector line and field.
        int 	Vect_get_line_cat (const struct Map_info *Map, int line, int field)
        """
        pass

    def pop(self, indx):
        pass

    def prune(self):
        """Remove duplicate points, i.e. zero length segments.

        int 	Vect_line_prune (struct line_pnts *Points)
        """
        pass

    def prune_thresh(self):
        """Remove points in threshold.
        int 	Vect_line_prune_thresh (struct line_pnts *Points, double threshold)

        """
        pass

    def remove(self, pnt):
        """Delete point at given index and move all points above down.
        int 	Vect_line_delete_point (struct line_pnts *Points, int index)

        """
        pass

    def reverse(self):
        """Reverse the order of vertices.
        void 	Vect_line_reverse (struct line_pnts *Points)
        """
        pass

    def segment(self):
        """Create line segment.
        int 	Vect_line_segment (const struct line_pnts *InPoints, double start, double end, struct line_pnts *OutPoints)
        """
        pass

    def wkt(self):
        pass

    def wkb(self):
        pass

    def distance(self, geom):
        pass


    def buffer(self, dist, type = 'circle'):
        pass

    def reset(self):
        """Reset line.
        void 	Vect_reset_line (struct line_pnts *Points)
        """
        pass



class Boundary(Line):
    """
    ['Vect_get_area_boundaries',
     'Vect_get_isle_boundaries',
     'bound_box',
     'struct_bound_box']
    """
    def __init__(self):
        # geometry type
        self.gtype = 'boundary'

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
     'Vect_isle_find_area',
     'Vect_point_in_island',
     'Vect_select_isles_by_box']
    """
    pass

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


    def __init__(self):
        #self.boundary
        #self.centroid
        # geometry type
        self.gtype = 'area'

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

        int Vect_get_area_boundaries(const struct Map_info *Map, int area, struct ilist *List)
        """

    def cats(self):
        """Get area categories.
        int Vect_get_area_cats (const struct Map_info *Map, int area, struct line_cats *Cats)
        """
        pass

    def get_first_cat(self):
        """Find FIRST category of given field and area.

        int Vect_get_area_cat(const struct Map_info *Map, int area, int field)
        """
        pass

    def contain_pnt(self):
        """Check if point is in area.
        int Vect_point_in_area(double x, double y, const struct Map_info *Map, int area, struct bound_box box)
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
        int 	Vect_get_area_points (const struct Map_info *Map, int area, struct line_pnts *BPoints)
        """
        pass

    def isles_boundary(self):
        """Creates list of boundaries for given isle.

        int Vect_get_isle_boundaries (const struct Map_info *Map, int isle, struct ilist *List)
        """

    def isles_points(self):
        """Returns polygon array of points for given isle.
        int 	Vect_get_isle_points (const struct Map_info *Map, int isle, struct line_pnts *BPoints)
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

