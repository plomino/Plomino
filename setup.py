from setuptools import setup, find_packages
import os

version = '1.13.2'

setup(name='Plomino',
      version=version,
      description="Create specific applications in Plone without developing. Created by Makina Corpus.",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "INSTALL.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='RAD, dynamic forms, web application builder',
      author='Eric BREHAULT',
      author_email='eric.brehault@makina-corpus.org',
      url='http://www.plomino.net',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'simplejson',
          'dm.sharedresource',
          'collective.js.jqueryui',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """
      )
