'''
A simple example of using ANTS to regrid one ancillary to another grid

Requires access/ngm, i.e., 
    module use /g/data/access/ngm/modules; module load ants/0.18
    module use /g/data/access/ngm/modules; module load ants/2.0.0
Or xp65, i.e.:
    module use /g/data/xp65/public/modules; module load conda/analysis3-25.08

xp65 environment still being determined, see: 
    https://forum.access-hive.org.au/t/ants-module-availability-in-xp65-analysis3-kernels/5149/16
    
'''

import ants

# define paths
datapath = '/g/data/rp23/experiments/2024-10-10_LWG_workingbee/JULES_ancil_HM'
source_path = f'{datapath}/qrparm.veg.frac_cci_12'
target_lsm_path = f'{datapath}/qrparm.mask_cci_1p5'

print('loading data')
source_cube = ants.load_cube(source_path) # surface cover fraction
target_lsm_cube = ants.load_cube(target_lsm_path) # land-sea mask

print('regridding with Area Weighted scheme')
scheme = ants.regrid.GeneralRegridScheme(horizontal_scheme="AreaWeighted")
regridded_cube = source_cube.regrid(target_lsm_cube, scheme)

print('making regridded cube lsm consistent with source, filling missing values')
ants.analysis.make_consistent_with_lsm(regridded_cube, target_lsm_cube, invert_mask=True)

print('saving as ancil and netcdf (accounting for ANTS version)')
output_filepath = f'./regridded_to_1p5'

# deal with different i/o in ANTS v0/v1 and v2
print('ANTS version:', ants.__version__)
if ants.__version__[0] != '2':
    print('saving with ants < 2 API')
    ants.save(regridded_cube, output_filepath, zlib=True)
else:
    print('saving with ants v2 API')
    ants.io.save.ancil(regridded_cube, output_filepath)
    ants.io.save.netcdf(regridded_cube, f'{output_filepath}.nc', zlib=True)

print('done!')

