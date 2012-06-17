# -*- coding: utf-8 -*-
"""
Created on Sat May 26 12:49:07 2012

@author: pietro
"""
import sys
sys.path.append( u'../../' )
import obj

#reload(obj)
elev = obj.Raster('elevation', mode = 'r')
elev.open(mslice = True)
for row in elev[:5]: print(row[:3])

new = obj.Raster('new', mode = 'w')
new.open()


c = 0
for row in elev: new[c] = row

new.close()
