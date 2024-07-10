import xarray as xr
import rasterio
from rasterio.transform import from_origin
import os
import numpy as np
def convert_netcdf_to_geotiff(netcdf_file, outputdir):
    ds = xr.open_dataset(netcdf_file)
    netcdf_file = netcdf_file.split('/')[-1]
    varaiable=netcdf_file.split('_')[0]
    product_name = netcdf_file.split('_')[3]
    product_name = product_name.split('.')[0]
    varaiable=netcdf_file.split('_')[0]
    data_var = ds[varaiable]
    if product_name == 'mod':
        data_var = data_var.isel(depth=0) 

    # iterate over the time dimension
    for i, time in enumerate(data_var.time):
        # Extract the data for the current time slice
        time_slice = data_var.sel(time=time)
        
        # Generate the output filename
        timestamp = str(time.values)
        timestamp=timestamp.split('T')[0]
        output_file = f'{timestamp}.tif'
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        output_file = os.path.join(outputdir, output_file)
        # Extract the spatial information
        transform = from_origin(ds.longitude.min().values, ds.latitude.max().values, 
                                ds.longitude.diff('longitude').mean().values, 
                                ds.latitude.diff('latitude').mean().values)
                                # Write the time slice to a GeoTIFF file
        # print(transform)
        with rasterio.open(
            output_file, 'w',
            driver='GTiff',
            height=time_slice.shape[0],
            width=time_slice.shape[1],
            count=1,
            dtype=time_slice.dtype,
            crs='EPSG:4326',
            transform=transform,
        ) as dst:
            time_slice=np.flip(time_slice, axis=0)
            dst.write(time_slice.values, 1)
        
        # print(f"Saved {output_file}")