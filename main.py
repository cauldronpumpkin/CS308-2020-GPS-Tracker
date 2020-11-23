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

fields = ('start_Lat', 'start_Long', 'mid_Lat', 'mid_Long',
          'end_Lat', 'end_Long',)

def pick_folder(*args):

    path = filedialog.askdirectory(
        initialdir="/", title="Select directory")

    if path != "":
        file_txt.config(text=path)
        dynamic_button.config(bg='green')
        filepath.set(path)
        filename.set(path.split('/')[-1])
        main(path)
    else:
        return

def dist_plot_window():
    l.configure(image=d, width=735, height=485, bg='white')
def speed_plot_window():
    l.configure(image=s, width=735, height=485, bg='white')
def ele_plot_window():
    l.configure(image=e, width=735, height=485, bg='white')


def Cordinate_form(root):
    # This is just a form, figure out a way to get input from it
    # Return a dict (ents) and pass it to Route Stats function
    form_frame = Frame(root, width=200, height=300)
    a = Label(form_frame, text="Start Latitude").grid(row=0, column=0)
    b = Label(form_frame, text="Start Longitude").grid(row=1, column=0)
    c = Label(form_frame, text="Mid Latitude").grid(row=2, column=0)
    d = Label(form_frame, text="Mid Longitude").grid(row=3, column=0)
    e = Label(form_frame, text="End Longitude").grid(row=4, column=0)
    f = Label(form_frame, text="End Longitude").grid(row=5, column=0)

    a1 = Entry(form_frame).grid(row=0, column=1)
    b1 = Entry(form_frame).grid(row=1, column=1)
    c1 = Entry(form_frame).grid(row=2, column=1)
    d1 = Entry(form_frame).grid(row=3, column=1)
    e1 = Entry(form_frame).grid(row=4, column=1)
    f1 = Entry(form_frame).grid(row=5, column=1)

    form_frame.place(relx=0.06, rely=0.2)


def Route_Stats(parameter_list):
    # When you press submit this function is triggered
    #In this function fill all the stats in their respective labels
    
    # Uncomment the following 
    
    # s1val.config(text="Value of stat")
    # s2val.config(text="Value of stat")
    # s3val.config(text="Value of stat")
    # s4val.config(text="Value of stat")
    # s5val.config(text="Value of stat")
    pass

def Process():
    plot()     


root = tk.Tk()
root.geometry("1500x1000")
root.title("GPS Route Analyser")
filename = StringVar()
filepath = StringVar()
# create all of the main containers
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

button_txt = Label(top_left, text="Pick Directory for user:", font=fontStyle1)
button_txt.place(relx=0.05, rely=0.83)
dynamic_button = tk.Button(top_left, text="Pick Directory", command=pick_folder, bg='red')
dynamic_button.place(relx=0.27, rely=0.82)
process_button = tk.Button(top_left, text="Process Data", command=Process)
process_button.place(relx=0.05, rely=0.89)
file_txt = Label(top_left)
file_txt.place(relx=0.45, rely=0.83)

route_header = Label(btm_left, text="Route Specific Stats", font=fontStyle)
route_header.place(relx=0.3)
route_txt = Label(btm_left, text="This section provides Route Specific statistics, Please enter the required co-ordinates:", font=fontStyle1)
route_txt.place(relx=0.1, rely=0.1)
Cordinate_form(btm_left)
stats_frame = Frame(btm_left, width=200, height=300)
s1 = Label(stats_frame, text="Route Distance: ").grid(row=0, column=0)
s2 = Label(stats_frame, text="Average Speed: ").grid(row=1, column=0)
s3 = Label(stats_frame, text="Highest Elevation: ").grid(row=2, column=0)
s4 = Label(stats_frame, text="Lowest Elevation: ").grid(row=3, column=0)
s5 = Label(stats_frame, text="Time Taken: ").grid(row=4, column=0)

s1val = Label(stats_frame).grid(row=0, column=1)
s2val = Label(stats_frame).grid(row=1, column=1)
s3val = Label(stats_frame).grid(row=2, column=1)
s4val = Label(stats_frame).grid(row=3, column=1)
s5val = Label(stats_frame).grid(row=4, column=1)

stats_frame.place(relx=0.65, rely=0.21)
submit_btn = tk.Button(btm_left, text="Submit", command=Route_Stats)
submit_btn.place(relx=0.5,rely=0.3)

d = PhotoImage(file = r"./dist_plot.png")
s = PhotoImage(file = r"./speed_plot.png")
e = PhotoImage(file = r"./ele_plot.png")
l = Label(btm_right)
l.place(relx=0, rely=0)


compare = Label(top_right, text="Compare your Stats with others", font=fontStyle)
compare.place(relx=0.22, rely=0.2)

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


root.mainloop()
