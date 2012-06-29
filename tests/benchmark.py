# -*- coding: utf-8 -*-
"""
Created on Sat Jun 16 20:24:56 2012

@author: pietro
"""
import numpy as np
import timeit
import collections
import sys, os

import optparse

sys.path.append(os.getcwd())

from grass.script import core as grasscore
import pygrass
#from grass.script.core import run_command, use_temp_region, del_temp_region

#classes for required options
strREQUIRED = 'required'

class OptionWithDefault(optparse.Option):
    ATTRS = optparse.Option.ATTRS + [strREQUIRED]

    def __init__(self, *opts, **attrs):
        if attrs.get(strREQUIRED, False):
            attrs['help'] = '(Required) ' + attrs.get('help', "")
        optparse.Option.__init__(self, *opts, **attrs)

class OptionParser(optparse.OptionParser):
    def __init__(self, **kwargs):
        kwargs['option_class'] = OptionWithDefault
        optparse.OptionParser.__init__(self, **kwargs)

    def check_values(self, values, args):
        for option in self.option_list:
            if hasattr(option, strREQUIRED) and option.required:
                if not getattr(values, option.dest):
                    self.error("option %s is required" % (str(option)))
        return optparse.OptionParser.check_values(self, values, args)

def run_benchmark(tests, ntimes):
    result = collections.OrderedDict()
    for key, val in tests.iteritems():
        result[key] = {}
        result[key]['timer'] = val
        result[key]['exec time'] = val.timeit( number=ntimes )
        print("{0}; {1:f}; sec/pass".format(key, result[key]['exec time']))
    return result

def print_benchmark(result):
    for key, val in result.iteritems():
        print("{0}; {1:f}; sec/pass".format(key, result[key]['exec time']))

def main():
    """Main function"""
    #usage
    usage = "usage: %prog [options] raster_map"
    parser = OptionParser(usage=usage)
    #password
    parser.add_option("-n", "--ntimes", dest="ntim",
                      help="number of run for each test")
    #username
    parser.add_option("-U", "--username", dest="user", default = "anonymous",
                      help="username for connect to ftp server")

    #random
    parser.add_option("-r", action="store_true", dest="rand",
                      help="If true generate a random map")


    #return options and argument
    (options, args) = parser.parse_args()
    #test if args[0] it is set
    if len(args) == 0:
        parser.error("You have to pass a raster map")
    elif len(args) > 1:
        parser.error("You have to pass only a map")

    raster_name = args[0]

    if options.rand:
        # generate the random map
        pygrass.raster.random_map_only_columns(raster_name, 'DCELL')

    grasscore.use_temp_region()

    grasscore.run_command('g.region', rast=raster_name, flags='p')

    print("Compare r.mapcalc and pygrass classes")


    rmapcalc_SETUP = "from grass.script.core import run_command"

    pygrass_SETUP = """import pygrass
import numpy as np
raster = pygrass.RasterRow('{0}', 'r')
raster.open()""".format(raster_name)

    pygrass_numpy_SETUP = """import pygrass
import numpy as np
raster = pygrass.RasterNumpy('{0}', overwrite = True)
raster.open()""".format(raster_name)

    TEST = collections.OrderedDict( [

    #
    # map += 2
    #
    ('r.mapcalc +2', timeit.Timer(stmt = """
    run_command('r.mapcalc', expression = 'new = %s + 2', overwrite = True)
    """ % raster_name, setup = rmapcalc_SETUP) ),

    ('RasterRow +2', timeit.Timer(stmt = """
    new = pygrass.RasterRow('new', mtype = 'DCELL', mode = 'w', overwrite = True)
    new.open(overwrite = True)
    for row in raster: new.put_row( row + 2)
    new.close()
    """, setup = pygrass_SETUP)),

    ('RasterSeg +2', timeit.Timer(stmt = """
    new = pygrass.RasterSegment('new', mtype = 'DCELL', overwrite = True)
    new.open()
    for irow, row in enumerate(raster): new.put_row(irow, row + 2)
    new.close()
    """, setup = pygrass_SETUP)),

    ('RasterNumpy +2', timeit.Timer(stmt = """
    el = raster + 2
    el.overwrite=True
    el.rename('new')
    el.close()
    """, setup = pygrass_numpy_SETUP)),

    #
    # 1 if map < 0 else 0
    #

    ('r.mapcalc if', timeit.Timer(stmt = """
    run_command('r.mapcalc', expression = 'new = if(%s < 50, 1, 0)', overwrite = True)
    """ % raster_name, setup = rmapcalc_SETUP) ),

    ('RasterRow if', timeit.Timer(stmt = """
    new = pygrass.RasterRow('new', mtype = 'DCELL', mode = 'w', overwrite = True)
    new.open(overwrite = True)
    for row in raster: new.put_row( row < 50)
    new.close()
    """, setup = pygrass_SETUP)),

    ('RasterSeg if', timeit.Timer(stmt = """
    new = pygrass.RasterSegment('new', mtype = 'DCELL', overwrite = True)
    new.open()
    for irow, row in enumerate(raster): new.put_row(irow, row < 50)
    new.close()
    """, setup = pygrass_SETUP)),

    ('RasterNumpy if', timeit.Timer(stmt = """
    el = raster < 50
    el.overwrite=True
    el.rename("newif")
    el.close()""", setup = pygrass_numpy_SETUP)),

    #
    # sqrt
    #

    ('r.mapcalc sqrt', timeit.Timer(stmt = """
    run_command('r.mapcalc', expression = 'new = sqrt(%s)', overwrite = True)
    """ % raster_name, setup = rmapcalc_SETUP) ),

    ('RasterRow sqrt', timeit.Timer(stmt = """
    new = pygrass.RasterRow('new', mtype = 'DCELL', mode = 'w', overwrite = True)
    new.open(overwrite = True)
    for row in raster: new.put_row(np.sqrt(row))
    new.close()
    """, setup = pygrass_SETUP)),

    ('RasterSeg sqrt', timeit.Timer(stmt = """
    new = pygrass.RasterSegment('new', mtype = 'DCELL', overwrite = True)
    new.open()
    for irow, row in enumerate(raster): new.put_row(irow, np.sqrt(row))
    new.close()
    """, setup = pygrass_SETUP)),

    ('RasterNumpy sqrt', timeit.Timer(stmt = """
    el = np.sqrt(raster)
    el.overwrite=True
    el.rename('new')
    el.close()
    """, setup = pygrass_numpy_SETUP)),

    ])

    result = run_benchmark(TEST, ntimes = int(options.ntim))
    print
    print('=' * 50)
    print
    print_benchmark(result)
    grasscore.del_temp_region()
#add options
if __name__ == "__main__":
    main()
