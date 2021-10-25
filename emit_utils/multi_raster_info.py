"""
This code does some useful manipulations on multiple raster files.

Author: Philip G. Brodrick, philip.brodrick@jpl.nasa.gov
"""


from osgeo import gdal
import numpy as np
import logging
import os


def get_bounding_extent(file_list: np.array, return_pixel_offsets=False, return_spatial_offsets=False,
                        return_global_lower_rights=False):
    """
    Get the outer bounded extent of a list of files, with options to also return pixel and
    spatial offsets of each file.  Pixel offsets assume everything is on the same grid.
    Args:
        file_list: array-like input of geospatial files
        return_pixel_offsets: flag indicating if per-file pixel offsets should be returned
        return_spatial_offsets: flag indicating if per-file spatial offsets should be returned
        return_global_lower_rights: flag indicating if per-file output-space lower right coordinates should be returned
    Returns:
        x_min, y_max, x_max, y_min, [offset_px_list (x,y tuples)], [offset_spatial_list (x,y tuples)], [global_lower_rights (x,y tuples)]
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
    global_lower_rights = []
    for trans, extent in zip(geotransforms, extents):
        x_offset_px = int(round((trans[0] - min_x)/trans[1]))
        x_offset_map = trans[0] - min_x

        y_offset_px = int(round((trans[3] - max_y)/trans[1]))
        y_offset_map = max_y - trans[3] # report in positive displacement units, arbitrary choice

        px_offsets.append((x_offset_px,y_offset_px))
        map_offsets.append((x_offset_map,y_offset_map))

        if return_global_lower_rights:
            x_lr_px = x_offset_px + extent[0]
            y_lr_px = y_offset_px + extent[1]
            global_lower_rights.append((x_lr_px, y_lr_px))


    if return_pixel_offsets:
        return_set += px_offsets

    if return_spatial_offsets:
        return_set += map_offsets

    return return_set


def get_bounding_extent_igms(file_list: np.array, return_per_file_xy=False):
    """
    Get the outer bounded extent of a list of IGMS, band-order x,y,z , with options to also return per-file bounding
    boxes.  No grid assumptions are required.
    Args:
        file_list: array-like input of geospatial files
        return_per_file_xy: flag indicating if per-file min/max xy maps should be returned
    Returns:
        x_min, y_max, x_max, y_min, [file_min_xy (x,y tuples)], [file_max_xy (x,y tuples)]
    """

    file_min_xy = []
    file_max_xy = []
    for file in file_list:
        dataset = gdal.Open(file, gdal.GA_ReadOnly)
        igm = dataset.ReadAsArray()[:2,...]
        file_min_xy.append((np.min(igm[0,...]), np.min(igm[1,...])))
        file_max_xy.append((np.max(igm[0,...]), np.max(igm[1,...])))
        logging.debug('File: {} loaded.  min xy: {}, max xy {}'.format(file, file_min_xy[-1], file_max_xy[-1]))

    # find bounding x and y coordinate locations
    min_x = np.nanmin([x[0] for x in file_min_xy])
    min_y = np.nanmin([x[1] for x in file_min_xy])
    max_x = np.nanmax([x[0] for x in file_max_xy])
    max_y = np.nanmax([x[1] for x in file_max_xy])
    logging.debug('Complete set min xy: {}, max xy: {}'.format((min_x, min_y),(max_x, max_y)))

    return_set = min_x, max_y, max_x, min_y
    if return_per_file_xy:
        return_set += file_min_xy, file_max_xy

    return return_set