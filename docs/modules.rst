Modules
=======

Modules code can be generated with the make function, you need to geerate
functions only the first time. The function remove some modules that have
parameters or flags name that are problematic. ::

    >>> from pygrass import modules
    >>> modules.make()
    Module not supported: r.describe           - flag is a number
    Module not supported: r.flow               - flag is a number
    Module not supported: r.in.srtm            - flag is a number
    Module not supported: r.out.arc            - flag is a number
    Module not supported: r.region             - bad parameter name: 3dview
    Module not supported: r.resamp.bspline     - bad parameter name: lambda
    Module not supported: r.rescale            - bad parameter name: from
    Module not supported: r.rescale.eq         - bad parameter name: from
    Module not supported: r.solute.transport   - in in the blacklist
    Module not supported: r.stats              - flag is a number
    Module not supported: r.walk               - bad parameter name: lambda
    Module not supported: r.watershed          - flag is a number

To interact with the python modules: ::

    >>> from pygrass.modules import raster as r

then call function as python function: ::

    >>> slp, asp = r.slope_aspect(elevation='elevation', slope='slp_f',
    ...                           aspect='asp_f', format='percent',
    ...                           overwrite=True)


The function accept Raster object as input, so it is possible to write: ::

    >>> import pygrass
    >>> elev = pygrass.RasterRow('elevation')
    >>> slp, asp = r.slope_aspect(elevation=elev, slope='slp_f',
    ...                           aspect='asp_f', format='percent',
    ...                           overwrite=True)


As default the function return RasterRow objects: ::

    >>> type(slp)
    <class 'pygrass.raster.RasterRow'>
    >>> type(asp)
    <class 'pygrass.raster.RasterRow'>


But it is possible to choose which Raster class should be returned by the
function, defining the option `rtype`. Possible values are: 'row', 'rowio',
'segment', 'numpy', 'str', 'free'.
'str' return the string name, the object that the user pass to the function. ::

    >>> import pygrass
    >>> elev = pygrass.RasterRow('elevation')
    >>> slp = pygrass.RasterRowIO('slp_f')
    >>> asp = pygrass.RasterSegment('asp_f')
    >>> dxx = pygrass.RasterNumpy('dxx')
    >>> slp, asp, dxx = r.slope_aspect(elevation=elev, slope=slp,
    ...                           aspect=asp, dxx = dxx, format='percent',
    ...                           overwrite=True, rtype = 'free')
    >>> type(slp)
    <class 'pygrass.raster.RasterRowIO'>
    >>> type(asp)
    <class 'pygrass.raster.RasterSegment'>
    >>> type(dxx)
    <class 'pygrass.raster.RasterNumpy'>

