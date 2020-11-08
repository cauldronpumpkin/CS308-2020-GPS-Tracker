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
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)


data = []


def main(path):

    global data

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
        distance_covered += distance.geodesic(
            (lat[i], long[i]), (lat[i + 1], long[i + 1])).km
        elevation_gain += max(0, ele[i + 1] - ele[i])

    return (distance_covered, elevation_gain)


def get_all_stats(routes):

    distance_covered, elevation_gain = get_distance_elevation(routes[0])

    indexes = [i for i in range(len(routes))]
    speeds = [distance_covered / (len(lat) / 3600) for lat, _, _ in routes]

    ret_info = {
        'distance_covered': distance_covered,
        'elevation_gain': elevation_gain,
        'speed_plot': (indexes, speeds)
    }

    return ret_info


def check_uniqueness(routes):

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

    global data

    routes = []
    for i in range(len(data)):
        coords, pair_of_coordinates = data[i]
        if start in pair_of_coordinates and end in pair_of_coordinates and (mid == (0, 0) or mid in pair_of_coordinates):

            idx_start = pair_of_coordinates[start]
            idx_mid = -1 if mid == (0, 0) else pair_of_coordinates[mid]
            idx_end = pair_of_coordinates[end]

            if (idx_start < idx_end and (idx_mid == -1 or (idx_start < idx_mid and idx_mid < idx_end))):
                routes.append((coords['lat'].tolist()[idx_start: idx_end], coords['long'].tolist()[
                              idx_start: idx_end], coords['ele'].tolist()[idx_start: idx_end]))
        else:
            continue

    if not(check_uniqueness(routes)):
        return False

    return get_all_stats(routes)


def get_attr_per_day():
    '''

    Returns a tuple of dictionaries for distance vs day, elevation-gain vs day and speed vs day plots

    '''

    dist_map, ele_map, speed_map = dict(), dict(), dict()
    for i in range(len(data)):
        time_series, ele_series, lat_series, long_series = data[i][0][
            'time'], data[i][0]['ele'], data[i][0]['lat'], data[i][0]['long']
        for j in range(len(data[i][0])):
            day = time_series[j].strftime("%x")
            print(day)
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

    FMT = "%H:%M:%S"

    for day, arr in dist_map.items():
        total_dist = total_time = 0
        tmp_dist = tmp_time = 0
        for i in range(len(arr) - 1):
            tmp_dist = distance.geodesic(
                (arr[i][0], arr[i][1]), (arr[i + 1][0], arr[i + 1][1])).km
            time_elapsed = datetime.strptime(
                arr[i + 1][2].strftime("%X"), FMT) - datetime.strptime(arr[i][2].strftime("%X"), FMT)
            days, seconds = time_elapsed.days, time_elapsed.seconds
            hours = days * 24 + seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            tmp_time = hours + minutes/60 + seconds/3600
            if(tmp_time < 0):
                print("Error: Time is negative")
                break
            total_dist += tmp_dist
            total_time += tmp_time
        if(tmp_time < 0):
            break
        dist_map[day] = total_dist
        speed_map[day] = total_dist/total_time

    return (dist_map, ele_map, speed_map)

# Overall Summary of data (all days)


def summarise():
    d, e, s = get_attr_per_day()
    d_key, d_val = Filter_data(d)
    e_key, e_val = Filter_data(e)
    s_key, s_val = Filter_data(s)
    window = Toplevel()
    window.geometry("500x300")
    window.title("Overall Stats ")

    mylist = Listbox(window, width=20, height=10)
    mylist.pack(padx=10, pady=10, fill="both", expand=True)

    mylist.insert(
        END, "Average distance covered per day (in Km): {}".format(round(np.mean(d_val), 2)))
    mylist.insert(
        END, "Average elevation gain per day (in feet): {}".format(round(np.mean(e_val), 2)))
    mylist.insert(
        END, "Max Speed reached (in Km/hr): {}".format(round(max(s_val), 2)))

    window.mainloop()

# Converts dict to list with key and value seprate, sorts dates also


def Filter_data(d):
    dk = []
    dval = []
    for key, val in d.items():
        dk.append(key)
    dk.sort(key=lambda date: datetime.strptime(date, "%m/%d/%y"))
    for i in dk:
        dval.append(d[i])
    return dk, dval

# For a particluar root stat, link it with gui as suitable


def Route_stat(start, end):
    stats = get_coordinates_info(start, end)
    if stats != False:
        print("Distance Covered: ", stats['distance_covered'])
        print("Elevation Gain: ", stats['elevation_gain'])
        print("Average Speed during Activity: ", stats['speed_plot'][1])
    else:
        print("Multiple routes possible, please specify")

# All the plots related to data here, there are three seprate windows for each plot


def plot():
    d, e, s = get_attr_per_day()
    d_key, d_val = Filter_data(d)
    e_key, e_val = Filter_data(e)
    s_key, s_val = Filter_data(s)
    plot_window1 = Toplevel()
    plot_window1.geometry("1900x1000")
    plot_window1.title("Plot for Distance vs. Date")

    plot_window2 = Toplevel()
    plot_window2.geometry("1900x1000")
    plot_window2.title("Plot for Elevation vs. Date")

    plot_window3 = Toplevel()
    plot_window3.geometry("1900x1000")
    plot_window3.title("Plot for Speed vs. Date")

    fig1 = Figure(figsize=(19, 10), dpi=100)

    plot1 = fig1.add_subplot()
    canvas1 = FigureCanvasTkAgg(fig1, master=plot_window1)
    canvas1.get_tk_widget().pack()
    toolbar1 = NavigationToolbar2Tk(canvas1, plot_window1)
    toolbar1.update()
    plot1.plot_date(d_key, d_val, xdate=True, linestyle='-')
    plot1.set_xlabel("Date")
    plot1.set_ylabel("Distance Covered (Km) ")
    plot1.set_title("Distance vs. Date")
    for tick in plot1.get_xticklabels():
        tick.set_rotation(90)

    fig2 = Figure(figsize=(19, 10), dpi=100)
    plot2 = fig2.add_subplot()
    canvas2 = FigureCanvasTkAgg(fig2, master=plot_window2)
    canvas2.get_tk_widget().pack()
    toolbar2 = NavigationToolbar2Tk(canvas2, plot_window2)
    toolbar2.update()
    plot2.plot_date(e_key, e_val, xdate=True, linestyle='-')
    plot2.set_xlabel("Date")
    plot2.set_ylabel("Elevation Gain (in feets)")
    plot2.set_title("Elevation vs. Date")
    for tick in plot2.get_xticklabels():
        tick.set_rotation(90)

    fig3 = Figure(figsize=(19, 10), dpi=100)

    plot3 = fig3.add_subplot()
    canvas3 = FigureCanvasTkAgg(fig3, master=plot_window3)
    canvas3.get_tk_widget().pack()
    toolbar3 = NavigationToolbar2Tk(canvas3, plot_window3)
    toolbar3.update()
    plot3.plot_date(s_key, s_val, xdate=True, linestyle='-')
    plot3.set_xlabel("Date")
    plot3.set_ylabel("Average Speed (Km/hr)")
    plot3.set_title("Average Speed vs. Date")
    for tick in plot3.get_xticklabels():
        tick.set_rotation(90)
    plot_window1.mainloop()
    plot_window2.mainloop()
    plot_window3.mainloop()
