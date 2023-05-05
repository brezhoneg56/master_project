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
import sys
######### PATHS ##########################
os.chdir(basepath)
################################        COMPUTE MY SWEEPs : sweep k in [1-n]       ################################
#AUTOMATIC FILE DELETION/CREATIION
folder_name="5_intervals"

####uncomment################################################################################################
#if os.path.exists(folder_name):
#    shutil.rmtree(folder_name)
#    print("Previous directory named "+folder_name+" has been replaced.")
############################################################################################################
#Primitive shooting : WOrks
#sol.primal_nofastpropagator_seq()
#Steffensen shooting : ongoing
os.chdir(steffensen_path)
#sol.computeSteffensenMethod(folder_name)

#############     FUNCTION     #################################################################################################
#Initialisation of Sweep 1  
#sweep_name="sweep1"
#pre.initializeLinearisation(folder_name, sweep_name) ##WORKS
#for k in range (1, n+1):
k=1
sweep_name=mysweep.format(k)
#print("\n\nStarting linearisation process for "+sweep_name+".\n")
#for i in range (1, n+1):
#    interval_name=myinterval.format(i)  
#    print("\nlinearisedPimpleDyMFoam\n" )
#    sol.linearisedPimpleDyMFoam(folder_name, sweep_name, i)
#    print("Done\n")
#    print("prepareNextLinearization\n")
#    pre.prepareNextLinearization(folder_name, k, i)
#    print("Linearisation Preparation Done\n")


i=2
print("Starting shooting update process for "+sweep_name+".\n")
#for i in range(2, n+1):
interval_name=myinterval.format(i)
print("prepareShootingUpdate\n")
    
pre.prepareShootingUpdate(folder_name, sweep_name, k, i)
print("Shooting Preparation Done")

i=1
interval_name=myinterval.format(i)

sol.computeShootingUpdate(folder_name, sweep_name, interval_name)
post.shootingUpdateP(folder_name, sweep_name, interval_name, k, i)
print("Shooting Updated.\n")

######################################################################################################################################

#for i in range (1, n+1):
#    interval_name=myinterval.format(i)
#    print("\nlinearisedPimpleDyMFoam\n")
#    sol.linearisedPimpleDyMFoam(folder_name, sweep_name, i)
#    print("Done\n")
#    print("prepareNextLinearization\n")
#    pre.prepareNextLinearization(folder_name, k, i)
#    print("Done\n")
#for i in range (2,n+1):
#    print("Starting shooting update process for "+sweep_name+".\n")
#    #for i in range(2, n+1):
#    interval_name=myinterval.format(i)
#    print("prepareShootingUpdate\n")
#        
#    pre.prepareShootingUpdate(folder_name, sweep_name, k, i)
#    print("Done")
#    sol.computeShootingUpdate(folder_name, sweep_name, interval_name)
#    post.shootingUpdateP(folder_name, sweep_name, interval_name, k, i, "shootingUpdateP")
#    print("Shooting Updated.\n")
#####################################################################################################