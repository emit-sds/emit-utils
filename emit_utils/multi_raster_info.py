"""
This code does some useful manipulations on multiple raster files.

Author: Philip G. Brodrick, philip.brodrick@jpl.nasa.gov
"""


import gdal
from typing import List
import numpy as np


def get_bounding_extent(file_list: List, return_pixel_offsets=False, return_spatial_offsets=False):
    """
    Get the outer bounded extent of a list of files, with options to also return pixel and
    spatial offsets of each file.  Pixel offsets assume everything is on the same grid.
    Args:
        file_list: array-like input of geospatial files
        return_pixel_offsets: flag indicating if per-file pixel offsets should be returned
        return_spatial_offsets: flag indicating if per-file spatial offsets should be returned
    Returns:
        x_min, y_max, x_max, y_min, [offset_px_list (x,y tuples)], [offset_spatial_list (x,y tuples)]
    """

    geotransforms = []
    extents = []
    for file in file_list:
        dataset = gdal.Open(file, gdal.GA_ReadOnly)
        geotransforms.append(dataset.GetGeoTransform())
        extents.append((dataset.RasterXSize, dataset.RasterYSize))

    # find bounding x and y coordinate locations
    min_x = np.nanmin([x[0] for x in geotransforms])
    max_x = np.nanmin([x[0] + x[1]*xs[0] for x, xs in zip(geotransforms, extents)])
    max_y = np.nanmax([x[3] for x in geotransforms])
    min_y = np.nanmin([x[3] + x[5]*xs[1] for x, xs in zip(geotransforms, extents)])

    return_set = min_x, max_y, max_x, min_y
    if return_pixel_offsets is False and return_spatial_offsets is False:
        return return_set

    px_offsets = []
    map_offsets = []
    for trans in geotransforms:
        x_offset_px = int(round((trans[0] - min_x)/trans[1]))
        x_offset_map = trans[0] - min_x

        y_offset_px = int(round((trans[3] - max_y)/trans[1]))
        y_offset_map = max_y - trans[3] # report in positive displacement units, arbitrary choice

        px_offsets.append((x_offset_px,y_offset_px))
        map_offsets.append((x_offset_map,y_offset_map))

    if return_pixel_offsets:
        return_set += px_offsets

    if return_spatial_offsets:
        return_set += map_offsets

    return return_set


