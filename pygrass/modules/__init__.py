# -*- coding: utf-8 -*-
"""
Created on Sat Jul  7 19:50:00 2012

@author: pietro
"""
from __future__ import print_function
from xml.etree.ElementTree import fromstring
from jinja2 import Environment
import subprocess

import sys, os
import fnmatch

# add the wxpython core to the python path
sys.path.append(os.path.join(os.environ['GISBASE'],
                             'etc','gui','wxpython','core'))
# import GetGRASSCommands
from globalvar import GetGRASSCommands as get_modules

CMDs = list(get_modules()[0])
CMDs.sort()

#/home/pietro/docdat/phd/GSoC2012/grass7/dist.x86_64-unknown-linux-gnu/etc/gui/wxpython/core/globalvar.py

# defien a new custom filter in jinja
def do_repr(obj):
    return repr(obj)

environment = Environment()
# add the custom filter
environment.filters['repr'] = do_repr

#=====================================================================
# TEMPLATES
#
# Raster template
RASTER = '''
#/bin/env python
# -*- coding: utf-8 -*-

#DO NOT MODIFY THIS FILE, IT IS AUTOMATICALLY GENERATED
import collections

# set path
import sys, os
sys.path.append(os.getcwd())
sys.path.append("%s/../.."%(os.getcwd()))

import pygrass

from grass.script import core

def free(a): return a

rastclass = {
'row'    : pygrass.RasterRow,
'rowio'  : pygrass.RasterRowIO,
'segment': pygrass.RasterSegment,
'numpy'  : pygrass.RasterNumpy,
'str'    : str,
'free'   : free}

{% for func in functions %}
#
# {{ func.cmd_name }}
#
{{ func.src }}



{% endfor %}

'''

# Function template
FUNCTION = '''
def {{ func_name }}({%- set count = 1 -%}
    {%- for p in parameters -%}
        {%- if p.required -%}
            {{ p.name }},{{ ' ' }}
        {%- elif p.has_key('default') -%}
            {{ p.name }} = {{ p.default|repr }},{{ ' ' }}
        {%- else -%}
            {{ p.name }} = None,{{ ' ' }}
        {%- endif -%}
        {%- if count % 3 == 0 -%}
            {{ '\n' + ' ' * func_name_len }}
        {%- endif -%}
        {%- set count = count + 1 -%}
    {%- endfor -%}
    {%- for f in flags -%}
        {{ f.name }} = False,{{ ' ' }}
        {%- if count % 3 == 0 -%}
            {{ '\n' + ' ' * func_name_len }}
        {%- endif -%}
        {%- set count = count + 1 -%}
    {%- endfor -%} rtype = 'row'):
    """{{ cmd_name }}
    {{description}}

    Parameters
    ----------
    {% for p in parameters %}
    {{ p.name }}: {{ p.type }},
        {%- if p.required -%}
            required,
        {%- else -%}
            optional,
        {%- endif -%}
        {%- if p.multiple %}
            multiple,
        {% endif %}
        {{ p.description }}
        {%- if p.has_key('values') -%}
            Values: {{ p['values']|join(', ') }}
        {%- endif %}{% endfor %}
    {%- for f in flags %}
    {{ f.name }}: boolean
        {{ f.description }}
    {%- endfor %}
    rtype: string
        choose which Raster class the function should return.
        Possible values are: 'row', 'rowio', 'segment', 'numpy', 'str', 'free'.
    """
    kargs = {} #collections.OrderedDict()
    # Check parameters type:
    {% for p in parameters %}
    if {{ p.name }} != None:
        if isinstance({{ p.name }}, list) or isinstance({{ p.name }}, tuple):
            kargs['{{ p.name }}'] = ','.join([{{ check[p.type] }}(i) for i in {{ p.name }}])
        else:
            kargs['{{ p.name }}'] = {{ check[p.type] }}({{ p.name }})
    {%- endfor %}

    kargs['flags'] = ''
    # add flags
    {%- for f in flags %}
    {%- if f.name in ('verbose','overwrite','quiet') %}
    kargs['{{ f.name }}'] = {{ f.name }}
    {%- else %}
    if {{ f.name }}: kargs['flags'] += '{{ f.name }}'
    {%- endif -%}
    {% endfor %}

    core.run_command('{{ cmd_name }}', **kargs)

    results = []
    #Choose which output should be return by the function
    {% for p in parameters %}
        {%- if p.has_key('gisprompt') and p.gisprompt.age == 'new' and p.gisprompt.prompt == 'raster' %}
    if {{ p.name }} != None: results.append(rastclass[rtype]({{ p.name }}))
        {%- endif -%}
    {%- endfor %}

    return tuple(results) if len(results) > 1 else results[0]
'''

getfromtag = {
'description' : lambda p: p.text.strip(),
'keydesc'     : lambda p: p.text.strip(),
'gisprompt'   : lambda p: dict(p.items()),
'default'     : lambda p: p.text.strip(),
'values'      : lambda p: [e.text.strip() for e in p.findall('value/name')],
'value'       : lambda p: None,
'guisection'  : lambda p: p.text.strip(),
'label'       : lambda p: None,
'suppress_required' : lambda p: None,
}

def cleanparamname(name):
    if name in ('lambda', 'from'):
        return '%s_' % name
    elif fnmatch.fnmatch(name, '[0,1,2,3,4,5,6,7,8,9]*'):
        return '_%s' % name
    else:
        return name

checktype = {'string' : 'str',
'integer': 'int',
'float': 'float',
}

def get_par(paramxml):
    par = dict(paramxml.items())
    #par['name'] = cleanparamname(par['name'])
    if par.has_key('required'):
        par['required'] = True if par['required'] == 'yes' else False
    else: par['required'] =  False
    if par.has_key('multiple'):
        par['multiple'] = True if par['multiple'] == 'yes' else False
    else: par['multiple'] =  False
    for p in paramxml:
        if getfromtag.has_key(p.tag):
            par[p.tag] = getfromtag[p.tag](p)
        else:
            print('New tag: %s, ignored' % p.tag )
    return par

def sort_params(params):
    last = 0
    for i in (i for i, p in enumerate(params) if p['required']):
        par = params.pop(i)
        params.insert(last, par)
        last += 1
    return params




def get_flag(flagxml):
    flag = {}
    flag['name'] = flagxml.get('name')
    flag['description'] = flagxml.find('description').text
    return flag


class Module(object):
    def __init__(self, name):
        self.cmd_name = name
        self.cmd = subprocess.Popen([self.cmd_name, "--interface-description"],
                                    stdout=subprocess.PIPE)
        self.xml = self.cmd.communicate()[0]
        #self.tree = ElementTree()
        self.tree = fromstring(self.xml)
        self.parameters = self.tree.findall("parameter")
        self.flags = self.tree.findall("flag")
        self.dparams = sort_params([get_par(p) for p in self.parameters])
        self.dflags = [get_par(f) for f in self.flags]

    def clean_name(self):
        return '_'.join(self.cmd_name.split('.')[1:])

    def get_dict(self):
        func = environment.from_string(FUNCTION)
        diz = {'parameters' : self.dparams, 'flags' : self.dflags,
               'check' : checktype, 'cmd_name' : self.cmd_name,
               'func_name' : self.clean_name()}
        diz['func_name_len'] = len(diz['func_name']) + 5
        diz['src'] = func.render(**diz)
        return diz


def filter_cmds(filter_string):
    """Return a list of grass commands filtered using
    the Unix shell-style wildcards

    Example
    -------

    >>> cmds = filter_cmds('t.rast.*')
    >>> cmds.sort()
    >>> cmds # doctest: +ELLIPSIS
    ['t.rast.aggregate', ..., 't.rast.to.rast3', 't.rast.univar']

    """
    return fnmatch.filter(CMDs, filter_string)


BLACKLIST = ['r.solute.transport',]
def rm_bad_modules(cmdlist):
    """Remove all the modules that use number as flags and bad parameter's name"""
    cleaned = []
    for cmd in cmdlist:
        add = True
        if cmd['cmd_name'] in BLACKLIST:
                print('Module not supported: %s - in in the blacklist' % cmd['cmd_name'].ljust(20))
                add = False
        else:
            for flag in cmd['flags']:
                if flag['name'] in '0123456789':
                    print('Module not supported: %s - flag is a number' % cmd['cmd_name'].ljust(20))
                    add = False
                    break
            for par in cmd['parameters']:
                if par['name'] in ('lambda', 'from'):
                    print('Module not supported: %s - bad parameter name: %s' % (cmd['cmd_name'].ljust(20), par['name']))
                    add = False
                    break
                elif par['name'][0] in '0123456789':
                    print('Module not supported: %s - bad parameter name: %s' % (cmd['cmd_name'].ljust(20), par['name']))
                    add = False
                    break
        if add: cleaned.append(cmd)
    return cleaned

def make():
    rasters_cmd = []
    for cmd in filter_cmds('r.*'):
        #print(cmd)
        modul = Module(cmd)
        rasters_cmd.append(modul.get_dict())
    # clean from bad modules
    clean_cmd = rm_bad_modules(rasters_cmd)
    #import pdb; pdb.set_trace()
    cwd = os.path.dirname( os.path.realpath( __file__ ) )
    raster = file(os.path.join(cwd, 'raster.py'), 'w+')
    rast = environment.from_string(RASTER)
    print(rast.render(functions = clean_cmd), file = raster)

#print(lfuncs[0]['src'])




