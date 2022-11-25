
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

def main(rawargs=None):
    parser = argparse.ArgumentParser(description="Apply OE to a block of data.")
    parser.add_argument('input_netcdf', type=str, help='File to convert.')
    parser.add_argument('output_dir', type=str, help='Base directory for output ENVI files')
    parser.add_argument('-ot', '--output_type', type=str, default='ENVI', choices=['ENVI'], help='Output format')
    parser.add_argument('--interleave', type=str, default='BIL', choices=['BIL','BIP','BSQ'], help='Interleave of ENVI file to write')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing file')
    args = parser.parse_args(rawargs)

    nc_ds = netCDF4.Dataset(args.input_netcdf, 'r', format='NETCDF4')

    if args.output_type == 'ENVI':
        dataset_names = list(nc_ds.variables.keys())
        for ds in dataset_names:
            output_name = os.path.join(args.output_dir, os.path.splitext(os.path.basename(args.input_netcdf))[0] + '_' + ds)
            if os.path.isfile(output_name) and args.overwrite is False:
                err_str = f'File {output_name} already exists. Please use --overwrite to replace'
                raise AttributeError(err_str)
            metadata = {
                'lines': nc_ds[ds].shape[0],
                'samples': nc_ds[ds].shape[1],
                'bands': nc_ds[ds].shape[2],
                'interleave': args.interleave,
                'header offset' : 0,
                'file type' : 'ENVI Standard',
                'data type' : envi_typemap[str(nc_ds[ds].dtype)],
                'interleave' : 'bil',
                'byte order' : 0
            }
            for key in list(nc_ds.__dict__.keys()):
                if key == 'summary':
                    metadata['description'] = nc_ds.__dict__[key]
                elif key not in ['geotransform','spatial_ref' ]:
                    metadata[key] = f'{{ {nc_ds.__dict__[key]} }}'

            band_parameters = nc_ds['sensor_band_parameters'].variables.keys() 
            for bp in band_parameters:
                if bp == 'wavelengths':
                    metadata['wavelength'] = np.array(nc_ds['sensor_band_parameters'].variables[bp]).astype(str).tolist()
                else:
                    metadata[bp] = np.array(nc_ds['sensor_band_parameters'].variables[bp]).astype(str).tolist()

            envi_ds = envi.create_image(envi_header(output_name), metadata, ext='', force=args.overwrite) 
            mm = envi_ds.open_memmap(interleave='bip',writable=True)
            mm[...] = np.array(nc_ds[ds])
            del mm, envi_ds











if __name__ == "__main__":
    main()