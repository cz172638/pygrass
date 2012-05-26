# -*- coding: utf-8 -*-
"""
Created on Sat May 26 12:49:07 2012

@author: pietro
"""
import sys
sys.path.append( u'../../' )
import obj

elev = obj.Raster('elevation', mode = 'r')
new = obj.Raster('new', mode = 'w')
elev.open()
new.open()


c = 0
for row in elev:
    new[c] = row

new.close()