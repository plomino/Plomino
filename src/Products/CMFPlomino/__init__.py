# -*- coding: utf-8 -*-
"""Init and utils."""

from Globals import DevelopmentMode
from time import time
from zope.i18nmessageid import MessageFactory
from zope import component
from zope.interface import implements

import interfaces

_ = MessageFactory('Products.CMFPlomino')


class PlominoSafeDomains:
    implements(interfaces.IPlominoSafeDomains)

    # by default, there is no domains allowed
    # but we can provide a IPlominoSafeDomains utility to declare some
    domains = []


component.provideUtility(PlominoSafeDomains, interfaces.IPlominoSafeDomains)


if DevelopmentMode:
    PROFILING = True

    class plomino_profiler:
        """ Decorator which helps to control what aspects to profile
        """
        def __init__(self, aspect=None):
            self.aspect = aspect

        def get_storage(self, context):
            storage = context.getCache("plomino.profiling")
            if not storage:
                storage = dict()
                context.setCache("plomino.profiling", storage)
            return storage

        def __call__(self, f):
            def newf(*args, **kwds):
                obj = args[0]
                request = getattr(obj, 'REQUEST', None)
                if request and self.aspect in request.cookies.get('plomino_profiler', ''):
                    start = time()
                    f_result = f(*args, **kwds)
                    duration = 1000 * (time() - start)
                    if self.aspect == "formulas":
                        id = args[1]
                    else:
                        id = obj.id
                    profiling = self.get_storage(obj)
                    aspect_times = profiling.get(self.aspect, [])
                    aspect_times.append([id, duration])
                    profiling[self.aspect] = aspect_times
                    return f_result
                else:
                    return f(*args, **kwds)
            newf.__doc__ = f.__doc__
            return newf
else:
    PROFILING = False

    class plomino_profiler:
        """"Transparent decorator, as profiling is only available if
        Zope runs in debug mode
        """
        def __init__(self, aspect=None):
            self.aspect = aspect

        def __call__(self, f):
            def newf(*args, **kwds):
                return f(*args, **kwds)

            newf.__doc__ = f.__doc__
            return newf
