from tkinter import filedialog, messagebox
from tkinter import ttk
import tkinter as tk
from tkinter import *
import string
from datetime import datetime
import matplotlib.pyplot as plt
from geopy import distance
import pandas as pd
import numpy as np
import gpxpy.gpx
import gpxpy
import os
from process_coordinates import *


fields = ('start_Lat', 'start_Long', 'mid_Lat', 'mid_Long',
          'end_Lat', 'end_Long',)


def pick_folder(*args):
    path = filedialog.askdirectory(
        initialdir="/", title="Select directory")

    if path != "":
        filepath.set(path)
        filename.set(path.split('/')[-1])
        main(path)
    else:
        return


def makeform(root, fields):
    entries = {}
    for field in fields:
        row = tk.Frame(root)
        lab = tk.Label(row, width=22, text=field+": ", anchor='w')
        ent = tk.Entry(row)
        ent.insert(0, "0")
        row.pack(side=tk.TOP,
                 fill=tk.X,
                 padx=5,
                 pady=5)
        lab.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT,
                 expand=tk.YES,
                 fill=tk.X)
        entries[field] = ent
    return entries


root = tk.Tk()
root.title("GPS Route Analyser")
mainframe = ttk.Frame(root)

filepath = StringVar()
filename = StringVar()

ttk.Label(mainframe, textvariable=filename).grid(
    column=1, row=1, sticky=(W, E))


ents = makeform(root, fields)
dynamic_button = tk.Button(root, text="Pick Directory", command=pick_folder)
dynamic_button.pack(side=tk.LEFT, padx=5, pady=5)
b1 = tk.Button(root, text='Show Overall Stats', command=summarise)
b1.pack(side=tk.LEFT, padx=5, pady=5)
b2 = tk.Button(root, text='Pictoral Analysis', command=plot)
b2.pack(side=tk.LEFT, padx=5, pady=5)
root.mainloop()

# basic gui with buttons & input field & folder select // a
# coordinates:  // d
# plots, stats  // d
# overall stats: plots, stats. // rahul
