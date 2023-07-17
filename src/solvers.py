# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 10:27:15 2023

@author: jcosson
"""
import os
import csv
import re
import threading
import subprocess
import multiprocessing
import sys
import shutil
import time
from concurrent import futures
from functools import partial
from src import boundary_conditions as bc, preprocessing as pre, solvers as sol, adjoint_solvers as adsol,  postprocessing as post
from config import primal_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, adjoint_path
from config import n, theta, T, a, deltaT, myinterval, mysweep, folder_name, maxCPU
###########################################################################

#########################   PRIMITIVE SHOOTING    #########################
def pimpleDyMFoam(basepath, folder_name, sweep_name, i):
    interval_name=myinterval.format(i)
    pimple_path=basepath + folder_name + "/" + sweep_name + "/" + interval_name   
    os.chdir(pimple_path) #Entering logfile path
    os.system('pimpleDyMFoam >pimple.log 2>&1')                
    print("Computation of " + interval_name + " is done. Writing into pimple.log ...")
    os.chdir(basepath) #back to main path
    return(0)

def loop_pimpleDyMFoam(basepath, folder_name, sweep_name, k): #Version V1 : Parallel call for all intervals within one sweep
    print("\nStarting shooting of " + sweep_name + "\n")
    print("Starting EXECUTOR ... \n")
    timer_pimpleDyMFoam= time.time()
    with futures.ProcessPoolExecutor(max_workers=maxCPU) as executor:
        for i in range(k, n+1):
            executor.submit(sol.pimpleDyMFoam, basepath, folder_name, sweep_name, i)
            print("Starting pimpleDyMFoam for interval " + str(i))
        print("\n\nAll simulations started. Waiting... \n")
    print("EXECUTOR pimpleDyMFoam terminated.\n\n")
    
    os.chdir(basepath + folder_name + "/")
    with open("pressureDropvalues.txt","a") as mapression:
        mapression.write("\n\nShooting of " + sweep_name + ":\n---------------------------------\n" )
    mapression.close()    
    
    #Stop Timer and write in logfile
    elapsed_time = time.time() - timer_pimpleDyMFoam
    #timer_pimple.append(elapsed_time)
    bc.timer_and_write(basepath, elapsed_time, "pimpleDyMFoam", sweep_name)
    
    post.preparePostProcessing(basepath, folder_name, sweep_name)
    post.computePressureDropFoam(basepath, folder_name, sweep_name)
    #os.chdir(basepath + folder_name)
    #with open("logtable.csv", 'a', newline='') as tab:
            #writer = csv.writer(tab)
            #writer.writerow([str(k), elapsed_time, (re.findall(r"[-+]?\d*\.\d+|\d+", post.computePressureDropFoam(basepath, folder_name, sweep_name)))])
    if k<n:
        pre.prepareMyNextSweep(basepath, k, folder_name)

#########################        LINEARIZATION        #########################

def linearisedPimpleDyMFoam(basepath, folder_name, sweep_name, i):
    #Executing linearisedPimpleDyMFoam for sweep k interval i
    interval_name=myinterval.format(i)
    lin_pimple_path=basepath + folder_name + "/" + sweep_name + "/" + interval_name
    os.chdir(lin_pimple_path)
    with open("lin_logfile"+sweep_name+"_"+interval_name+".txt","w") as logfile:
        subprocess.run(['linearisedPimpleDyMFoam'], stdout=logfile, stderr=subprocess.STDOUT)
    print("Linearisation of " + interval_name + " is done. Writing into lin_logfile ...")
    os.chdir(basepath) #back to main path

def loop_linearisedPimpleDyMFoam(basepath, folder_name, sweep_name, k):
    #Version V1 : Parallel call for all intervals within one sweep
    lin_time=time.time()
    print("\nStarting linearisation of " + sweep_name + "\n")
    print("Starting LIN EXECUTOR ... \n")
    
    for i in range(k+1, n+1):
        pre.prepareNextLinearization(basepath, folder_name, k, i)
    with futures.ProcessPoolExecutor(max_workers=maxCPU) as executor:        
        for i in range(k+1, n+1):#k.essayer 2, on ne lin pas dans 1
            executor.submit(linearisedPimpleDyMFoam, basepath, folder_name, sweep_name, i)
            print("Starting linearisedPimpleDyMFoam for interval " + str(i))
        
        print("\n\nAll Linearisations started, Waiting... \n")
    os.chdir(basepath + folder_name + "/")
    #Stopping intermediate timer and writing into logfile
    elapsed_time = time.time() - lin_time
    bc.timer_and_write(basepath, elapsed_time, "linearisedPimpleDyMFoam", sweep_name)
    print("LIN EXECUTOR terminated \n\n") 

######################### UPDATE AND DEFECT #########################

def computeShootingUpdate(basepath, folder_name, g, i):
    sweep_name=mysweep.format(g)
    interval_name=myinterval.format(i)
    
    # Calls compute shootingupdate from openfoam
    if not os.path.exists(basepath + folder_name + "/" + sweep_name + "/preProcessing/"):
        os.mkdir(basepath + folder_name + "/" + sweep_name + "/preProcessing/")
    os.chdir(basepath + folder_name + "/" + sweep_name + "/preProcessing/")
    with open("shooting_update_logfile"+sweep_name+"_"+interval_name+".txt","w") as logfile:
        subprocess.run(['computeShootingUpdate'], stdout=logfile, stderr=subprocess.STDOUT)

def computeDefect(basepath, sweep_name, k, i):
    interval_name=myinterval.format(i)
    previous_interval=myinterval.format(i-1)
    pre.prepareDefectComputation(basepath, sweep_name, interval_name, previous_interval, i)
    os.chdir(basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingDefect")
    with open("shooting_defect_logfile"+sweep_name+"_"+interval_name+".txt","w") as logfile:
        subprocess.run(['computeShootingDefect'], stdout=logfile, stderr=subprocess.STDOUT)        

def loop_computeDefect(basepath, sweep_name, k):
    print("\nComputing Defect ...")
    with futures.ProcessPoolExecutor(max_workers=maxCPU) as executor:
        for i in range(2, n+1): #2, n+1
            executor.submit(computeDefect, basepath, sweep_name, k, i)
    os.chdir(basepath)

def computeNewtonUpdate(basepath, sweep_name, i, k):
    interval_name=myinterval.format(i)
    pre.prepareNewtonUpdate(basepath, folder_name, sweep_name, k, interval_name, i)
    os.chdir(basepath + folder_name + "/" + sweep_name + "/" + interval_name)     
    with open("rel_newton_update_logfile"+sweep_name+"_"+interval_name+".txt","w") as logfile:
        os.chdir(basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingUpdate")
        subprocess.run(['relaxedComputeNewtonUpdate'], stdout=logfile, stderr=subprocess.STDOUT)  #before : computeNewtonUpdate
    os.chdir(basepath)
    if i<n and k<n:
        post.prepareNextNewton(basepath, folder_name, sweep_name, k, interval_name, i)

def loop_computeNewtonUpdate(basepath, folder_name, sweep_name, k):
    print("\nComputing Newton Update...")
    with futures.ProcessPoolExecutor(max_workers=maxCPU) as executor:
        for i in range(k+2, n+1): #depart à 2
             executor.submit(computeNewtonUpdate, basepath, sweep_name, i, k)


##################     FUNCTIONS FOR MAIN EXECUTION     ###################

def OLDprimal_nofastpropagator_seq(basepath): #change name (eg primal or adjoint + shooting method) primal_nofastpropagator_steffensen
    #Strating Timer
    start_time=time.time()
    
    #Verify if folder_name exists, and offers to delete it if so
    bc.checking_existence(basepath, folder_name)
    
    #Initializing the case
    bc.sweep_1_initialization(basepath, folder_name)

    # Starting loops over all sweeps
    for s in range(1, n+1):
        sweep_name=mysweep.format(s)
        loop_pimpleDyMFoam(basepath, folder_name, sweep_name, s)
        
        #Sarting Defect Computation
        computeDefect(basepath, sweep_name, s)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    num_minutes=int(elapsed_time/60)
    num_seconds=elapsed_time%60
    print("Elapsed time:", num_minutes, " minutes, ", num_seconds, "seconds")
    bc.timer_and_write(basepath, elapsed_time, "all subintervals", sweep_name)

def OLDcomputeSteffensenMethod(basepath, folder_name):
    start_time=time.time()
    print("\n\nStarting Steffensen's Method for " + folder_name + ".\n")
    
    #Initialisation of Sweep 1  
    sweep_name="sweep1"
    pre.initializeLinearisation(basepath, folder_name, sweep_name)
    
    #Linearisation preparation and cmputation from Sweep 2 to n
    for k in range (1, n+1):
        sweep_name=mysweep.format(k)
        with futures.ProcessPoolExecutor(max_workers=maxCPU) as executor:
            for i in range (1, n+1):
                executor.submit(linearisedPimpleDyMFoam, basepath, folder_name, sweep_name, i)
                pre.prepareNextLinearization(basepath, folder_name, k, i)
    
    # Preparation and Computation of shootingUpdate
    print("Starting shooting update process for " + sweep_name + ".\n")
    for k in range (1, n):
        for i in range (2, n+1):
            sweep_name=mysweep.format(k)
            m=1
            interval_name=myinterval.format(i)
            pre.prepareShootingUpdate(basepath, folder_name, sweep_name, k, i)
            interval_name=myinterval.format(m)
            sol.computeShootingUpdate(basepath, folder_name, sweep_name, interval_name)
            post.shootingUpdateP(basepath, folder_name, sweep_name, interval_name, k, m)
            m=m + 1
            if k==n-1:
                print("Steffensen's Method terminated. Sweep " + str(k) + " updated.")
                return(0)
        if k>3:
            g=k-2
            post.erase_all_files(basepath, folder_name, g)
            print("The files were succefully deleted. See exceptions above.")
    elapsed_time = time.time() - start_time        
    bc.timer_and_write(basepath, elapsed_time, "all subintervals", sweep_name)



# THE BIG SOLVERs
def primal_shooting_stef_update(basepath, erasing, event):
    
    #Verify if folder_name exists, and offers to delete it if so
    bc.checking_existence(basepath, folder_name)
    
    #Starting Timer for entire Process
    start_time_ALL=time.time()
    
    #Initilisation for Sweep1
    bc.sweep_1_initialization(basepath, folder_name) #One sync version
    
    deletion_counter=-1
    # STARTING MAIN LOOP
    for k in range(1, n+1):
    ######################    
        #Intermediate counter start
        start_time=time.time()
        #Naming current sweep
        sweep_name = mysweep.format(k)

        #Starting primitive Shooting in Sweep k over all subintervals
        loop_pimpleDyMFoam(basepath, folder_name, sweep_name, k) #One sync version        

        #Newline for defect
        loop_computeDefect(basepath, sweep_name, k)
        if k==2:
            print("Starting the adjoint ...\n")
            #event.set()
        
        #Starting linearisation for Sweep k over all subintervals
        loop_linearisedPimpleDyMFoam(basepath, folder_name, sweep_name, k) #One sync version

        #Starting Newton Update
        loop_computeNewtonUpdate(basepath, folder_name, sweep_name, k)
        
        # Deleting Files after Sweep k Done
        if erasing=="yes":
            if (deletion_counter>0):
                print("Deleting files...\n")
                post.erase_all_files(basepath, folder_name, k)
                print("The files for " + mysweep.format(deletion_counter)+ " in primal_path were succefully deleted. See exceptions above.")
        deletion_counter+=1

        #Stopping intermediate timer and writing into logfile
        elapsed_time = time.time() - start_time
        bc.timer_and_write(basepath, elapsed_time, "subintervals", sweep_name)
    print("Steffensen's Method terminated. Sweep " + str(k) + " updated.")

    #Stopping timer and writing into logfile
    total_time=time.time()-start_time_ALL
    bc.timer_and_write(basepath, total_time, folder_name, sweep_name)
    post.store_all_values(basepath, folder_name)

#################### OPTIONS  ##########################################

def coupling_threads():
    # Create an event object for synchronization
    event = threading.Event()
    
    # Create threads for the two functions
    thread1 = threading.Thread(target=sol.primal_shooting_stef_update(primal_path, "yes", event))
    thread2 = threading.Thread(target=adsol.computeAdjoint(adjoint_path, event))
    
    # Start the threads
    thread1.start()
    thread2.start()
    
    # Wait for the threads to finish
    thread1.join()
    thread2.join()


def the_new_shooting_manager(deleting, choice):
    if choice ==0:
        primal_shooting_stef_update(primal_path, "no", "event")        
        adsol.computeAdjoint(adjoint_path, "yes", "event")
    
    # PRIMAL
    if choice==1:
        os.chdir(primal_path)
        #OLDprimal_nofastpropagator_seq(primal_path)
        primal_shooting_stef_update(primal_path, "no", "no")
    # PRIMAL + NEWTON UPDATE
    if choice==2:
        os.chdir(primal_path)
        primal_shooting_stef_update(primal_path, deleting, "event")        
        adsol.computeAdjoint(adjoint_path, deleting, "event")
        
    #ADJOINT
    if choice == 3:
        os.chdir(adjoint_path)
        adsol.computeAdjoint(adjoint_path, deleting, "event")
        
    #COUPLING
    if choice ==4:
        print("Warning: This option is not ready yet")
    if choice >4:
        choice=input("Enter of of the options displayed below:\n1 - Primal\n2 - Primal + Newton Update\n3 - Adjoint (Requires a full completed Primal Case with the same name)\n4 - Coupled Primal and Adjoint\n\n")
        the_new_shooting_manager(deleting, choice)


    