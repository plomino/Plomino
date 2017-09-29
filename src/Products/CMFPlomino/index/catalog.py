# -*- coding: utf-8 -*-

from Products.ZCatalog.ZCatalog import Catalog
from Missing import MV

# Plomino
from Products.CMFPlomino.contents.view import decode_name
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
                params = decode_name(name)
                if len(params) == 3:
                    marker, viewname, columnname = params
                    if not obj.isSelectedInView(viewname):
                        v = None
                    else:
                        #TODO: what happens if the view/column no longer exists?
                        # any reason need to covert value 
                        # from computeColumnValue into string?
                        v = obj.computeColumnValue(viewname, columnname)
                else:

                    v = None
                record.append(v)
            else:
                #in this case we don't want acquired scripts etc. Only direct attributes
                attr = getattr(obj.aq_explicit, name, MV)
                if attr is not MV and safe_callable(attr):
                    attr = getattr(obj, name)()
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
