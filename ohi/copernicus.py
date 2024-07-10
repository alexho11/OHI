import numpy as np
import os
from django.conf import settings
from copernicusmarine import subset

def download_cm_data_radius(dataset_name, start_date, end_date,variable,coord):
    output_dir=os.path.join('copernicus-data')
    os.makedirs(output_dir, exist_ok=True)
    # the coordinates are the center of the circle and radius (10km or 50km)
    product=dataset_name.split("_",2)[1]
    output_filename = f"{variable}_{start_date}_{end_date}_{product}.nc",
    lon,lat,radius=coord
    # convert radius to degree
    delta_lat=radius/110.574
    delta_lon=radius/(111.32*np.cos(lat))
    # calculate the min and max lat and lon
    min_lon=lon-delta_lon
    max_lon=lon+delta_lon
    min_lat=lat-delta_lat
    max_lat=lat+delta_lat
    subset(
        username='stong',
        password="'Vn4]+~;j?^wTmS",
        dataset_id=dataset_name,
        variables=[variable],
        minimum_latitude=min_lat,
        maximum_latitude=max_lat,
        minimum_longitude=min_lon,
        maximum_longitude=max_lon,
        start_datetime = f"{start_date}T00:00:00",
        end_datetime = f"{end_date}T23:59:59",
        minimum_depth=0,
        maximum_depth=10,
        force_download=True,
        output_filename = output_filename[0],
        output_directory = output_dir
    )

def download_health(output_dir,start_date, end_date, coord):
    lon,lat,radius=coord
    # convert radius to degree
    delta_lat=radius/110.574
    delta_lon=radius/(111.32*np.cos(lat))
    # calculate the min and max lat and lon
    min_lon=lon-delta_lon
    max_lon=lon+delta_lon
    min_lat=lat-delta_lat
    max_lat=lat+delta_lat
    variables=['so','CHL','RRS412','nppv','o2', 'ph','no3','po4']
    dataset_names = ['cmems_mod_glo_phy-so_anfc_0.083deg_P1D-m',
                   'cmems_obs-oc_glo_bgc-plankton_my_l4-gapfree-multi-4km_P1D',
                   'c3s_obs-oc_glo_bgc-reflectance_my_l3-multi-4km_P1D', 
                   'cmems_mod_glo_bgc-bio_anfc_0.25deg_P1D-m',
                   'cmems_mod_glo_bgc-bio_anfc_0.25deg_P1D-m',
                   'cmems_mod_glo_bgc-car_anfc_0.25deg_P1D-m',
                   'cmems_mod_glo_bgc-nut_anfc_0.25deg_P1D-m',
                   'cmems_mod_glo_bgc-nut_anfc_0.25deg_P1D-m']
    for i in range(len(variables)):
        dataset_name=dataset_names[i]
        variable=variables[i]
        product=dataset_name.split("_",2)[1]
        output_filename = f"{variable}_{start_date}_{end_date}_{product}.nc",
        
        subset(
            username='stong',
            password="'Vn4]+~;j?^wTmS",
            dataset_id=dataset_name,
            variables=[variable],
            minimum_latitude=min_lat,
            maximum_latitude=max_lat,
            minimum_longitude=min_lon,
            maximum_longitude=max_lon,
            start_datetime = f"{start_date}T00:00:00",
            end_datetime = f"{end_date}T23:59:59",
            minimum_depth=0,
            maximum_depth=10,
            force_download=True,
            output_filename = output_filename[0],
            output_directory = output_dir
        ) 