# CCI Based Land Ancillary Suite

We have created an ancillary creation suite, building on work from Martin Best and Siyuan Tian, which generates ancillaries at arbitrary resolution. At its core is the CCI land cover dataset at 300m resolution. The resolution can be described either by a grid definition, or a supplied land mask.

## Stages in the Workflow

### `ancil_lct.py`

Usage: `ancil_lct.py <source>`, where `source` is the source vegetation distribution NetCDF file. Creates a new land cover map, and optionally a new land mask.

#### Arguments

* `--target-grid <path>`: Optional, grid definition file. One of `--target-grid` or `--target-lsm` must be specified.
* `--target-lsm <path>`: Optional, target land-sea mask to project onto. One of `--target-grid` or `--target-lsm` must be specified.
* `--transform-path <path>`: JSON file describing the mapping from source land cover types to the target types e.g. CABLE.
* `--ants-config <path>`: ANTS config file for the app.
* `--use-new-saver`: Optional, whether to use the new ANTS saver, which additionally saves to NetCDF.
* `-o <path>`: File name to write the output to. If `--use-new-saver` is specified, then also saves to NetCDF with the `.nc` extension.
* `-landseamask-output <path>`: Required if using `--target-grid`, the path to write the generated land-sea mask to.

The important part of this stage is the mapping from the source tile classes to the target tiles. This is done by a `N x M` matrix, where N is the number of input types, and M the output.

### `ancil_general_regrid.py`

Usage: `ancil_general_grid.py <source>`, where `source` is the source ancillary dataset. Regrids the ancillary dataset to the target resolution.

#### Arguments

* `--ants_config <path>`: ANTS config file for the app.
* `--target-lsm <path>`: Land-sea mask file to project onto.
* `-o <path>`: File name to write the output to.

### `ancil_lct_postproc_c4.py`

Usage: `ancil_lct_postproc_c4.py <source>`, where `source` is the original land cover map as NetCDF. Splits the initial C3 grass land cover into C3 and C4 cover.

#### Arguments

* `--islscpiic4 <path>`: C4 grass fractions at the same resolution as the original land cover map.
* `--c3level <int>`: Tile index containing the C3 grass.
* `--c4level <int>`: Tile index containing the C4 grass.
* `--use-new-saver`: Optional, whether to use the new ANTS saver, which additionally saves to NetCDF.
* `-o <path>`: File name to write the output to. If `--use-new-saver` is specified, then also saves to NetCDF with the `.nc` extension.

### `ancil_lai.py`

Usage: `ancil_lai.py <lai_source> <lct_source>`, where `lai_source` is the NetCDF file describing LAI and `lct_source` is the land cover map as NetCDF. Generates the LAI per tile, using user-defined ratios between tiles.

#### Arguments

* `--relative_weights <path>`: JSON file describing the weightings to be applied per PFT to the local LAI. See the documentation in the `ancil_lct.py` for a complete description of the process.
* `--ants-config <path>`: ANTS config file for the app.
* `--use-new-saver`: Optional, whether to use the new ANTS saver, which additionally saves to NetCDF.
* `-o <path>`: File name to write the output to. If `--use-new-saver` is specified, then also saves to NetCDF with the `.nc` extension.

### `ancil_canopy_heights.py`

Usage: `ancil_canopy_heights.py <source>`, where `source` is the NetCDF file describing the LAI. Generates the canopy height per tile, using user defined weightings and an a given input canopy height dataset.

#### Arguments

* `--canopy-height-factors <path>`: JSON file describing the ratio between LAI and canopy height per tile.
* `--trees-dataset <path>`: NetCDF file describing the canopy heights, to be applied to tree tiles.
* `--tree-ids <ints>`: Comma separated list of integers, describing which PFTs on the land cover map are trees.
* `--ants-config <path>`: ANTS config file for the app.
* `--use-new-saver`: Optional, whether to use the new ANTS saver, which additionally saves to NetCDF.
* `-o <path>`: File name to write the output to. If `--use-new-saver` is specified, then also saves to NetCDF with the `.nc` extension.

### `ancil_soils.py`

Usage: `ancil_soils.py <source>`, where `source` is a NetCDF file describing the soil hydrology. Generates the soil hydrology ancillaries.

#### Arguments

* `--lct-ancillary <path>`: UM ancillary file describing the land cover.
* `--soils-lookup <path>`: JSON file containing the soils lookup table.
* `--ants-config <path>`: ANTS config file for the app.
* `--use-new-saver`: Optional, whether to use the new ANTS saver, which additionally saves to NetCDF.
* `-o <path>`: File name to write the output to. If `--use-new-saver` is specified, then also saves to NetCDF with the `.nc` extension.

### `ancil_topographic_index.py`

Usage: `ancil_topographic_index.py <source>`, where `source` is a NetCDF file describing the topography.

#### Arguments

* `--lct-ancillary <path>`: UM ancillary file describing the land cover.
* `--ants-config <path>`: ANTS config file for the app.
* `--use-new-saver`: Optional, whether to use the new ANTS saver, which additionally saves to NetCDF.
* `-o <path>`: File name to write the output to. If `--use-new-saver` is specified, then also saves to NetCDF with the `.nc` extension.



