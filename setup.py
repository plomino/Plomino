from setuptools import setup, find_packages
import os

version = '1.16.1'

setup(name='Products.CMFPlomino',
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
          'jsonutil',
          'collective.js.jqueryui',
          'collective.js.datatables',
          'collective.codemirror',
          'plomino.tinymce',
          'Products.CMFPlone',
      ],
      extras_require={
        'test': ['plone.app.testing',
                 'Products.PloneTestCase',
                 'selenium',
                 'archetypes.schemaextender' # to test import/export of extended fields
        ],
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """
      )
