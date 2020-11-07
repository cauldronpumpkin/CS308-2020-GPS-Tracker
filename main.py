from process_coordinates import *
main("./data/")
print(get_coordinates_info((31.771511, 76.984304), (31.770879, 76.98317)))
import os
import gpxpy
import gpxpy.gpx
import numpy as np
import pandas as pd
from geopy import distance
#import matplotlib.pyplot as plt
from datetime import datetime
import string
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox


fields = ('start_input_1', 'start_input_2', 'start_elevation', 'end_input_1', 'end_input_2','end_elevation')


def pick_file(*args):
    path =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("txt files","*.txt"),("all files","*.*")))

    if path != "":
        filepath.set(path)
        filename.set(path.split('/')[-1])
        dynamic_button['text'] = "Coordinates"
        #dynamic_button['command'] = refresh
    else:
        return


def makeform(root, fields):
    entries = {}
    for field in fields:
        print(field)
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

ttk.Label(mainframe, textvariable=filename).grid(column=1, row=1, sticky=(W, E))


ents = makeform(root, fields)
dynamic_button = tk.Button(root, text="Pick File", command=pick_file)
dynamic_button.pack(side=tk.LEFT, padx=5, pady=5)
b1 = tk.Button(root, text='Calculate',
           command=(lambda e=ents: calculate(e)))
b1.pack(side=tk.LEFT, padx=5, pady=5)
root.mainloop()

# basic gui with buttons & input field & folder select // a
# coordinates:  // d
# plots, stats  // d
# overall stats: plots, stats. // rahul
