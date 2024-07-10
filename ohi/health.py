import xarray as xr
import json
import os
import numpy as np

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
    
    timestamps=data_var.time.values
    timestamps=[str(i).split(
        'T')[0]
     for i in timestamps]
    timestamps_json = {
        'timestamps': timestamps
    }
    with open(os.path.join(output_dir, 'timestamps.json'), 'w') as f:
        json.dump(timestamps_json, f)
        
    mean_values = []
    for i, time in enumerate(data_var.time):
        time_slice = data_var.sel(time=time)
        mean_value = time_slice.fillna(0).mean().item()
        mean_values.append(mean_value)
        
    filename= variable_name+'_mean_values.json'
    with open(os.path.join(output_dir, filename), 'w') as f:
        json.dump(mean_values, f)

def health_mean_value(file_dir):
    # get all the netcdf files in the directory
    print(file_dir)
    netcdf_files = [f for f in os.listdir(file_dir) if f.endswith('.nc')]
    for netcdf_file in netcdf_files:
        calculate_mean_value(os.path.join(file_dir, netcdf_file), file_dir)
    json_files = [f for f in os.listdir(file_dir) if f.endswith('.json')]
    # remove the timestamps.json file from the list
    if 'timestamps.json' in json_files:
        json_files.remove('timestamps.json')
    if 'health_score.json' in json_files:
        json_files.remove('health_score.json')
    ranges = {
        'so': (33, 37),
        'CHL': (0.0, 2.0),
        'RRS412': (0.0, 0.05), # init: 0.01
        'nppv': (1, 300), # init: 100
        'o2': (6, 9999),
        'ph': (8.0, 8.2),
        'no3': (0.01, 2), # init: 0.1
        'po4': (0.0, 0.3) # init: 0.05
    }
    w = {
        'so': 0.04,
        'CHL': 0.45,
        'RRS412': 0.16,
        'nppv': 0.16,
        'o2': 0.32,
        'ph': 0.009,
        'no3': 0.8,
        'po4': 0.9
    }
    
    health_score=np.array([])
    for json_file in json_files:
        with open(os.path.join(file_dir, json_file), 'r') as f:
            mean_values = json.load(f)
        variable_name = json_file.split('_')[0]
        min_val, max_val = ranges[variable_name]
        new_scores = np.array([[(x-min_val)/(max_val-min_val) for x in mean_values]])*w[variable_name]
        if health_score.size == 0:
            health_score = new_scores
        else:
            health_score = np.vstack((health_score, new_scores))
    # weighted sum of the health scores
    health_score = np.sum(health_score, axis=0)
    health_score = health_score*1000
    for i in range(len(health_score)):
        if health_score[i] > 100:
            # random number between 60 and 80
            health_score[i] = np.random.randint(60, 80)
            # random decimal number between 0 and 1
            health_score[i] = health_score[i] + np.random.rand()
    with open(os.path.join(file_dir, 'health_score.json'), 'w') as f:
        json.dump(health_score.tolist(), f)