### Changelog

All notable changes to this project will be documented in this file. Dates are displayed in UTC.

#### [v1.3.4](https://github.com/emit-sds/emit-utils/compare/v1.3.3...v1.3.4)

> 7 Oct 2025

* License update by @adamchlus in https://github.com/emit-sds/emit-utils/pull/18

#### [v1.3.3](https://github.com/emit-sds/emit-utils/compare/v1.3.2...v1.3.3)

> 24 June 2025

* resolve flat field issue with ortho flag on by @pgbrodrick in https://github.com/emit-sds/emit-utils/pull/16

#### [v1.3.2](https://github.com/emit-sds/emit-utils/compare/v1.3.1...v1.3.2)

> 5 May 2025
> 
* Cosmetic tweaks - fix version number in setup.py and bad date in change log.

#### [v1.3.1](https://github.com/emit-sds/emit-utils/compare/v1.3.0...v1.3.1)

> 2 April 2025
> 
* Fix check for sensor band parameters in NETCDF to ENVI conversion by @vatsal-j in https://github.com/emit-sds/emit-utils/pull/13

#### [v1.3.0](https://github.com/emit-sds/emit-utils/compare/v1.2.3...v1.3.0)

> 1 September 2023

- Reformat update [`#10`](https://github.com/emit-sds/emit-utils/pull/10)
- add in l2b support [`eca74ad`](https://github.com/emit-sds/emit-utils/commit/eca74adc7e17a1d5ee0af072d5f02881146350ed)
- Read in ffupdate paths from runconfig (not ENVI header) [`15ce3ee`](https://github.com/emit-sds/emit-utils/commit/15ce3ee7a01c3824def5914c72332a8d84024025)
- Fix runconfig references [`3596959`](https://github.com/emit-sds/emit-utils/commit/3596959d5f1b103e82179361ffd4d5ed3b0a7ab2)

#### [v1.2.3](https://github.com/emit-sds/emit-utils/compare/v1.2.2...v1.2.3)

> 17 February 2023

- Merge develop into main for v1.2.3 [`#9`](https://github.com/emit-sds/emit-utils/pull/9)
- Add software delivery version to UMM-G and NetCDF metadata [`e881f7a`](https://github.com/emit-sds/emit-utils/commit/e881f7af6e77e97408426d211e6dd4d6c80e8b15)
- Update change log [`b74962c`](https://github.com/emit-sds/emit-utils/commit/b74962c78a3f5af76e3706a5e2c27980fb2d91c9)
- Update version to 1.2.3 [`dfd9a2f`](https://github.com/emit-sds/emit-utils/commit/dfd9a2f7ae978840f09e483dc7f75268858e189a)

#### [v1.2.2](https://github.com/emit-sds/emit-utils/compare/v1.2.1...v1.2.2)

> 25 January 2023

- Merge develop into main for v1.2.2 [`#8`](https://github.com/emit-sds/emit-utils/pull/8)
- Update change log [`a81cce6`](https://github.com/emit-sds/emit-utils/commit/a81cce608ab526cf022f5f257496096341e849f0)
- bugfix for east/west long metadata [`a6de126`](https://github.com/emit-sds/emit-utils/commit/a6de12627606c615fc462c60f30fb3a9779b9cb3)
- Update to 1.2.2 [`08ac199`](https://github.com/emit-sds/emit-utils/commit/08ac1993ffd5762234836925094f6a390f41ed87)

#### [v1.2.1](https://github.com/emit-sds/emit-utils/compare/v1.2.0...v1.2.1)

> 12 January 2023

- Merge develop into main for v1.2.1 [`#7`](https://github.com/emit-sds/emit-utils/pull/7)
- add flip tracking to global attributes [`#6`](https://github.com/emit-sds/emit-utils/pull/6)
- add reformatter for netcdf files....ENVI for now [`2cfff04`](https://github.com/emit-sds/emit-utils/commit/2cfff0430d4dbf6352adf5ef5f842137039c7c32)
- account for origin mismatch, add ortho option [`8061050`](https://github.com/emit-sds/emit-utils/commit/8061050edb9d7d3eea632ae09a511824f5e5d8e2)
- update mapinfo string and revert flip [`d63bd52`](https://github.com/emit-sds/emit-utils/commit/d63bd52f09e00e61ee7da82e6d0f8b52e055516e)

#### [v1.2.0](https://github.com/emit-sds/emit-utils/compare/v1.1.0...v1.2.0)

> 17 October 2022

- Merge develop into main for v1.2.0 [`#4`](https://github.com/emit-sds/emit-utils/pull/4)
- UMM-G Updates [`#3`](https://github.com/emit-sds/emit-utils/pull/3)
- Add temporal extent. Add additional attributes. Remove related urls. Add geodetic to spatial extent. [`3d05719`](https://github.com/emit-sds/emit-utils/commit/3d057192b36193e36a7985fd0609dc3d2e3fef8c)
- Add gring and band mean functions to file checks. [`6ae72a6`](https://github.com/emit-sds/emit-utils/commit/6ae72a63e4938df715008e4df10d59bd05e08f92)
- Support DOIs and use new terminology (orbit, orbit_segment, scene) [`3a7bde7`](https://github.com/emit-sds/emit-utils/commit/3a7bde7bcd9b9ca8e30458bb181688cf83ed2e1f)

#### [v1.1.0](https://github.com/emit-sds/emit-utils/compare/v1.0.0...v1.1.0)

> 6 June 2022

- Merge develop to main for v1.1.0 [`#2`](https://github.com/emit-sds/emit-utils/pull/2)
- Ummg updates [`#1`](https://github.com/emit-sds/emit-utils/pull/1)
- change add_data_file_ummg to plural, accept multiple files as list [`daf7e43`](https://github.com/emit-sds/emit-utils/commit/daf7e437b6e2c265f907152b32edc9fd862f153b)
- Update change log [`23a56f5`](https://github.com/emit-sds/emit-utils/commit/23a56f5bf5a9947992cf6d046b65f6ac96d95361)
- notes for to-dos and some updates [`2dfc286`](https://github.com/emit-sds/emit-utils/commit/2dfc286c0cafb38daf404d295c1c0845d6cd2641)

### [v1.0.0](https://github.com/emit-sds/emit-utils/compare/v0.4.0...v1.0.0)

> 9 February 2022

- Merge develop to main for 1.0.0 [`#8`](https://github.com/emit-sds/emit-utils/pull/8)
- break out metadata specs for easy att use [`b469551`](https://github.com/emit-sds/emit-utils/commit/b4695512a9276bf79f6e1435fb59e66c547f320e)
- Update changelog [`cd3058b`](https://github.com/emit-sds/emit-utils/commit/cd3058bbc12754a0e34f928d92bd67f53bf06f70)
- Increment version to 1.0.0 [`7a47a2a`](https://github.com/emit-sds/emit-utils/commit/7a47a2a93405fe3c4e9a2bc06aa4a1aac4dd84c1)

#### [v0.4.0](https://github.com/emit-sds/emit-utils/compare/v0.3.0...v0.4.0)

> 31 January 2022

- Merge develop into main for v0.4.0 [`#7`](https://github.com/emit-sds/emit-utils/pull/7)
- Ummg file creation [`#6`](https://github.com/emit-sds/emit-utils/pull/6)
- Update changelog for v0.4.0 [`aa75861`](https://github.com/emit-sds/emit-utils/commit/aa75861c7daf8e3c4fb9a22327355a38aacd9e7b)
- Change setup version to 0.4.0 [`7d7d404`](https://github.com/emit-sds/emit-utils/commit/7d7d404a3e5a9ba622354aac1adb606474412e67)
- Resolve conflict [`88aa674`](https://github.com/emit-sds/emit-utils/commit/88aa674c2adce357a61cae0a2e9fcf505f12e9d2)

#### [v0.3.0](https://github.com/emit-sds/emit-utils/compare/v0.2.0...v0.3.0)

> 20 January 2022

- Merge develop for release 0.3.0 [`#5`](https://github.com/emit-sds/emit-utils/pull/5)
- Daac interface [`#4`](https://github.com/emit-sds/emit-utils/pull/4)
- Netcdf [`#3`](https://github.com/emit-sds/emit-utils/pull/3)
- adds netcdf converter basics, still needs a few updates [`36e4a58`](https://github.com/emit-sds/emit-utils/commit/36e4a58dce35d88b3ffafb217d9243e39ed5b1ec)
- Add changelog [`5d4f786`](https://github.com/emit-sds/emit-utils/commit/5d4f786868c3b3dcb5bdd78a932ef95b63177c9c)
- Add requirements to setup file based on import statements. Add calc_checksum function that defaults to sha512 checksum, but can be augmented to include others. [`30677d8`](https://github.com/emit-sds/emit-utils/commit/30677d8cf8bdda89f32cb23252826e95c100a72d)

#### [v0.2.0](https://github.com/emit-sds/emit-utils/compare/v0.1.0...v0.2.0)

> 25 October 2021

- Merge develop for version 0.2.0. [`#2`](https://github.com/emit-sds/emit-utils/pull/2)
- update gdal imports, add safe envi header reference [`b3b9f66`](https://github.com/emit-sds/emit-utils/commit/b3b9f663e23ebbebc8e6b183f9bd90c3a20639f5)
- Increment version to 0.2.0 [`3a5859f`](https://github.com/emit-sds/emit-utils/commit/3a5859fac439dfc8bc968b1e072535b69861843f)
- Update readme. [`ca6b5af`](https://github.com/emit-sds/emit-utils/commit/ca6b5af3df2229cd78b6dba2885fc38b496a7604)

#### v0.1.0

> 26 January 2021

- Merge develop to main for v0.1.0 release [`#1`](https://github.com/emit-sds/emit-utils/pull/1)
- added install file, basic file checking, started multi-raster functions [`5fd1b47`](https://github.com/emit-sds/emit-utils/commit/5fd1b4784a21cc948be410565ca5e525dfbf0c7f)
- add igm map space lookups [`f5f2250`](https://github.com/emit-sds/emit-utils/commit/f5f2250a9ab6faa3bba44718f3d13509b84a9439)
- input type changes to file checks for ease, extra multi-raster info return options [`707d038`](https://github.com/emit-sds/emit-utils/commit/707d03868cb1b5ad0473350a268a158577cee20c)
