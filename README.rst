Introduction
============

Plomino is a powerful and flexible web-based application builder for Plone.

Features
========

* create your own custom applications from a web interface without programming
* create and design forms in WYSIWYG mode
* easily embed charts or maps
* create specific actions with formula (compute fields, send emails, ...)
* adapt the application behaviour depending on the user access rights and roles
* import/export your application structure and/or your application data

Installation
============

To deploy Plomino, you need to edit your ``buildout.cfg`` file
and add the following in the ``eggs`` section::

    eggs =
         ...
         Products.CMFPlomino

Then you have to run ``buildout`` to realize your configuration::

    bin/buildout -N

Installation on Plone 4.0 and 4.1
=================================

If you're using Plone version older than 4.2 you'll need to add some
more directives to your buildout.cfg.
Plomino depends on plone.app.registry and plomino.tinymce requires
Products.TinyMCE>=1.2.13. To make Plomino work on pre-4.2 Plone sites
you need to pin those versions in your versions.cfg section::

    Products.TinyMCE=1.2.13
    collective.js.jqueryui=1.8.16.9

and use a known good set for plone.app.registry.

This means extending your buildout from::

    http://good-py.appspot.com/release/plone.app.registry/1.0b2?plone=4.0.9

replacing 4.0.9 with the actual version you need.

Support
=======

You can find support on the freenode IRC channel #plomino or using the `GitHub
issue tracker <https://github.com/plomino/Plomino/issues>`_

Tests
=====

Plomino is continuously tested on Travis |travisstatus|_ and the code coverage 
is tracked on coveralls.io |coveralls|_.

.. |travisstatus| image:: https://secure.travis-ci.org/plomino/Plomino.png?branch=github-main
.. _travisstatus:  http://travis-ci.org/plomino/Plomino

.. |coveralls| image:: https://coveralls.io/repos/plomino/Plomino/badge.png?branch=github-main
.. _coveralls: https://coveralls.io/r/plomino/Plomino?branch=github-main

Credits
=======

Authors
-------

* Eric BREHAULT <eric.brehault@makina-corpus.org>

Contributors
------------

* Jean Jordaan <jean.jordaan@gmail.com>
* Silvio Tomatis <silviot@gmail.com>

Companies
---------
|makinacom|_

* `Planet Makina Corpus <http://www.makina-corpus.org>`_
* `Contact us <mailto:python@makina-corpus.org>`_


.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com
