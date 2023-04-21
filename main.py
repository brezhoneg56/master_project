# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 09:42:28 2023

@author: jcosson
"""
## $pvd . a quoi sert cette commande?
#os.system("cp -r /home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/undeformed_turbulent/constant /home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/moderate_deformed/primal/four_intervals/sweep1")
import os
from src import solvers as sol
######### PATHS ########################## 
basepath="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/moderate_deformed/primal/primitive_shooting/"
calcs_undeformed="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/undeformed_turbulent/"
ref_cases_mod_def="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/reference_cases/moderate_deformed_SDuct/"
project_path="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/scripts/master_project/"
os.chdir(basepath)
################################        INITIALIZATION      ################################
#folder_name=input("Name your folder: ")

#folder_name="deux_intervals"
n=5; #Amount of sweeps / shooting intervals
theta=0.4; #Starting time in seconds
T=0.1; #Length of one period
a=5; #Amount of sweeps in the first loop
myinterval="interval{}"
mysweep="sweep{}"
# After testing is done, please uncomment the following
#n=int(input("Set the number of shooting intervals: "));
#theta=input("Define the starting time (example: 0.4): ");

################################        COMPUTE MY SWEEPs : sweep k in [1-n]       ################################

sol.computeEverything(basepath, n, T, theta, a)