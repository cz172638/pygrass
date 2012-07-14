# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 10:23:15 2012

@author: pietro


Example:
import grass.modules as modules

1) Running r.slope.aspect
rsa = modules.factory("r.slope.aspect", elevation=elev, slope='slp_f',
...                           format='percent', overwrite=True)

2) Creating a run-able module object and run later
rsa = modules.factory("r.slope.aspect", elevation='elev', slope='slp_f',
...                           format='percent', flags='g',
overwrite=True, run=False)
rsa.run()
# or for cluster environments of wps server
rsa.remote_run(node="cluster_node_3")

3) Creating a module object and run later with arguments
rsa = modules.factory("r.slope.aspect")
rsa.run(elevation='elev', slope='slp_f', format='percent', flags='g',
overwrite=True)

4) Create the module object input step by step and run later
rsa = modules.factory("r.slope.aspect")
rsa.inputs["elevation"] = "elev"
rsa.inputs["format"] = 'percent'
rsa.outputs["slope"] = "slp_f"
rsa.flags = "g"
rsa.overwrite = True
rsa.run()

# For all above:

if rsa.return_state == 0:
    print "Run successfully"
    print rsa.stdout
    print rsa.stderr

# print some metadata

print rsa.name
print rsa.description
print rsa.keywords
print rsa.inputs
print rsa.inputs["elev"].description
print rsa.inputs["elev"].type
print rsa.inputs["elev"].multiple
print rsa.inputs["elev"].required
print rsa.outputs
...

if rsa.outputs["aspect"] == None:
    print "Aspect is not computed"
"""
from __future__ import print_function
import subprocess
import collections
from itertools import izip_longest
from xml.etree.ElementTree import fromstring
import numpy as np


#
# this dictionary is used to extract the value of interest from the xml
# the lambda experssion is used to define small simple functions,
# is equivalent to: ::
#
# def f(p):
#     return p.text.strip()
#
# and then we call f(p)
#
_GETFROMTAG = {
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

_GETTYPE = {
'string' : str,
'integer': np.int32,
'float'  : np.float32,
'double' : np.float64,
}

class ParameterError(Exception): pass
class FlagError(Exception): pass

def _element2dict(xparameter):
    diz = dict(xparameter.items())
    for p in xparameter:
        if _GETFROMTAG.has_key(p.tag):
            diz[p.tag] = _GETFROMTAG[p.tag](p)
        else:
            print('New tag: %s, ignored' % p.tag )
    return diz

# dictionary used to create docstring for the objects
_DOC = {
#------------------------------------------------------------
# head
'head' : """{cmd_name}({cmd_params})

Parameters
----------

""",
#------------------------------------------------------------
# param
'param' : """{name}: {default}{required}{multi}{ptype}
    {description}{values}""",
#------------------------------------------------------------
# flag_head
'flag_head' : """
Flags
------
""",
#------------------------------------------------------------
# flag
'flag' : """{name}: {default}
    {description}""",
#------------------------------------------------------------
# foot
'foot' : """run: True, optional
    If True execute the module.
stdin: PIPE,
    Set the standard input
stdout: PIPE
    Set the standard output
stderr: PIPE
    Set the standard error"""}


class Parameter(object):

    def __init__(self, xparameter = None, diz = None):
        self._value = None
        diz = _element2dict(xparameter) if xparameter != None else diz
        if diz == None: raise TypeError('Xparameter or diz are required')
        self.name = diz['name']
        self.required = True if diz['required'] == 'yes' else False
        self.multiple = True if diz['multiple'] == 'yes' else False
        # check the type
        if _GETTYPE.has_key(diz['type']):
            self.type = _GETTYPE[diz['type']]
            self.typedesc = diz['type']
            self._type = _GETTYPE[diz['type']]
        else:
            raise TypeError('New type: %s, ignored' % diz['type'] )

        self.description = diz['description']
        self.keydesc = diz['keydesc'] if diz.has_key('keydesc') else None
        self.values = [self._type(i) for i in diz['values']] if diz.has_key('values') else None
        self.default = self._type(diz['default']) if diz.has_key('default') else None
        self.guisection = diz['guisection'] if diz.has_key('guisection') else None
        if diz.has_key('gisprompt'):
            self.type = diz['gisprompt']['prompt']
            self.input = False if diz['gisprompt']['age'] == 'new' else True
        else:
            self.input = True


    def _get_value(self):
        return self._value

    def _set_value(self, value):
        #import pdb; pdb.set_trace()
        if isinstance(value, list) or isinstance(value, tuple):
            if self.multiple:
                # check each value
                self._value = [val for val in value if isinstance(value, self._type)]
            else:
                raise TypeError('The Parameter <%s>, not support multiple inputs' % self.name)
        elif isinstance(value, self._type):
            if self.values:
                if value in self.values:
                    self._value = value
                else:
                    raise TypeError('The Parameter <%s>, must be one of: %r' % (self.name, self.values))
            else:
                self._value = value
        else:
            raise TypeError('The Parameter <%s>, require: %s' % (self.name, self.typedesc))

    # here the property function is used to transform value in an attribute
    # in this case we define which function must be use to get/set the value
    value = property(fget = _get_value, fset = _set_value)


    def __str__(self):
        if isinstance(self._value, list) or isinstance(self._value, tuple):
            value = ','.join([ str(v) for v in self._value])
        else:
            value = str(self._value)
        return "%s=%s" % (self.name, value)

    def __repr__(self):
        return "Parameter <%s> (required:%s, type:%s, multiple:%s)" % (self.name,
               "yes" if self.required else "no", self.type,
               "yes" if self.multiple else "no")

    # here we use property with a decorator, in this way we mask a method as
    # a class attribute
    @property
    def __doc__(self):
        """Return the docstring of the parameter

        {name}: {default}{required}{multi}{ptype}
            {description}{values}"","""
        return _DOC['param'].format(name = self.name,
               default = repr(self.default) + ', ' if self.default else '',
               required = 'required, ' if self.required else 'optional, ',
               multi = 'multi' if self.multiple else '',
               ptype = self.typedesc, description = self.description,
               values = '\n    Values: {vls}'.format(
                        vls = ', '.join([repr(val) for val in self.values]))
                        if self.values else '')


class TypeDict(collections.OrderedDict):
    def __init__(self, dict_type, *args, **kargs):
        self.type = dict_type
        super(TypeDict, self).__init__(*args, **kargs)

    def __setitem__(self, key, value):
        if isinstance(value, self.type):
            super(TypeDict, self).__setitem__(key, value)
        else:
            cl = repr(self.type).strip().replace("'",'').replace('>','').split('.')
            raise TypeError('The value: %r is not a %s object' % (value, cl[-1].title()))

    @property
    def __doc__(self):
        return '\n'.join([self.__getitem__(obj).__doc__ for obj in self.__iter__()])

    def __call__(self):
        return [self.__getitem__(obj) for obj in self.__iter__()]

class Flag(object):
    def __init__(self, xflag = None, diz = None):
        self.value = None
        diz = _element2dict(xflag) if xflag != None else diz
        self.name = diz['name']
        self.special = True if self.name in ('verbose', 'overwrite', 'quiet', 'run') else False
        self.description = diz['description']
        self.default = diz['default'] if diz.has_key('default') else None
        self.guisection = diz['guisection'] if diz.has_key('guisection') else None

    def __str__(self):
        if self.value:
            if self.special:
                return '--%s' % self.name[0]
            else:
                return '-%s' % self.name
        else:
            return ''

    def __repr__(self):
        return "Flag <%s> (%s)" % (self.name, self.description)

    @property
    def __doc__(self):
        """
        {name}: {default}
            {description}"""
        return _DOC['flag'].format(name = self.name,
               default = repr(self.default), description = self.description)


class Factory(object):

    def __init__(self, cmd, *args, **kargs):
        self.name = cmd
        # call the command with --interface-description
        get_cmd_xml = subprocess.Popen([cmd, "--interface-description"],
                                       stdout=subprocess.PIPE)
        # get the xml of the module
        self.xml = get_cmd_xml.communicate()[0]
        # transform and parse the xml into an Elemen class:
        # http://docs.python.org/library/xml.etree.elementtree.html
        tree = fromstring(self.xml)

        #
        # extract parameters from the xml
        #
        self.params_list = [Parameter(p) for p in tree.findall("parameter")]
        self.inputs = TypeDict(Parameter)
        self.outputs = TypeDict(Parameter)
        self.required = []
        # Insert parameters into input/output and required
        for par in self.params_list:
            if par.input:
                self.inputs[par.name] = par
            else:
                self.outputs[par.name] = par
            if par.required:
                self.required.append(par)

        #
        # extract flags from the xml
        #
        flags_list = [Flag(f) for f in tree.findall("flag")]
        self.flags_dict = TypeDict(Flag)
        for flag in flags_list:
            self.flags_dict[flag.name] = flag

        #
        # Add new attributes to the class
        #
        self._flags = ''
        self._run = True
        self.stdin = subprocess.PIPE
        self.stdout = subprocess.PIPE
        self.stderr = subprocess.PIPE
        self.popen = None

        if args or kargs:
            self.__call__(*args, **kargs)

    def _get_flags(self):
        return self._flags

    def _set_flags(self, value):
        if isinstance(value, str):
            # we need to check if the flag is valid, special flags are not allow
            if value in [flg for flg in self.flags_dict \
                         if not self.flags_dict[flg].special ] :
                self._flags = value
            else:
                raise TypeError('Flag not valid')
        else:
            raise TypeError('The flags attribute must be a string')

    flags = property(fget = _get_flags, fset = _set_flags)

    def __call__(self, *args, **kargs):
        if not args and not kargs:
            self.run()
            return
        #
        # check for extra kargs, set attribute and remove from dictionary
        #
        if 'run' in kargs:
            self._run = kargs['run']
            del(kargs['run'])
        if 'flags' in kargs:
            self.flags = kargs['flags']
            del(kargs['flags'])
        if 'stdin' in kargs:
            self.stdin = kargs['stdin']
            del(kargs['stdin'])
        if 'stdout' in kargs:
            self.stdout = kargs['stdout']
            del(kargs['stdout'])
        if 'stderr' in kargs:
            self.stderr = kargs['stderr']
            del(kargs['stderr'])
        #
        # check args
        #
        for param, arg in zip(self.params_list, args):
            param.value = arg
        for key, val in kargs.items():
            if key in self.inputs:
                self.inputs[key].value = val
            elif key in self.outputs:
                self.outputs[key].value = val
            elif key in self.flags_dict:
                # we need to add this, because some parameters (overwrite,
                # verbose and quiet) work like parameters
                self.flags_dict[key].value = val
            else:
                raise ParameterError('Parameter not found')

        #
        # check reqire parameters
        #
        for par in self.required:
            if par.value == None:
                raise ParameterError("Required parameter <%s> not set." % par.name)

        #
        # check flags parameters
        #
        if self.flags:
            # check each character in flags
            for flag in self.flags:
                if flag in self.flags_dict:
                    self.flags_dict[flag].value = True
                else:
                    raise FlagError('Flag "%s" not valid.')

        #
        # check if execute
        #
        if self._run:
            self.run()

    @property
    def __doc__(self):
        """{cmd_name}({cmd_params})
        """
        head = _DOC['head'].format(cmd_name = self.name,
               cmd_params = ('\n' + (' ' * (len(self.name) + 1))).join(
               [', '.join(
               [str(i) for i in line if i != None])
               for line in izip_longest(*[iter(self.params_list)]*3)]),)
        params = '\n'.join([par.__doc__ for par in self.params_list])
        flags = self.flags_dict.__doc__
        return '\n'.join([head, params, _DOC['flag_head'], flags])


    def make_cmd(self):
        args = [self.name, ]
        for par in self.params_list:
            if par.value != None:
                args.append(str(par))
        for flg in self.flags_dict:
            if self.flags_dict[flg].value != None:
                args.append(str(self.flags_dict[flg]))
        return args

    def run(self, node = None):
        cmd = self.make_cmd()
        print(repr(cmd))
        self.popen = subprocess.Popen(cmd, stdin=self.stdin)#,
                                      #stdout=self.stout, stderr=self.stderr )





#slp = Factory('r.slope.aspect')
