from setuptools import setup, find_packages
import os

version = '1.0'

def read(*rnames):
    setupdir =  os.path.dirname( os.path.abspath(__file__))
    return open(
        os.path.join(setupdir, *rnames)
    ).read()

p = os.path.dirname(__file__)
long_description = '%s' % (
	""
)
setup(name='PlominoDoc',
      version=version,
      description="",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Mathieu Pasquet',
      author_email='kiorky@cryptelium.net',
      #url='',
      #license='BSD',
      namespace_packages=['PlominoDoc',],
      include_package_data=True,
      zip_safe=False,
      packages=find_packages('src'),
      extras_require={'test': ['ipython', 'zope.testing', ]},
      package_dir = {'': 'src'},
      install_requires=[
          #'setuptools',
          'Sphinx',
          'Pygments',
          'docutils',
      ],
      entry_points={
      },
     )
