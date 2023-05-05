# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 10:27:15 2023

@author: jcosson
"""
import os
import subprocess
from src import boundary_conditions as bc, preprocessing as pre, solvers as sol, postprocessing as post
from config import primal_path, primitive_path, steffensen_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, basepath
from config import n, theta, T, a, deltaT, myinterval, mysweep
########################################################################################################

#################################### OPENFOAM SINGLE SOLVERS ##########################################
def pimpleDyMFoam(folder_name, sweep_name, i):
    interval_name=myinterval.format(i)
    pimple_path=basepath+folder_name+"/"+sweep_name+"/"+interval_name
    print("Executing pimpleDyMFoam in "+folder_name+'/'+sweep_name+'/'+interval_name+'\n\n')
    os.chdir(pimple_path) #Entering logfile path
    
    #Open a log file and pipe the output of PimpleDyMFoam into the log        
    with open("logfile.txt","w") as logfile:
        result=subprocess.run(['pimpleDyMFoam'], stdout=logfile, stderr=subprocess.STDOUT)            
    print("Computation of "+interval_name+" is done.\n\nWriting into pimple.log ...\n")
    os.chdir(basepath) #back to main path
    print("Done.\n\n")
    print("End of loop for interval "+str(i)+".")
    return(result)

def linearisedPimpleDyMFoam(folder_name, sweep_name, i):
    #Executing linearisedPimpleDyMFoam for sweep k interval i
    interval_name=myinterval.format(i)
    lin_pimple_path=basepath+folder_name+"/"+sweep_name+"/"+interval_name
    if not os.path.exists(basepath+folder_name+"/"+sweep_name):    
        os.mkdir(basepath+folder_name+"/"+sweep_name)
    print("Executing linearisedPimpleDyMFoam in "+folder_name+'/'+sweep_name+'/'+interval_name+'\n\n')
    if not os.path.exists(lin_pimple_path):    
        os.mkdir(lin_pimple_path)
        print("Directory created at "+lin_pimple_path+".\n")
    os.chdir(lin_pimple_path)
    with open("logfile.txt","w") as logfile:
        subprocess.run(['linearisedPimpleDyMFoam'], stdout=logfile, stderr=subprocess.STDOUT)
    print("Computation of "+interval_name+" is done.\n\nWriting into pimple.log ...\n")
    os.chdir(basepath) #back to main path
    print("Done.\n\n")
    print("End of loop for interval "+str(i)+".")

def computeShootingUpdate(folder_name, sweep_name, interval_name):
    # Calls compute shootingupdate from openfoam
    print("Computing Shooting Update for "+sweep_name+" in "+interval_name+".\n")
    os.chdir(steffensen_path+folder_name+"/"+sweep_name+"/preProcessing/")
    #with open("logfile.txt","w") as logfile:
        #result=subprocess.run(['computeShootingUpdate'], stdout=logfile, stderr=subprocess.STDOUT)
    subprocess.run(['computeShootingUpdate'])    
    #return(result)
########################################################################################################

####################################### OPENFOAM PROCESSES #############################################
def loop_pimpleDyMFoam(folder_name):
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
########################################################################################################

################################## FUNCTIONS FOR MAIN EXECUTION ########################################

def primal_nofastpropagator_seq(): #change name (eg primal or adjoint+shooting method) primal_nofastpropagator_steffensen
    for s in range(a, n+1):
        print(s)
        folder_name=str(s)+"_intervals_parallel"
        os.mkdir(folder_name)
        bc.sweep_1_initialization(folder_name)
        loop_pimpleDyMFoam(folder_name)

def computeSteffensenMethod(folder_name):
    #Initialisation of Sweep 1  
    sweep_name="sweep1"
    pre.initializeLinearisation(folder_name, sweep_name) ##WORKS
    for k in range (1, n+1):
        sweep_name=mysweep.format(k)
        print("\n\nStarting linearisation process for "+sweep_name+".\n")
        for i in range (1, n+1):
            interval_name=myinterval.format(i)  
            print("\nlinearisedPimpleDyMFoam\n" )
            sol.linearisedPimpleDyMFoam(folder_name, sweep_name, i)
            print("Done\n")
            print("prepareNextLinearization\n")
            pre.prepareNextLinearization(folder_name, k, i)
            print("Linearisation Preparation Done\n")
        for i in range (2, n+1):
            m=1
            print("Starting shooting update process for "+sweep_name+".\n")
            #for i in range(2, n+1):
            interval_name=myinterval.format(i)
            print("prepareShootingUpdate\n")
            if not k==n:
                pre.prepareShootingUpdate(folder_name, sweep_name, k, i)
            print("Shooting Preparation Done")
            interval_name=myinterval.format(m)
            sol.computeShootingUpdate(folder_name, sweep_name, interval_name)
            post.shootingUpdateP(folder_name, sweep_name, interval_name, k, m)
            print("Shooting Updated.\n")
            m=m+1
    print("Steffensen's Method terminated.")