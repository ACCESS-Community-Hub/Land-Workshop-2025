# The mule Python Package

### The tool you don't want to use, but sometimes you have to

The `mule` python package is developed by the UK Met Office for working with various UM formats. There is a Github repository for the code at (git@github.com:metomi/mule.git), but this is not used for development and is only updated sporadically. The ACCESS-NRI fork of `mule` can be pulled from the Conda channel `accessnri` via `conda install accessnri::mule`. It is also available from the `conda/analysis3-25.08` and later environments on `xp65`.

## What is it

`mule` is a tool for inspecting and manipulating the pure data contained within UM files. The files contain a fixed length header, which is just an array of numerical values, and a series of 2D arrays with numerical metadata. The metadata is not discernable without a key, which `mule` provides a passable key for.

## When to use it

One would use `mule` when:

* You want to manipulate the underlying data without any abstractions obfuscating what's going on under the hood.
* The file is not readable by Iris e.g. ACCESS-ESM1.6 restart.

## Working with a Fields File

We'll focus on working with UM fields files, as this is where my experience lies. I suspect PP files, the other format handled by `mule`, are less likely to have issues with Iris. Opening a fields file acts similar to NetCDF- it really just loads the metadata into memory, and provides a view to the underlying pure data.

```python
import mule

>>> ff = mule.FieldsFile.from_file("/g/data/vk83/prerelease/configurations/inputs/access-esm1p6/modern/pre-industrial/restart/2025.08.01/atmosphere/restart_dump.astart")
>>> ff.
ff.COMPONENTS                  ff.WRITE_OPERATORS             ff.compressed_field_index2     ff.fixed_length_header         ff.real_constants              ff.to_file(
ff.DATASET_TYPES               ff.additional_parameters       ff.compressed_field_index3     ff.from_file(                  ff.remove_empty_lookups()      ff.validate(
ff.FIELD_CLASSES               ff.attach_stashmaster_info(    ff.copy(                       ff.from_template(              ff.row_dependent_constants     
ff.READ_PROVIDERS              ff.column_dependent_constants  ff.extra_constants             ff.integer_constants           ff.stashmaster                 
ff.WORD_SIZE                   ff.compressed_field_index1     ff.fields                      ff.level_dependent_constants   ff.temp_historyfile
```

In my experience, many of these attributes will either be either empty or contain nonsensical data. The fields likely to be of interest are:

* `ff.integer_constants`: particularly `num_rows, num_cols`, which describe the grid size.
    ```python
    >>> ff.integer_constants.
    ff.integer_constants.CREATE_DIMS            ff.integer_constants.from_file(             ff.integer_constants.num_passive_tracers    ff.integer_constants.sh_zonal_begin
    ff.integer_constants.DTYPE                  ff.integer_constants.height_algorithm       ff.integer_constants.num_radiation_vars     ff.integer_constants.sh_zonal_flag
    ff.integer_constants.HEADER_MAPPING         ff.integer_constants.integer_mdi            ff.integer_constants.num_rows               ff.integer_constants.sh_zonal_period
    ff.integer_constants.MDI                    ff.integer_constants.meaning_interval       ff.integer_constants.num_soil_hydr_levels   ff.integer_constants.shape
    ff.integer_constants.amip_current_day       ff.integer_constants.n_steps_since_river    ff.integer_constants.num_soil_levels        ff.integer_constants.suhe_level_cutoff
    ff.integer_constants.amip_first_month       ff.integer_constants.num_boundary_levels    ff.integer_constants.num_tracer_adv_levels  ff.integer_constants.suhe_level_weight
    ff.integer_constants.amip_first_year        ff.integer_constants.num_cloud_levels       ff.integer_constants.num_tracer_levels      ff.integer_constants.timestep
    ff.integer_constants.amip_flag              ff.integer_constants.num_cols               ff.integer_constants.num_wet_levels         ff.integer_constants.to_file(
    ff.integer_constants.copy()                 ff.integer_constants.num_conv_levels        ff.integer_constants.ozone_current_month    ff.integer_constants.triffid_call_period
    ff.integer_constants.dumps_in_mean          ff.integer_constants.num_field_types        ff.integer_constants.radiation_timestep     ff.integer_constants.triffid_last_step
    ff.integer_constants.empty(                 ff.integer_constants.num_land_points        ff.integer_constants.raw                    
    ff.integer_constants.first_constant_rho     ff.integer_constants.num_ozone_levels       ff.integer_constants.river_num_rows         
    ff.integer_constants.frictional_timescale   ff.integer_constants.num_p_levels           ff.integer_constants.river_row_length
    ```

* `ff.real_constants`: particularly `start_lon, start_lat, col_spacing, row_spacing` which describe the grid domain and spacing.
    ```python
    >>> ff.real_constants.
    ff.real_constants.CREATE_DIMS         ff.real_constants.atmos_second        ff.real_constants.from_file(          ff.real_constants.row_spacing
    ff.real_constants.DTYPE               ff.real_constants.atmos_year          ff.real_constants.mass                ff.real_constants.shape
    ff.real_constants.HEADER_MAPPING      ff.real_constants.col_spacing         ff.real_constants.mean_diabatic_flux  ff.real_constants.start_lat
    ff.real_constants.MDI                 ff.real_constants.copy()              ff.real_constants.north_pole_lat      ff.real_constants.start_lon
    ff.real_constants.atmos_day           ff.real_constants.empty(              ff.real_constants.north_pole_lon      ff.real_constants.to_file(
    ff.real_constants.atmos_hour          ff.real_constants.energy              ff.real_constants.raw                 ff.real_constants.top_theta_height
    ff.real_constants.atmos_minute        ff.real_constants.energy_drift        ff.real_constants.real_mdi
    ```

* `ff.fields`: list of references to each of the numerical fields contained in the file.

Each of the fields contains further metadata, in numerical form. Unfortunately, the names of these attributes are anything but descriptive:

```python
>>> field_0 = ff.fields[0]
>>> field_0.
f0.DTYPE_INT           f0.bhlev               f0.brsvd3              f0.lbdatd              f0.lbhrd               f0.lbproc              f0.lbtim               f0.lbyr
f0.DTYPE_REAL          f0.bhrlev              f0.brsvd4              f0.lbday               f0.lblev               f0.lbproj              f0.lbtyp               f0.lbyrd
f0.HEADER_MAPPING      f0.blev                f0.bzx                 f0.lbdayd              f0.lblrec              f0.lbrel               f0.lbuser1             f0.num_values()
f0.NUM_LOOKUP_INTS     f0.bmdi                f0.bzy                 f0.lbegin              f0.lbmin               f0.lbrow               f0.lbuser2             f0.raw
f0.NUM_LOOKUP_REALS    f0.bmks                f0.copy()              f0.lbexp               f0.lbmind              f0.lbrsvd1             f0.lbuser3             f0.set_data_provider(
f0.bacc                f0.bplat               f0.empty()             f0.lbext               f0.lbmon               f0.lbrsvd2             f0.lbuser4             f0.stash
f0.bdatum              f0.bplon               f0.get_data()          f0.lbfc                f0.lbmond              f0.lbrsvd3             f0.lbuser5             f0.to_file(
f0.bdx                 f0.brlev               f0.lbcfc               f0.lbft                f0.lbnpt               f0.lbrsvd4             f0.lbuser6             
f0.bdy                 f0.brsvd1              f0.lbcode              f0.lbhem               f0.lbnrec              f0.lbrvc               f0.lbuser7             
f0.bgor                f0.brsvd2              f0.lbdat               f0.lbhr                f0.lbpack              f0.lbsrce              f0.lbvc
```

The quantity represented by a given field is specified by the `lbuser4` attribute, which is the stash code of the field. The `stash` associated with the field does not contain any information yet- a STASHmaster file is required to give human meaning to the field.

### Attaching STASHmaster files

STASHmaster files contain information some additional information about the fields. The STASHmaster files are typically distinguised by the version of the UM they're associated with, so you need to know which version of the UM is relevant for the given use case. It's possible to provide custom STASHmaster files, for cases when the existing STASH has been modified e.g. ACCESS-ESM. By using a STASHmaster along with a fields file, it is possible to retrieve fields from a fields file by name.

```python
>>> ff.fields[0].stash

>>> sm = mule.STASHmaster.from_file("/g/data/access/umdir/vn7.3/ctldata/STASHmaster/STASHmaster_A")
>>> ff.attach_stashmaster_info(sm)
>>> ff.fields[0].stash
<stashmaster._STASHentry object: SC:    2 - "U COMPNT OF WIND AFTER TIMESTEP">
```

The keys of the STASHmaster are strings represting the stash code, and the values containing information about the field. Note that for ACCESS-ESM1.6, to have an accurate STASHmaster file, a merge of the UM7.3 STASHmaster at `/g/data/access/umdir/vn7.3/ctldata/STASHmaster/STASHmaster_A` and in the [access-esm1.6-configs](https://github.com/ACCESS-NRI/access-esm1.6-configs) (e.g. on branch `dev-preindustrial+concentrations` at `atmosphere/prefix.PRESM_A`) is required. This can be achieved via typical updating one STASH with the other.

```python
>>> sm = mule.STASHmaster.from_file("/g/data/access/umdir/vn7.3/ctldata/STASHmaster/STASHmaster_A")
>>> sm_extension = mule.STASHmaster.from_file("<access-esm1.6-repo>/atmosphere/prefix.PRESM_A")
>>> sm.update(sm_extension)
>>> ff.attach_stashmaster_info(sm)
```

### Using the STASH to select fields

Now that the fields file has a STASHmaster file attached, the fields in the file can effectively be searched via name. There are a couple of ways to do this:

1. Check against the field's associated STASH name:
    ```python
    for field in ff.fields:
        if "SOIL MOISTURE LAYER 1 (ON TILES)" in field.stash.name:
            <do something with the field>
    ```
    It's recommended to use `in` rather than `==`, as the UM fields often have trailing whitespace.

2. Check the field's stash code against the STASH entry:
    ```python
    # Search the stash for fields matching a name- returns a subsection of the original
    sm_selection = ff.stashmaster.by_regex("SOIL MOISTURE LAYER 1 (ON TILES)")

    # Get the stash code(s)- this may be multiple codes, if the prior string matched multiple fields
    stash_codes = list(sm_selection.values())

    for field in ff.fields:
        if field.lbuser4 == stash_codes[0]:
            <do something with the field>
    ```

Each of the fields is specifically a 2D array in the z/pseudo-level and time. To determine which z/pseudo-level a field describes, inspect the `field.lbuser5` attribute. The attribute describing the time slice depends on the frequency- for monthly variables, most likely to be of interest to land folks, the attribute is `field.lbmon`.

The same field name is often used across multiple "sections" in the stash. If you know which section of the STASH the desired field is in, you can filter the stash with

```python
sm_section = sm.by_section(<section_number>)
# or
sm_section = ff.stashmaster.by_section(<section_number>)
```

Again, this is simply another stash, which can be used with `by_regex` or attached to a fields file. Unfortunately, it's not always obvious which section is desired, but in the case of ESM1.6 restart dumps, section 0 is the prognostic section, while section 3 is the diagnostics, so section 0 will almost always be the section of interest.

### Modifying a field

Once the desired field has been selected, there are 2 ways of modifying said field.

1. Modifying the data directly. This is done by modifying a field's data provider. The data provider can be set to simply point to new `mule.ArrayDataProvider` as demonstrated here:
    ```
    f = ff.fields[0]    # Pick a random field to modify
    new_data = f.get_data() * 2     # Get the array of data originally assocated with the field and double it
    f.set_data_provider(mule.ArrayDataProvider(new_data))
    ```
    Now the first field in the file points to a new array, which was built based on the original.
2. Using a `mule.DataOperator`. This requires the construction of a new `mule.DataOperator` class. This is a fair bit less intuitive to use. This method is explained in some reasonable detail in their open source documentation. Only two things are required: definition of `new_field` and `transform` functions, with `__init__` being optional. An equivalent example to the above is shown here:
    ```python
    class ExampleScalarOperator(mule.DataOperator)
        
        def __init__(self, scalar):
            self.scalar = scalar

        def new_field(self, source_field):
            field = source_field.copy()
            return field

        def transform(self, source_field, new_field):
            new_data = source_field.get_data() * 2

            return data

    scalar_op = ExampleScalarOperator(2)
    f = ff.fields[0]
    new_field = ExampleScalarOperator(f)
    ff.fields[0] = new_field
    ```

    Think of the `new_field` method as setting up the field, and `transform` as populating the new field. Note that the `source_field` could also be a list of fields.

### Saving the fields file

A fields file has an attached `to_file` which nominally, one would use to write the file back to disk. In practice, this method significantly runs into validation problems, for reasons beyond my understanding. To get around this, we use the following function:

```python
def to_file(fields_file, output_path):
    self.validate(filename=output_file, warn=True)
    with open(output_path, 'wb') as outfile:
        self._write_to_file(outfile)
```

### Putting it all together

For a somewhat relevant example, let's set the labile carbon pool on a new PFT (12) to half the values on the evergreen broadleaf tiles. We'll restrict the action to be only on the land points.

```python
import mule

# Set up the fields file
init_rst = mule.FieldsFile.from_file("/g/data/vk83/configurations/inputs/access-esm1p6/modern/pre-industrial/restart/atmosphere/restart_dump.astart")
base_stash = mule.STASHmaster.from_file("/g/data/access/umdir/vn7.3/ctldata/STASHmaster/STASHmaster_A")
stash_ext = mule.STASHmaster.from_file("dev-preindustrial+concentrations/atmosphere/prefix.PRESM_A")    # This is the location of the ACCESS-ESM1.6 config
base_stash.update(stash_ext)

init_rst.attach_stashmaster_info(base_stash.by_section(0))      # Get the prognostic section 0 of the stash

# Get the land mask
mask_stash_code = list(init_rst.stashmaster.by_regex("LAND MASK").values())[0].item

for field in init_rst.fields:
    if field.lbuser4 == mask_stash_code:
        mask = field.get_data()

# Now get the EGBL labile carbon
labile_stash_code = list(init_rst.stashmaster.by_regex("CARBON POOL LABILE ON TILES").values())[0].item

for field in init_rst.fields:
    if field.lbuser4 == labile_stash_code and field.lbuser5 == 2:
        egbl_labile_carbon = field.get_data()

new_PFT_labile_carbon = egbl_labile_carbon.copy()
new_PFT_labile_carbon[mask] /= 2

# Place it into the new PFTs field
for field in init_rst.fields:
    if field.lbuser4 == labile_stash_code and field.lbuser5 == 12:
        field.set_data_provider(ArrayDataProvider(new_PFT_labile_carbon))

# Write to disk, using the to_file function from above
to_file(init_rst, "new_restart.astart")
``` 
