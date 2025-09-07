# This script demonstrates how to modify a specific field from a UM fields file using mule.
# It takes the labile carbon pools from the evergreen broadleaf tile, halves it, then places
# the new halved pools into tile 12 which was previously unused. This action is specifically
# performed on the land tiles.

import mule

def to_file(fields_file, output_path):
    """Custom function used to bypass the built-in to_file method."""
    self.validate(filename=output_file, warn=True)
    with open(output_path, 'wb') as outfile:
        self._write_to_file(outfile)

if __name__ == "__main__":

    # Set up the fields file from the restart
    restart = mule.FieldsFile.from_file("/g/data/vk83/configurations/inputs/access-esm1p6/modern/pre-industrial/restart/atmosphere/restart_dump.astart")
    base_stash = mule.STASHmaster.from_file("/g/data/access/umdir/vn7.3/ctldata/STASHmaster/STASHmaster_A")
    stash_ext = mule.STASHmaster.from_file("dev-preindustrial+concentrations/atmosphere/prefix.PRESM_A")    # This is the location of the ACCESS-ESM1.6 config
    base_stash.update(stash_ext)
    
    # Get the prognostic section of the stash
    prog_stash = base_stash.by_section(0)
    restart.attach_stashmaster_info(prog_stash)
    
    # Get the land mask first
    # Order of operations here:
    # 1. Select stash entries with .by_regex("LAND MASK")- should be only 1
    # 2. Get the values from that single entry
    # 3. Turn it into a length-1 list, and take the first and only item
    # 4. Get the stash code from the .item attribute to compare to lbuser4
    mask_stash_code = list(restart.stashmaster.by_regex("LAND MASK").values())[0].item

    for field in restart.fields:
        if field.lbuser4 == mask_stash_code:
            mask = field.get_data()

    # Now get the EGBL labile carbon
    labile_stash_code = list(init_rst.stashmaster.by_regex("CARBON POOL LABILE ON TILES").values())[0].item

    # Get the source tile
    source_tile = 2
    for field in restart.fields:
        if field.lbuser4 == labile_stash_code and field.lbuser5 == source_tile:
            egbl_labile_carbon = field.get_data()

    # Do some operations with the labile carbon field, only where the mask is true
    new_PFT_labile_carbon = egbl_labile_carbon.copy()
    new_PFT_labile_carbon[mask] /= 2

    # Place it into the new PFTs field
    target_tile = 12
    for field in restart.fields:
        if field.lbuser4 == labile_stash_code and field.lbuser5 == target_tile:
            field.set_data_provider(ArrayDataProvider(new_PFT_labile_carbon))

    # Write to disk, using the to_file function from above
    to_file(restart, "new_restart.astart")
