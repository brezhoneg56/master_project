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

basepath=primal_path

sol.primal_shooting_stef_update(basepath, "yes")

#post.store_all_values(basepath, folder_name)

#for k in range(1, n+1):
#    post.erase_all_files(basepath, folder_name, k)



def store_for_plot_defect(basepath, sweep_name, interval_name, file):
    table = []
    ### Partie Defect :
    _, flux_value = post.fetch_values_defect(basepath, file, sweep_name, interval_name)
    velocity_value, _ = post.fetch_values_defect(basepath, file, sweep_name, interval_name)
    #with open("logtable.csv", 'a', newline='') as tab:
    #writer = csv.writer(tab)
    # Store the variables in a table or data structure of your choice
    table_defect=table.append((velocity_value, flux_value))
    # Write the row to the CSV file
    #writer.writerow([velocity_value, flux_value])
    return table_defect



def store_all_values(basepath, folder_name):
    os.chdir(basepath + folder_name)
    print("All value will be stored in a CSV file as follows:\n")
    print("Row number = Sweep Number, pressureDrop, velocity defect, continuity defect (flux), primalWallTime, SweepWallTime, AccumulatedTime")
    print("Wrinting into logtable in  " + basepath + folder_name)
    table = []
    os.chdir(basepath + folder_name)
    with open("logtable.csv", 'a', newline='') as tab:
        for k in range(1, n+1):
            sweep_name=mysweep.format(k)
            #path_file=basepath + folder_name + "/" + sweep_name + "/logfiles/pressureDrop.txt"
            #find_logfile(basepath, "pressureDrop.txt")
            for i in range(2, n+1):
                interval_name=myinterval.format(i)
                #Write Sweep Number
                #store_for_plot(basepath, folder_name, sweep_name)
                
                #Fetch pressureDrop
                pressure_path=find_logfile(basepath, sweep_name, interval_name, "pressureDrop.txt")
                #os.chdir(pressure_path)
                try:
                    pressureDrop=post.fetch_values(basepath, pressure_path, "pressureDrop is     ")
                except Exception as pressure:
                    print("Pressure Drop not found")
                    pressureDrop=0
                #Fetch Velocity and Continuity Defects:
                try:
                    flux_path=find_logfile(basepath, sweep_name, interval_name, ("shooting_defect_logfile" + sweep_name + "_" + interval_name + ".txt"))
                    #print(flux_path)
                except Exception as shoot:
                    print("Shooting Defect not found")
                    flux_path=0
                _, flux_value = post.fetch_values_defect(basepath, sweep_name, interval_name, flux_path)
                velocity_value, _ = post.fetch_values_defect(basepath, sweep_name, interval_name, flux_path)
        
                writer = csv.writer(tab)
                # Store the variables in a table or data structure of your choice
                table.append((sweep_name, pressureDrop, velocity_value, flux_value))
                # Write the row to the CSV file
        writer.writerow([table])
    return table

def find_logfile(basepath, sweep_name, interval_name, thefile):
    #max_depth = 5  # Maximum depth to search for the file
    #for k in range(1, n+1):
    file_path = basepath + folder_name + "/" + sweep_name + "/logfiles/"
    for root, dirs, files in os.walk(file_path):
        #current_depth = root.count(os.sep) - file_path.count(os.sep)
        #if current_depth <= max_depth and thefile in files:
        if thefile in files:
            logfile_path = os.path.join(root, thefile)
            #print(logfile_path)
            return (logfile_path)
        else:
            print(thefile + " not found")



def fetch_values_defect(basepath, sweep_name, interval_name, path_file):
    #path_file = basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingDefect/" + "shooting_defect_logfile" + sweep_name + "_" + interval_name + ".txt"
    with open(path_file, "r") as myfile:
        text = myfile.read()

        # Regular expression pattern to capture the value
        velocity = r"defects \(velocity\): sum local = ([\d.e+-]+)"
        fluxes = r"defects \(fluxes\): sum local = ([\d.e+-]+)"

        # Search for the pattern in each line
        for line in text.split('\n'):
            velocity_match = re.search(velocity, line)
            flux_match = re.search(fluxes, line)
            if velocity_match:
                velocity_defect = velocity_match.group(1)
                #print("defects (velocity): sum local:", velocity_defect)
            if flux_match:
                flux_defect = flux_match.group(1)
                #print("defects (fluxes): sum local:", flux_defect)
        return(velocity_defect, flux_defect)

def fetch_values(basepath, path_file, line_to_find):
    with open(path_file, "r") as myfile:
        text = myfile.read()
        # Regular expression pattern to capture the value
        #velocity = r"defects \(velocity\): sum local = ([\d.e+-]+)"
        line_to_find=line_to_find + "([\d.e+-]+)"
        # Search for the pattern in each line
        for line in text.split('\n'):
            match = re.search(line_to_find, line)
            if match:
                the_value = match.group(1)
        return(the_value)


#store_all_values(basepath, folder_name)

#pressure_path=find_logfile(basepath, "pimple_interval4.log")
