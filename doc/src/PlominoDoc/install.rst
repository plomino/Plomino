-------------------
Installation
-------------------

Prerequisites
-------------

Plomino is a Plone products, so to install Plomino, you first need to
install Plone: go to http://plone.org, download Plone and follow the
instructions.

Deploy Plomino egg
------------------

To deploy the Plomino product, you need to edit your ``buildout.cfg`` and
add the following in the eggs section and in the ZCML section::

    eggs =
         ...
         Plomino
         plomino.tinymce
         
    zcml =
         ...
         plomino.tinymce

Then you have to run your buildout::

    bin/buildout -N

It will download the latest Plomino version (and its dependencies) from the 
http://pypi.python.org/ repository and deploy it in your Zope instance.

Now you can restart your Zope instance and in your Plone site, go to 
*Site setup / Add-on products*.

Here you should see ``Plomino`` and ``plomino.tinymce`` in the list of
installable products. Select them and click *Install*.

Once done, Plomino is installed, so when you are in a folder, you can add a 
new Plomino database using the Plone *"Add new..."* menu.
