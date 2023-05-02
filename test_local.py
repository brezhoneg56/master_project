# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 09:42:28 2023

@author: jcosson
"""
## $pvd . a quoi sert cette commande?
#os.system("cp -r /home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/undeformed_turbulent/constant /home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/moderate_deformed/primal/four_intervals/sweep1")
import os
from src import solvers as sol, preprocessing as prep
import shutil
import sys
######### PATHS ##########################
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#PRIMAL PATHS
primal_path="D:/Users/Lucie/Documents/OneDrive - Helmut-Schmidt-Universität/HSU/Year 4/Master_WT23_FT23/master_project/"
primitive_path="D:/Users/Lucie/Documents/OneDrive - Helmut-Schmidt-Universität/HSU/Year 4/Master_WT23_FT23/master_project/local_test"
steffensen_path="D:/Users/Lucie/Documents/OneDrive - Helmut-Schmidt-Universität/HSU/Year 4/Master_WT23_FT23/master_project/"
#CALCS PATHS
calcs_undeformed="D:/Users/Lucie/Documents/OneDrive - Helmut-Schmidt-Universität/HSU/Year 4/Master_WT23_FT23/master_project/"
#REFERENCE PATHS
ref_cases="D:/Users/Lucie/Documents/OneDrive - Helmut-Schmidt-Universität/HSU/Year 4/Master_WT23_FT23/master_project/"
ref_cases_mod_def="D:/Users/Lucie/Documents/OneDrive - Helmut-Schmidt-Universität/HSU/Year 4/Master_WT23_FT23/master_project/"
#MY PROJECTS PATHS
project_path="D:/Users/Lucie/Documents/OneDrive - Helmut-Schmidt-Universität/HSU/Year 4/Master_WT23_FT23/master_project/"
# CHOOSE YOUR BASE WORKING PATH
basepath=primitive_path
os.chdir(basepath)
################################        INITIALIZATION      ################################
#folder_name=input("Name your folder: ")

#folder_name="deux_intervals"
n=4; #Amount of sweeps / shooting intervals
theta=0.4; #Starting time in seconds
T=0.1; #Length of one period
a=4; #Amount of sweeps in the first loop
deltaT=T/n
myinterval="interval{}"
mysweep="sweep{}"

#def get_var():
#    return n, steffensen_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, basepath, theta, T, a, deltaT, myinterval, mysweep, primitive_path, primal_path

# After testing is done, please uncomment the following
#n=int(input("Set the number of shooting intervals: "));
#theta=input("Define the starting time (example: 0.4): ");
################################        COMPUTE MY SWEEPs : sweep k in [1-n]       ################################
folder_name="4_intervals_parallel"
if os.path.exists(folder_name):
    shutil.rmtree(folder_name)
#Primitive shooting : works
#sol.primal_nofastpropagator_seq()

#Steffensen shooting : ongoing


#os.chdir(steffensen_path)

#prep.prepareSteffensen(n, theta, folder_name, steffensen_path, primitive_path, ref_cases)