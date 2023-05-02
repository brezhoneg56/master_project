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
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.chdir(basepath)
################################        INITIALIZATION      ################################
#def get_var():
#    return n, steffensen_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, basepath, theta, T, a, deltaT, myinterval, mysweep, primitive_path, primal_path

################################        COMPUTE MY SWEEPs : sweep k in [1-n]       ################################
folder_name="4_intervals_parallel"
if os.path.exists(folder_name):
    shutil.rmtree(folder_name)
#Primitive shooting : works
sol.primal_nofastpropagator_seq()

#Steffensen shooting : ongoing
print(primal_path+primitive_path+steffensen_path+calcs_undeformed+ref_cases+ref_cases_mod_def+project_path+basepath)


#os.chdir(steffensen_path)

#prep.prepareSteffensen(n, theta, folder_name, steffensen_path, primitive_path, ref_cases)