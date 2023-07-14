"""
A simple script to reformat EMIT netCDFs to alternate formats.

Author: Philip G. Brodrick, philip.brodrick@jpl.nasa.gov
"""
import argparse
import netCDF4
import numpy as np
from spectral.io import envi
from emit_utils.file_checks import envi_header
import os


envi_typemap = {
    'uint8': 1,
    'int16': 2,
    'int32': 3,
    'float32': 4,
    'float64': 5,
    'complex64': 6,
    'complex128': 9,
    'uint16': 12,
    'uint32': 13,
    'int64': 14,
    'uint64': 15
}

def single_image_ortho(img_dat, glt, glt_nodata_value=0):
    """Orthorectify a single image

    Args:
        img_dat (array like): raw input image
        glt (array like): glt - 2 band 1-based indexing for output file(x, y)
        glt_nodata_value (int, optional): Value from glt to ignore. Defaults to 0.

    Returns:
        array like: orthorectified version of img_dat
    """
    outdat = np.zeros((glt.shape[0], glt.shape[1], img_dat.shape[-1]))
    valid_glt = np.all(glt != glt_nodata_value, axis=-1)
    glt[valid_glt] -= 1 # account for 1-based indexing
    outdat[valid_glt, :] = img_dat[glt[valid_glt, 1], glt[valid_glt, 0], :]
    return outdat


def main(rawargs=None):
    parser = argparse.ArgumentParser(description="Apply OE to a block of data.")
    parser.add_argument('input_netcdf', type=str, help='File to convert.')
    parser.add_argument('output_dir', type=str, help='Base directory for output ENVI files')
    parser.add_argument('-ot', '--output_type', type=str, default='ENVI', choices=['ENVI'], help='Output format')
    parser.add_argument('--interleave', type=str, default='BIL', choices=['BIL','BIP','BSQ'], help='Interleave of ENVI file to write')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing file')
    parser.add_argument('--orthorectify', action='store_true', help='Orthorectify data')
    args = parser.parse_args(rawargs)

    nc_ds = netCDF4.Dataset(args.input_netcdf, 'r', format='NETCDF4')

    if os.path.isdir(args.output_dir) is False:
        err_str = f'Output directory {args.output_dir} does not exist - please create or try again'
        raise AttributeError(err_str)

    if args.orthorectify:
        glt = np.zeros(list(nc_ds.groups['location']['glt_x'].shape) + [2], dtype=np.int32)
        glt[...,0] = np.array(nc_ds.groups['location']['glt_x'])
        glt[...,1] = np.array(nc_ds.groups['location']['glt_y'])

    if args.output_type == 'ENVI':
        dataset_names = list(nc_ds.variables.keys())
        for ds in dataset_names:
            output_name = os.path.join(args.output_dir, os.path.splitext(os.path.basename(args.input_netcdf))[0] + '_' + ds)
            if os.path.isfile(output_name) and args.overwrite is False:
                err_str = f'File {output_name} already exists. Please use --overwrite to replace'
                raise AttributeError(err_str)
            nbands = 1
            if len(nc_ds[ds].shape) > 2:
                nbands = nc_ds[ds].shape[2]

            metadata = {
                'lines': nc_ds[ds].shape[0],
                'samples': nc_ds[ds].shape[1],
                'bands': nbands,
                'interleave': args.interleave,
                'header offset' : 0,
                'file type' : 'ENVI Standard',
                'data type' : envi_typemap[str(nc_ds[ds].dtype)],
                'byte order' : 0
            }

            for key in list(nc_ds.__dict__.keys()):
                if key == 'summary':
                    metadata['description'] = nc_ds.__dict__[key]
                elif key not in ['geotransform','spatial_ref' ]:
                    metadata[key] = f'{{ {nc_ds.__dict__[key]} }}'

            if args.orthorectify:
                metadata['lines'] = glt.shape[0]
                metadata['samples'] = glt.shape[1]
                gt = np.array(nc_ds.__dict__["geotransform"])
                metadata['map info'] = f'{{Geographic Lat/Lon, 1, 1, {gt[0]}, {gt[3]}, {gt[1]}, {gt[5]*-1},WGS-84}}'

                metadata['coordinate system string'] = f'{{ {nc_ds.__dict__["spatial_ref"]} }}' 

            if 'sensor_band_parameters' in nc_ds.__dict__.keys():
                band_parameters = nc_ds['sensor_band_parameters'].variables.keys() 
                for bp in band_parameters:
                    if bp == 'wavelengths' or bp == 'radiance_wl':
                        metadata['wavelength'] = np.array(nc_ds['sensor_band_parameters'].variables[bp]).astype(str).tolist()
                    elif bp == 'radiance_fwhm':
                        metadata['fwhm'] = np.array(nc_ds['sensor_band_parameters'].variables[bp]).astype(str).tolist()
                    elif bp == 'observation_bands':
                        metadata['band names'] = np.array(nc_ds['sensor_band_parameters'].variables[bp]).astype(str).tolist()
                    else:
                        metadata[bp] = np.array(nc_ds['sensor_band_parameters'].variables[bp]).astype(str).tolist()
            
            if 'wavelength' in list(metadata.keys()) and 'band names' not in list(metadata.keys()):
                metadata['band names'] = metadata['wavelength']

            envi_ds = envi.create_image(envi_header(output_name), metadata, ext='', force=args.overwrite) 
            mm = envi_ds.open_memmap(interleave='bip',writable=True)

            dat = np.array(nc_ds[ds])
            if len(dat.shape) == 2:
                dat = dat.reshape((dat.shape[0],dat.shape[1],1))

            if args.orthorectify:
                mm[...] = single_image_ortho(dat, glt)
            else:
                mm[...] = np.array(dat)
            del mm, envi_ds


if __name__ == "__main__":
    main()