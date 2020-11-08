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
from functools import partial
from process_coordinates import *
import time


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
process_coordinates_data_args = partial(process_coordinates_data, ents)
b3 = tk.Button(root, text='Process Coordinates', command=process_coordinates_data_args)
b3.pack(side=tk.LEFT, padx=5,pady=5)
b1 = tk.Button(root, text='Show Overall Stats', command=summarise)
b1.pack(side=tk.BOTTOM, padx=5, pady=5)
b2 = tk.Button(root, text='Plot Overall Data', command=plot)
b2.pack(side=tk.BOTTOM, padx=5, pady=5)
root.mainloop()
