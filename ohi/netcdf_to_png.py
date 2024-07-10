import json
import xarray as xr
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np
import os

def apply_colormap(data, colormap='viridis'):
    norm = Normalize(vmin=data.min(), vmax=data.max())
    colormap = plt.get_cmap(colormap)
    rgba = colormap(norm(data))  # Returns an RGBA array of shape (M, N, 4)
    rgba = np.flip(rgba, axis=0)
    return rgba

def save_png_with_transparency(data, filepath):
    rgba = np.dstack((data, 255 * np.ones(data.shape[:2], dtype='uint8')))
    
    # Make black pixels transparent
    mask = np.all(data == [0, 0, 0], axis=-1)
    rgba[mask, 3] = 0
    
    image = Image.fromarray(rgba, 'RGBA')
    image.save(filepath)

# def save_json(data, bounds, filepath):
#     json_data = {
#         'data': data.tolist(),
#         'bounds': bounds
#     }
#     with open(filepath, 'w') as f:
#         json.dump(json_data, f)

def save_bounds(bounds, filepath):
    with open(filepath, 'w') as f:
        json.dump(bounds, f)


def convert_netcdf_to_png_and_json(netcdf_file, output_dir, colormap='viridis'):
    ds = xr.open_dataset(netcdf_file)
    print(netcdf_file)
    netcdf_file = netcdf_file.split('/')[-1]
    variable_name = netcdf_file.split('_')[0]
    product_name = netcdf_file.split('_')[3]
    product_name = product_name.split('.')[0]
    print(product_name)
    print(variable_name)
    data_var = ds[variable_name]
    if product_name == 'mod':
        data_var = data_var.isel(depth=0) 
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamps=data_var.time.values
    timestamps=[str(i).split(
        'T')[0]
     for i in timestamps]
    timestamps_json = {
        'timestamps': timestamps
    }
    for i, time in enumerate(data_var.time):
        time_slice = data_var.sel(time=time)
        
        # Apply colormap to convert the grayscale data to RGB
        rgb_data = apply_colormap(time_slice, colormap)
        
        timestamp = str(time.values)
        timestamp=timestamp.split('T')[0]
        output_png_file = os.path.join(output_dir, f'{timestamp}.png')
        output_json_file = os.path.join(output_dir, 'timestamp_bounds.json')
        
        # Save the RGB data as a PNG image with transparency
        # save_png_with_transparency(rgb_data, output_png_file)
        img = Image.fromarray((rgb_data * 255).astype(np.uint8))
        img.save(output_png_file)
        


        
        # print(f"Saved PNG: {output_png_file}")
        # print(f"Saved JSON: {output_json_file}")
            # Save the original data and location bounds as a JSON file
    bounds = {
        'north': ds.latitude.max().item(),
        'south': ds.latitude.min().item(),
        'east': ds.longitude.max().item(),
        'west': ds.longitude.min().item()
    }
    save_bounds(bounds, output_json_file)

def calculate_mean_value(netcdf_file, output_dir):
    ds = xr.open_dataset(netcdf_file)
    netcdf_file = netcdf_file.split('/')[-1]
    variable_name = netcdf_file.split('_')[0]
    product_name = netcdf_file.split('_')[3]
    product_name = product_name.split('.')[0]
    data_var = ds[variable_name]
    if product_name == 'mod':
        data_var = data_var.isel(depth=0) 
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    mean_values = []
    for i, time in enumerate(data_var.time):
        time_slice = data_var.sel(time=time)
        mean_value = time_slice.mean().item()
        mean_values.append(mean_value)

    with open(os.path.join(output_dir, 'mean_values.json'), 'w') as f:
        json.dump(mean_values, f)
            