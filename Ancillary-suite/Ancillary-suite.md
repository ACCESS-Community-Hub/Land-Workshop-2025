# CCI Based Land Ancillary Suite

We have created an ancillary creation suite, building on work from Martin Best and Siyuan Tian, which generates ancillaries at arbitrary resolution. At its core is the CCI land cover dataset at 300m resolution. The resolution can be described either by a grid definition, or a supplied land mask.

## Stages in the Workflow

1. Map the input land cover map to the new grid with `ancil_lct.py`, specified either by a grid definition file or a landmask. A crosswalking table is used to convert input land cover types to output types.
2. Regrid a C4 grass fraction dataset to the desired resolution with `ancil_general_regrid.py`.
3. Split the C3 grass into C3 and C4 grasses, based on the regridded C4 dataset with `ancil_postproc_c4.py`.
4. Regrid the LAI NetCDF dataset to the desired resolution with `ancil_general_regrid.py`.
5. Assign LAI to the respective tiles using defined ratios of LAI between tiles with `ancil_lai.py`.
6. Compute canopy heights based on a NetCDF tree height dataset and a per-PFT empirical relationship to LAI with `ancil_canopy_heights.py`.
7. Merge the LAI and canopy heights into a `vegfunc` file with `ancil_2anc.py`.
8. Compute soil hydrology using an input NetCDF dataset and a lookup table with `ancil_soils.py`.
9. Compute topogrophy using an input NetCDF dataset with `ancil_topographic_index.py`.
10. Compute soil albedo using an input NetCDF dataset with `ancil_soil_albedo.py`.
11. Merge the hydrology and albedo ancillaries with `append.py`.
12. Compute soil constituent fractions using a UM ancillary file with `ancil_soil_dust.py`.
13. Compute soil roughness using the original LAI dataset with `ancil_soil_roughness.py`.

## What's missing

This is close to the full set ancillaries required for a CABLE gridinfo file. There are a few things missing:

* Tile classification (`iveg`): What restrictions to the various modes of operation e.g. POP put on the tile distribution?
* Soil moisture and temperature (`SoilMoist` and `SoilTemp`): These are state variables that aren't created by the ancillary suite. Should probably be moved out of gridinfo.
* Snow depth (`SnowDepth`): Another state variable, again should be moved out of gridinfo.
* Soil specific heat capacity (`css`): Ancillary suite creates heat capacity, which can be used with density to compute specific heat capacity. Does CABLE only use the product of specific heat capacity and density? If so, should it just be changed to volumetric heat capacity?
* Soil density (`rhosoil`): Is this used for anything other than specific to volumetric heat capacity conversion?
* `isoil` and `SoilOrder`: Are these actively used? What do they mean, where do they come from?
* Cell area (`Area`): Is this necessary in offline?

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

### `ancil_soil_albedo.py`

Usage: `ancil_soil_albedo.py <source>`, where `source` is a NetCDF file describing soil albedo. Generate the soil albedo ancillaries.

#### Arguments

* `--lct-ancillary <path>`: UM ancillary file describing the land cover.
* `--ants-config <path>`: ANTS config file for the app.
* `--use-new-saver`: Optional, whether to use the new ANTS saver, which additionally saves to NetCDF.
* `-o <path>`: File name to write the output to. If `--use-new-saver` is specified, then also saves to NetCDF with the `.nc` extension.

### `ancil_soil_dust.py`

Usage: `ancil_soil_albedo.py <source>`, where `source` is a UM ancillary file describing soil dust. Generates the soil dust ancillaries.

#### Arguments

* `--lct-ancillary <path>`: UM ancillary file describing the land cover.
* `--ants-config <path>`: ANTS config file for the app.
* `--use-new-saver`: Optional, whether to use the new ANTS saver, which additionally saves to NetCDF.
* `-o <path>`: File name to write the output to. If `--use-new-saver` is specified, then also saves to NetCDF with the `.nc` extension.

### `ancil_soil_roughness.py`

Usage: `ancil_soil_roughness.py <source>`, where `source` is a NetCDF file describing the soil roughness. Generates the soil roughness ancillary, with assistance from an LAI dataset.

#### Arguments

* `--target-lsm <path>`: Land-sea mask file to project onto.
* `--leaf-area-index <path>`: NetCDF file describing the leaf area index.
* `--use-new-saver`: Optional, whether to use the new ANTS saver, which additionally saves to NetCDF.
* `-o <path>`: File name to write the output to. If `--use-new-saver` is specified, then also saves to NetCDF with the `.nc` extension.
