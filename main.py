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

#def primal_shooting_stef_update(basepath):
#    
#    #Implementing counters    
#    #g=1
#    countershooting=1
#    
#    #Verify if folder_name exists, and offers to delete it if so
#    bc.checking_existence(folder_name)
#    
#    #Starting Timer for entire Process
#    start_time_ALL=time.time()
#    
#    #Initilisation for Sweep1
#    bc.sweep_1_initialization(basepath, folder_name)
#
#    # STARTING MAIN LOOP
#    for k in range(1, n+1):
#    ######################    
#
#        #Intermediate counter start
#        start_time=time.time()
#        #Naming current sweep
#        sweep_name = mysweep.format(k)
#
#        #Starting primitive Shooting in Sweep k over all subintervals
#        sol.loop_pimpleDyMFoam(basepath, folder_name, sweep_name, k)
#
#        #Stopping intermediate timer and writing into logfile
#        elapsed_time = time.time() - start_time
#        bc.timer_and_write(elapsed_time, "pimpleDyMFoam", sweep_name)
#
#        #Starting intermediate timer
#        lin_time=time.time()
#
#        #Starting linearisation for Sweep k over all subintervals
#        sol.loop_linearisedPimpleDyMFoam(basepath, folder_name, sweep_name, k)
#
#        #Stopping intermediate timer and writing into logfile
#        elapsed_time = time.time() - lin_time
#        bc.timer_and_write(elapsed_time, "linearisedPimpleDyMFoam", sweep_name)
#
#        #Implementing counter for shooting update
#        countershooting=countershooting+1
#
#        #Intricated for-loop for shooting update, over all subintervals (i), but depending on sweep
#        if not k==n-1:        
#            for i, j in zip(range(2, n+1),range(countershooting, n+n)):
#             post.the_shooting_update_for_all(sweep_name, k, i, j)
#
#        # Deleting Files after Sweep k Done        
#        #ans=input("Do you want to delete useless files? (Y/N)     \n   \n")
#        #if ans=="Y" or ans=="y":
#        print("Deleting files...\n")
#        post.erase_all_files(basepath, folder_name, k)
#                
#        #Stopping intermediate timer and writing into logfile
#        elapsed_time = time.time() - start_time        
#        bc.timer_and_write(elapsed_time, sweep_name, sweep_name)
#        
#    print("Steffensen's Method terminated. Sweep " + str(k) + " updated.")
#    #Delete 2 last dirs:
#    if k==n:
#        try:
#            for k in range(n-1, n+1):
#                sweep_name=mysweep.format(k)
#                for i in range(1, n+1):
#                    interval_name=myinterval.format(i)
#                    path_files=basepath+folder_name+"/"+sweep_name+"/"+interval_name
#                    post.erasefiles(path_files)
#        except:
#            print("Problem deleting last files.")
#    
#    #Stopping timer and writing into logfile
#    total_time=time.time()-start_time_ALL
#    bc.timer_and_write(total_time, folder_name, sweep_name)
    
####################

sol.primal_shooting_stef_update(basepath)
