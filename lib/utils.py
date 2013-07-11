import wx
from pubsub import pub
import functools
import inspect
import unittest
from .topics import TOGGLE

import os
import errno
import datetime

def wxdate2pydate(date):
     assert isinstance(date, wx.DateTime)
     if date.IsValid():
         ymd = map(int, date.FormatISODate().split('-'))
         return datetime.date(*ymd)
     else:
         return None

def silentremove(filename):
    try:
        os.remove(filename)
    except OSError, e: # this would be "except OSError as e:" in python 3.x
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occured
class Record(object):
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

def setter(*attrs):
    def decorator(func):
        @functools.wraps(func)
        def new_func(*args, **kwargs):
            self = args[0]
            params = _dict_as_called(func, args, kwargs)
            for a in attrs:
                assert a in params, repr(a)+" not in "+repr(params)
                setattr(self, a, params[a])
            return func(*args, **kwargs)
        return new_func
    return decorator


def _dict_as_called(function, args, kwargs):
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

def threadsafe(f):
    @functools.wraps(f)
    def new_func(self, *args, **kargs):
        with self.lock:
            return f(self, *args, **kargs)
    return new_func


class FunctionDisabledError(Exception):
    def __init__(self, func_name):
        self.func_name=func_name
    def __str__(self):
        return self.func_name+"() has been disabled "

def run_if_enabled(func):
        @functools.wraps(func)
        def new_func(self, *args, **kargs):
            name = func.__name__
            if name in self._enabled and (not self._enabled[name]):
                raise FunctionDisabledError(name)
            else:
                return func(self, *args, **kargs)
        return new_func

class ToggleableMethods:
    def __init__(self):
        self._enabled = {}

    def enable(self, method_name):
        self._enabled[method_name]=True
        pub.sendMessage((TOGGLE,method_name),enabled=True)

    def disable(self, method_name):
        self._enabled[method_name]=False
        pub.sendMessage((TOGGLE,method_name),enabled=False)

    def batchEnable(self, methods):
        for m in methods:
            self.enable(m)

    def batchDisable(self, methods):
        for m in methods:
            self.disable(m)


from os.path import splitext
def get_save_path_from_dialog(dlg, extension=None):
    path = None
    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()
        if extension is not None and dlg.GetFilterIndex() == 0:
            path=splitext(path)[0]
            path = path + '.'+ extension
    return path
