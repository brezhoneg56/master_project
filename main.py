# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 09:42:28 2023

@author: jcosson
"""
## $pvd . a quoi sert cette commande?
#os.system("cp -r /home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/undeformed_turbulent/constant /home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/moderate_deformed/primal/four_intervals/sweep1")
import os
from src import boundary_conditions as bc, preprocessing as pre, solvers as sol, postprocessing as post
######### PATHS ########################## 
basepath="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/moderate_deformed/primal/"
calcs_undeformed="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/undeformed_turbulent/"
ref_cases_mod_def="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/reference_cases/moderate_deformed_SDuct/"
project_path="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/scripts/master_project/"
os.chdir(basepath)
################################        INITIALIZATION      ################################
#folder_name=input("Name your folder: ")

#folder_name="deux_intervals"
n=3;
theta=0.4;
T=0.1;

myinterval="interval{}"
mysweep="sweep{}"
# After testing is done, please uncomment the following
#n=int(input("Set the number of shooting intervals: "));
#theta=input("Define the starting time (example: 0.4): ");

################################        COMPUTE MY SWEEPs : sweep k in [1-n]       ################################

sol.computeEverything(basepath, n, T, theta)