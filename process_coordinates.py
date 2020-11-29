import os
from tkinter import filedialog, messagebox
from tkinter import ttk
import tkinter as tk
from tkinter import *
import string
from matplotlib.figure import Figure
import gpxpy
import gpxpy.gpx
import numpy as np
import pandas as pd
from geopy import distance
from PIL import ImageTk, Image
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil import parser
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)


data = dict()
d = e = s = None
rider = ""

#function to define main which takes path as input parameter and processes the co-ordinates
def main(path):

    global data
    #taking file's path as input.
    files = os.listdir(path)
    #selecting directory from lists of directory.
    for dir in os.listdir(path):
        data[dir] = []      #creating data list of length directories
        for file in os.listdir(os.path.join(path, dir)):    #creating path of the selected file.
            name = str(file).split('.')[0]
            gpx_file = open(os.path.join(os.path.join(path, dir), file), 'r')
            #creating try and except block to continue in case the file's path was not correctly found.
            try: 
                gpx = gpxpy.parse(gpx_file)
            except:
                continue
            #getting segments of input from file
            segment = gpx.tracks[0].segments[0]
            #creating dataframe for input variables for latitudes, longitudes, elevation and time.
            coords = pd.DataFrame([{
                'lat': p.latitude,
                'long': p.longitude,
                'ele': p.elevation,
                'time': p.time} for p in segment.points])
            #taking input as pair of coordinates and rounding them off to 4 places.
            pair_of_coords = {}
            for i, p in enumerate(segment.points):
                pair_of_coords[(round(p.latitude, 4), round(p.longitude, 4))] = i
            #appending coordinates, coordinates pair and name as a list in data list we creating.  
            data[dir].append((coords, pair_of_coords, name))
    #returning data list for processing in main.py
    return data

#function to get distance and elevation of the data.
def get_distance_elevation(route):
    #taking latitude, longitude, elevation and time values from route list.
    lat, lon, ele, _, t = route
    #intialising the total distance, total time and elevation gain .
    total_dist = 0
    total_time = 0
    elevation_gain = 0
    
    FMT = "%m/%d/%Y, %H:%M:%S"
    #running loop to calculate total distance , total time and elevation gain .
    for i in range(len(lat) - 1):
        #to calculate elevation gain we are taking maximum of 0 and difference between the next coordinate elevation so not inculde the negative difference.
        elevation_gain += max(0, ele[i + 1] - ele[i])
        #calculating temporary distance between current point and next immedeate point .
        tmp_dist = distance.geodesic(
                (lat[i], lon[i]), (lat[i + 1], lon[i + 1])).km
        #calculating time passes between cirrent and next immediate point by taking the difference, needed to calculate speed.
        time_elapsed = abs(datetime.strptime(
            t[i + 1].strftime(FMT), FMT) - datetime.strptime(t[i].strftime(FMT), FMT))
        days, seconds = time_elapsed.days, time_elapsed.seconds     #calculating days and seconds from time elapsed.
        hours = days * 24 + seconds // 3600     #calculating hours int the total days.
        minutes = (seconds % 3600) // 60    #calculating minutes by taking modulo for 3600 for seconds and finally integer dividing by 60 to take minutes.
        seconds = seconds % 60      #calculating seconds by taking modulo.
        total_dist += abs(tmp_dist)     #calculating total distance taking absolute addition of the temporary distance so as not to calculate displacement in return 
        total_time += abs(hours + minutes/60 + seconds/3600)    #calculating total time so as to calculate speed.
    
    return (total_dist, elevation_gain, total_time)

#function to get all the statistics from the data.
def get_all_stats(routes):
    #intialising the distance covered, elevation gain and time taken.
    distance_covered = 0
    elevation_gain = 0
    time_taken = 0

    names = [name for _, _, _, name, _ in routes]   
    speeds = []        #intialising speed list for every input.
    for i, route in enumerate(routes):
        d, e, t = get_distance_elevation(route) #getting distance , elevation, time for this point from get_distance_elevation function.
        speeds.append(round((d / t), 2))    #calculating speed till now by dividing by time.
        distance_covered = (distance_covered + d) / (i + 1)     #calculating distance_covered by adding distance in total distance. 
        elevation_gain = (elevation_gain + e) / (i + 1)        #adding elevation for this point in total elevation gain.
        time_taken = (time_taken + t) / (i + 1)                #updating total time taken.
    #adding the stats int the dictionary.
    ret_info = {
        'distance_covered': distance_covered,
        'elevation_gain': elevation_gain,
        'time_taken': time_taken,
        'speed_plot': (names, speeds)
    }
    
    if len(routes) == 0:
        return 0
    #returning the stats stored in ret_info dict.
    return ret_info

#function to check the uniqueness of the route.
def check_uniqueness(routes):
    #if length of route is zero then the path is not unique.
    if len(routes) == 0:
        return 0
    #calculating distance and elevation array.
    dist_arr = np.array([get_distance_elevation(route)[0] for route in routes])
    ele_arr = np.array([get_distance_elevation(route)[1] for route in routes])
    #calculating mean of distance and elevation by dividing with the total numebr of points.
    dist_mean = sum(dist_arr) / len(dist_arr)
    ele_mean = sum(ele_arr) / len(ele_arr)
    #updating the distance and elevation array.
    dist_arr = dist_arr - [dist_mean]
    ele_arr = ele_arr - [ele_mean]
    #if in diatance array abs distance array and abs elevation array afer updating is greater than 0.1 and 1 respectively then it is not a unique path.
    for i in range(len(dist_arr)):
        if (abs(dist_arr[i]) > 0.1 or abs(ele_arr[i]) > 1):
            return False
    #if after updating distance array and elevation array is less than 0.1 and 1 respectively then it is a unique path.
    return True

#getting coordinates information from data.
def get_coordinates_info(rider_name, start, end, mid=(0, 0)):

    global data
    #raise error of no file is selected but given the command to select data.
    if len(data) == 0:
        messagebox.showerror("Error", "Select GPX directory first.")
        return
    #raise error is rider name is not selected.
    if(rider_name == ""):
        messagebox.showerror("Error", "Select a rider first.")
        return
        
    routes = []         #creating routes list to get all the info of the coordinates.
    for i in range(len(data[rider_name])):
        coords, pair_of_coordinates, name = data[rider_name][i]
        if start in pair_of_coordinates and end in pair_of_coordinates and (mid == (0, 0) or mid in pair_of_coordinates):

            idx_start = pair_of_coordinates[start]
            idx_mid = -1 if mid == (0, 0) else pair_of_coordinates[mid]
            idx_end = pair_of_coordinates[end]

            if (idx_start < idx_end and (idx_mid == -1 or (idx_start < idx_mid and idx_mid < idx_end))):
                routes.append((coords['lat'].tolist()[idx_start: idx_end], coords['long'].tolist()[
                              idx_start: idx_end], coords['ele'].tolist()[idx_start: idx_end], name, coords['time'].tolist()[idx_start:idx_end]))
        else:
            continue

    if len(routes) == 0:
        return 0
    #returning the coordinates info by sending the routes list in get_all_stats function to process the routes list and split it into usable stats. 
    return get_all_stats(routes)

#Returns a tuple of dictionaries for distance vs day, elevation-gain vs day and speed vs day plots
def get_attr_per_day(rider_name):
    
    global data
    #intialising dist_map , ele_map and speed_map.
    dist_map, ele_map, speed_map = dict(), dict(), dict()
    for i in range(len(data[rider_name])):   #running loop for data to calculate dist_map, ele_map and speed_map.   
        time_series, ele_series, lat_series, long_series = data[rider_name][i][0][
            'time'], data[rider_name][i][0]['ele'], data[rider_name][i][0]['lat'], data[rider_name][i][0]['long']
        for j in range(len(data[rider_name][i][0])):
            day = time_series[j].strftime("%x")     
            if day not in dist_map:
                dist_map[day] = []
            if day not in ele_map:
                ele_map[day] = []
            ele_map[day].append(ele_series[j])
            dist_map[day].append(
                (lat_series[j], long_series[j], time_series[j]))

    for day, arr in ele_map.items():    #getting element _map for that day by taking elevation gain
        ele_gain = 0
        for i in range(len(arr) - 1):
            ele_gain += max(0, arr[i + 1] - arr[i]) #elevation cannot be negative.
        ele_map[day] = ele_gain

    FMT = "%m/%d/%Y, %H:%M:%S"      #calculating date and time.

    for day, arr in dist_map.items():
        total_dist = total_time = 0     #intialising total distance and total time 
        tmp_dist = tmp_time = 0         #intialising temp distance and temp time.
        for i in range(len(arr) - 1):       #updating total distance and total time for every day.
            tmp_dist = distance.geodesic(
                (arr[i][0], arr[i][1]), (arr[i + 1][0], arr[i + 1][1])).km
            time_elapsed = abs(datetime.strptime(
                arr[i + 1][2].strftime(FMT), FMT) - datetime.strptime(arr[i][2].strftime(FMT), FMT))
            days, seconds = time_elapsed.days, time_elapsed.seconds
            hours = days * 24 + seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            total_dist += abs(tmp_dist)
            total_time += abs(hours + minutes/60 + seconds/3600)
        dist_map[day] = total_dist      #updating distance map for that day.
        speed_map[day] = total_dist/total_time      #updating speed for that day by dividing by total time.

    return (dist_map, ele_map, speed_map)



#function to give overall summary of the data.
def summarise(rider_name):

    global d,e,s,rider
    #raise error in case no rider name is selected.
    if(rider == ""):
        messagebox.showerror("Error", "Please select the primary rider first!")
        return
    #raise error if the data list is empty.
    if len(data[rider_name]) == 0:
        messagebox.showerror("Error", "No data found for " + rider_name)
        return


    if(rider_name == rider):
        if(d == None):
            d, e, s = get_attr_per_day(rider_name)
        return (round(np.mean(tuple(d.values())), 2), round(np.mean(tuple(e.values())), 2), round(max(tuple(s.values())), 2))
    else:
        d1, e1, s1 = get_attr_per_day(rider_name)
        return (round(np.mean(tuple(d1.values())), 2), round(np.mean(tuple(e1.values())), 2), round(max(tuple(s1.values())), 2))


def Filter_data(d):
    '''

    Converts dict to list with key and value seprate, sorts dates also

    '''

    dk = []
    dval = []
    for key, val in d.items():
        dk.append(key)
    dk.sort(key=lambda date: datetime.strptime(date, "%d/%m/%y"))
    for i in dk:
        dval.append(d[i])
    return dk, dval


def plot(rider_name):
    '''

    All the plots related to data here, there are three seprate windows for each plot

    '''


    global d, e, s, rider
    #rasiing error in case no file selected or no rider name is provider.
    if(rider == rider_name):
        return
    
    if len(data) == 0:
        messagebox.showerror("Error", "Select GPX directory first.")
        return

    if len(data[rider_name]) == 0:
        messagebox.showerror("Error", "No data found for " + rider_name)
        return
    
    if (d == None or rider_name != rider):
        d, e, s = get_attr_per_day(rider_name)
        rider = rider_name

    d_key, d_val = Filter_data(d)
    e_key, e_val = Filter_data(e)
    s_key, s_val = Filter_data(s)

    plt.clf()   #window to plot distance covered each day.

    plt.stem(d_key, d_val)
    plt.ylabel("Distance Covered (Km) ")
    plt.title("Distance vs. Date")
    plt.xticks(rotation='vertical')
    plt.savefig("dist_plot.png", bbox_inches='tight')

    plt.clf()   #window to plot speed for each day.

    plt.stem(s_key, s_val)
    plt.ylabel("Average Speed (Km/hr) ")
    plt.title("Speed vs. Date")
    plt.xticks(rotation='vertical')
    plt.savefig("speed_plot.png", bbox_inches='tight')

    plt.clf()   #window to plot elevation gain every day.
    
    plt.stem(e_key, e_val)
    plt.ylabel("Elevation Gain (feets) ")
    plt.title("Elevation vs. Date")
    plt.xticks(rotation='vertical')
    plt.savefig("ele_plot.png", bbox_inches='tight')


def isFloat(temp):
    try:
        float(temp)
        return 1
    except:
        return 0

#function to process coordinates data by giving entries and rider name as parameter and no parameter is selected then intializing it to None. 
def process_coordinates_data(ents, rider_name=None):
    
    global rider
    #selecting rider name if no rider name is selected.
    if rider_name == None:
        rider_name = rider

    start = 0
    mid = (0, 0)
    end = 0
    #raising error if no gps file or rider is selected.
    if len(data) == 0:
        messagebox.showerror("Error", "Select GPX directory first.")
        return 0

    if rider_name == "":
        messagebox.showerror("Error", "Select a Rider first.")
        return 0
    #getting float entries.
    if isFloat(ents['start_Lat'].get()) and isFloat(ents['start_Long'].get()):
        start = (round(float(ents['start_Lat'].get()), 4),
                 round(float(ents['start_Long'].get()), 4))
    if isFloat(ents['mid_Lat'].get()) and isFloat(ents['mid_Long'].get()):
        mid = (round(float(ents['mid_Lat'].get()), 4), round(float(ents['mid_Long'].get()), 4))
    if isFloat(ents['end_Lat'].get()) and isFloat(ents['end_Long'].get()):
        end = (round(float(ents['end_Lat'].get()), 4), round(float(ents['end_Long'].get()), 4))

    if (start == 0 or end == 0):
        messagebox.showerror("Error", "Enter valid start and end coordinates.")
        return 0
    #getting coordinates information by passing the float entries in get_coordinates_info function.
    info = get_coordinates_info(rider_name, start, end, mid)
    #raise error incase no information is provided.
    if info == 0:
        messagebox.showerror("Error", "No path Exists.")
        return 0
    #intialising the return dictionary.
    ret = {}
    ret['speed'] = float(sum(info['speed_plot'][1]) / len(info['speed_plot'][0]))   #retuning speed info in ret dictionary.
    ret['dist'] = info['distance_covered']      #updating ret dictionary by getting the information of coordinates from the entries.
    ret['ele'] = info['elevation_gain']
    ret['time'] = info['time_taken']

    return ret
