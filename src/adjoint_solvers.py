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
            os.chdir(adjoint_path + folder_name + "/" + sweep_name + "/" + interval_name + "/adjointShootingDefect/")
            subprocess.run(['computeAdjointShootingDefect'], stdout=logfile, stderr=subprocess.STDOUT)        
    os.chdir(basepath)

def computeAdjointNewtonUpdate(basepath, sweep_name, i, k):
    interval_name=myinterval.format(i)
    pre.prepareAdjointNewtonUpdate(basepath, folder_name, sweep_name, k, interval_name, i)
    os.chdir(basepath + folder_name + "/" + sweep_name + "/" + interval_name)     
    with open("rel_adj_newton_update_logfile"+sweep_name+"_"+interval_name+".txt","w") as logfile:
        os.chdir(basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/adjointShootingUpdate")
        subprocess.run(['adjointRelaxedComputeNewtonUpdate'], stdout=logfile, stderr=subprocess.STDOUT)  #before : computeNewtonUpdate
    os.chdir(basepath)
    

def loop_computeAdjointNewtonUpdate(basepath, folder_name, sweep_name, k):
    start_time_ad_pimple=time.time()
    print("\nComputing Adjoint Newton Update...")
    with futures.ProcessPoolExecutor(max_workers=maxCPU) as executor:
        for i in range(n-k, 0, -1): #déart à n au lieu de n-1
            executor.submit(computeAdjointNewtonUpdate, basepath, sweep_name, i, k)
            # FileNotFoundError: [Errno 2] No such file or directory: '/home/jcosson/workspace/henersj_shootingdata/calcs/moderate_deformed/adjoint/9_intervals_adjoint_10-07/sweep1/interval8/-0.489/linUaf'
        #computeAdjointNewtonUpdate(basepath, sweep_name, i, k)
    #with futures.ProcessPoolExecutor(max_workers=maxCPU) as executor:
        for i in range(n, 0, -1):
            interval_name=myinterval.format(i)
            if k<n:
                #post.prepareNextAdjointNewton(basepath, folder_name, sweep_name, k, interval_name, i) # Dynamic Solution
                #executor.submit(post.prepare_adjoint_fixed_primal, basepath, folder_name, sweep_name, k, interval_name, i) #Fixed solution
                post.prepare_adjoint_fixed_primal(basepath, folder_name, sweep_name, k, interval_name, i)
        for i in range(n-k, 1, -1):
            interval_name=myinterval.format(i)
            if k<n:
                post.prepare_adjoint_state_variables(basepath, folder_name, sweep_name, k, interval_name, i)
    #Intermediate Timer
    elapsed_time = time.time() - start_time_ad_pimple      
    bc.timer_and_write(basepath, elapsed_time, sweep_name, "adjoint folder")
##################     FUNCTIONS FOR MAIN EXECUTION     ###################

def computeAdjoint(basepath, erasing, event):
    # Wait for the signal from the first function
    #event.wait()
    
    #Starting Timer for entire Process
    start_time_ALL=time.time()
    
    #Verify if folder_name exists, and offers to delete it if so
    bc.checking_existence(basepath, folder_name)
    print("Preparing files for adjoint computation...\n")
    
    #Preparing files for adjoint computation
    pre.initializeMyAdjoint(folder_name, "sweep1")
    print("done")
    deletion_counter=-1
    #Initialization loop over all Sweeps    
    for k in range (1, n+1): #(1, n+1)
        start_time=time.time()
        sweep_name=mysweep.format(k)
        
        #Computing Adjoint Pimple
        adsol.loop_adjoint_pimpleDyMFoam(folder_name, sweep_name, k)
        
        ##Intermediate Timer
        #elapsed_time = time.time() - start_time        
        #bc.timer_and_write(basepath, elapsed_time, sweep_name, "adjoint folder")
        
        #Computing Adjoint Defect
        print("\nADJOINT DEFECT...\n")
        adsol.computeAdjointDefect(adjoint_path, sweep_name, k)
        
        #Computing Adjoint Linearization
        print("\nADJOINT LINEARIZATION...\n")
        adsol.loop_linearised_adjoint_pimpleDyMFoam(folder_name, sweep_name, k)
        
        #Starting Adjoint Newton Update AND PREPARING NEXT SWEEP
        adsol.loop_computeAdjointNewtonUpdate(adjoint_path, folder_name, sweep_name, k)
        
        # Deleting Files after Sweep k Done
        if erasing=="yes":
            if (deletion_counter>0):
                print("Deleting files...\n")
                #post.erase_all_adjoint_files(basepath, folder_name, k)
                #post.erase_primal_adjoint_files(primal_path, adjoint_path, folder_name, k)
                post.erase_all_files(primal_path, folder_name, k)
                post.erase_all_adjoint_files(adjoint_path, folder_name, k)
                print("The files for " + mysweep.format(deletion_counter)+ " in primal_path were succefully deleted. See exceptions above.")
        deletion_counter+=1         
        
        
        
        #Stopping intermediate timer and writing into logfile
        elapsed_time = time.time() - start_time
        bc.timer_and_write(basepath, elapsed_time, "adjoint_subintervals", sweep_name) #### mettre adjoint
        os.chdir(basepath + folder_name + "/")
        with open("pressureDropvalues.txt","a") as mapression:
            mapression.write("\n\nAdjoint shooting of " + sweep_name + ":\n---------------------------------\n" )
        mapression.close() 
       
    #Final Timer
    elapsed_time = time.time() - start_time_ALL       
    bc.timer_and_write(basepath, elapsed_time, "adjoint computation", folder_name)
    post.store_all_adjoint_values(basepath, folder_name)