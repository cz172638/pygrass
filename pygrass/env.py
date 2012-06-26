# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 12:38:48 2012

@author: pietro
"""
import grass.lib.gis as libgis
from grass.script import core as grasscore

def remove(**kargs):
    grasscore.run_command('g.remove', **kargs)


def rename(oldname, newname, maptype):
    grasscore.run_command('g.rename',
                          **{maptype : '{old},{new}'.format(old = oldname,
                                                            new = newname),})

def copy(existingmap, newmap, maptype):
    grasscore.run_command('g.copy',
                          **{maptype : '{old},{new}'.format(old = existingmap,
                                                            new = newmap),})

def get_mapset(mapname, mapset = ''):
    return libgis.G_find_raster(mapname, '')

def exist(mapname, mapset = ''):
    mapset = get_mapset(mapname, mapset)
    if mapset :
        return True
    else:
        return False