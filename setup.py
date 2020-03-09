# -*- coding: utf-8 -*-
"""Installer for the Products.CMFPlomino package."""

from setuptools import find_packages
from setuptools import setup


long_description = (
    open('README.md').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')


setup(
    name='Products.CMFPlomino',
    version='0.9.36.dev0',
    description="Application builder for Plone",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 5.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='Python Plone',
    author='Eric BREHAULT',
    author_email='ebrehault@gmail.com',
    url='http://pypi.python.org/pypi/Products.CMFPlomino',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup','ide']),
    namespace_packages=['Products'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'plone.api',
        'setuptools',
        'plone.app.dexterity',
        'jsonutil',
        'unicodecsv',
        'collective.instancebehavior',
        'pyquery < 1.3.0', # seems to break labels in macros somehow. Need to fix
        'plone.rest>=1.0a7',
        'plone.restapi>=1.0a11',
        'Products.CMFPlone > 5.0.8', #for tinymce 4.4.3 (mockup >= 2.4.0). and need branch=5.0.x-include-ajax-haed
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            'plone.app.contenttypes',
            'plone.app.robotframework[debug]',
            'plone.app.form', #required by plone.app.async
            'plone.app.async',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
