"""
Core utility package to support EMIT data processing.

Author: Philip G. Brodrick, philip.brodrick@jpl.nasa.gov
"""

from setuptools import setup, find_packages

setup(name='emit_utils',
      packages=find_packages(),
      include_package_data=True,
      version='0.2.0',
      install_requires=['gdal>=2.0'],
      python_requires='>=3',
      platforms='any',
      classifiers=['Programming Language :: Python :: 3',
                   'License :: OSI Approved :: Apache Software License',
                   'Operating System :: OS Independent'])
