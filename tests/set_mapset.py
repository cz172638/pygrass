# -*- coding: utf-8 -*-
"""
Created on Thu Aug 23 11:07:38 2012

@author: pietro

"""
import os
import subprocess
from grass.script import core as grasscore

DBNAME = 'pygrassdb_doctest'

def read_gisrc(gisrcpath):
    gisrc = open(gisrcpath, 'r')
    diz = {}
    for row in gisrc:
        key, val = row.split(':')
        diz[key.strip()] = val.strip()
    return diz

gisrc = read_gisrc(os.environ['GISRC'])


#
# Create DB
#
print("\n\nCreate a new DB: %s...\n" % DBNAME)
subprocess.Popen(['createdb', '--encoding=UTF-8',
                  '--owner=%s' % os.environ['USER'],
                  '--host=localhost',
                  '--username=%s' % os.environ['USER'],
                  '--no-password',
                  DBNAME])

#
# set postgreSQL
#
print("\n\nSet Postgres connection...\n")
grasscore.run_command('db.connect', driver='pg',
                      database='host=localhost,dbname=%s' % DBNAME)

grasscore.run_command('db.login', user=os.environ['USER'])
print("\n\nCopy the map from PERMANENT to user1...\n")
grasscore.run_command('g.copy',
                      vect="boundary_municp@PERMANENT,boundary_municp_pg",
                      overwrite=True)
print("\n\nBuild topology...\n")
grasscore.run_command('v.build', map='boundary_municp_pg', overwrite=True)


#
# set sqlite
#
db = [gisrc['GISDBASE'], gisrc['LOCATION_NAME'], gisrc['MAPSET'], 'sqlite.db']
print("\n\nSet Sqlite connection...\n")
grasscore.run_command('db.connect', driver='sqlite',
                      database=os.path.join(db))
print("\n\nCopy the map from PERMANENT to user1...\n")
grasscore.run_command('g.copy',
                      vect="boundary_municp@PERMANENT,boundary_municp_sqlite")
print("\n\nBuild topology...\n")
grasscore.run_command('v.build', map='boundary_municp_sqlite', overwrite=True)