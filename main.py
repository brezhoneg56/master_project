# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 09:42:28 2023

@author: jcosson
"""
## $pvd . a quoi sert cette commande?
#os.system("cp -r /home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/undeformed_turbulent/constant /home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/moderate_deformed/primal/four_intervals/sweep1")
import os
from config import primal_path, primitive_path, steffensen_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, basepath
from config import n, theta, T, a, deltaT, myinterval, mysweep
from src import solvers as sol, preprocessing as prep
import shutil
import sys
######### PATHS ##########################
os.chdir(basepath)
################################        COMPUTE MY SWEEPs : sweep k in [1-n]       ################################
#AUTOMATIC FILE DELETION/CREATIION
folder_name="4_intervals_parallel"
if os.path.exists(folder_name):
    shutil.rmtree(folder_name)

#Primitive shooting : WOrks
#sol.primal_nofastpropagator_seq()
k=1
#Steffensen shooting : ongoing
os.chdir(steffensen_path)
sweep_name="sweep1"
interval_name="interval1"
prep.prepareLinearization(folder_name, sweep_name, interval_name,k)
#prep.prepareSteffensen(n, theta, folder_name, steffensen_path, primitive_path, ref_cases)