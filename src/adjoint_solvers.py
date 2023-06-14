# -*- coding: utf-8 -*-
"""
Created on Tue May 30 17:12:18 2023

@author: jcosson
"""
import os
import threading
import subprocess
import multiprocessing
import sys
import shutil
import time
from concurrent import futures
from functools import partial
from src import boundary_conditions as bc, preprocessing as pre, solvers as sol, postprocessing as post, adjoint_solvers as adsol
from config import primal_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, adjoint_path
from config import n, theta, T, a, deltaT, myinterval, mysweep, folder_name, maxCPU

#########################   ADJOINT SHOOTING    #########################
def adjointPimpleDyMFoam(folder_name, sweep_name, i):
    interval_name=myinterval.format(i)
    pimple_path=adjoint_path + folder_name + "/" + sweep_name + "/" + interval_name   
    os.chdir(pimple_path) #Entering logfile path
    os.system('adjointPimpleDyMFoam >adjoint_pimple.log 2>&1')                
    print("Adjoint computation of " + interval_name + " is done. Writing into pimple.log ...")
    os.chdir(adjoint_path) #back to main path
    return(0)
    
def loop_adjoint_pimpleDyMFoam(folder_name, sweep_name, k): #Version V1 : Parallel call for all intervals within one sweep
    start_time=time.time()
    print("\nStarting shooting of " + sweep_name + "\n")
    print("Starting ADJ EXECUTOR ... \n")
    with futures.ProcessPoolExecutor(max_workers=maxCPU) as executor:
        for i in range(n-k+1, 0, -1): #(n, k-1, -1)
            executor.submit(adjointPimpleDyMFoam, folder_name, sweep_name, i)
            print("Starting adjointPimpleDyMFoam for interval " + str(i))
        print("\n\nAll simulations started. Waiting... \n")
    print("ADJ EXECUTOR adjointPimpleDyMFoam terminated.\n\n")
    elapsed_time = time.time() - start_time
    os.chdir(adjoint_path)
    bc.timer_and_write(adjoint_path, elapsed_time, "adjointPimpleDyMFoam", sweep_name)
    post.prepareAdjointPostProcessing(adjoint_path, folder_name, sweep_name)
    post.computeAdjointPressureDropFoam(adjoint_path, folder_name, sweep_name)
    
#########################        LINEARIZATION        #########################

def adjointLinearisedPimpleDyMFoam(basepath, folder_name, sweep_name, i):
    #Executing linearisedPimpleDyMFoam for sweep k interval i
    interval_name=myinterval.format(i)
    lin_pimple_path=basepath + folder_name + "/" + sweep_name + "/" + interval_name
    os.chdir(lin_pimple_path)
    with open("adjoint_lin_logfile"+sweep_name+"_"+interval_name+".txt","w") as logfile:
        subprocess.run(['linearisedAdjointPimpleDyMFoam'], stdout=logfile, stderr=subprocess.STDOUT)
        #subprocess.run(['linearisedPimpleDyMFoam'])
    print("Adjoint linearisation of " + interval_name + " is done. Writing into lin_logfile ...")
    os.chdir(basepath) #back to main path

def loop_linearised_adjoint_pimpleDyMFoam(folder_name, sweep_name, k):  ###A TESTER SANS PARALEL    
    print("\nStarting adjoint linearisation of " + sweep_name + "\n")
    print("Starting LIN ADJ EXECUTOR ... \n")
    pre.prepareNextAdjointLinearization(adjoint_path, folder_name, k)
    start_time=time.time()
    with futures.ProcessPoolExecutor(max_workers=maxCPU) as executor:        
        for i in range(1, n+1):#k.essayer 2, on ne lin pas dans 1
            executor.submit(adjointLinearisedPimpleDyMFoam, adjoint_path, folder_name, sweep_name, i)
            print("Starting adjointLinearisedPimpleDyMFoam for interval " + str(i))
        print("\n\nAll Adjoint linearisations started, Waiting... \n")
    print("LIN ADJ EXECUTOR terminated \n\n")
    elapsed_time = time.time() - start_time
    bc.timer_and_write(adjoint_path, elapsed_time, "adjointLinearisedPimpleDyMFoam", sweep_name)

######################### UPDATE AND DEFECT #########################

def computeAdjointDefect(basepath, sweep_name, k):
    print("\nComputing Adjoint Defect ...")
    for i in range(n, 1, -1): # avant n-1 
        interval_name=myinterval.format(i-1)
        previous_interval=myinterval.format(i) #avant i-1 mais on va à l'envers
        pre.prepareAdjointDefectComputation(adjoint_path, sweep_name, interval_name, previous_interval, i)
        os.chdir(adjoint_path + folder_name + "/" + sweep_name + "/" + interval_name)
        with open("adjoint_shooting_defect_logfile"+sweep_name+"_"+interval_name+".txt","w") as logfile:
            os.chdir(adjoint_path + folder_name + "/" + sweep_name + "/" + interval_name + "/adjointShootingDefect")
            subprocess.run(['computeAdjointShootingDefect'], stdout=logfile, stderr=subprocess.STDOUT)        
    os.chdir(basepath)

def computeAdjointNewtonUpdate(basepath, sweep_name, i, k):
    interval_name=myinterval.format(i)
    pre.prepareAdjointNewtonUpdate(basepath, folder_name, sweep_name, k, interval_name, i)
    os.chdir(basepath + folder_name + "/" + sweep_name + "/" + interval_name)     
    with open("rel_adj_newton_update_logfile"+sweep_name+"_"+interval_name+".txt","w") as logfile:
        os.chdir(basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/adjointShootingUpdate")
        subprocess.run(['relaxedComputeAdjointNewtonUpdate'], stdout=logfile, stderr=subprocess.STDOUT)  #before : computeNewtonUpdate
    os.chdir(basepath)
    if i<n and k<n:
        post.prepareNextAdjointNewton(basepath, folder_name, sweep_name, k, interval_name, i)

def loop_computeAdjointNewtonUpdate(basepath, folder_name, sweep_name, k):
    print("\nComputing Adjoint Newton Update...")
    with futures.ProcessPoolExecutor(max_workers=maxCPU) as executor:
        for i in range(n-k+1, 0, -1): #déart à n au lieu de n-1
             executor.submit(computeAdjointNewtonUpdate, basepath, sweep_name, i, k)

##################     FUNCTIONS FOR MAIN EXECUTION     ###################

def computeAdjoint(basepath, event):
    # Wait for the signal from the first function
    event.wait()
    
    #Starting Timer for entire Process
    start_time=time.time()
    
    #Verify if folder_name exists, and offers to delete it if so
    bc.checking_existence(basepath, folder_name)
    print("Preparing files for adjoint computation...\n")
    
    #Preparing files for adjoint computation
    pre.initializeMyAdjoint(folder_name, "sweep1")
    print("done")
    #Initialization loop over all Sweeps    
    for k in range (1, n+1): #(1, n+1)
        sweep_name=mysweep.format(k)
        
        #Computing Adjoint Pimple
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
        
        if k<n:
            pre.prepareMyNextAdjointSweep(basepath, k, folder_name)
            
            #Renaming Time folder with "-"
            next_sweep_name=mysweep.format(k+1)
            pre.prepareTimeFolders(folder_name, next_sweep_name, k)
            
        #Stopping intermediate timer and writing into logfile
        elapsed_time = time.time() - start_time
        bc.timer_and_write(basepath, elapsed_time, "adjoint_subintervals", sweep_name) #### mettre adjoint
       
    #Final Timer
    elapsed_time = time.time() - start_time        
    bc.timer_and_write(basepath, elapsed_time, "adjoint computation", folder_name)
    post.store_all_adjoint_values(basepath, folder_name)


### NOT WORKING YET
#def combined_shooting_stef_update():
#    basepath=primal_path
#    #Verify if primal folder_name exists, and offers to delete it if so
#    bc.checking_existence(primal_path, folder_name)
#    #Verify if adjoint folder_name exists, and offers to delete it if so
#    bc.checking_existence(adjoint_path, folder_name)
#    #Starting Timer for entire Process
#    start_time_ALL=time.time()
#    #Initilisation for Sweep1
#    bc.sweep_1_initialization(basepath, folder_name) #One sync version
#    # STARTING MAIN LOOP
#    for k in range(1, n+1):
#    ######################    
#        #Intermediate counter start
#        start_time=time.time()
#        #Naming current sweep
#        sweep_name = mysweep.format(k)
#        #Starting primitive Shooting in Sweep k over all subintervals
#        sol.loop_pimpleDyMFoam(basepath, folder_name, sweep_name, k) #One sync version        
#        #Newline for defect
#        sol.loop_computeDefect(basepath, sweep_name, k)
#        #Starting linearisation for Sweep k over all subintervals
#        sol.loop_linearisedPimpleDyMFoam(basepath, folder_name, sweep_name, k) #One sync version
#        #Starting Newton Update
#        sol.loop_computeNewtonUpdate(basepath, folder_name, sweep_name, k)
#        ###### Adjoint
#        start_time=time.time()
#        basepath=adjoint_path
#        sweep_name=mysweep.format(k)
#        #Renaming Time folder with "-"
#        pre.prepareTimeFolders(folder_name, sweep_name)
#        #Preparing files for adjoint computation
#        if sweep_name=="sweep1":
#            pre.initializeMyAdjoint(folder_name, sweep_name)
#        sweep_name=mysweep.format(k)
#        loop_adjoint_pimpleDyMFoam(folder_name, sweep_name, k)
#        #Computing Adjoint Defect
#        print("\nADJOINT DEFECT...\n")
#        computeAdjointDefect(adjoint_path, sweep_name, k)
#        #Computing Adjoint Linearization
#        print("\nADJOINT LINEARIZATION...\n")
#        loop_linearised_adjoint_pimpleDyMFoam(folder_name, sweep_name, k)
#        #Starting Adjoint Newton Update
#        loop_computeAdjointNewtonUpdate(basepath, folder_name, sweep_name, k)
#        ###############
#        basepath=primal_path
#        erasing="no"
#        # Deleting Files after Sweep k Done    
#        if erasing=="yes":
#            print("Deleting files...\n")
#            post.erase_all_files(basepath, folder_name, k)
#            print("The files were succefully deleted. See exceptions above.")
#        
#        #Stopping intermediate timer and writing into logfile
#        elapsed_time = time.time() - start_time
#        bc.timer_and_write(basepath, elapsed_time, "subintervals", sweep_name)  
#    print("Steffensen's Method terminated. Sweep " + str(k) + " updated.")
#    #Stopping timer and writing into logfile
#    total_time=time.time()-start_time_ALL
#    bc.timer_and_write(basepath, total_time, folder_name, sweep_name)
#    post.store_all_values(basepath, folder_name)