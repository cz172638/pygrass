# -*- coding: utf-8 -*-
"""
Created on Sat Jun 16 20:24:56 2012

@author: pietro
"""
import numpy as np
import timeit
import collections
import sys, os

sys.path.append(os.getcwd())

import pygrass


region = pygrass.region.Region()

# TODO overwrite not working
elev = pygrass.RasterRow('elev_bench', 'w', overwrite = True)

print("Generate an elevation map...")
row_buf = pygrass.Buffer((region.rows,), 'DCELL')
elev.open('w', 'DCELL', overwrite = True)
for _ in xrange(region.rows):
    row_buf.data = (np.random.random(region.cols,)*100).data
    elev.put_row(row_buf)
elev.close()
print("Done!\n")

print("Compare r.mapcalc and pygrass classes")


TEST = collections.OrderedDict( [

#
# map += 2
#
('r.mapcalc +2', timeit.Timer(stmt = """
run_command('r.mapcalc', expression = 'new = elev_bench + 2', overwrite = True)
""", setup = "from grass.script.core import run_command") ),

('RasterRow +2', timeit.Timer(stmt = """
new = pygrass.RasterRow('new', mtype = 'DCELL', mode = 'w', overwrite = True)
new.open(overwrite = True)
for row in elev: new.put_row( row + 2)
new.close()
""", setup = """import pygrass
elev = pygrass.RasterRow('elev_bench', 'r')
elev.open()""")),

('RasterSeg +2', timeit.Timer(stmt = """
new = pygrass.RasterSegment('new', mtype = 'DCELL', overwrite = True)
new.open()
for irow, row in enumerate(elev): new.put_row(irow, row + 2)
new.close()
""", setup = """import pygrass
elev = pygrass.RasterRow('elev_bench', 'r')
elev.open()""")),

#
# 1 if map < 0 else 0
#

('r.mapcalc if', timeit.Timer(stmt = """
run_command('r.mapcalc', expression = 'new = if(elev_bench < 50, 1, 0)', overwrite = True)
""", setup = "from grass.script.core import run_command") ),

('RasterRow if', timeit.Timer(stmt = """
new = pygrass.RasterRow('new', mtype = 'DCELL', mode = 'w', overwrite = True)
new.open(overwrite = True)
for row in elev: new.put_row( row < 50)
new.close()
""", setup = """import pygrass
elev = pygrass.RasterRow('elev_bench', 'r')
elev.open()""")),

('RasterSeg if', timeit.Timer(stmt = """
new = pygrass.RasterSegment('new', mtype = 'DCELL', overwrite = True)
new.open()
for irow, row in enumerate(elev): new.put_row(irow, row < 50)
new.close()
""", setup = """import pygrass
elev = pygrass.RasterRow('elev_bench', 'r')
elev.open()""")),

#
# sqrt
#

('r.mapcalc sqrt', timeit.Timer(stmt = """
run_command('r.mapcalc', expression = 'new = sqrt(elev_bench)', overwrite = True)
""", setup = "from grass.script.core import run_command") ),

('RasterRow sqrt', timeit.Timer(stmt = """
new = pygrass.RasterRow('new', mtype = 'DCELL', mode = 'w', overwrite = True)
new.open(overwrite = True)
for row in elev: new.put_row(np.sqrt(row))
new.close()
""", setup = """import pygrass
import numpy as np
elev = pygrass.RasterRow('elev_bench', 'r')
elev.open()""")),

('RasterSeg sqrt', timeit.Timer(stmt = """
new = pygrass.RasterSegment('new', mtype = 'DCELL', overwrite = True)
new.open()
for irow, row in enumerate(elev): new.put_row(irow, np.sqrt(row))
new.close()
""", setup = """import pygrass
import numpy as np
elev = pygrass.RasterRow('elev_bench', 'r')
elev.open()""")),


])

def run_benchmark(tests, ntimes):
    result = collections.OrderedDict()
    for key, val in tests.iteritems():
        result[key] = {}
        result[key]['timer'] = val
        result[key]['exec time'] = val.timeit( number=ntimes )
        print("{0}; {1:f} sec/pass".format(key, result[key]['exec time']))
    return result

def print_benchmark(result):
    for key, val in result.iteritems():
        print("{0}; {1:f} sec/pass".format(key, result[key]['exec time']))


result = run_benchmark(TEST, ntimes = 10)
print
print('=' * 50)
print
print_benchmark(result)