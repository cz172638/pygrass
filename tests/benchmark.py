# -*- coding: utf-8 -*-
"""
Created on Sat Jun 16 20:24:56 2012

@author: pietro
"""
import numpy as np
import timeit
from grass.script.core import run_command

import pygrass


region = pygrass.region.Region()

elev = pygrass.RasterRow('elev_bench', 'w')
X = np.linspace(region.west, region.east, region.cols, endpoint = True)
Y = np.linspace(region.west, region.east, region.rows, endpoint = True)

print("Generate an elevation map")
row_buf = pygrass.Buffer(X.shape, 'DCELL')
elev.open('w', 'DCELL')
for y in Y:
    print(y)
    row_buf.data = np.sin(np.sqrt(X**2 + y**2)).data
    elev.put_row(row_buf)
elev.close()


print("Compare r.mapcalc and pygrass")

import collections

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
run_command('r.mapcalc', expression = 'new = if(elev_bench < 0, 1, 0)', overwrite = True)
""", setup = "from grass.script.core import run_command") ),

('RasterRow if', timeit.Timer(stmt = """
new = pygrass.RasterRow('new', mtype = 'DCELL', mode = 'w', overwrite = True)
new.open(overwrite = True)
for row in elev: new.put_row( row < 0)
new.close()
""", setup = """import pygrass
elev = pygrass.RasterRow('elev_bench', 'r')
elev.open()""")),

('RasterSeg if', timeit.Timer(stmt = """
new = pygrass.RasterSegment('new', mtype = 'DCELL', overwrite = True)
new.open()
for irow, row in enumerate(elev): new.put_row(irow, row < 0)
new.close()
""", setup = """import pygrass
elev = pygrass.RasterRow('elev_bench', 'r')
elev.open()""")),

])

def run_benchmark(tests, ntimes):
    for key, val in tests.iteritems():
        print("{0}; {1:f} sec/pass".format(key, val.timeit( number=ntimes )))


run_benchmark(TEST, ntimes = 10)