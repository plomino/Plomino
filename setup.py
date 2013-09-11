from setuptools import setup, find_packages
import os

version = '1.17.4'

setup(name='Products.CMFPlomino',
      version=version,
      description=(
          "Create specific applications in Plone without developing. "
          "Created by Makina Corpus."),
      long_description="\n".join([
          open("README.rst").read(),
          open(os.path.join("docs", "INSTALL.txt")).read(),
          open(os.path.join("docs", "HISTORY.txt")).read()]),
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
          'python-dateutil>=1.5',
          'plone.app.registry',
          'plone.app.jquery',
          'zope.app.component',  # Helps Plone 4.0, should not hurt elsewhere.
          'zope.globalrequest',  # This one too.
      ],
      extras_require={
          'test': [
              'plone.app.testing[robot]>=4.2.2',
              'python-dateutil',  # (import error without this)
              'plone.app.robotframework',
              'Products.PloneTestCase',
              'selenium',
              # to test import/export of extended fields:
              'archetypes.schemaextender'
              ],
          },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """
      )
