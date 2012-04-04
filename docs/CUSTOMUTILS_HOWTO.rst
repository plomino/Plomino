How to provide a custom Plomino util as a plugin
================================================

Plomino provides a set of utility functions in ``PlominoUtils``
(``DateToString``, ``asUnicode``, etc.).

In addition, custom Plomino utilities can be declared to Plomino from a
custom package, and they will be available from any Plomino formula.

Example::

    from zope import component
    from Products.PythonScripts.Utility import allow_module

Create the utility methods in your extension module (e.g.
``mypackage.mymodule``)::

    import simplejson as json

    def jsonify(obj):
        return json.dumps(obj)

    def dejsonify(s):
        return json.loads(s)

Create a class to declare them::

    class UnepUtils:
        module = "mypackage.mymodule"
        methods = ['jsonify', 'dejsonify']

Declare the module as safe so it can be called from Python Scripts
(all Plomino formula are Python Scripts)::

    allow_module("mypackage.mymodule")

And register it with Plomino in a ``configure.zcml`` file::

  <utility
        name="MyUtils"
        provides="Products.CMFPlomino.interfaces.IPlominoUtils"
        component="mypackage.mymodule"
        />

Now, ``jsonify`` and ``dejsonify`` can be used in any Plomino formula.
