# -*- coding: utf-8 -*-

from Products.ZCatalog.ZCatalog import Catalog
from Missing import MV

# Plomino
from ..utils import asUnicode

try:
    from DocumentTemplate.cDocumentTemplate import safe_callable
except ImportError:
    # Fallback to python implementation to avoid dependancy on DocumentTemplate
    import types

    def safe_callable(ob):
        # Works with ExtensionClasses and Acquisition.
        if hasattr(ob, '__class__'):
            return hasattr(ob, '__call__') or isinstance(ob, types.ClassType)
        else:
            return callable(ob)


class PlominoCatalog(Catalog):
    """ Plomino catalog (just overloads recordify method)
    """

    def recordify(self, obj):
        """ Turns an obj into a record tuple """
        record = []
        # the unique id is always the first element
        for name in self.names:
            if name.startswith("PlominoViewColumn_"):
                marker, viewname, columnname = name.split('_')
                if not obj.isSelectedInView(viewname):
                    v = None
                else:
                    v = asUnicode(
                        obj.computeColumnValue(viewname, columnname))
                record.append(v)
            else:
                attr = getattr(obj, name, MV)
                if attr is not MV and safe_callable(attr):
                    attr = attr()
                if isinstance(attr, str):
                    attr = attr.decode('utf-8')
                elif isinstance(attr, (list, tuple)):
                    new_value = []
                    for v in attr:
                        if isinstance(v, str):
                            v = v.decode('utf-8')
                        new_value.append(v)
                    attr = new_value
                record.append(attr)
        return tuple(record)
