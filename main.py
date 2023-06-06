# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 09:42:28 2023

@author: jcosson
"""
import os
import re
import time
import config as c
import subprocess
from concurrent import futures
import csv
from config import primal_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, adjoint_path;
from config import n, theta, T, a, t, deltaT, myinterval, mysweep, folder_name, maxCPU;
from src import solvers as sol, preprocessing as pre, postprocessing as post, boundary_conditions as bc, adjoint_solvers as adsol
import sys
import shutil
import concurrent.futures

################                  PATH                     ################
c.headings()
################           CHOICE OF COMPUTATION           ################

#sol.the_shooting_manager()

basepath="/home/julien/workspace/Simulations/"

#sol.primal_shooting_stef_update(basepath, "yes")

#post.plot_results(basepath)
#post.store_all_values(basepath, folder_name)



# def plot_my_data(basepath, filename, x_axis, y_axis, title):
#     os.chdir(basepath + folder_name)
#     with open(filename, 'r') as file:
#         lines = file.readlines()

#     modified_lines = []
#     for line in lines:
#         if line.startswith('set title'):
#             modified_lines.append("set title '" + title + "'\n")
#         elif line.startswith("plot 'logtable.csv'"):
#             parts = line.split("using ")
#             parts[1] = str(x_axis) + ":" + str(y_axis)
#             modified_lines.append("using ".join(parts))
#         else:
#             modified_lines.append(line)

#     with open(filename, 'w') as file:
#         file.writelines(modified_lines)

#     # Example usage:
#         #filename = 'path/to/file'
#         #modify_plot_code_in_file(filename, 6, 2, "Custom Plot Title")

def plot_my_data(basepath, filename, x_axis, y_axis, title, k):
    os.chdir(basepath + folder_name)
    
    # Read the first and last lines of logtable.csv
    with open("logtable.csv", 'r') as file:
        first_line = file.readline().strip().split('    ')
        last_line = file.readlines()[-1].strip().split('    ')

    # Get the column values based on x_axis and y_axis
    num_columns = len(first_line)
    x_min = float(first_line[min(x_axis - 1, num_columns - 1)])
    x_max = float(last_line[min(x_axis - 1, num_columns - 1)])
    y_min = float(first_line[min(y_axis - 1, num_columns - 1)])
    y_max = float(last_line[min(y_axis - 1, num_columns - 1)])

    axis_labels = {
        1: "Sweep [-]",
        2: "Pressure Drop [Nm, E-7]",
        3: "Impuls Defect [kg.m.s⁻¹]",
        4: "Continuity Defect [kg.m.s⁻¹]",
        5: "Wall Time Primal [s]",
        6: "Total Accumulated Time [s]"
    }
    xrange_values = {
        1: "[{}:{}]\n".format(0,k+1),
        2: "[{}:{}]\n".format(0,x_max),
        3: "[{}:{}]\n".format(0,x_max),
        4: "[{}:{}]\n".format(0,x_max),
        5: "[{}:{}]\n".format(0,x_max),
        6: "[{}:{}]\n".format(0,x_max),
    }
    yrange_values = {
        1: "[0:{}]\n".format(k+1),
        2: "[0:1.5]\n",
        3: "[{}:{}]\n".format(y_max,y_min),
        4: "[{}:{}]\n".format(y_max,y_min),
        5: "[{}:{}]\n".format(0,y_max + 50),
        6: "[{}:{}]\n".format(0,y_max),
    }

    with open(filename, 'r') as file:
        lines = file.readlines()

    modified_lines = []
    for line in lines:
        if line.startswith('set title'):
            new_title="Plot for " + str(n) + " subintervals"
            modified_lines.append("set title '" + new_title + "'\n")
        elif line.startswith("set xlabel"):
            modified_lines.append("set xlabel '" + axis_labels[x_axis] + "'\n")
        elif line.startswith("set ylabel"):
            modified_lines.append("set ylabel '" + axis_labels[y_axis] + "'\n")
        elif line.startswith("set xrange"):
            modified_lines.append("set xrange " + xrange_values[x_axis])
        elif line.startswith("set yrange"):
            modified_lines.append("set yrange " + yrange_values[y_axis])
        elif line.startswith("plot 'logtable.csv'"):
            parts = line.split("using ")
            parts[1] = str(x_axis) + ":" + str(y_axis)
            if y_axis == 2:
                parts[1] = str(x_axis) + ":(${}*10e6)".format(y_axis)
            modified_lines.append("using ".join(parts) + " with linespoints ls 1 title 'Primal Shooting',")
        elif line.startswith("set output "):
            
            # Construct the plot filename based on the given options
            plot_filename = "plot_{}_{}_{}.eps".format(x_axis, y_axis, title)
            modified_lines.append("set output '" + plot_filename + "'\n")
        else:
            modified_lines.append(line)

    with open(filename, 'w') as file:
        file.writelines(modified_lines)

    # Execute the bash command to generate the plot
    subprocess.run(["gnuplot", filename])
    # # Example usage:
        # filename = 'path/to/file'
        # modify_plot_code_in_file(filename, 6, 2, "Custom Plot Title")

def all_plots():
    plot_my_data(basepath, "shootingManagerOutput.plot", 6, 2, folder_name, n)
    plot_my_data(basepath, "shootingManagerOutput.plot", 6, 1, folder_name, n)
    plot_my_data(basepath, "shootingManagerOutput.plot", 1, 2, folder_name, n)
    plot_my_data(basepath, "shootingManagerOutput.plot", 1, 3, folder_name, n)
    plot_my_data(basepath, "shootingManagerOutput.plot", 1, 4, folder_name, n)
    plot_my_data(basepath, "shootingManagerOutput.plot", 1, 5, folder_name, n)


all_plots()

#plot_my_data(basepath, "shootingManagerOutput.plot", 6, 2, folder_name, n)

