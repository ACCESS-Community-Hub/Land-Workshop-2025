
'''
This example is for adjusting a JULES-based UM startdump

Which after processing is:
    python u-dr216/bin/adjust_soil_ics.py --fpath /path/to/RAL3P2_astart --mask_file /path/to/ancils/fire_mask.nc
'''

import argparse

parser = argparse.ArgumentParser(description='adjusts initial condition soil moisture prior to inner nest recon')
parser.add_argument('--fpath', help='fpath to startdump',default='/scratch/fy29/mjl561/cylc-run/u-dr216/share/cycle/20200114T0000Z/control/d0198/RAL3P2/ics/RAL3P2_astart')
parser.add_argument('--mask_file', help='path to fire mask NetCDF file', default='/scratch/fy29/mjl561/cylc-run/ancil_blue_mountains/share/data/ancils/Bluemountains/d0198/fire_mask.nc')
parser.add_argument('--plot', help='whether to plot result to ics dir', default=False, action='store_true')
args = parser.parse_args()

import ants
import numpy as np
import mule
import xarray as xr
import os
import shutil

###############################################################################

sm_reduction_factor = 0.5  # 50% reduction

###############################################################################

def main(original_path):

    print(f'processing {original_path}')

    # get soil moisture data
    cb = ants.load_cube(original_path, constraint='moisture_content_of_soil_layer')

    # Load pre-created fire mask
    if os.path.exists(args.mask_file):
        print(f"Loading fire mask from: {args.mask_file}")
        mask_da = xr.open_dataarray(args.mask_file)
        mask = mask_da.values.astype(bool)
        print(f"Loaded mask with {np.sum(mask)} fire-affected grid cells")
    else:
        print(f"ERROR: Fire mask file not found: {args.mask_file}")
        print("Please run create_fire_mask.py first to generate the mask file")
        return

    print('updating files')

    # make changes to ics file with mule
    backup_fpath = original_path+'_original'
    stashid = 9  # for moisture content of soil layer stash m01s00i009

    cb_adjusted = cb.copy()
    # Broadcast mask to match the shape of cb_adjusted.data
    mask_broadcast = np.broadcast_to(mask, cb_adjusted.data.shape)
    cb_adjusted.data[mask_broadcast] *= sm_reduction_factor

    # Create backup of original file
    print(f'Creating backup: {backup_fpath}')
    shutil.copy2(original_path, backup_fpath)
    
    # Save adjusted data to original file path (overwriting original)
    # Use backup file as template to preserve all other fields
    save_adjusted_cube(cb_adjusted, original_path, backup_fpath, stashid)

    if args.plot:
        print('plotting changes')
        # Get bounds for plotting (currently using the full domain)
        lons = cb.coord('longitude').points
        lats = cb.coord('latitude').points
        xmin, xmax = lons.min(), lons.max()
        ymin, ymax = lats.min(), lats.max()
        # get filename from args.fname
        domain = os.path.basename(original_path).split('_astart')[0]

        # Create comprehensive comparison plot
        plot_soil_moisture_comparison(cb, cb_adjusted, xmin, xmax, ymin, ymax, domain)

    return

def save_adjusted_cube(cb_adjusted, output_path, template_path, stashid):
    """Save the adjusted cube using MULE
    
    Args:
        cb_adjusted: The modified iris cube with adjusted soil moisture
        output_path: Path where the updated file should be saved
        template_path: Path to the original complete file to use as template
        stashid: STASH code for the fields to update (9 for soil moisture)
    """
    
    # Convert iris cube to mule UMfile using the template (original complete file)
    ancil = mule.AncilFile.from_file(template_path)
    arr = cb_adjusted.data.data
    
    j = 0
    for i, field in enumerate(ancil.fields):
        if field.lbuser4 == stashid:
            print(f'updating field {i}: {field.lbuser4}')
            array_provider = mule.ArrayDataProvider(arr[j, :, :])
            ancil.fields[i].set_data_provider(array_provider)
            j += 1
    
    # Save using mule
    print(f'saving updated ancil to {output_path} with mule')
    try:
        ancil.to_file(output_path)
    except Exception as e:
        print(e)
        print('WARNING: MULE validation being disabled')
        ancil.validate = lambda *args, **kwargs: True
        ancil.to_file(output_path)


if __name__ == '__main__':
    print('functions loaded')
    main(args.fpath)