# -*- coding: utf-8 -*-
"""
Created on Tue May 30 17:12:18 2023

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
from src import boundary_conditions as bc, preprocessing as pre, solvers as sol, postprocessing as post
from config import primal_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, adjoint_path
from config import n, theta, T, a, deltaT, myinterval, mysweep, folder_name

def prepareAdjointDefectComputation(basepath, sweep_name, interval_name, previous_interval, i): #for computeDefect
    
    #Fetch shootingDefect from ref_Cases    
    src_shootingDefect = ref_cases + "shootingDefect/"
    dest_shootingDefect = basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingDefect/"
    #shutil.copytree(src_shootingDefect, dest_shootingDefect)
    
    startingTime=str(bc.decimal_analysis(theta + (i-1)*deltaT))
    endingTime=str(bc.decimal_analysis(theta + (i-1)*deltaT))
    
    adjointStartingTime=str(-bc.decimal_analysis(theta + (i-1)*deltaT))
    adjointEndingTime=str(-bc.decimal_analysis(theta + (i-1)*deltaT)) 

    #Fetch U, p, phi from current interval
    src_U=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + startingTime + "/Ua"
    src_p=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + startingTime + "/pa"
    src_phi=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + startingTime + "/phia"
    
    dest_U=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingDefect/0/UInit_right"
    dest_p=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingDefect/0/pInit_right"
    dest_phi=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingDefect/0/phiInit_right"

    shutil.copyfile(src_U, dest_U)
    shutil.copyfile(src_p, dest_p)
    shutil.copyfile(src_phi, dest_phi)

    #Fetch U, p, phi from previous interval  (interval5)
    src_U=basepath + folder_name + "/" + sweep_name + "/" + previous_interval + "/" + adjointEndingTime + "/Ua" #modif
    src_p=basepath + folder_name + "/" + sweep_name + "/" + previous_interval + "/" + adjointEndingTime + "/pa" #modif
    src_phi=basepath + folder_name + "/" + sweep_name + "/" + previous_interval + "/" + adjointEndingTime + "/phia" #modif
    
    dest_U=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingDefect/0/UaShootEnd" #modif
    dest_p=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingDefect/0/paShootEnd" #modif
    dest_phi=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingDefect/0/phiaShootEnd" #modif

    shutil.copyfile(src_U, dest_U) #same
    shutil.copyfile(src_p, dest_p) #same
    shutil.copyfile(src_phi, dest_phi) #same

def computeAdjointDefect(basepath, sweep_name, k):
    #int1_Defect(basepath, sweep_name)
    print("\nComputing Defect ...")
    for i in range(n-1, 1, -1): #2, n+1  
        interval_name=myinterval.format(i)
        previous_interval=myinterval.format(i+1) #avant i-1 mais on va à l'envers
        prepareAdjointDefectComputation(adjoint_path, sweep_name, interval_name, previous_interval, i)
        os.chdir(adjoint_path + folder_name + "/" + sweep_name + "/" + interval_name)
        with open("adjoint_shooting_defect_logfile"+sweep_name+"_"+interval_name+".txt","w") as logfile:
            os.chdir(adjoint_path + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingDefect")
            subprocess.run(['computeAdjointShootingDefect'], stdout=logfile, stderr=subprocess.STDOUT)        
    os.chdir(basepath)

### ADJOINT

def adjointPimpleDyMFoam(folder_name, sweep_name, i):
    interval_name=myinterval.format(i)
    pimple_path=adjoint_path + folder_name + "/" + sweep_name + "/" + interval_name   
    os.chdir(pimple_path) #Entering logfile path
    print(pimple_path)    
    os.system('adjointPimpleDyMFoam >adjoint_pimple.log 2>&1')                
    print("Computation of " + interval_name + " is done. Writing into pimple.log ...")
    os.chdir(adjoint_path) #back to main path
    return(0)
    
def loop_adjoint_pimpleDyMFoam(folder_name, sweep_name, k): #Version V1 : Parallel call for all intervals within one sweep
    print("\nStarting shooting of " + sweep_name + "\n")
    print("Starting ADJ EXECUTOR ... \n")
    with futures.ProcessPoolExecutor(max_workers=13) as executor:
        for i in range(n, k-1, -1):
            executor.submit(adjointPimpleDyMFoam, folder_name, sweep_name, i)
        #adjointPimpleDyMFoam(folder_name, sweep_name, i)
            print("Starting adjointPimpleDyMFoam for interval " + str(i))
        print("\n\nAll simulations started. Waiting... \n")
    print("ADJ EXECUTOR adjointPimpleDyMFoam terminated.\n\n")
    #A priori inutiale:
    #post.preparePostProcessing(adjoint_path, folder_name, sweep_name)
    #post.computePressureDropFoam(adjoint_path, folder_name, sweep_name)

def adjointLinearisedPimpleDyMFoam(basepath, folder_name, sweep_name, i):
    #Executing linearisedPimpleDyMFoam for sweep k interval i
    interval_name=myinterval.format(i)
    lin_pimple_path=basepath + folder_name + "/" + sweep_name + "/" + interval_name
    os.chdir(lin_pimple_path)
    with open("lin_logfile"+sweep_name+"_"+interval_name+".txt","w") as logfile:
        subprocess.run(['linearisedPimpleDyMFoam'], stdout=logfile, stderr=subprocess.STDOUT)
        #subprocess.run(['linearisedPimpleDyMFoam'])
    print("Linearisation of " + interval_name + " is done. Writing into lin_logfile ...")
    os.chdir(basepath) #back to main path

def loop_linearised_adjoint_pimpleDyMFoam(folder_name, sweep_name, k):
    print("linfor " + sweep_name)
    
    #with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
    print("\nStarting adjoint linearisation of " + sweep_name + "\n")
    print("Starting LIN ADJ EXECUTOR ... \n")
    #if k==1:
    #    pre.initializeLinearisation(basepath, folder_name, sweep_name)
    for i in range(1, n+1):#k, essayer 2
        pre.prepareNextLinearization(adjoint_path, folder_name, k, i)
    with futures.ProcessPoolExecutor(max_workers=13) as executor:        
        for i in range(1, n+1):#k.essayer 2, on ne lin pas dans 1
            executor.submit(adjointLinearisedPimpleDyMFoam, adjoint_path, folder_name, sweep_name, i)
            print("Starting adjointLinearisedPimpleDyMFoam for interval " + str(i))
        
        print("\n\nAll Adjoint linearisations started, Waiting... \n")
    print("LIN ADJ EXECUTOR terminated \n\n")

def computeAdjoint():
    #Starting Timer for entire Process
    start_time=time.time()
    
    #Verify if folder_name exists, and offers to delete it if so
    bc.checking_existence(adjoint_path + folder_name)
    print("Preparing files for adjoint computation...\n")
    
    #Initialization loop over all Sweeps    
    for k in range (1, n+1):
        sweep_name=mysweep.format(k)
        
        #Renaming Time folder with "-"
        pre.prepareTimeFolders(folder_name, sweep_name)
        
        #Preparing files for adjoint computation
        pre.initializeMyAdjoint(folder_name, sweep_name)
    
    #Intermediate Timer
    elapsed_time = time.time() - start_time        
    bc.timer_and_write(elapsed_time, "copying files", "adjoint folder")
    
    #Starting adjointPimpleDyMFoam for Sweep k
    for k in range (1, n+1):
        sweep_name=mysweep.format(k)
        loop_adjoint_pimpleDyMFoam(folder_name, sweep_name, k)
        
        #Computing Adjoint Defect
        print("\nDEFECT...\n")
        computeAdjointDefect(adjoint_path, sweep_name, k)
        
        #Computing Adjoint Linearization
        print("\nLINEARIZATION...\n")
        loop_linearised_adjoint_pimpleDyMFoam(folder_name, sweep_name, k)
    
    #Final Timer
    elapsed_time = time.time() - start_time        
    bc.timer_and_write(elapsed_time, "adjointPimpleDyMFoam", folder_name)