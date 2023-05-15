# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 09:42:28 2023

@author: jcosson
"""
import os
import time
import config as c
from config import primal_path, primitive_path, steffensen_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path;
from config import n, theta, T, a, t, deltaT, myinterval, mysweep, folder_name;
from src import solvers as sol, preprocessing as pre, postprocessing as post
import sys
import shutil
################                  PATH                     ################
c.headings()
################           CHOICE OF COMPUTATION           ################
#Primitive shooting :
basepath=primitive_path
os.chdir(basepath)

#sol.primal_nofastpropagator_seq(basepath)
#sol.computeSteffensenMethod(basepath, folder_name)

for k in range(1, n+1):
    sweep_name=mysweep.format(k)
    for i in range(1, n+1):
        interval_name=myinterval.format(i)
        post.erasefiles(basepath, folder_name, sweep_name, interval_name)

################################################################


