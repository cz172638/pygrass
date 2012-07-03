.. _raster-label:

Raster
======

PyGrass use 4 different Raster classes, that respect the 4 different approaches
of C grass API. PyGrass Allow user to open the maps, in read and write mode,
row by row (:ref:`RasterRow-label` class) using the
`Raster library`_, using the `RowIO library`_ (:ref:`RasterRowIO-label` class),
using the `Segmentation library`_ that allow users to read and write the map
at the same time (:ref:`RasterSegment-label` class), and using the numpy
interface to the map (:ref:`RasterNumpy-label` class).


==========================  =======================  ========  ============
Class Name                  C library                Read      Write
==========================  =======================  ========  ============
:ref:`RasterRow-label`      `Raster library`_        randomly  sequentially
:ref:`RasterRowIO-label`    `RowIO library`_         cached    no
:ref:`RasterSegment-label`  `Segmentation library`_  cached    randomly
:ref:`RasterNumpy-label`    `numpy.memmap`_          cached    randomly
==========================  =======================  ========  ============


All these classes share common methods and attributes, necessary to address
common tasks as rename, remove, open, close, exist, isopen.
In the next exmples we instantiate a RasterRow object. ::

    >>> import pygrass
    >>> elev = pygrass.RasterRow('elevation')
    >>> elev.name
    'elevation'
    >>> print(elev)
    elevation@PERMANENT
    >>> elev.exist()
    True
    >>> elev.isopen()
    False
    >>> new = pygrass.RasterRow('new')
    >>> new.exist()
    False
    >>> new.isopen()
    False


We can rename the map:   ::

    >>> # setting the attribute
    >>> new.name = 'new_map'
    >>> print(new)
    new_map
    >>> # or using the rename methods
    >>> new.rename('new')
    >>> print(new)
    new




.. _RasterCategory-label:

Categories
----------

It is possible to check if the map has or not the categories with the
``has_cats`` method. ::

    >>> elev.has_cats()
    False

Opening a map that has category, for example the "landcove_1m" raster map
from the North Carolina mapset. The ``has_cats`` method return True. ::

    >>> land = pygrass.RasterRow('landcover_1m')
    >>> land.has_cats()
    True

Get and set the categories title, with: ::

    >>> land.cats_title
    'Rural area: Landcover'
    >>> land.cats_title = 'Rural area: Landcover2'
    >>> land.cats_title
    'Rural area: Landcover2'
    >>> land.cats_title = 'Rural area: Landcover'

Get the number of categories of the map with: ::

    >>> land.num_cats()
    11

See all the categories with: ::

    >>> land.cats
    [('pond', 1, 1),
     ('forest', 2, 2),
     ('developed', 3, 3),
     ('bare', 4, 4),
     ('paved road', 5, 5),
     ('dirt road', 6, 6),
     ('vineyard', 7, 7),
     ('agriculture', 8, 8),
     ('wetland', 9, 9),
     ('bare ground path', 10, 10),
     ('grass', 11, 11)]

Access to single category, using Rast_get_ith_cat(), with: ::

    >>> land.cats[0]
    ('pond', 1, 1)
    >>> land.cats['pond']
    ('pond', 1, 1)
    >>> land.get_cat(0)
    ('pond', 1, 1)
    >>> land.get_cat('pond')
    ('pond', 1, 1)

Add new or change existing categories: ::

    >>> land.set_cat('label', 1, 1)
    >>> land.get_cat('label')
    ('label', 1, 1)
    >>> land.set_cat('pond', 1, 1)


Sort categories, with: ::

    >>> land.sort_cats()


Copy categories from another raster map with: ::

    >>> land.copy_cats(elev)

Read and Write: ::

    >>> land.read_cats()
    >>> #land.write_cats()

Get a Category object or set from a Category object: ::

    >>> cats = land.get_cats()
    >>> land.set_cats(cats)



.. _RasterRow-label:

RastRow
-------

The RasterRow class use the Grass C API to read and write the map, there is not
support to read and write to the same map at the same time, for this
functionality, please see the RasterSegment class.
The RasterRow class allow to read in a randomly order the row from a map, but
it is only possible to write the map using only a sequence order, therefore every
time you are writing a new map, the row is add to the file as the last row. ::

    >>> pygrass = reload(pygrass)
    >>> elev = pygrass.RasterRow('elevation')
    >>> # the cols attribute is set from the current region only when the map is open
    >>> elev.cols
    >>> elev.open()
    >>> elev.isopen()
    True
    >>> elev.cols
    1500
    >>> # we can read the elevation map, row by row
    >>> for row in elev[:5]: print(row[:3])
    [ 141.99613953  141.27848816  141.37904358]
    [ 142.90461731  142.39450073  142.68611145]
    [ 143.81854248  143.54707336  143.83972168]
    [ 144.56524658  144.58493042  144.86477661]
    [ 144.99488831  145.22894287  145.57142639]
    >>> # we can open a new map in write mode
    >>> new = pygrass.RasterRow('new', mode = 'w')
    >>> new.open()
    >>> # for each elev row we can perform computation, and write the result into
    >>> # the new map
    >>> for row in elev:
    ...     new.put_row(row < 144)
    ...
    >>> # close the maps
    >>> new.close()
    >>> elev.close()
    >>> # check if the map exist
    >>> new.exist()
    True
    >>> # we can open the map in read mode
    >>> new.open('r')
    >>> for row in new[:5]: print(row[:3])
    [1 1 1]
    [1 1 1]
    [1 1 1]
    [0 0 0]
    [0 0 0]
    >>> new.close()
    >>> new.remove()
    >>> new.exist()
    False


.. _RasterRowIO-label:

RasterRowIO
-----------

The RasterRowIO class use the grass `RowIO library`_, and implement a row
cache. The RasterRowIO class support only reading the raster, because the
raster rows can only be written in sequential order, writing by row id is not
supported by design. Hence, we should use the rowio lib only for caching rows
for reading and use the default row write access as in the RasterRow class. ::

    >>> pygrass = reload(pygrass)
    >>> elev = pygrass.RasterRowIO('elevation')
    >>> elev.open()
    >>> for row in elev[:5]: print(row[:3])
    [ 141.99613953  141.27848816  141.37904358]
    [ 142.90461731  142.39450073  142.68611145]
    [ 143.81854248  143.54707336  143.83972168]
    [ 144.56524658  144.58493042  144.86477661]
    [ 144.99488831  145.22894287  145.57142639]
    >>> elev.close()



.. _RasterSegment-label:

RastSegment
-----------

The RasterSegment class use the grass segment library, it work dividing the
raster map into small different files, that grass read load into the memory
and write to the hardisk.
The segment library allow to open a map in a read-write mode. ::

    >>> pygrass = reload(pygrass)
    >>> elev = pygrass.RasterSegment('elevation')
    >>> elev.open()
    >>> for row in elev[:5]: print(row[:3])
    [ 141.99613953  141.27848816  141.37904358]
    [ 142.90461731  142.39450073  142.68611145]
    [ 143.81854248  143.54707336  143.83972168]
    [ 144.56524658  144.58493042  144.86477661]
    [ 144.99488831  145.22894287  145.57142639]
    >>> new = pygrass.RasterSegment('new')
    >>> new.open()
    >>> for irow in xrange(elev.rows):
    ...     new[irow] = elev[irow] < 144
    ...
    >>> for row in new[:5]: print(row[:3])
    [1 1 1]
    [1 1 1]
    [1 1 1]
    [0 0 0]
    [0 0 0]

The RasterSegment class define two methods to read and write the map:

    * ``get_row`` that return the buffer object with the row that call the
      C function ``segment_get_row``. ::

        >>> # call explicity the method
        >>> elev_row0 = elev.get_row(0)
        >>> # call implicity the method
        >>> elev_row0 = elev[0]

    * ``get`` that return the value of the call map that call the
      C function ``segment_get``. ::

        >>> # call explicity the method
        >>> elev_val_0_0 = elev.get(0, 0)
        >>> # call implicity the method
        >>> elev_val_0_0 = elev[0, 0]

Similarly to write the map, with ``put_row``, to write a row and with ``put``
to write a single value to the map. ::

    >>> # compare the cell value get using the ``get`` method, and take the first
    >>> # value of the row with the ``get_row`` method
    >>> elev[0, 0] == elev[0][0]
    True
    >>> # write a new value to a cell,
    >>> new[0, 0] = 10
    >>> new[0, 0]
    10
    >>> new.close()
    >>> new.exist()
    True
    >>> new.remove()
    >>> elev.close()
    >>> elev.remove()



.. _RasterNumpy-label:

RasterNumpy
-----------

The RasterNumpy class, is based on the `numpy.memmap`_ class If you open an
existing map, the map will be copied on a binary format, and read to avoid
to load all the map in memory. ::

    >>> import pygrass
    >>> elev = pygrass.RasterNumpy('elevation', 'PERMANENT')
    >>> elev.open()
    >>> for row in elev[:5]: print(row[:3])
    [ 141.99613953  141.27848816  141.37904358]
    [ 142.90461731  142.39450073  142.68611145]
    [ 143.81854248  143.54707336  143.83972168]
    [ 144.56524658  144.58493042  144.86477661]
    [ 144.99488831  145.22894287  145.57142639]
    >>> # in this case RasterNumpy is an extention of the numpy class
    >>> # therefore you may use all the fancy things of numpy.
    >>> elev[:5, :3]
    RasterNumpy([[ 141.99613953,  141.27848816,  141.37904358],
           [ 142.90461731,  142.39450073,  142.68611145],
           [ 143.81854248,  143.54707336,  143.83972168],
           [ 144.56524658,  144.58493042,  144.86477661],
           [ 144.99488831,  145.22894287,  145.57142639]], dtype=float32)
    >>> el = elev < 144
    >>> el[:5, :3]
    RasterNumpy([[1, 1, 1],
           [1, 1, 1],
           [1, 1, 1],
           [0, 0, 0],
           [0, 0, 0]], dtype=int32)
    >>> el.name == None
    True
    >>> # give a name to the new map
    >>> el.name = 'new'
    >>> el.close()
    >>> el.remove()




.. _Raster library: http://grass.osgeo.org/programming7/rasterlib.html/
.. _RowIO library: http://grass.osgeo.org/programming7/rowiolib.html
.. _Segmentation library: http://grass.osgeo.org/programming7/segmentlib.html
.. _numpy.memmap: http://docs.scipy.org/doc/numpy/reference/generated/numpy.memmap.html

