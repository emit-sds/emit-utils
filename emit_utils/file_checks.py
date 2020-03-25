"""
This code performs simple file checks, with particular consideration of geospatial files.

Author: Philip G. Brodrick, philip.brodrick@jpl.nasa.gov
"""

import os
import gdal
import logging
from typing import List


def check_files_exist(file_list: List):
    """ Check if files exist on the system.
    Args:
        file_list: array-like of files to check
    Returns:
        None
    """
    anybad = False
    for file in file_list:
        if os.path.isfile(file) is False:
            logging.error('File: {} does not exist'.format(file))
            anybad = True

    if anybad:
        FileNotFoundError('Files missing, check logs for details')


def check_raster_drivers(file_list: List):
    """ Check if files have a recognized gdal raster driver (e.g., can be opened).
    Args:
        file_list: array-like of files to check
    Returns:
        None
    """
    anybad = False
    for file in file_list:
        if gdal.Open(file, gdal.GA_ReadOnly) is None:
            logging.error('Input GLT file: {} not a recognized raster format'.format(file))
            anybad = True
    if anybad:
        FileNotFoundError('Files not in recognized raster format, check logs for details')


def check_same_raster_projections(file_list: List):
    """ Check that files have the same projection.  Assumes input files exist and are rasters.
    Args:
        file_list: array-like of files to check
    Returns:
        None
    """
    anybad = False
    base_projection = gdal.Open(file_list[0], gdal.GA_ReadOnly).GetGCPSpatialRef()
    for file in file_list:
        dataset = gdal.Open(file, gdal.GA_ReadOnly)
        if dataset.GetGCPSpatialRef() != base_projection:
            logging.error('Projection in file {} differs from projection in file {}'.format(file, file_list[0]))
            anybad = True
    if anybad:
        AttributeError('Files have mismatched projections, check logs for details')


def check_same_raster_resolutions(file_list: List, fractional_tolerance: float = 0.0001):
    """ Check that files have the same resolution.  Assumes input files exist and are rasters.
    Args:
        file_list: array-like of files to check
        fractional_tolerance: relative tolerance deemed acceptable for resolution mismatch
    Returns:
        None
    """
    anybad = False
    base_trans = gdal.Open(file_list[0], gdal.GA_ReadOnly).GetGeoTranform()
    for file in file_list:
        transform = gdal.Open(file, gdal.GA_ReadOnly).GetGeoTransform()
        if abs((transform[1] - base_trans[1])/base_trans[1]) < fractional_tolerance and \
           abs((transform[5] - base_trans[5]) / base_trans[5]) < fractional_tolerance:
            logging.error('Resolution in file {} differs from resolution in file {}'.format(file, file_list[0]))
            anybad = True
    if anybad:
        AttributeError('Files have mismatched resolutions, check logs for details')


def check_raster_files(file_list: List, fractional_tolerance: float = 0.0001, map_space: bool = False):
    """ Check that files exist, are openable by gdal, and have the same projections
    and resolutions (if necessary)
    Args:
        file_list: array-like of files to check
        fractional_tolerance: relative tolerance deemed acceptable for resolution mismatch
        map_space:
    Returns:
        None
    """

    check_files_exist(file_list)
    check_raster_drivers(file_list)
    if map_space:
        check_same_raster_projections(file_list)
        check_same_raster_resolutions(file_list, fractional_tolerance=fractional_tolerance)


