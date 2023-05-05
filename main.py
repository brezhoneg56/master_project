# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 09:42:28 2023

@author: jcosson
"""
## $pvd . a quoi sert cette commande?
#os.system("cp -r /home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/undeformed_turbulent/constant /home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/moderate_deformed/primal/four_intervals/sweep1")
import os
from config import primal_path, primitive_path, steffensen_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, basepath;
from config import n, theta, T, a, t, deltaT, myinterval, mysweep;
from src import solvers as sol, preprocessing as pre, postprocessing as post
import shutil
######### PATHS ##########################
os.chdir(basepath)
################################        COMPUTE MY SWEEPs : sweep k in [1-n]       ################################
#AUTOMATIC FILE DELETION/CREATIION
folder_name="5_intervals"

####uncomment################################################################################################
if os.path.exists(folder_name):
    shutil.rmtree(folder_name)
    print("Previous directory named "+folder_name+" has been replaced.")
############################################################################################################
#Primitive shooting : WOrks
#sol.primal_nofastpropagator_seq()
#Steffensen shooting : ongoing
os.chdir(steffensen_path)
sol.computeSteffensenMethod(folder_name)

#############     FUNCTION     #################################################################################################
