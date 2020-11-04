import os
import gpxpy
import gpxpy.gpx
import pandas as pd
import matplotlib.pyplot as plt
from geopy import distance

data = []

def main():
    global data

    path = "./data/"
    files = os.listdir(path)
    
    for file in files:
        gpx_file = open(os.path.join(path, file), 'r')
        gpx = gpxpy.parse(gpx_file)

        segment = gpx.tracks[0].segments[0]
        coords = pd.DataFrame([{
            'lat': p.latitude,
            'long': p.longitude,
            'ele': p.elevation,
            'time': p.time} for p in segment.points])
        
        pair_of_coords = {}
        for i, p in enumerate(segment.points):
            pair_of_coords[(p.latitude, p.longitude)] = i
        
        data.append((coords, pair_of_coords))

    return data

def get_distance_elevation(route):

    lat, long, ele = route

    distance_covered = 0
    elevation_gain = 0

    for i in range(len(lat) - 1):
        distance_covered += distance.geodesic((lat[i], long[i]), (lat[i + 1], long[i + 1])).km
        elevation_gain += max(0, ele[i + 1] - ele[i])
    
    return (distance_covered, elevation_gain)

def get_all_stats(routes):

    distance_covered, elevation_gain = get_distance_elevation(routes[0])
    
    indexes = [i for i in range(len(routes))]
    speeds = [distance_covered / (len(lat) / 3600) for lat,_,_ in routes]

    ret_info = {
        'distance_covered': distance_covered,
        'elevation_gain': elevation_gain,
        'speed_plot': (indexes, speeds)
    }

    return ret_info
    
def get_coordinates_info(start, end, mid = (0, 0)):

    routes = []
    for i in range(len(data)):
        coords, pair_of_coordinates = data[i]
        if start in pair_of_coordinates and end in pair_of_coordinates:
            idx_start = pair_of_coordinates[start]
            idx_end = pair_of_coordinates[end]
            if (idx_start < idx_end):
                routes.append((coords['lat'].tolist()[idx_start : idx_end], coords['long'].tolist()[idx_start : idx_end], coords['ele'].tolist()[idx_start : idx_end]))
        else:
            continue

    return get_all_stats(routes)

def fun():
    global data

main()