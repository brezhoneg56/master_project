# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 10:27:15 2023

@author: jcosson
"""
import os
import subprocess
import multiprocessing
import sys
import shutil
import time
from concurrent import futures
from functools import partial
from src import boundary_conditions as bc, preprocessing as pre, solvers as sol, adjoint_solvers as adsol,  postprocessing as post
from config import primal_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, adjoint_path
from config import n, theta, T, a, deltaT, myinterval, mysweep, folder_name
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
    with futures.ProcessPoolExecutor(max_workers=14) as executor:
        for i in range(k, n+1):
            executor.submit(sol.pimpleDyMFoam, basepath, folder_name, sweep_name, i)
            print("Starting pimpleDyMFoam for interval " + str(i))
        print("\n\nAll simulations started. Waiting... \n")
    print("EXECUTOR pimpleDyMFoam terminated.\n\n")
    post.preparePostProcessing(basepath, folder_name, sweep_name)
    post.computePressureDropFoam(basepath, folder_name, sweep_name)
    if k<n:
        pre.prepareMyNextSweep(basepath, k, folder_name)

#########################      LINEARIZATION      #########################

def linearisedPimpleDyMFoam(basepath, folder_name, sweep_name, i):
    #Executing linearisedPimpleDyMFoam for sweep k interval i
    interval_name=myinterval.format(i)
    lin_pimple_path=basepath + folder_name + "/" + sweep_name + "/" + interval_name
    os.chdir(lin_pimple_path)
    with open("lin_logfile"+sweep_name+"_"+interval_name+".txt","w") as logfile:
        subprocess.run(['linearisedPimpleDyMFoam'], stdout=logfile, stderr=subprocess.STDOUT)
        #subprocess.run(['linearisedPimpleDyMFoam'])
    print("Linearisation of " + interval_name + " is done. Writing into lin_logfile ...")
    os.chdir(basepath) #back to main path

def loop_linearisedPimpleDyMFoam(basepath, folder_name, sweep_name, k): #Version V1 : Parallel call for all intervals within one sweep
    #with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
    print("\nStarting linearisation of " + sweep_name + "\n")
    print("Starting LIN EXECUTOR ... \n")
    #if k==1:
    #    pre.initializeLinearisation(basepath, folder_name, sweep_name)
    for i in range(1, n+1):#k, essayer 2
        pre.prepareNextLinearization(basepath, folder_name, k, i)
    with futures.ProcessPoolExecutor(max_workers=14) as executor:        
        for i in range(1, n+1):#k.essayer 2, on ne lin pas dans 1
            executor.submit(linearisedPimpleDyMFoam, basepath, folder_name, sweep_name, i)
            print("Starting linearisedPimpleDyMFoam for interval " + str(i))
        
        print("\n\nAll Linearisations started, Waiting... \n")
    print("LIN EXECUTOR terminated \n\n") 

def computeShootingUpdate(basepath, folder_name, g, i):
    sweep_name=mysweep.format(g)
    interval_name=myinterval.format(i)
    
    # Calls compute shootingupdate from openfoam
    if not os.path.exists(basepath + folder_name + "/" + sweep_name + "/preProcessing/"):
        os.mkdir(basepath + folder_name + "/" + sweep_name + "/preProcessing/")
    os.chdir(basepath + folder_name + "/" + sweep_name + "/preProcessing/")
    with open("shooting_update_logfile"+sweep_name+"_"+interval_name+".txt","w") as logfile:
        subprocess.run(['computeShootingUpdate'], stdout=logfile, stderr=subprocess.STDOUT)

def int1_Defect(basepath, sweep_name): #for computeDefect
    i=1
    interval_name="interval1"
    endingTime=str(bc.decimal_analysis(theta + (i-1)*deltaT))
    
    src_U=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + endingTime + "/U"
    src_p=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + endingTime + "/p"
    src_phi=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + endingTime + "/phi"
    
    dest_U=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + endingTime + "/UShootEnd"
    dest_p=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + endingTime +"/pShootEnd"
    dest_phi=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + endingTime + "/phiShootEnd"

    shutil.copyfile(src_U, dest_U)
    shutil.copyfile(src_p, dest_p)
    shutil.copyfile(src_phi, dest_phi)

def computeDefect(basepath, sweep_name, k):
    int1_Defect(basepath, sweep_name)
    print("\nComputing Defect ...")
    for i in range(2, n+1): #2, n+1
        interval_name=myinterval.format(i)
        previous_interval=myinterval.format(i-1)
        #print("Previous interval: " + previous_interval)
        #Comment out???
        pre.prepareDefectComputation(basepath, sweep_name, interval_name, previous_interval, i)
        os.chdir(basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingDefect")
        with open("shooting_defect_logfile"+sweep_name+"_"+interval_name+".txt","w") as logfile:
            subprocess.run(['computeShootingDefect'], stdout=logfile, stderr=subprocess.STDOUT)        
    os.chdir(basepath)

def computeNewtonUpdate(basepath, folder_name, sweep_name, k):
    print("\nComputing Newton Update...")
    if k+1==n:
        sys.exit
    for i in range(k+2, n+1): #depart à 2
        interval_name=myinterval.format(i)
        pre.prepareNewtonUpdate(basepath, folder_name, sweep_name, k, interval_name, i)
        os.chdir(basepath + folder_name + "/" + sweep_name + "/" + interval_name)     
        with open("newton_update_logfile"+sweep_name+"_"+interval_name+".txt","w") as logfile:
            os.chdir(basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingUpdate")
            subprocess.run(['computeNewtonUpdate'], stdout=logfile, stderr=subprocess.STDOUT)
        os.chdir(basepath)
        if i<n and k<n:
            post.prepareNextNewton(basepath, folder_name, sweep_name, k, interval_name, i)


###################### FUNCTIONS FOR MAIN EXECUTION #######################

def primal_nofastpropagator_seq(basepath): #change name (eg primal or adjoint + shooting method) primal_nofastpropagator_steffensen
    #Strating Timer
    start_time=time.time()
    
    #Verify if folder_name exists, and offers to delete it if so
    bc.checking_existence(folder_name)
    
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
    bc.timer_and_write(elapsed_time, "all subintervals", sweep_name)

def computeSteffensenMethod(basepath, folder_name):
    start_time=time.time()
    print("\n\nStarting Steffensen's Method for " + folder_name + ".\n")
    
    #Initialisation of Sweep 1  
    sweep_name="sweep1"
    pre.initializeLinearisation(basepath, folder_name, sweep_name)
    
    #Linearisation preparation and cmputation from Sweep 2 to n
    for k in range (1, n+1):
        sweep_name=mysweep.format(k)
        with futures.ProcessPoolExecutor(max_workers=14) as executor:
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
    bc.timer_and_write(elapsed_time, "all subintervals", sweep_name)



# THE BIG SOLVERs
def primal_shooting_stef_update(basepath, erasing):
    
    #Implementing counters    
    #g=1
    countershooting=1
    
    #Verify if folder_name exists, and offers to delete it if so
    bc.checking_existence(folder_name)
    
    #Starting Timer for entire Process
    start_time_ALL=time.time()
    
    #Initilisation for Sweep1
    bc.sweep_1_initialization(basepath, folder_name) #One sync version

    # STARTING MAIN LOOP
    for k in range(1, n+1):
    ######################    

        #Intermediate counter start
        start_time=time.time()
        #Naming current sweep
        sweep_name = mysweep.format(k)

        #Starting primitive Shooting in Sweep k over all subintervals
        sol.loop_pimpleDyMFoam(basepath, folder_name, sweep_name, k) #One sync version

        #Stopping intermediate timer and writing into logfile
        elapsed_time = time.time() - start_time
        bc.timer_and_write(elapsed_time, "pimpleDyMFoam", sweep_name)

        #Newline for defect
        computeDefect(basepath, sweep_name, k)

        #Starting intermediate timer
        lin_time=time.time()

        #Starting linearisation for Sweep k over all subintervals
        sol.loop_linearisedPimpleDyMFoam(basepath, folder_name, sweep_name, k) #One sync version

        #Stopping intermediate timer and writing into logfile
        elapsed_time = time.time() - lin_time
        bc.timer_and_write(elapsed_time, "linearisedPimpleDyMFoam", sweep_name)

        #Starting Newton Update
        computeNewtonUpdate(basepath, folder_name, sweep_name, k)

        #Implementing counter for shooting update
        countershooting=countershooting+1

        # Deleting Files after Sweep k Done    
        if erasing=="yes":
            print("Deleting files...\n")
            post.erase_all_files(basepath, folder_name, k)
            print("The files were succefully deleted. See exceptions above.")
        
        #Stopping intermediate timer and writing into logfile
        elapsed_time = time.time() - start_time        
        bc.timer_and_write(elapsed_time, "all subintervals", sweep_name)
        
    print("Steffensen's Method terminated. Sweep " + str(k) + " updated.")

    #Stopping timer and writing into logfile
    total_time=time.time()-start_time_ALL
    bc.timer_and_write(total_time, folder_name, sweep_name)
        
###########################################################################

def the_shooting_manager():
    process=input("Do you want to start the entire process? (Primal + Update + Adjoint) (Y/N) (stop to exit)     \n   \n")
    ##############
    if process=="stop":
        sys.exit()
   ###############
   # 
    if process=="Y" or process=="y" or process=="yes":
        erasing=input("Do you you to delete time files and configuration files after computation? (Y/N) (stop to exit)    \n   \n")
        if erasing=="stop":
             sys.exit()
        if erasing=="Y" or erasing=="y" or erasing=="yes":
            primal_shooting_stef_update(primal_path, "yes")
        elif erasing=="N" or erasing=="n" or erasing=="no":
            primal_shooting_stef_update(primal_path, "no")
        else:
            print("Please answer by yes or no.")
            the_shooting_manager()
    
    
    elif process=="N" or process=="n" or process=="no":
        choice=input("Enter of of the options displayed below:\n1 - Primal\n2 - Primal + Newton Update\n3 - Adjoint (Requires a full completed Primal Case with the same name)\n\n")
        #print("")
        if choice=="1":
            primal_nofastpropagator_seq(primal_path)
        if choice=="2":
            primal_shooting_stef_update(primal_path, erasing)
        if choice=="3":
            adsol.computeAdjoint()
        else:
            print("Please enter one of the displayed possibilities.")
            the_shooting_manager()
    