# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 09:42:28 2023

@author: jcosson
"""
import os
import time
import config as c
import subprocess
from concurrent import futures

from config import primal_path, primitive_path, steffensen_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path;
from config import n, theta, T, a, t, deltaT, myinterval, mysweep, folder_name;
from src import solvers as sol, preprocessing as pre, postprocessing as post, boundary_conditions as bc
import sys
import shutil
import concurrent.futures

################                  PATH                     ################
c.headings()
################           CHOICE OF COMPUTATION           ################
#Primitive shooting :
basepath=primitive_path
os.chdir(basepath)
    
####################

#The big Solver
sol.primal_shooting_stef_update(basepath)

#Testing Primitive + Defect
#sol.primal_nofastpropagator_seq(basepath)
#for k in range(1, n+1):
#k=1
#sweep_name=mysweep.format(k)
#    sol.computeDefect(basepath, sweep_name, k)
#    sol.loop_linearisedPimpleDyMFoam(basepath, folder_name, sweep_name, k) #One sync version
#    sol.computeSteffensenMethod(basepath, folder_name) 
#sol.computeNewtonUpdate(basepath, folder_name, sweep_name, k)
#    post.erase_all_files(basepath, folder_name, k)