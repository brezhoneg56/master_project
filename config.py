# -*- coding: utf-8 -*-
"""
Created on Tue May  2 12:10:07 2023

@author: Lucie
"""

####### CONFIG FILE ########
# Here, you can adapt the different paths to your structure.

#PRIMAL PATHS
primal_path="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/moderate_deformed/primal/"
primitive_path="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/moderate_deformed/primal/primitive_shooting/"
steffensen_path="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/moderate_deformed/primal/steffenssens_method/"
#CALCS PATHS
calcs_undeformed="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/undeformed_turbulent/"
#REFERENCE PATHS
ref_cases="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/reference_cases/"
ref_cases_mod_def="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/reference_cases/moderate_deformed_SDuct/"
#MY PROJECTS PATHS
project_path="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/scripts/master_project/"
# CHOOSE YOUR BASE WORKING PATH
basepath=primitive_path

## VARIABLES
# After testing is done, please uncomment the following
#n=int(input("Set the number of shooting intervals: "));
#theta=input("Define the starting time (example: 0.4): ");
n=4; #Amount of sweeps / shooting intervals
theta=0.4; #Starting time in seconds
T=0.1; #Length of one period
a=4; #Amount of sweeps in the first loop
deltaT=T/n
myinterval="interval{}"
mysweep="sweep{}"