-------------------
Installation
-------------------

Prerequisites
-------------

Plomino is a Plone products, so to install Plomino, you first need to install 
Plone : go to plone.org, download Plone and follow the instructions.

Deploy Plomino egg
------------------

To deploy the Plomino product, you need to edit your buildout.cfg and add 
the following in the eggs section and in the zcml section::

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
pypi.python.org repository and deploy it in your Zope instance.

Now you can restart your Zope instance and in your Plone site, go to Site 
setup / Add-on products.

Here you should see Plomino and plomino.tinymce in the list of installable 
products, select them and click Install.

Once done, Plomino is installed, so when you are in a folder, you can add a 
new Plomino database uisng the Plone "Add new..." menu.