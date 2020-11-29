from tkinter import filedialog, messagebox
from tkinter import ttk
import tkinter.font as tkFont
import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
import string
from datetime import datetime
import matplotlib.pyplot as plt
from geopy import distance
import pandas as pd
import numpy as np
import gpxpy.gpx
import gpxpy
import os
from functools import partial
from process_coordinates import *
import time
from PIL import Image

fields = ('start_Lat', 'start_Long', 'mid_Lat', 'mid_Long',
          'end_Lat', 'end_Long',)


class LoadingScreen(Toplevel):
    progress_bar = None

    def __init__(self, master = None):
        super().__init__(master = master)
        self.title("Loading Screen")
        ws = master.winfo_screenwidth()
        hs = master.winfo_screenheight()
        x = (ws/2) - 250
        y = (hs/2) - 100
        self.geometry('%dx%d+%d+%d' % (200,200,x,y))    
        self.progress_bar = ttk.Progressbar(self, orient= HORIZONTAL, length = 100, mode = 'determinate')
        self.progress_bar.place(relx=0.25, rely=0.45)
        self.progress_bar['value'] = 0
    
    def increment_loading(self, increment):
        self.progress_bar['value'] = increment
        self.update_idletasks()
        if(increment == 100):
            time.sleep(0.2)

def Process(rider_name):

    global dist_img, speed_img, ele_img, rider

    plot(rider_name)     
    rider = rider_name
    dist_img = PhotoImage(file = r"./dist_plot.png")
    speed_img= PhotoImage(file = r"./speed_plot.png")
    ele_img = PhotoImage(file = r"./ele_plot.png")

def call_primary_buttons():
    global data, root, rider_name

    def process_data_button(event):
        load = LoadingScreen(root)
        load.grab_set()
        load.increment_loading(20)
        Process(rider_name.get())
        load.increment_loading(40)
        try:
            Label(top_right, text=rider_name.get() + " Statistics", font=fontStyle1).place(relx=0.20, rely=0.40)
            lb = Listbox(top_right, width=40, height=7)
            lb.place(relx=0.05, rely=0.45)
            p1, p2, p3 = summarise(rider_name.get())
            load.increment_loading(60)
            lb.insert(1, "Average distance covered per day (in Km): {}".format(p1))
            lb.insert(2, "Average elevation gain per day (in feet): {}".format(p2))
            lb.insert(3, "Max Speed reached (in Km/hr): {}".format(p3))
        except:
            print("{} has no data".format(rider_name.get()))
        load.increment_loading(100)
        load.grab_release()
        load.destroy()
    
    def compare_data_button(event):
        load = LoadingScreen(root)
        load.grab_set()
        load.increment_loading(25)
        try:
            Label(top_right, text=other_rider_name.get() + " Statistics", font=fontStyle1).place(relx=0.65, rely=0.40)
            lb = Listbox(top_right, width=40, height=7)
            lb.place(relx=0.50, rely=0.45)
            load.increment_loading(50)
            p1, p2, p3 = summarise(other_rider_name.get())
            lb.insert(1, "Average distance covered per day (in Km): {}".format(p1))
            lb.insert(2, "Average elevation gain per day (in feet): {}".format(p2))
            lb.insert(3, "Max Speed reached (in Km/hr): {}".format(p3))
            load.increment_loading(75)
        except:
            print("{} has no data".format(other_rider_name.get()))
        load.increment_loading(100)
        load.grab_release()
        load.destroy()

    Label(top_left, text="Select the rider: ", font=fontStyle1).place(relx=0.27, rely=0.91)
    rider_chosen = ttk.Combobox(top_left, width = 20, textvariable = rider_name)
    rider_chosen['values'] = tuple(data.keys())
    rider_chosen.place(relx=0.45,rely=0.91)
    rider_chosen.bind('<<ComboboxSelected>>', process_data_button)

    compare = Label(top_right, text="Compare your Stats with others", font=fontStyle)
    compare.place(relx=0.22, rely=0.2)

    Label(top_right, text="Select rider to compare with: ", font=fontStyle1).place(relx=0.15, rely=0.30)
    other_rider_name = tk.StringVar()
    other_rider_chosen = ttk.Combobox(top_right, width = 20, textvariable = other_rider_name)
    other_rider_chosen['values'] = tuple(data.keys())
    other_rider_chosen.place(relx=0.42,rely=0.30)
    other_rider_chosen.bind('<<ComboboxSelected>>', compare_data_button)



def pick_folder(*args):

    global ents, btm_left

    path = filedialog.askdirectory(
        initialdir="/", title="Select directory")

    if path != "":
        file_txt.config(text=path)
        dynamic_button.config(bg='green')
        filepath.set(path)
        filename.set(path.split('/')[-1])
        main(path)
        call_primary_buttons()
        ents = Coordinate_form(btm_left)
    else:
        return


def dist_plot_window():
    global dist_img, rider
    if rider == "":
        messagebox.showerror("Error", "Select a Rider first.")
        return 
    l.configure(image=dist_img, width=735, height=485, bg='white')

def speed_plot_window():
    global speed_img, rider
    if rider == "":
        messagebox.showerror("Error", "Select a Rider first.")
        return 
    l.configure(image=speed_img, width=735, height=485, bg='white')

def ele_plot_window():
    global ele_img, rider
    if rider == "":
        messagebox.showerror("Error", "Select a Rider first.")
        return 
    l.configure(image=ele_img, width=735, height=485, bg='white')



def Coordinate_form(root):
    '''
    
    This is just a form, figure out a way to get input from it
    Return a dict (ents) and pass it to Route Stats function
    
    '''

    global data, other_rider_segment
    
    form_frame = Frame(root, width=200, height=300)
    Label(form_frame, text="Start Latitude").grid(row=0, column=0)
    Label(form_frame, text="Start Longitude").grid(row=1, column=0)
    Label(form_frame, text="Mid Latitude").grid(row=2, column=0)
    Label(form_frame, text="Mid Longitude").grid(row=3, column=0)
    Label(form_frame, text="End Longitude").grid(row=4, column=0)
    Label(form_frame, text="End Longitude").grid(row=5, column=0)

    # (31.7743, 76.9814) (31.7749, 76.9816)

    a1 = Entry(form_frame)
    a1.grid(row=0, column=1)
    b1 = Entry(form_frame)
    b1.grid(row=1, column=1)
    c1 = Entry(form_frame)
    c1.grid(row=2, column=1)
    d1 = Entry(form_frame)
    d1.grid(row=3, column=1)
    e1 = Entry(form_frame)
    e1.grid(row=4, column=1)
    f1 = Entry(form_frame)
    f1.grid(row=5, column=1)

    # a1 = Entry(form_frame)
    # a1.grid(row=0, column=1)
    # a1.insert(0, "31.7743")
    # b1 = Entry(form_frame)
    # b1.grid(row=1, column=1)
    # b1.insert(0, "76.9814")
    # c1 = Entry(form_frame)
    # c1.grid(row=2, column=1)
    # d1 = Entry(form_frame)
    # d1.grid(row=3, column=1)
    # e1 = Entry(form_frame)
    # e1.grid(row=4, column=1)
    # e1.insert(0, "31.7749")
    # f1 = Entry(form_frame)
    # f1.grid(row=5, column=1)
    # f1.insert(0, "76.9816")

    Label(root, text="Compare with: ", font=fontStyle1).place(relx=0.6, rely=0.2)
    other_rider_chosen = ttk.Combobox(root, width = 20, textvariable = other_rider_segment)
    other_rider_chosen['values'] = tuple(data.keys())
    other_rider_chosen.place(relx=0.75,rely=0.2)
    other_rider_chosen.bind('<<ComboboxSelected>>', process_other_rider_segment)

    submit_btn = tk.Button(root, text="Submit", command=Route_Stats)
    submit_btn.place(relx=0.5,rely=0.3)


    form_frame.place(relx=0.06, rely=0.2)

    return {'start_Lat': a1, 'start_Long': b1, 'mid_Lat': c1, 'mid_Long': d1, 'end_Lat': e1, 'end_Long': f1}


def process_other_rider_segment(event):

    global ents, other_rider_segment

    load = LoadingScreen(root)
    load.grab_set()
    load.increment_loading(20)
    Process(rider_name.get())
    load.increment_loading(40)
    stats = process_coordinates_data(ents, other_rider_segment.get())

    try:
        Label(btm_left, text=other_rider_segment.get() + " Statistics", font=fontStyle1).place(relx=0.65, rely=0.65)
        lb = Listbox(btm_left, width=40, height=4)
        lb.place(relx=0.5, rely=0.7)
        lb.insert(1, "Average Time taken: {} min".format(round(stats['time'] * 60, 2)))
        lb.insert(2, "Average speed: {} km/hr".format(round(stats['speed'], 2)))
        lb.insert(3, "Number of trips: {}".format(stats['trips']))
        load.increment_loading(60)
    except:
        print("{} has no data".format(other_rider_segment.get()))

    load.increment_loading(100)
    load.grab_release()
    load.destroy()


def Route_Stats():

    global ents

    load = LoadingScreen(root)
    load.grab_set()
    load.increment_loading(20)
    Process(rider_name.get())
    load.increment_loading(40)
    stats = process_coordinates_data(ents)

    try:
        Label(btm_left, text=rider_name.get() + " Statistics", font=fontStyle1).place(relx=0.20, rely=0.65)
        lb = Listbox(btm_left, width=40, height=4)
        lb.place(relx=0.05, rely=0.7)
        lb.insert(1, "Average Time taken: {} min".format(round(stats['time'] * 60, 2)))
        lb.insert(2, "Average speed: {} km/hr".format(round(stats['speed'], 2)))
        lb.insert(3, "Number of trips: {}".format(stats['trips']))
        load.increment_loading(60)
    except:
        print("{} has no data".format(rider_name.get()))
    
    load.increment_loading(100)
    load.grab_release()
    load.destroy()

root = tk.Tk()
root.geometry("1500x1000")
root.title("GPS Route Analyser")
filename = StringVar()
filepath = StringVar()

# (31.7547, 76.9689) (31.7798, 76.9846)

# (31.7743, 76.9814) (31.7749, 76.9816)

# create all of the main containers

rider_name = tk.StringVar()
other_rider_segment = tk.StringVar()

top_left = Frame(root, width=750, height=500, pady=3, highlightcolor='black',highlightthickness=4, highlightbackground='black')
top_right = Frame(root, width=750, height=500, padx=3, pady=3, highlightcolor='black', highlightthickness=4, highlightbackground='black')
btm_left = Frame(root, width=750, height=500, pady=3, highlightcolor='black', highlightthickness=4, highlightbackground='black')
btm_right = Frame(root, width=750, height=500, pady=3, highlightcolor='black', highlightthickness=4, highlightbackground='black')

fontStyle = tkFont.Font(family="Lucida Grande", size=20)
fontStyle1 = tkFont.Font(family="Lucida Grande", size=10)
top_left.grid(row=0, column=0)
top_right.grid(row=0, column=1)
btm_left.grid(row=1, column=0)
btm_right.grid(row=1, column=1)


intro = Label(top_left, text='Welcome to GPS route Analyser', font=fontStyle)
intro.place(relx=0.2)
intro_text = Label(top_left, text="This program helps user to Analyse his/her physical performance using data from gpx files for the routes", font=fontStyle1)
intro_text.place(relx=0.05, rely=0.1)

canvas = Canvas(top_left, width = 300, height = 300)      
canvas.place(relx=0.25, rely=0.15)  

img = PhotoImage(file="./logo.png")      
canvas.create_image(20,25, anchor=NW, image=img)   


Label(top_left, text="Pick Directory for user:", font=fontStyle1).place(relx=0.05, rely=0.83)


file_txt = Label(top_left)
file_txt.place(relx=0.45, rely=0.83)



dynamic_button = tk.Button(top_left, text="Pick Directory", command=pick_folder, bg='red')
dynamic_button.place(relx=0.27, rely=0.82)



route_header = Label(btm_left, text="Route Specific Stats", font=fontStyle)
route_header.place(relx=0.3)
route_txt = Label(btm_left, text="This section provides Route Specific statistics, Please enter the required co-ordinates:", font=fontStyle1)
route_txt.place(relx=0.1, rely=0.1)



ents = None

try:
    dist_img = PhotoImage(file = r"./dist_plot.png")
    speed_img = PhotoImage(file = r"./speed_plot.png")
    ele_img = PhotoImage(file = r"./ele_plot.png")
except:
    im = Image.new('RGB', (580,484))
    for img_name in ("dist_plot", "speed_plot", "ele_plot"):
        im.save(img_name + ".png",format("PNG"))
    dist_img = PhotoImage(file = r"./dist_plot.png")
    speed_img = PhotoImage(file = r"./speed_plot.png")
    ele_img = PhotoImage(file = r"./ele_plot.png")


l = Label(btm_right)
l.place(relx=0, rely=0)



graphs = Label(top_right, text="Overall Statistics", font=fontStyle)
graphs.place(relx=0.35)
graphs_txt = Label(top_right, text="Click the respective button to display the plot", font=fontStyle1)
graphs_txt.place(relx=0.3, rely=0.07)
dist_btn = tk.Button(top_right, text="Distance vs Date", command=dist_plot_window)
dist_btn.place(relx=0.05,rely=0.12)
speed_btn = tk.Button(top_right, text="Speed vs Date", command=speed_plot_window)
speed_btn.place(relx=0.4,rely=0.12)
elevation_btn = tk.Button(top_right, text="Elevation vs Date", command=ele_plot_window)
elevation_btn.place(relx=0.7,rely=0.12)
mainloop()