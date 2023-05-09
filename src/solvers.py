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
from src import boundary_conditions as bc, preprocessing as pre, solvers as sol, postprocessing as post
from config import primal_path, primitive_path, steffensen_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, basepath
from config import n, theta, T, a, deltaT, myinterval, mysweep
########################################################################################################

#################################### OPENFOAM SINGLE SOLVERS ##########################################
def pimpleDyMFoam(folder_name, sweep_name, i):
    interval_name=myinterval.format(i)
    pimple_path=basepath+folder_name+"/"+sweep_name+"/"+interval_name
    print("Executing pimpleDyMFoam in "+folder_name+'/'+sweep_name+'/'+interval_name+'.')
    os.chdir(pimple_path) #Entering logfile path
    
    #Open a log file and pipe the output of PimpleDyMFoam into the log        
    with open("logfile.txt","w") as logfile:
        result=subprocess.run(['pimpleDyMFoam'], stdout=logfile, stderr=subprocess.STDOUT)            
    print("Computation of "+interval_name+" is done. Writing into pimple.log ...\n")
    os.chdir(basepath) #back to main path
    return(result)

def linearisedPimpleDyMFoam(folder_name, sweep_name, i):
    #Executing linearisedPimpleDyMFoam for sweep k interval i
    interval_name=myinterval.format(i)
    lin_pimple_path=basepath+folder_name+"/"+sweep_name+"/"+interval_name
    if not os.path.exists(basepath+folder_name+"/"+sweep_name):    
        os.mkdir(basepath+folder_name+"/"+sweep_name)
    print("Executing linearisedPimpleDyMFoam in "+folder_name+'/'+sweep_name+'/'+interval_name+".")
    if not os.path.exists(lin_pimple_path):    
        os.mkdir(lin_pimple_path)
    os.chdir(lin_pimple_path)
    with open("logfile.txt","w") as logfile:
        subprocess.run(['linearisedPimpleDyMFoam'], stdout=logfile, stderr=subprocess.STDOUT)
    print("Computation of "+interval_name+" is done. Writing into pimple.log ...\n")
    os.chdir(basepath) #back to main path

def computeShootingUpdate(folder_name, sweep_name, interval_name):
    # Calls compute shootingupdate from openfoam
    print("Computing Shooting Update for "+sweep_name+".\n")
    os.chdir(steffensen_path+folder_name+"/"+sweep_name+"/preProcessing/")
    with open("logfile.txt","w") as logfile:
        subprocess.run(['computeShootingUpdate'], stdout=logfile, stderr=subprocess.STDOUT)
    #subprocess.run(['computeShootingUpdate'])    
########################################################################################################

####################################### OPENFOAM PROCESSES #############################################
def OLDloop_pimpleDyMFoam(folder_name):
    for k in range(1, n+1):
        sweep_name=mysweep.format(k)
        ## COMPUTE MY INTERVAL
        print("\nStarting shooting of "+sweep_name+"\n")
        for i in range(k, n+1):
            sol.pimpleDyMFoam(folder_name, sweep_name,i)
        post.preparePostProcessing(folder_name, sweep_name)
        post.computePressureDropFoam(folder_name, sweep_name)
        while (k<n):
            pre.prepareMyNextSweep(k, folder_name)
            break
    return(myinterval, mysweep)


## PARALLEL TEST #################

def run_pimpleDyMFoam(folder_name, sweep_name, i):
    sol.pimpleDyMFoam(folder_name, sweep_name, i)

def loop_pimpleDyMFoam(folder_name):
    pool = multiprocessing.Pool()
    for k in range(1, n+1):
        sweep_name = mysweep.format(k)
        print("\nStarting shooting of "+sweep_name+"\n")
        for i in range(k, n+1):
            pool.apply_async(run_pimpleDyMFoam, args=(folder_name, sweep_name, i))
        post.preparePostProcessing(folder_name, sweep_name)
        post.computePressureDropFoam(folder_name, sweep_name)
        pool.close()
        while (k<n):
            pre.prepareMyNextSweep(k, folder_name)
            break
        
        pool.join()
    return(myinterval, mysweep)
######################################




########################################################################################################

################################## FUNCTIONS FOR MAIN EXECUTION ########################################

def primal_nofastpropagator_seq(): #change name (eg primal or adjoint+shooting method) primal_nofastpropagator_steffensen
    for s in range(a, n+1):
        print(s)
        folder_name=str(s)+"_intervals_parallel"
        if os.path.exists(folder_name):
            ans=input(print("WARNING: Directory "+folder_name+" already exists. Do you want to replace it ? (Y/N)     \n   \n"))
        if ans=="Y" or ans=="y":
            shutil.rmtree(folder_name)
        else:
            sys.exit()
        os.mkdir(folder_name)
        bc.sweep_1_initialization(folder_name)
        loop_pimpleDyMFoam(folder_name)

def computeSteffensenMethod(folder_name):
    print("\n\nStarting Steffensen's Method for "+folder_name+".\n")
    #Initialisation of Sweep 1  
    sweep_name="sweep1"
    pre.initializeLinearisation(folder_name, sweep_name)
    #Linearisation preparation and cmputation from Sweep 2 to n
    for k in range (1, n+1):
        sweep_name=mysweep.format(k)
        for i in range (1, n+1):
            interval_name=myinterval.format(i)  
            sol.linearisedPimpleDyMFoam(folder_name, sweep_name, i)
            pre.prepareNextLinearization(folder_name, k, i)
    # Preparation and Computation of shootingUpdate
    for k in range (1, n+1):
        for i in range (2, n+1):
            sweep_name=mysweep.format(k)
            #if not k==n:
            m=1
            print("Starting shooting update process for "+sweep_name+".\n")
            #for i in range(2, n+1):
            interval_name=myinterval.format(i)
            pre.prepareShootingUpdate(folder_name, sweep_name, k, i)
            interval_name=myinterval.format(m)
            sol.computeShootingUpdate(folder_name, sweep_name, interval_name)
            post.shootingUpdateP(folder_name, sweep_name, interval_name, k, m)
            m=m+1
            if k==n-1:
                print("Steffensen's Method terminated. Sweep "+str(k)+"updated.")
                return(0)

