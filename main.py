# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 09:42:28 2023

@author: jcosson
"""
import os
import time
import config as c
import subprocess
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

def primal_shooting_stef_update(basepath):
    g=1
#Function:
    if os.path.exists(folder_name):
            ans=input("WARNING: Directory " + folder_name + " already exists. Do you want to replace it ? (Y/N)     \n   \n")
            if ans=="Y" or ans=="y":
                for g in range(1, n + 1):
                    if os.path.exists("sweep" + str(g)):
                        shutil.rmtree("sweep" + str(g))
                shutil.rmtree(folder_name)
                #os.mkdir(folder_name)
            else:
                sys.exit()

    start_time_ALL=time.time()
    bc.sweep_1_initialization(basepath, folder_name)
    for k in range(1, n+1):
        start_time=time.perf_counter()
        sweep_name = mysweep.format(k)
        sol.loop_pimpleDyMFoam(basepath, folder_name, sweep_name, k)
        
##Function:
        if k==1:
            pre.initializeLinearisation(basepath, folder_name, sweep_name)

        sol.loop_linearisedPimpleDyMFoam(basepath, folder_name, sweep_name, k)

        g=g+1
        print("g="+str(g))
        for i, j in range ((2, n+1),(g, n+1)):
            sweep_name=mysweep.format(k)
            #if not k==n:
            m=1 #Counter for Shooting update is always i-1
            print("Starting shooting update process for " + sweep_name + ".\n")
            #for i in range(2, n + 1):
            interval_name=myinterval.format(i)
            pre.prepareShootingUpdate(basepath, folder_name, sweep_name, k, j)
            interval_name=myinterval.format(m)
            #if k>1:
            sol.computeShootingUpdate(basepath, folder_name, k, interval_name)
            post.shootingUpdateP(basepath, folder_name, sweep_name, interval_name, k, m)
            m=m+1 #Counter for Shooting Update



        if k==n-1:
            print("Steffensen's Method terminated. Sweep " + str(k) + " updated.")
            return(0)
        #post.erase_all_files(basepath, folder_name, g)
        end_time = time.time()
        elapsed_time = end_time - start_time
        num_minutes=int(elapsed_time/3600)
        num_seconds=elapsed_time%3600
        print("Elapsed time:", elapsed_time, "seconds")
    end_time = time.time()
    total_time=end_time-start_time_ALL
    num_minutes=int(total_time/60)
    num_seconds=total_time%60
    print("Elapsed time:", elapsed_time, "seconds")

primal_shooting_stef_update(basepath)