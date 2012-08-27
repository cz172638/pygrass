# -*- coding: utf-8 -*-
"""
Created on Thu Aug 23 11:07:38 2012

@author: pietro

"""
import os
import subprocess
import optparse

from grass.script import core as grasscore

DBNAME = 'pygrassdb_doctest'

def read_gisrc(gisrcpath):
    gisrc = open(gisrcpath, 'r')
    diz = {}
    for row in gisrc:
        key, val = row.split(':')
        diz[key.strip()] = val.strip()
    return diz

def main():
    # default option
    gisrc = read_gisrc(os.environ['GISRC'])
    user = os.environ['USER']
    # start optparse
    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-U", "--user", dest="user", default=user,
                      help="PostgreSQL user [default=%default]")
    parser.add_option("-P", "--password", dest="passwd", default=None,
                      help="PostgreSQL password for user [default=%default]")
    parser.add_option("-D", "--database", dest="db", default=DBNAME,
                      help="PostgreSQL database name [default=%default]")                      
                      
    (opts, args) = parser.parse_args()
    #
    # Create DB
    #
    print("\n\nCreate a new DB: %s...\n" % DBNAME)
    createdb = ['createdb', '--encoding=UTF-8', '--owner=%s' % opts.user,
                '--host=localhost', '--username=%s' % opts.user, DBNAME]
    if opts.passwd:
        createdb.append("--password=%s" % opts.passwd)
    else:
        createdb.append("--no-password")
    subprocess.Popen(createdb)
    
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
                          vect="boundary_municp@PERMANENT,boundary_municp_sqlite",
                          overwrite=True)
    print("\n\nBuild topology...\n")
    grasscore.run_command('v.build', map='boundary_municp_sqlite', overwrite=True)
    
if __name__ == "__main__":
    main()