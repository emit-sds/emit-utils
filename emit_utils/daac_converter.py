"""
This code contains support code for formatting products to NetCDF for the LP DAAC.

Authors: Philip G. Brodrick, philip.brodrick@jpl.nasa.gov
         Nimrod Carmon, nimrod.carmon@jpl.nasa.gov
"""

import hashlib
import netCDF4
import os

from datetime import datetime, timedelta
from osgeo import gdal, osr
from spectral.io import envi
from typing import List

from emit_utils.file_checks import envi_header

NODATA = -9999.

def _get_spatial_extent_res(path, projection_epsg=4326):
    """
    Get the spatial extent of a dataset, converted to a specified projection
    Args:
        path: path of file to get extent from, assumes this is projected
        projection_epsg: epsg number of the projection of the output extent
    Returns:
        List: extent of image in format [upper left x, upper left y, lower left x, lower left y]
        float: ground sampling distances
    """
    ds = gdal.Open(path)
    trans = ds.GetGeoTransform()

    ul = [trans[0], trans[3]]
    lr = [trans[0] + trans[1] * ds.RasterXSize, trans[3] + trans[5] * ds.RasterYSize]
    srs = osr.SpatialReference()
    srs.ImportFromWkt(ds.GetProjection())

    dst = osr.SpatialReference()
    dst.ImportFromEPSG(projection_epsg)
    transformer = osr.CoordinateTransformation(srs, dst)

    output_extent = [0,0,0,0]
    output_extent[0], output_extent[1], _ = transformer.TransformPoint(*ul)
    output_extent[2], output_extent[3], _ = transformer.TransformPoint(*lr)

    return output_extent, trans[1]


def add_variable(nc_ds, nc_name, data_type, long_name, units, data, kargs):
    kargs['fill_value'] = NODATA

    nc_var = nc_ds.createVariable(nc_name, data_type, **kargs)
    nc_var.long_name = long_name
    if units is not None:
        nc_var.units = units

    if data_type is str:
        for _n in range(len(data)):
            nc_var[_n] = data[_n]
    else:
        nc_var[...] = data
    nc_ds.sync()


def add_loc(nc_ds, loc_envi_file):
    """
    Add a location file to the netcdf output
    Args:
        nc_ds: output netcdf dataset to modify (mutable)
        loc_envi_file: envi formatted location file to add from

    Returns:

    """
    loc = envi.open(envi_header(loc_envi_file)).open_memmap(interleave='bip')
    add_variable(nc_ds, "location/lat", "d", "Longitude (WGS-84)", "degrees east", loc[..., 0].copy(),
                 {"dimensions": ("number_of_scans", "pixels_per_scan")} )

    add_variable(nc_ds, "location/lon", "d", "Latitude (WGS-84)", "degrees north", loc[..., 1].copy(),
                 {"dimensions": ("number_of_scans", "pixels_per_scan")} )

    add_variable(nc_ds, "location/z", "d", "Surface Elevation", "m", loc[..., 2].copy(),
                 {"dimensions": ("number_of_scans", "pixels_per_scan")} )
    nc_ds.sync()


def add_glt(nc_ds, glt_envi_file):
    """
    Add a location file to the netcdf output
    Args:
        nc_ds: output netcdf dataset to modify (mutable)
        glt_envi_file: envi formatted location file to add from

    Returns:
    """
    glt = envi.open(envi_header(glt_envi_file)).open_memmap(interleave='bip')
    add_variable(nc_ds, "location/glt_x", "i4", "GLT Sample Lookup", "pixel location",
                 glt[..., 0].copy(), {"dimensions": ("ortho_y", "ortho_x")})

    add_variable(nc_ds, "location/glt_y", "i4", "GLT Line Lookup", "pixel location",
                 glt[..., 1].copy(), {"dimensions": ("ortho_y", "ortho_x")})
    nc_ds.sync()


def makeDims(nc_ds: netCDF4.Dataset, primary_envi_file: str, glt_envi_file: str = None):
    """
    Set the dimensions of the netcdf otuput file
    Args:
        nc_ds: output netcdf dataset to modify (mutable)
        primary_envi_file: envi dataset (bil, bip, or bsq format) that can be read for key metadata
        glt_envi_file: envi dataset (bil, bip, or bsq format) that can be read for key metadata

    Returns:
    """

    primary_ds = envi.open(envi_header(primary_envi_file))
    nc_ds.createDimension('number_of_scans', int(primary_ds.metadata['lines']))
    nc_ds.createDimension('pixels_per_scan', int(primary_ds.metadata['samples']))
    nc_ds.createDimension('number_of_bands', int(primary_ds.metadata['bands']))

    # Geographical Dimensions
    if glt_envi_file is not None:
        glt_ds = gdal.Open(glt_envi_file, gdal.GA_ReadOnly)
        nc_ds.createDimension('ortho_y', glt_ds.RasterYSize)
        nc_ds.createDimension('ortho_x', glt_ds.RasterXSize)

    # flush
    nc_ds.sync()


def makeGlobalAttr(nc_ds: netCDF4.Dataset, primary_envi_file: str, glt_envi_file: str = None):
    """
    Set up global attributes that are universal.  Required attributes that should be populated by individual PGEs
    are flagged with None values
    Args:
        nc_ds: mutable netcdf dataset to be updated
        primary_envi_file: envi dataset (bil, bip, or bsq format) that can be read for key metadata
        glt_envi_file: envi dataset (bil, bip, or bsq format) that can be read for key metadata
    Returns:
    """

    primary_ds = envi.open(envi_header(primary_envi_file))

    # required and highly recommended
    nc_ds.ncei_template_version = "NCEI_NetCDF_Swath_Template_v2.0"  # required by cheatsheet
    nc_ds.title = "EMIT L1B At-Sensor Calibrated Radiance and Geolocation Data Swath, 72km, V001"
    nc_ds.summary = "The Earth Surface Mineral Dust Source Investigation (EMIT) is an Earth Ventures-Instrument (EVI-4) \
        Mission that maps the surface mineralogy of arid dust source regions via imaging spectroscopy in the visible and \
        short-wave infrared (VSWIR). Installed on the International Space Station (ISS), the EMIT instrument is a Dyson \
        imaging spectrometer that uses contiguous spectroscopic measurements from 410 to 2450 nm to resolve absoprtion \
        features of iron oxides, clays, sulfates, carbonates, and other dust-forming minerals. During its one-year mission, \
        EMIT will observe the sunlit Earth's dust source regions that occur within +/-52° latitude and produce maps of the \
        source regions that can be used to improve forecasts of the role of mineral dust in the radiative forcing \
        (warming or cooling) of the atmosphere."

    nc_ds.keywords = "Imaging Spectroscopy, minerals, EMIT, dust, radiative forcing"
    nc_ds.Conventions = "CF-1.63, ACDD-1.3"
    # Not required or highly recommended.
    nc_ds.sensor = "EMIT (Earth Surface Mineral Dust Source Investigation)"
    nc_ds.instrument = "EMIT"
    nc_ds.platform = "ISS"
    nc_ds.processing_version = "V1.0"
    nc_ds.Conventions = "CF-1.63"
    nc_ds.institution = "NASA Jet Propulsion Laboratory/California Institute of Technology"
    nc_ds.license = "https://science.nasa.gov/earth-science/earth-science-data/data-information-policy/"
    nc_ds.naming_authority = "LPDAAC"
    dt_now = datetime.now()
    nc_ds.date_created = dt_now.strftime("%Y-%m-%dT%H:%M:%SZ")
    nc_ds.keywords_vocabulary = "NASA Global Change Master Directory (GCMD) Science Keywords"
    nc_ds.stdname_vocabulary = "NetCDF Climate and Forecast (CF) Metadata Convention"
    nc_ds.creator_name = "Jet Propulsion Laboratory/California Institute of Technology"
    nc_ds.creator_email = "sarah.r.lundeen@jpl.nasa.gov"
    nc_ds.creator_url = "https://earth.jpl.nasa.gov/emit/"
    nc_ds.project = "Earth Surface Mineral Dust Source Investigation"
    nc_ds.project_url = "https://emit.jpl.nasa.gov/"
    nc_ds.publisher_name = "USGS LPDAAC"
    nc_ds.publisher_url = "https://lpdaac.usgs.gov"
    nc_ds.publisher_email = "lpdaac@usgs.gov"
    nc_ds.identifier_product_doi_authority = "http://dx.doi.org"

    #nc_ds.processing_level = "XXXX TO BE UPDATED"

    nc_ds.flight_line = os.path.basename(primary_envi_file)[:31]

    nc_ds.time_coverage_start = primary_ds.metadata['emit acquisition start time']
    nc_ds.time_coverage_end = primary_ds.metadata['emit acquisition stop time']
    nc_ds.product_version = primary_ds.metadata['emit software build version']
    nc_ds.history = "PGE Input files: " + ", ".join(primary_ds.metadata['emit pge input files'])

    # only include spatial information if provided (may not be available for all PGEs)
    if glt_envi_file is not None:
        ul_lr, res = _get_spatial_extent_res(glt_envi_file)
        nc_ds.easternmost_longitude = ul_lr[0]
        nc_ds.northernmost_latitude = ul_lr[1]
        nc_ds.westernmost_longitude = ul_lr[2]
        nc_ds.southernmost_latitude = ul_lr[3]
        nc_ds.spatialResolution = res

    nc_ds.day_night_flag = primary_ds.metadata['emit acquisition daynight']

    nc_ds.sync()  # flush


def calc_checksum(path, hash_alg="sha512"):
    checksum = {}
    if hash_alg.lower() == "sha512":
        h = hashlib.sha512()
    with open(path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            h.update(byte_block)
    return h.hexdigest()
