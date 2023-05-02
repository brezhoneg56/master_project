# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 10:27:15 2023

@author: jcosson
"""
import os
import subprocess
from src import boundary_conditions as bc, preprocessing as pre, solvers as sol, postprocessing as post
#from .. import main
import sys
#sys.path.append('../')

from config import primal_path, primitive_path, steffensen_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, basepath
from config import n, theta, T, a, deltaT, myinterval, mysweep
print(primal_path+primitive_path+steffensen_path+calcs_undeformed+ref_cases+ref_cases_mod_def+project_path+basepath)

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

def linearisedPimpleDyMFoam(folder_name, sweep_name):
    #Executing linearisedPimpleDyMFoam for sweep k interval i
    i=2
    sweep_name="sweep1"
    interval_name=myinterval.format(i)
    lin_pimple_path=basepath+folder_name+"/"+sweep_name+"/"+interval_name
    print("Executing linearisedPimpleDyMFoam in "+folder_name+'/'+sweep_name+'/'+interval_name+'\n\n')
    os.chdir(lin_pimple_path)
    with open("logfile.txt","w") as logfile:
        result=subprocess.run(['linearisedPimpleDyMFoam'], stdout=logfile, stderr=subprocess.STDOUT)            
    print("Computation of "+interval_name+" is done.\n\nWriting into pimple.log ...\n")
    os.chdir(basepath) #back to main path
    print("Done.\n\n")
    print("End of loop for interval "+str(i)+".")
    return(result)
    
    
    
def loop_pimpleDyMFoam(folder_name):
    deltaT=T/n
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

def primal_nofastpropagator_seq(): #change name (eg primal or adjoint+shooting method) primal_nofastpropagator_steffensen
    for s in range(a, n+1):
        print(s)
        folder_name=str(s)+"_intervals_parallel"
        os.mkdir(folder_name)
        bc.sweep_1_initialization(folder_name)
        loop_pimpleDyMFoam(folder_name)
        
#NO def primal_nofastpropagator_steffensen(): #change name (eg primal or adjoint+shooting method) primal_nofastpropagator_steffensen
#    for s in range(a, n+1):
#        print(s)
#        folder_name=str(s)+"_intervals"
#        os.mkdir(folder_name)
#        bc.sweep_1_initialization(folder_name)
#        loop_pimpleDyMFoam(folder_name)

def computeShootingUpdate():
    # Calls compute shootingupdate from openfoam
    print(".")
def computeSteffensenMethod():
    #executes in for-k sweep and for-i interval:
        #prepareLinearization()
        #linearisedPimpleDyMFoam()
        #prepareShootingUpdate()
        #computeShootingUpdate()
        print("stef test")