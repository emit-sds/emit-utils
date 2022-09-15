"""
This code performs simple file checks, with particular consideration of geospatial files.

Author: Philip G. Brodrick, philip.brodrick@jpl.nasa.gov
"""

import os
from osgeo import gdal
import logging
import numpy as np
from spectral.io import envi


def check_cloudfraction(mask_file: str, mask_band=7) -> float:
    """
    Determines the cloud fraction from a mask file

    Args:
        mask_file (str): mask file (EMIT style)
        mask_band (int, optional): Band number to estimate clouds from.

    Returns:
        float: cloud fraction as rounded percent (0-100)
    """
    ds = envi.open(envi_header(mask_file))
    clouds = ds.open_memmap(interleave='bip')[...,mask_band]
    
    fraction = np.sum(clouds > 0) * 100 / np.product(clouds.shape) 
    return int(np.round(fraction))


def check_daynight(obs_file: str, zenith_band=4):
    """
    Determine if an acquisition is from daytime or nighttime
    Args:
        obs_file: path to scene observation file

    Returns:
        daynight: string indicator of day/night
    """
    ds = envi.open(envi_header(obs_file))
    zenith = ds.open_memmap(interleave='bip').open_memmap()[...,zenith_band]
    min_zenith = np.percentile(zenith[zenith != -9999], 2)
    max_zenith = np.percentile(zenith[zenith != -9999], 98)
    if min_zenith < 90 and max_zenith < 90:
        return 'day'
    else:
        return 'night'

def check_files_exist(file_list: np.array):
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
        raise FileNotFoundError('Files missing, check logs for details')


def check_raster_drivers(file_list: np.array):
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
        raise FileNotFoundError('Files not in recognized raster format, check logs for details')


def check_same_raster_projections(file_list: np.array):
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
        raise AttributeError('Files have mismatched projections, check logs for details')


def check_same_raster_resolutions(file_list: np.array, fractional_tolerance: float = 0.0001):
    """ Check that files have the same resolution.  Assumes input files exist and are rasters.
    Args:
        file_list: array-like of files to check
        fractional_tolerance: relative tolerance deemed acceptable for resolution mismatch
    Returns:
        None
    """
    anybad = False
    base_trans = gdal.Open(file_list[0], gdal.GA_ReadOnly).GetGeoTransform()
    for file in file_list:
        transform = gdal.Open(file, gdal.GA_ReadOnly).GetGeoTransform()
        if abs((transform[1] - base_trans[1])/base_trans[1]) > fractional_tolerance and \
           abs((transform[5] - base_trans[5]) / base_trans[5]) > fractional_tolerance:
            logging.error('Resolution difference. File {} resolution: {} {}\n'
                          '                       File {} resolution: {} {} '.format(file, transform[1], transform[5], file_list[0], base_trans[1], base_trans[5]))
            anybad = True
    if anybad:
        raise AttributeError('Files have mismatched resolutions, check logs for details')


def check_raster_files(file_list: np.array, fractional_tolerance: float = 0.0001, map_space: bool = False):
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


def envi_header(inputpath):
    """
    Convert a envi binary/header path to a header, handling extensions
    Args:
        inputpath: path to envi binary file
    Returns:
        str: the header file associated with the input reference.

    """
    if os.path.splitext(inputpath)[-1] == '.img' or os.path.splitext(inputpath)[-1] == '.dat' or os.path.splitext(inputpath)[-1] == '.raw':
        # headers could be at either filename.img.hdr or filename.hdr.  Check both, return the one that exists if it
        # does, if not return the latter (new file creation presumed).
        hdrfile = os.path.splitext(inputpath)[0] + '.hdr'
        if os.path.isfile(hdrfile):
            return hdrfile
        elif os.path.isfile(inputpath + '.hdr'):
            return inputpath + '.hdr'
        return hdrfile
    elif os.path.splitext(inputpath)[-1] == '.hdr':
        return inputpath
    else:
        return inputpath + '.hdr'


def netcdf_ext(basepath):
    """
    Give filename with consistent netcdf output file extention
    Args:
        basepath: path with or without netcdf extension
    Returns:
        str: the basepath with the netcdf extension
    """

    if os.path.splitext(basepath)[-1] == ".nc":
        return os.path.splitext(basepath)[0] + '.nc'
    else:
        return basepath + '.nc'


def get_gring_boundary_points(glt_hdr_path: str):
    hdr = envi.read_envi_header(glt_hdr_path)
    # Assume the gring list starts with "Geographic Lon/Lat" followed by pairs of lon/lat
    gring = hdr["gring"]
    points = []
    for i in range(1, len(gring), 2):
        points.append([float(gring[i]), float(gring[i + 1])])
    return points


def get_band_mean(input_file: str, band) -> float:
    """
    Determines the mean of a band
    Args:
        input_file (str): obs file (EMIT style)
        band (int, optional): Band number retrieve average from.
    Returns:
        float: mean value of given band
    """
    ds = envi.open(envi_header(input_file))
    target = ds.open_memmap(interleave='bip')[..., band]

    good = target > -9990

    return np.mean(target[good])