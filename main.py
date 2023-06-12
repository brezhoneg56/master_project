# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 09:42:28 2023

@author: jcosson
"""
import os
import re
import time
import config as c
import subprocess
from concurrent import futures
import csv
from config import primal_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, adjoint_path;
from config import n, theta, T, a, t, deltaT, myinterval, mysweep, folder_name, maxCPU;
from src import solvers as sol, preprocessing as pre, postprocessing as post, boundary_conditions as bc, adjoint_solvers as adsol
import sys
import shutil
import concurrent.futures

################                  PATH                     ################
c.headings()
################           CHOICE OF COMPUTATION           ################

#sol.the_shooting_manager()
def computeAdjoint(basepath):
    #Starting Timer for entire Process
    start_time=time.time()
    
    #Verify if folder_name exists, and offers to delete it if so
    bc.checking_existence(basepath, folder_name)
    print("Preparing files for adjoint computation...\n")
    
    #Preparing files for adjoint computation
    #pre.prepareTimeFolders(folder_name, "sweep1", 1) # NE FONCTIONNE PLUS EN INIT, RAJOUTE À INITALIZE
    pre.initializeMyAdjoint(folder_name, "sweep1")
    print("done")
    #Initialization loop over all Sweeps    
    for k in range (1, n+1):
        sweep_name=mysweep.format(k)
    
        sweep_name=mysweep.format(k)
        adsol.loop_adjoint_pimpleDyMFoam(folder_name, sweep_name, k)
        
        #Intermediate Timer
        elapsed_time = time.time() - start_time        
        bc.timer_and_write(basepath, elapsed_time, sweep_name, "adjoint folder")
        
        #Computing Adjoint Defect
        print("\nADJOINT DEFECT...\n")
        adsol.computeAdjointDefect(adjoint_path, sweep_name, k)
        
        #Computing Adjoint Linearization
        print("\nADJOINT LINEARIZATION...\n")
        adsol.loop_linearised_adjoint_pimpleDyMFoam(folder_name, sweep_name, k)
        
        #Starting Adjoint Newton Update
        adsol.loop_computeAdjointNewtonUpdate(basepath, folder_name, sweep_name, k)
        
        if k<n: #A FAIRE !!!
            pre.prepareMyNextAdjointSweep(basepath, k, folder_name)
            #Renaming Time folder with "-"
            sweep_name=mysweep.format(k+1)
            pre.prepareTimeFolders(folder_name, sweep_name, k)
       
    #Final Timer
    elapsed_time = time.time() - start_time        
    bc.timer_and_write(basepath, elapsed_time, "adjointPimpleDyMFoam", folder_name)

computeAdjoint(adjoint_path)
#k=1
##Renaming Time folder with "-"
#
#        
#if k<n: #A FAIRE !!!
#    pre.prepareMyNextAdjointSweep(adjoint_path, k, folder_name)
#    sweep_name=mysweep.format(k+1)
#    pre.prepareTimeFolders(folder_name, sweep_name, k)
#k=2
#sweep_name=mysweep.format(k)
#os.chdir(adjoint_path)
#adsol.loop_adjoint_pimpleDyMFoam(folder_name, sweep_name, k)


