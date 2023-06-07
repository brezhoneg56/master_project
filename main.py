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

#sol.primal_shooting_stef_update(basepath, "yes")

#post.plot_results(basepath)
#post.store_all_values(basepath, folder_name)

#post.all_plots_new(basepath)
#post.multiple_plots(basepath, "multiplePlotShooting.plot", 2, 6, new_folder, k)
#plot_my_data(basepath, "shootingManagerOutput.plot", 6, 2, folder_name, n)

# Execute the bash command to generate the plot
filename="multiplePlotShooting.plot"
#/home/jcosson/workspace/henersj_shootingdata/calcs/moderate_deformed/primal/multiplePlotShooting.plot
os.chdir(basepath)
print(basepath)
#subprocess.run(["gnuplot", filename])
intervals = [1, 2, 3, 5, 7, 10, 14, 28, 56, 100]
x = [6, 1, 1, 1, 1]
y = [2, 2, 3, 4, 5]

#print(len(x))

for z in range(0, (len(x))):
    #print(x[z], y[z])
    post.multiple_plots(basepath, filename, x[z], y[z], intervals)