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

def calculate_speed(lat, long):
    dist_covered = 0
    time_taken = len(lat) / 3600
    for i in range(len(lat) - 1):
        dist_covered += distance.geodesic((lat[i], long[i]), (lat[i + 1], long[i + 1])).km

    return dist_covered / time_taken

def get_speed_estimates(routes):
    indexes = [i for i in range(len(routes))]
    speeds = [calculate_speed(lat, long) for lat, long in routes]
    
    return (indexes, speeds)


def find_coordinates(start, end, mid = (0, 0)):
    routes = []
    for i in range(len(data)):
        coords, pair_of_coordinates = data[i]
        if start in pair_of_coordinates and end in pair_of_coordinates:
            idx0 = pair_of_coordinates[start]
            idx1 = pair_of_coordinates[end]
            if (idx0 < idx1):
                routes.append((coords['lat'].tolist()[idx0 : idx1], coords['long'].tolist()[idx0 : idx1]))
        else:
            continue
    return get_speed_estimates(routes)



def fun():
    global data
    return len(data)

main()