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
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil import parser
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)


data = dict()
d = e = s = None
rider = ""




def main(path):

    global data

    files = os.listdir(path)

    for dir in os.listdir(path):
        data[dir] = []
        for file in os.listdir(os.path.join(path, dir)):
            name = str(file).split('.')[0]
            gpx_file = open(os.path.join(os.path.join(path, dir), file), 'r')

            try:
                gpx = gpxpy.parse(gpx_file)
            except:
                continue

            segment = gpx.tracks[0].segments[0]
            coords = pd.DataFrame([{
                'lat': p.latitude,
                'long': p.longitude,
                'ele': p.elevation,
                'time': p.time} for p in segment.points])

            pair_of_coords = {}
            for i, p in enumerate(segment.points):
                pair_of_coords[(p.latitude, p.longitude)] = i

            data[dir].append((coords, pair_of_coords, name))
    return data


def get_distance_elevation(route):

    lat, lon, ele, _ = route

    distance_covered = 0
    elevation_gain = 0

    for i in range(len(lat) - 1):
        distance_covered += distance.geodesic(
            (lat[i], lon[i]), (lat[i + 1], lon[i + 1])).km
        elevation_gain += max(0, ele[i + 1] - ele[i])

    return (distance_covered, elevation_gain)


def get_all_stats(routes):

    distance_covered, elevation_gain = get_distance_elevation(routes[0])

    names = [name for _, _, _, name in routes]
    speeds = [distance_covered / float(len(lat) / 3600)
              for lat, _, _, _ in routes]

    ret_info = {
        'distance_covered': distance_covered,
        'elevation_gain': elevation_gain,
        'speed_plot': (names, speeds)
    }

    return ret_info


def check_uniqueness(routes):

    if len(routes) == 0:
        return 0

    dist_arr = np.array([get_distance_elevation(route)[0] for route in routes])
    ele_arr = np.array([get_distance_elevation(route)[1] for route in routes])

    dist_mean = sum(dist_arr) / len(dist_arr)
    ele_mean = sum(ele_arr) / len(ele_arr)

    dist_arr = dist_arr - [dist_mean]
    ele_arr = ele_arr - [ele_mean]

    for i in range(len(dist_arr)):
        if (abs(dist_arr[i]) > 0.1 or abs(ele_arr[i]) > 1):
            return False

    return True


def get_coordinates_info(start, end, mid=(0, 0)):

    global data, rider

    if len(data) == 0:
        messagebox.showerror("Error", "Select GPX directory first.")
        return

    if(rider == ""):
        messagebox.showerror("Error", "Select a rider first.")
        return
        
    routes = []
    for i in range(len(data[rider])):
        coords, pair_of_coordinates, name = data[rider][i]
        if start in pair_of_coordinates and end in pair_of_coordinates and (mid == (0, 0) or mid in pair_of_coordinates):

            idx_start = pair_of_coordinates[start]
            idx_mid = -1 if mid == (0, 0) else pair_of_coordinates[mid]
            idx_end = pair_of_coordinates[end]

            if (idx_start < idx_end and (idx_mid == -1 or (idx_start < idx_mid and idx_mid < idx_end))):
                routes.append((coords['lat'].tolist()[idx_start: idx_end], coords['long'].tolist()[
                              idx_start: idx_end], coords['ele'].tolist()[idx_start: idx_end], name))
        else:
            continue

    if not(check_uniqueness(routes)):
        return False

    return get_all_stats(routes)


def get_attr_per_day(rider_name):
    '''

    Returns a tuple of dictionaries for distance vs day, elevation-gain vs day and speed vs day plots

    '''
    global data
    
    dist_map, ele_map, speed_map = dict(), dict(), dict()
    for i in range(len(data[rider_name])):
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

    for day, arr in ele_map.items():
        ele_gain = 0
        for i in range(len(arr) - 1):
            ele_gain += max(0, arr[i + 1] - arr[i])
        ele_map[day] = ele_gain

    FMT = "%m/%d/%Y, %H:%M:%S"

    for day, arr in dist_map.items():
        total_dist = total_time = 0
        tmp_dist = tmp_time = 0
        for i in range(len(arr) - 1):
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
        dist_map[day] = total_dist
        speed_map[day] = total_dist/total_time

    return (dist_map, ele_map, speed_map)




def summarise(rider_name):
    '''
    
    Overall Summary of data (all days)

    '''

    global d,e,s,rider

    if(rider == ""):
        messagebox.showerror("Error", "Please select the primary rider first!")
        return

    if len(data[rider_name]) == 0:
        messagebox.showerror("Error", "No data found for " + rider_name)
        return


    if(rider_name == rider):
        if(d == None):
            d, e, s = get_attr_per_day(rider_name)
        return (round(np.mean(tuple(d.values())), 2), round(np.mean(tuple(e.values())), 2), round(max(tuple(s.values())), 2))
    else:
        messagebox.showinfo("Loading", "Please Close this and wait for 5-10 seconds")
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
    dk.sort(key=lambda date: datetime.strptime(date, "%m/%d/%y"))
    for i in dk:
        dval.append(d[i])
    return dk, dval




def Route_stat(start, end):
    '''
    
    For a particluar root stat, link it with gui as suitable

    '''
    stats = get_coordinates_info(start, end)
    if stats != False:
        print("Distance Covered: ", stats['distance_covered'])
        print("Elevation Gain: ", stats['elevation_gain'])
        print("Average Speed during Activity: ", stats['speed_plot'][1])
    else:
        print("Multiple routes possible, please specify")



def plot(rider_name):
    '''

    All the plots related to data here, there are three seprate windows for each plot

    '''


    global d, e, s, rider

    if(rider == rider_name):
        return
    
    if len(data) == 0:
        messagebox.showerror("Error", "Select GPX directory first.")
        return

    if len(data[rider_name]) == 0:
        messagebox.showerror("Error", "No data found for " + rider_name)
        return
    
    if (d == None or rider_name != rider):
        messagebox.showinfo(
            "Loading", "Please Close this and wait for 5-10 seconds")
        d, e, s = get_attr_per_day(rider_name)
        rider = rider_name

    d_key, d_val = Filter_data(d)
    e_key, e_val = Filter_data(e)
    s_key, s_val = Filter_data(s)

    plt.clf()

    plt.stem(d_key, d_val)
    plt.ylabel("Distance Covered (Km) ")
    plt.title("Distance vs. Date")
    plt.xticks(rotation='vertical')
    plt.savefig("dist_plot.png", bbox_inches='tight')

    plt.clf()

    plt.stem(s_key, s_val)
    plt.ylabel("Average Speed (Km/hr) ")
    plt.title("Speed vs. Date")
    plt.xticks(rotation='vertical')
    plt.savefig("speed_plot.png", bbox_inches='tight')

    plt.clf()
    
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


def process_coordinates_data(ents, rider_name):

    if len(data) == 0:
        messagebox.showerror("Error", "Select GPX directory first.")
        return 0

    start = 0
    mid = 0
    end = 0 

    if isFloat(ents['start_Lat'].get()) and isFloat(ents['start_Long'].get()):
        start = (float(ents['start_Lat'].get()),
                 float(ents['start_Long'].get()))
    if isFloat(ents['mid_Lat'].get()) and isFloat(ents['mid_Long'].get()):
        mid = (float(ents['mid_Lat'].get()), float(ents['mid_Long'].get()))
    if isFloat(ents['end_Lat'].get()) and isFloat(ents['end_Long'].get()):
        end = (float(ents['end_Lat'].get()), float(ents['end_Long'].get()))

    if (start == 0 or end == 0):
        messagebox.showerror("Error", "Enter valid start and end coordinates.")
        return 0

    info = get_coordinates_info(start, end, rider_name, mid=(0, 0))

    if info == 0:
        messagebox.showerror("Error", "More than one path exists or no path.")
        return 0

    plot_window = Toplevel()
    plot_window.geometry("1000x1000")
    plot_window.title("Statistics")

    fig = Figure(figsize=(9, 9), dpi=100)

    plot = fig.add_subplot(111)

    plot.scatter(info['speed_plot'][0], info['speed_plot'][1])

    plot.set_title("Speed throughout trips (in km/hr)")

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.draw()

    toolbar = NavigationToolbar2Tk(canvas, plot_window)
    toolbar.update()

    canvas.get_tk_widget().pack()

    summary_window = Toplevel()
    summary_window.geometry("400x300")
    mylist = Listbox(summary_window, width=20, height=10)
    mylist.pack(padx=10, pady=10, fill="both", expand=True)

    mylist.insert(END, "Distance Covered (in Km): {}".format(
        info['distance_covered']))
    mylist.insert(END, "Elevation Gain (in feet): {}".format(
        info['elevation_gain']))
    mylist.insert(END, "Mean Speed: {}".format(np.mean(info['speed_plot'][1])))
    mylist.insert(END, "Standard Deviation of speed: {}".format(
        np.std(info['speed_plot'][1])))

    plot_window.mainloop()
    summary_window.mainloop()
