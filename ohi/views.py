from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.conf import settings
from django.contrib.auth import authenticate,login,logout
import numpy as np
import os
from .models import Dataset, DataRecord, HealthRecord
from .copernicus import download_cm_data_radius, download_health
import json
import xarray as xr
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from .netcdf_to_png import convert_netcdf_to_png_and_json, calculate_mean_value
import glob
from .raster import convert_netcdf_to_geotiff
from .health import health_mean_value
# Create your views here.

# read the parameters from the database
parameters=Dataset.objects.values_list('variable', flat=True)



def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('ohi:login'))
    return render(request, 'ohi/index.html')

def download(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('ohi:login'))
    if request.method == 'POST':
        lon = float(request.POST.get('lon'))
        lat = float(request.POST.get('lat'))
        radius = int(request.POST.get('radius'))
        param = request.POST.getlist('sel_param')
        print(f"Received lon: {lon}, lat: {lat}, param: {param}")
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        print(f"Received start_date: {start_date}, end_date: {end_date}")
        dataset_name = Dataset.objects.get(variable=param[0].upper()).dataset_name
        print(f"Dataset name: {dataset_name}")
        variable =Dataset.objects.get(variable=param[0].upper()).var_name
        download_cm_data_radius(dataset_name, start_date, end_date, variable, [lon,lat,radius])
        data_record = DataRecord(variable=variable, start_date=start_date, end_date=end_date, lon=lon, lat=lat, radius=radius)
        data_record.save()
        return JsonResponse({'message': 'Data downloaded successfully'})
    return render(request, 'ohi/download.html',{
        'params':parameters
    })

def login_view(request):
    if request.method == 'POST':
        username=request.POST['username']
        password=request.POST['password']

        user=authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return HttpResponseRedirect(reverse('ohi:index'))
        else:
            return render(request, 'ohi/login.html', {
                'error': 'Invalid username or password'
            })
    return render(request, 'ohi/login.html')

def logout_view(request):
    logout(request)
    return render(request, 'ohi/login.html',{
        'message': 'Logged out.'
    })



def params(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('ohi:login'))
    
    records=DataRecord.objects.all()
    health_records=HealthRecord.objects.all()
    return render(request, 'ohi/params.html',{
        'records':records,
        'health_records':health_records
    })

def health(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('ohi:login'))
    if request.method == 'POST':
        lon = float(request.POST.get('lon'))
        lat = float(request.POST.get('lat'))
        radius = int(request.POST.get('radius'))
        print(f"Received lon: {lon}, lat: {lat}")
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        print(f"Received start_date: {start_date}, end_date: {end_date}")
        health_record = HealthRecord( start_date=start_date, end_date=end_date, lon=lon, lat=lat, radius=radius)
        health_record.save()
        # get the health record id
        health_record_id=health_record.id
        output_dir=os.path.join('visuals/health/'+str(health_record_id))
        os.makedirs(output_dir, exist_ok=True)
        # download the data
        download_health(output_dir, start_date, end_date, [lon,lat,radius])
        return JsonResponse({'message': 'Data downloaded successfully'})
    return render(request, 'ohi/health.html')

def overview(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('ohi:login'))
    return render(request, 'ohi/overview.html')

def delete_record(request):
    if request.method == 'POST' and request.user.is_authenticated:
        record_id=request.POST.get('id')
        print(f"Received record_id: {record_id}")
        if not record_id:
            return JsonResponse({'success': False}, status=400)
        record=get_object_or_404(DataRecord, id=record_id)
        # delete the file
        product=Dataset.objects.get(var_name=record.variable).dataset_name.split("_",2)[1]
        filename = record.variable + '_' + str(record.start_date)+'_'+str(record.end_date)  +'_'+ product +'.nc'
        filename = os.path.join( 'copernicus-data', filename)
        if os.path.exists(filename):
            os.remove(filename)
            print(f"File {filename} deleted")
        record.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)
def delete_health_record(request):
    if request.method == 'POST' and request.user.is_authenticated:
        record_id=request.POST.get('id')
        # print(f"Received record_id: {record_id}")
        if not record_id:
            return JsonResponse({'success': False}, status=400)
        record=get_object_or_404(HealthRecord, id=record_id)
        # delete the folder
        foldername = os.path.join( '/visuals/health/', str(record_id))
        if os.path.exists(foldername):
            import shutil
            shutil.rmtree(foldername)
            # print(f"Folder {foldername} deleted")
        record.delete()
        return JsonResponse({'success': True})
def progress(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('ohi:login'))
    return render(request, 'ohi/progress.html')

def param_visual(request):
    if request.method == 'POST' and request.user.is_authenticated:
        record_id=request.POST.get('id')
        if not record_id:
            return JsonResponse({'success': False}, status=400)
        record=get_object_or_404(DataRecord, id=record_id)
        print(f"Received record_id: {record_id}")
        product=Dataset.objects.get(var_name=record.variable).dataset_name.split("_",2)[1]
        filename = record.variable + '_' + str(record.start_date)+'_'+str(record.end_date)  +'_'+ product +'.nc'
        filename = os.path.join( 'copernicus-data', filename)
        var_unit=Dataset.objects.get(var_name=record.variable).unit
        var_name=record.variable
        print(filename)
        if os.path.exists(filename):
            # visual the data here
            output_dir = os.path.join( 'visuals',str(record_id))
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                convert_netcdf_to_png_and_json(filename, output_dir)
                convert_netcdf_to_geotiff(filename, output_dir)
                calculate_mean_value(filename, output_dir)
            # visualize in html
            print(f"Visualizing record_id: {record_id}" )
            png_files = sorted(glob.glob(os.path.join(output_dir, '*.png')))
            json_files = sorted(glob.glob(os.path.join(output_dir, 'timestamp_bounds.json')))
            tiff_files = sorted(glob.glob(os.path.join(output_dir, '*.tif')))
            timestamps = [os.path.basename(f).replace('.png', '').split('_')[-1] for f in png_files]
            mean_values = sorted(glob.glob(os.path.join(output_dir, 'mean_values.json')))
            
            bounds=[]
            for f in json_files:
                with open(f, 'r') as file:
                    data = json.load(file)
                    bounds.append(data)
            # print(f"Timestamps: {timestamps}")
            # print(f"PNG files: {png_files}")
            # print(f"Bounds: {bounds}")
            mean_value = []
            for f in mean_values:
                with open(f, 'r') as file:
                    data = json.load(file)
                    mean_value.append(data)
            context = {
                'record_id': record_id,
                'timestamps': timestamps,
                'png_files': [os.path.basename(f) for f in png_files],
                'tiff_files': [os.path.basename(f) for f in tiff_files],
                'bounds': bounds,
                'mean_value': mean_value,
                'unit': var_unit,
                'variable': var_name
            }
            return JsonResponse({'success': True, 'redirect_url': request.build_absolute_uri(request.path) + '?record_id=' + str(record_id)})
        else:
            return JsonResponse({'success': False, 'message': 'File not found'})
    elif request.method == 'GET':
        record_id = request.GET.get('record_id')
        record = get_object_or_404(DataRecord, id=record_id)
        var_unit = Dataset.objects.get(var_name=record.variable).unit
        var_name = record.variable
        output_dir = os.path.join('visuals', str(record_id))

        png_files = sorted(glob.glob(os.path.join(output_dir, '*.png')))
        json_files = sorted(glob.glob(os.path.join(output_dir, 'timestamp_bounds.json')))
        tiff_files = sorted(glob.glob(os.path.join(output_dir, '*.tif')))
        timestamps = [os.path.basename(f).replace('.png', '').split('_')[-1] for f in png_files]
        mean_values = sorted(glob.glob(os.path.join(output_dir, 'mean_values.json')))

        bounds=[]
        for f in json_files:
            with open(f, 'r') as file:
                data = json.load(file)
                bounds.append(data)
        mean_value = []
        for f in mean_values:
            with open(f, 'r') as file:
                data = json.load(file)
                mean_value.append(data)

        context = {
            'record_id': record_id,
            'timestamps': timestamps,
            'png_files': [os.path.basename(f) for f in png_files],
            'tiff_files': [os.path.basename(f) for f in tiff_files],
            'bounds': bounds,
            'mean_value': mean_value,
            'unit': var_unit,
            'variable': var_name
        }

        return render(request, 'ohi/param_visual.html', context)
    return JsonResponse({'success': False}, status=400)

def health_visual(request):
    if request.method == 'POST' and request.user.is_authenticated:
        record_id=request.POST.get('id')
        if not record_id:
            return JsonResponse({'success': False}, status=400)
        record=get_object_or_404(HealthRecord, id=record_id)
        # print(f"Received record_id: {record_id}")
        output_dir = os.path.join( 'visuals/health/',str(record_id))

        health_mean_value(output_dir)
        return JsonResponse({'success': True, 'redirect_url': request.build_absolute_uri(request.path) + '?record_id=' + str(record_id)})
    elif request.method == 'GET':
        record_id = request.GET.get('record_id')
        # print(f"Received record_id: {record_id}")
        output_dir = os.path.join( 'visuals/health/',str(record_id))
        
        health_mean_value(output_dir)
        record=get_object_or_404(HealthRecord, id=record_id)
        lon=record.lon
        lat=record.lat
        radius=record.radius
        start_date=record.start_date
        end_date=record.end_date
        json_files = sorted(glob.glob(os.path.join(output_dir, '*mean_values.json')))
        timestamps = sorted(glob.glob(os.path.join(output_dir, 'timestamps.json')))
        health_score=sorted(glob.glob(os.path.join(output_dir, 'health_score.json')))
        context = {
            'record_id': record_id,
            'json_files': [os.path.basename(f) for f in json_files],
            'timestamps': [os.path.basename(f) for f in timestamps],
            'health_score': [os.path.basename(f) for f in health_score],
            'lon': lon,
            'lat': lat,
            'radius': radius,
            'start_date': start_date,
            'end_date': end_date
        }
        return render(request, 'ohi/health_visual.html', context)


def hotspots(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('ohi:login'))
    return render(request, 'ohi/hotspots.html')