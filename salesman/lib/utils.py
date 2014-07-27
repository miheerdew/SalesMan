#Copyright (C) 2013  Miheer Dewaskar <miheerdew@gmail.com>
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>

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
    return translate(table, text)


def translate(table, text):
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

def setter(*names):
    """Returns a decorator, which sets the names given as arguments
    (to setter) on the object using arguments from the function call,
    and then calls the original function. Note that all the names
    must be present as function arguments.

    For Example

    >>> class A:
    ...     @setter('a','b','c')
    ...     def __init__(self, a, b, c):
    ...         pass
    ...     @setter('d', 'e')
    ...     def func(self, d, e=1, f=2):
    ...         self.d, self.e, d, e
    ...         assert f == 2
    ...     @setter('d')
    ...     def func2(self):
    ...        pass
    ...
    >>> o=A(1,2,3)
    >>> o.a, o.b, o.c
    (1, 2, 3)
    >>> o.d
    Traceback (most recent call last):
    AttributeError: A instance has no attribute 'd'
    >>> o.func(e=3,d=3)
    >>> o.d, o.e
    (3, 3)
    >>> o.f
    Traceback (most recent call last):
    AttributeError: A instance has no attribute 'f'
    >>> o.func2()
    Traceback (most recent call last):
    AssertionError: 'd' not found in arguments
    """
    def decorator(func):
        @functools.wraps(func)
        def new_func(*args, **kwargs):
            self = args[0]
            params = dict_as_called(func, args, kwargs)
            for a in names:
                assert a in params, "{!r} not found in arguments".format(a)
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
        To be used on objects of type ToggelableMethods.

        """
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

def normalizeString(string):
    r"""Converts a string to a reasonable normal form.

    >>> normalizeString("asd  Adsbs \t  \n Bd a   ")
    'asd adsbs bd a'
    """
    return ' '.join(w.lower() for w in string.split())

def standardizeString(string):
    r"""Gives a beautified version of the normalization of the string.

    Currently just removes extra spaces.
    >>> standardizeString("asd  Adsbs \t  \n Bd a   ")
    'asd Adsbs Bd a'
    """
    return ' '.join(w for w in string.split())

if __name__ == '__main__':
    import doctest
    doctest.testmod()
