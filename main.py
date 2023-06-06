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
print(folder_name)

post.all_plots(basepath)

#plot_my_data(basepath, "shootingManagerOutput.plot", 6, 2, folder_name, n)

