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
import json
import numpy as np

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

    add_variable(nc_ds, "location/elev", "d", "Surface Elevation", "m", loc[..., 2].copy(),
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


def get_required_ummg():
    """ Get the required UMMG base dictionary

    Returns:
        ummg: dictionary with required parameters

    """
    ummg = {}
    ummg['MetadataSpecification'] = {}
    ummg['GranuleUR'] = ''
    ummg['ProviderDates'] = []
    ummg['CollectionReference'] = ''
    return ummg


def initialize_ummg(granule_name: str, creation_time: datetime, collection_name: str, collection_version: str = "001"):
    """ Initialize a UMMG metadata output file
    Args:
        granule_name: granule UR tag
        creation_time: creation timestamp
        collection_name: short name of collection reference
        collection_version: collection version

    Returns:
        dictionary representation of ummg
    """

    ummg = get_required_ummg()
    ummg['MetadataSpecification'] = {'URL': 'https://cdn.earthdata.nasa.gov/umm/granule/v1.6.3', 'Name': 'UMM-G',
                                     'Version': '1.6.3'}

    #
    #ummg['Platforms'] = {'ShortName': 'ISS', 'Instruments': {'ShortName': 'EMIT'} }
    #ummg['AdditionalAttributes'] = [{'Name': 'SPATIAL_RESOLUTION', 'Values': ["60.0"]}]
    ummg['GranuleUR'] = granule_name
    ummg['ProviderDates'].append({'Date': creation_time.strftime("%Y-%m-%dT%H:%M:%SZ"), 'Type': "Insert"})
    ummg['CollectionReference'] = {
        "ShortName": collection_name,
        "Version": collection_version
    }
    return ummg


class SerialEncoder(json.JSONEncoder):
    """Encoder for json to help ensure json objects can be passed to the workflow manager.
    """

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        else:
            return super(SerialEncoder, self).default(obj)


def dump_json(json_content: dict, filename: str):
    """
    Dump the dictionary to an output json file
    Args:
        json_content: dictionary to write out
        filename: output filename to write to
    """

    with open(filename, 'w', errors='ignore') as fout:
        fout.write(json.dumps(json_content, indent=2, sort_keys=False, cls=SerialEncoder))


def add_boundary_ummg(ummg: dict, boundary_points: list):
    """
    Add boundary points list to UMMG in correct format
    Args:
        ummg: existing UMMG to augment
        boundary_points: list of lists, each major list entry is a pair of (lon, lat) coordinates

    Returns:
        dictionary representation of ummg
    """


    formatted_points_list = []
    for point in boundary_points:
        formatted_points_list.append({'Longitude': point[0], 'Latitude': point[1]})

    # For GPolygon, add the first point again to close out
    formatted_points_list.append({'Longitude': boundary_points[0][0], 'Latitude': boundary_points[0][1]})

    hsd = {"HorizontalSpatialDomain":
              {"Geometry":
                  {"GPolygons": [
                      {'Boundary':
                           {'Points': formatted_points_list}}
                  ]}
              }
          }


    ummg['SpatialExtent'] = hsd
    return ummg


def add_data_file_ummg(ummg: dict, data_file_name: str, daynight: str, file_format: str ='NETCDF-4'):
    """
    Add boundary points list to UMMG in correct format
    Args:
        ummg: existing UMMG to augment
        data_file_name: path to existing data file to add
        file_format: description of file type

    Returns:
        dictionary representation of ummg with new data granule
    """
    prod_datetime_str = None
    for subdict in ummg['ProviderDates']:
        if subdict['Type'] == 'Insert':
            prod_datetime_str = subdict['Date']
            break

    ummg['DataGranule'] = {
        'DayNightFlag': daynight,
        'ArchiveAndDistributionInformation': [{
            "Name": os.path.basename(data_file_name),
            "SizeInBytes": os.path.getsize(data_file_name),
            "Format": file_format,
            "Checksum": {
                'Value': calc_checksum(data_file_name),
                'Algorithm': 'SHA-512'
            }
        }]
    }
    if prod_datetime_str is not None:
        ummg['DataGranule']['ProductionDateTime'] = prod_datetime_str

    return ummg


def write_ummg(output_filename: str, ummg: dict):
    """
    Write UMMG file to disk
    Args:
        output_filename: destination to write file to
        ummg: dictionary to write out

    Returns:
        none
    """
    errors = check_ummg()
    if len(errors) > 0:
        return errors

    with open(output_filename, errors='ignore') as fout:
        fout.write(json.dumps(ummg, indent=2, sort_keys=False))


def check_ummg(ummg: dict):
    """
    Args:
        ummg: dict to check for UMMG format

    Returns:
        error: list of errors

    """
    error_list = []
    base_ummg = get_required_ummg()
    for key in base_ummg.keys():
        if key not in ummg.keys() or isinstance(type(base_ummg[key]), type(ummg[key])) is False:
            error_list.append(f'Key {key} missing or formatted incorrectly')

    return error_list


def calc_checksum(path, hash_alg="sha512"):
    checksum = {}
    if hash_alg.lower() == "sha512":
        h = hashlib.sha512()
    with open(path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            h.update(byte_block)
    return h.hexdigest()
