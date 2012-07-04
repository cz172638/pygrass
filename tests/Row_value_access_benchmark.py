# -*- coding: utf-8 -*-
"""
Created on Sat Jun 16 20:24:56 2012

@author: soeren
"""
import numpy as np
import time
import collections
import sys, os
sys.path.append(os.getcwd())
sys.path.append("%s/.."%(os.getcwd()))

import grass.lib.gis as libgis
import grass.lib.raster as libraster
import grass.script as core
import pygrass
import ctypes

def RasterNumpy_value_access_if():
    print "RasterNumpy_value_access_if"
    test_a = pygrass.RasterNumpy(name="test_a", mtype="CELL", mode="r+")
    test_a.open()
    
    test_c = pygrass.RasterNumpy(name="test_c", mtype="CELL", mode="w+", overwrite=True)
    test_c.open()
    
    for row in xrange(test_a.rows):
        for col in xrange(test_a.cols):
            test_c[row, col] = test_a[row, col] > 50
    
    test_a.close()
    test_c.close()

def RasterNumpy_value_access_add():
    print "RasterNumpy_value_access_add"
    test_a = pygrass.RasterNumpy(name="test_a", mode="r+")
    test_a.open()
    
    test_b = pygrass.RasterNumpy(name="test_b", mode="r+")
    test_b.open()
    
    test_c = pygrass.RasterNumpy(name="test_c", mtype="DCELL", mode="w+", overwrite=True)
    test_c.open()
    
    for row in xrange(test_a.rows):
        for col in xrange(test_a.cols):
            test_c[row, col] = test_a[row, col] + test_b[row, col]
    
    test_a.close()
    test_b.close()
    test_c.close()
    
def RasterNumpy_row_access_if():
    print "RasterNumpy_row_access_if"
    test_a = pygrass.RasterNumpy(name="test_a", mtype="CELL", mode="r+")
    test_a.open()
    
    test_c = pygrass.RasterNumpy(name="test_c", mtype="CELL", mode="w+", overwrite=True)
    test_c.open()
    
    for row in xrange(test_a.rows):
        test_c[row] = test_a[row] > 50
    
    test_a.close()
    test_c.close()

def RasterNumpy_row_access_add():
    print "RasterNumpy_row_access_add"
    test_a = pygrass.RasterNumpy(name="test_a", mode="r+")
    test_a.open()
    
    test_b = pygrass.RasterNumpy(name="test_b", mode="r+")
    test_b.open()
    
    test_c = pygrass.RasterNumpy(name="test_c", mtype="DCELL", mode="w+", overwrite=True)
    test_c.open()
    
    for row in xrange(test_a.rows):
        test_c[row] = test_a[row] + test_b[row]
    
    test_a.close()
    test_b.close()
    test_c.close()

def RasterNumpy_map_access_if():
    print "RasterNumpy_map_access_if"
    test_a = pygrass.RasterNumpy(name="test_a", mtype="CELL", mode="r+")
    test_a.open()
    
    test_c = pygrass.RasterNumpy(name="test_c", mtype="CELL", mode="w+", overwrite=True)
    test_c.open()
    
    test_c = test_a > 50
    
    test_a.close()
    test_c.close()

def RasterNumpy_map_access_add():
    print "RasterNumpy_map_access_add"
    test_a = pygrass.RasterNumpy(name="test_a", mode="r+")
    test_a.open()
    
    test_b = pygrass.RasterNumpy(name="test_b", mode="r+")
    test_b.open()
    
    test_c = pygrass.RasterNumpy(name="test_c", mtype="DCELL", mode="w+", overwrite=True)
    test_c.open()
    
    test_c = test_a + test_b
    
    test_a.close()
    test_b.close()
    test_c.close()

def RasterSegment_value_access_if():
    print "RasterSegment_row_access_if"
    test_a = pygrass.RasterSegment(name="test_a")
    test_a.open(mode="r")
    
    test_c = pygrass.RasterSegment(name="test_c")
    test_c.open(mode="w", mtype="CELL", overwrite=True)
    
    buff_a = pygrass.Buffer(test_a.cols, test_a.mtype)
    
    for row in xrange(test_a.rows):
        test_a.get_row(row, buff_a)
        for col in xrange(test_a.cols):
            test_c.put(row, col, buff_a[col] > 50)
    
    test_a.close()
    test_c.close()

def RasterSegment_value_access_add():
    print "RasterSegment_row_access_add"
    test_a = pygrass.RasterSegment(name="test_a")
    test_a.open(mode="r")
    
    test_b = pygrass.RasterSegment(name="test_b")
    test_b.open(mode="r")
    
    test_c = pygrass.RasterSegment(name="test_c")
    test_c.open(mode="w", mtype="DCELL", overwrite=True)
    
    buff_a = pygrass.Buffer(test_a.cols, test_a.mtype)
    buff_b = pygrass.Buffer(test_b.cols, test_b.mtype)
    
    for row in xrange(test_a.rows):
        test_a.get_row(row, buff_a)
        test_b.get_row(row,buff_b)
        for col in xrange(test_a.cols):
            test_c.put(row, col, buff_a[col] + buff_b[col])
    
    test_a.close()
    test_b.close()
    test_c.close()

def RasterSegment_row_access_if():
    print "RasterSegment_row_access_if"
    test_a = pygrass.RasterSegment(name="test_a")
    test_a.open(mode="r")
    
    test_c = pygrass.RasterSegment(name="test_c")
    test_c.open(mode="w", mtype="CELL", overwrite=True)
    
    buff_a = pygrass.Buffer(test_a.cols, test_a.mtype)
    
    for row in xrange(test_a.rows):
        test_a.get_row(row, buff_a)
        test_c.put_row(row, buff_a > 50)
    
    test_a.close()
    test_c.close()

def RasterSegment_row_access_add():
    print "RasterSegment_row_access_add"
    test_a = pygrass.RasterSegment(name="test_a")
    test_a.open(mode="r")
    
    test_b = pygrass.RasterSegment(name="test_b")
    test_b.open(mode="r")
    
    test_c = pygrass.RasterSegment(name="test_c")
    test_c.open(mode="w", mtype="DCELL", overwrite=True)
    
    buff_a = pygrass.Buffer(test_a.cols, test_a.mtype)
    buff_b = pygrass.Buffer(test_b.cols, test_b.mtype)
    
    for row in xrange(test_a.rows):
        test_a.get_row(row, buff_a)
        test_b.get_row(row,buff_b)
        test_c.put_row(row, buff_a + buff_b)
    
    test_a.close()
    test_b.close()
    test_c.close()
    
def RasterRow_value_access_add():
    print "RasterRow_value_access_add"
    
    test_a = pygrass.RasterRow(name="test_a")
    test_a.open(mode="r")
    
    test_b = pygrass.RasterRow(name="test_b")
    test_b.open(mode="r")
    
    test_c = pygrass.RasterRow(name="test_c")
    test_c.open(mode="w", mtype="FCELL", overwrite=True)
    
    buff_a = pygrass.Buffer(test_a.cols, test_a.mtype)
    buff_b = pygrass.Buffer(test_b.cols, test_b.mtype)
    buff_c = pygrass.Buffer(test_b.cols, test_b.mtype)
    
    for row in xrange(test_a.rows):
        test_a.get_row(row, buff_a)
        test_b.get_row(row,buff_b)
        
        for col in xrange(test_a.cols):
            buff_c[col] = buff_a[col] + buff_b[col]
            
        test_c.put_row(buff_c)
    
    test_a.close()
    test_b.close()
    test_c.close()

def RasterRow_value_access_if():
    print "RasterRow_value_access_if"
    
    test_a = pygrass.RasterRow(name="test_a")
    test_a.open(mode="r")
    
    test_c = pygrass.RasterRow(name="test_c")
    test_c.open(mode="w", mtype="CELL", overwrite=True)
    
    buff_a = pygrass.Buffer(test_a.cols, test_a.mtype)
    buff_c = pygrass.Buffer(test_a.cols, test_a.mtype)
    
    for row in xrange(test_a.rows):
        test_a.get_row(row, buff_a)
        
        for col in xrange(test_a.cols):
            buff_c[col] = buff_a[col] > 50
        
        test_c.put_row(buff_c)
    
    test_a.close()
    test_c.close()

def RasterRowIO_row_access_add():
    print "RasterRowIO_row_access_add"
    
    test_a = pygrass.RasterRowIO(name="test_a")
    test_a.open(mode="r")
    
    test_b = pygrass.RasterRowIO(name="test_b")
    test_b.open(mode="r")
    
    test_c = pygrass.RasterRowIO(name="test_c")
    test_c.open(mode="w", mtype="FCELL", overwrite=True)
    
    buff_a = pygrass.Buffer(test_a.cols, test_a.mtype)
    buff_b = pygrass.Buffer(test_b.cols, test_b.mtype)
    
    for row in xrange(test_a.rows):
        test_a.get_row(row, buff_a)
        test_b.get_row(row,buff_b)
        test_c.put_row(buff_a + buff_b)
    
    test_a.close()
    test_b.close()
    test_c.close()

def RasterRowIO_row_access_if():
    print "RasterRowIO_row_access_if"
    
    test_a = pygrass.RasterRowIO(name="test_a")
    test_a.open(mode="r")
    
    test_c = pygrass.RasterRowIO(name="test_c")
    test_c.open(mode="w", mtype="CELL", overwrite=True)
    
    buff_a = pygrass.Buffer(test_a.cols, test_a.mtype)
    
    for row in xrange(test_a.rows):
        test_a.get_row(row, buff_a)
        test_c.put_row(buff_a > 50)
    
    test_a.close()
    test_c.close()
    
def RasterRow_row_access_add():
    print "RasterRow_row_access_add"
    
    test_a = pygrass.RasterRow(name="test_a")
    test_a.open(mode="r")
    
    test_b = pygrass.RasterRow(name="test_b")
    test_b.open(mode="r")
    
    test_c = pygrass.RasterRow(name="test_c")
    test_c.open(mode="w", mtype="FCELL", overwrite=True)
    
    buff_a = pygrass.Buffer(test_a.cols, test_a.mtype)
    buff_b = pygrass.Buffer(test_b.cols, test_b.mtype)
    
    for row in xrange(test_a.rows):
        test_a.get_row(row, buff_a)
        test_b.get_row(row,buff_b)
        test_c.put_row(buff_a + buff_b)
    
    test_a.close()
    test_b.close()
    test_c.close()

def RasterRow_row_access_if():
    print "RasterRow_row_access_if"
    
    test_a = pygrass.RasterRow(name="test_a")
    test_a.open(mode="r")
    
    test_c = pygrass.RasterRow(name="test_c")
    test_c.open(mode="w", mtype="CELL", overwrite=True)
    
    buff_a = pygrass.Buffer(test_a.cols, test_a.mtype)
    
    for row in xrange(test_a.rows):
        test_a.get_row(row, buff_a)
        test_c.put_row(buff_a > 50)
    
    test_a.close()
    test_c.close()

def mapcalc_add():
    print "mapcalc_add"
    core.mapcalc("test_c = test_a + test_b", quite=True, overwrite=True)
    
def mapcalc_if():
    print "mapcalc_if"
    core.mapcalc("test_c = if(test_a > 50, 1, 0)", quite=True, overwrite=True)
    
def mytimer(func, runs=1):
    
    t = 0.0
    for _ in xrange(runs):
        start = time.time()
        func()
        end = time.time()
        t = t + end - start
    
    #print "r.mapcalc with add statement: %gs"%(t/runs)
    return t/runs
    
def run_benchmark(resolution_list, runs):
    
    results = []
    
    for resolution in resolution_list:

        core.use_temp_region()
        core.run_command('g.region', e=50, w=-50, n=50, s=-50, res=resolution, flags='p')

        # Adjust the computational region for this process
        region = libgis.Cell_head()
        libraster.Rast_get_window(ctypes.byref(region))
        region.e = 50
        region.w = -50
        region.n = 50
        region.s = -50
        region.ew_res = resolution
        region.ns_res = resolution
        
        libgis.G_adjust_Cell_head(ctypes.byref(region), 0, 0)
        
        libraster.Rast_set_window(ctypes.byref(region))
        libgis.G_set_window(ctypes.byref(region))
        
        # Create two raster maps with random numbers
        core.mapcalc("test_a = rand(0, 100)", quite=True, overwrite=True)
        core.mapcalc("test_b = rand(0.0, 1.0)", quite=True, overwrite=True)
        
        results.append("\n\n###################################################################")
        results.append("### Benchmark cols = %i rows = %i cells = %i"%(region.cols, region.rows, region.cols*region.rows))
        results.append("###################################################################")
        
        results.append("\n\n# equation: c = a + b\n")
        t = mytimer(mapcalc_add, runs)
        results.append("r.mapcalc............................ time %g"%(t))
        
        t = mytimer(RasterRow_row_access_add, runs)
        results.append("RasterRow row access................. time %g"%(t))
        
        t = mytimer(RasterRow_value_access_add, runs)
        results.append("RasterRow value access............... time %g"%(t))
        
        t = mytimer(RasterRowIO_row_access_add, runs)
        results.append("RasterRowIO row access............... time %g"%(t))
        
        t = mytimer(RasterSegment_row_access_add, runs)
        results.append("RasterSegment row access............. time %g"%(t))
        
        t = mytimer(RasterSegment_value_access_add, runs)
        results.append("RasterSegment value access........... time %g"%(t))
        
        t = mytimer(RasterNumpy_map_access_add, runs)
        results.append("RasterNumpy map access............... time %g"%(t))
        
        #t = mytimer(RasterNumpy_row_access_add, runs)
        #results.append("RasterNumpy row access............... time %g"%(t))
        
        t = mytimer(RasterNumpy_value_access_add, runs)
        results.append("RasterNumpy value access............. time %g"%(t))
        
        #######################################################################
        
        results.append("\n\n# equation: c = if a > 50 then 1 else 0\n")
        t = mytimer(mapcalc_if, runs)
        results.append("r.mapcalc............................ time %g"%(t))
        
        t = mytimer(RasterRow_row_access_if, runs)
        results.append("RasterRow row access................. time %g"%(t))

        t = mytimer(RasterRow_value_access_if, runs)
        results.append("RasterRow value access............... time %g"%(t))
        
        t = mytimer(RasterRowIO_row_access_if, runs)
        results.append("RasterRowIO row access............... time %g"%(t))
        
        t = mytimer(RasterSegment_row_access_if, runs)
        results.append("RasterSegment row access............. time %g"%(t))
        
        t = mytimer(RasterSegment_value_access_if, runs)
        results.append("RasterSegment value access........... time %g"%(t))
        
        t = mytimer(RasterNumpy_map_access_if, runs)
        results.append("RasterNumpy map access............... time %g"%(t))
        
        #t = mytimer(RasterNumpy_row_access_if, runs)
        #results.append("RasterNumpy row access............... time %g"%(t))
        
        t = mytimer(RasterNumpy_value_access_if, runs)
        results.append("RasterNumpy value access............. time %g"%(t))

        core.del_temp_region()
    
    for result in results:
        print result

def main():
    """Main function"""
    
    res = [1, 0.25, 0.1, 0.05]
    
    run_benchmark(res, 5)


#add options
if __name__ == "__main__":
    main()
