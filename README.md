<h1 align="center">emit-utils</h1>

Welcome to the EMIT utils science data system repository.  To understand how this repository is linked to the rest of the emit-sds repositories, please see [the repository guide](https://github.com/emit-sds/emit-main/wiki/Repository-Guide).

The emit utils repository provides general convenience utilities used broadly throughout the emit-sds.  This repository can be installed locally by:

```
git clone git@github.com:emit-sds/emit-utils.git
pip install --editable git@github.com:emit-sds/emit-utils.git
```

In addition to integrated utilities, this repository includes a reformatting script to convert EMIT netCDF files (as delivered to the LP DAAC) to ENVI files.  Simply run:

```
python emit_utils/reformat.py example.nc OUTPUT_DIR
```

Optionally, the '--orthorectify' option can be added to use the embedded GLT for rapid orthorectification.