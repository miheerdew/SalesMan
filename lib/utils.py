import functools
import inspect
import unittest
import os
import errno
import datetime
import wx

#from pubsub import pub
from wx.lib.pubsub import setupkwargs
# regular pubsub import
from wx.lib.pubsub import pub

def text_to_html(text):
    table = {'\n':'<br>',
            '<':'le;',
            '>':'ge;'}

    return ''.join(table.get(i,i) for i in text)

def ensure_dir_exists(dirname):
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

def wxdate_to_pydate(date):
    "Convert from wx.DateTime to datetime.date"
    assert isinstance(date, wx.DateTime)
    if date.IsValid():
         ymd = map(int, date.FormatISODate().split('-'))
         return datetime.date(*ymd)
    else:
         return None

def silent_remove(filename):
    "Remove filename if exists"
    try:
        os.remove(filename)
    except OSError, e: # this would be "except OSError as e:" in python 3.x
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occured


def dict_as_called(function, args, kwargs):
    """ return a dict of all the args and kwargs as the keywords they would
    be received in a real function call.  It does not call function.
    """
    names, args_name, kwargs_name, defaults = inspect.getargspec(function)

    # assign basic args
    params = {}
    if args_name:
        basic_arg_count = len(names)
        params.update(zip(names[:], args))  # zip stops at shorter sequence
        params[args_name] = args[basic_arg_count:]
    else:
        params.update(zip(names, args))

    # assign kwargs given
    if kwargs_name:
        params[kwargs_name] = {}
        for kw, value in kwargs.iteritems():
            if kw in names:
                params[kw] = value
            else:
                params[kwargs_name][kw] = value
    else:
        params.update(kwargs)

    # assign defaults
    if defaults:
        for pos, value in enumerate(defaults):
            if names[-len(defaults) + pos] not in params:
                params[names[-len(defaults) + pos]] = value

    return params
def setter(*attrs):
    """A decorator generator,which sets the attrs on the object
    using arguments from the function call

    >>>class A
    ... @setter('a','b','c')
    ... def __init__(self, a, b, c):
    ...   print (self.a, self.c, self.b)
    ...
    >>>obj=A('f',False,3)
    ('f',3,False)
    >>>obj.a
    'f'
    >>>obj.b
    False
    >>>obj.c
    3
    """
    def decorator(func):
        @functools.wraps(func)
        def new_func(*args, **kwargs):
            self = args[0]
            params = dict_as_called(func, args, kwargs)
            for a in attrs:
                assert a in params, repr(a)+" not in "+repr(params)
                setattr(self, a, params[a])
            return func(*args, **kwargs)
        return new_func
    return decorator


def threadsafe(f):
    """A wrapper to make the function threadsafe using the lock
    obtained from the GetLock attr on object"""
    @functools.wraps(f)
    def new_func(self, *args, **kargs):
        with self.GetLock():
            return f(self, *args, **kargs)
    return new_func

class Record(object):
    """A Record type, can be called as mini-mutable-named-tuple"""
    def __init__(self, **kwargs):
        for a in self.attrs:
            setattr(self, a, kwargs[a])

    def __iter__(self):
        for a in self.attrs:
            yield getattr(self,a)

    def __getitem__(self, index):
        return getattr(self, self.attrs[index])

    def __str__(self):
        return "("+ ','.join(["{}={}".format(a,getattr(self,a)) for a in self.attrs])+")"

    def __repr__(self):
        return str(self)

class FunctionDisabledError(Exception):
    "Raise when function is disable, yet it is being run"
    def __init__(self, func_name):
        self.func_name=func_name
    def __str__(self):
        return self.func_name+"() has been disabled "

def run_if_enabled(func):
        """A decorator that runs a function only if it is enabled.
        To be used on methods of a subclass of ToggelableMethods"""
        @functools.wraps(func)
        def new_func(self, *args, **kargs):
            name = func.__name__
            if self.isEnabled(name):
                return func(self, *args, **kargs)
            else:
                raise FunctionDisabledError(name)
        return new_func

class ToggleableMethods(object):
    """A class that provides toggleable methods

    """
    def __init__(self):
        self._enabled_functions = {}

    def isEnabled(self, func_name):
        return (func_name not in self._enabled_functions) or \
                (self._enabled_functions[func_name])

    def _validate_method(self, method_name):
        assert hasattr(self,method_name), method_name
        assert callable(getattr(self, method_name))

    def enable(self, method_name):
        self._validate_method(method_name)
        self._enabled_functions[method_name]=True
        pub.sendMessage(method_name,enabled=True)

    def disable(self, method_name):
        self._validate_method(method_name)
        self._enabled_functions[method_name]=False
        pub.sendMessage(method_name,enabled=False)

    def batchEnable(self, methods):
        for m in methods:
            self.enable(m)

    def batchDisable(self, methods):
        for m in methods:
            self.disable(m)


def get_save_path_from_dialog(dlg, extension=None):
    path = None
    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()
        if extension is not None and dlg.GetFilterIndex() == 0:
            path=os.path.splitext(path)[0]
            path = path + '.'+ extension
    return path
