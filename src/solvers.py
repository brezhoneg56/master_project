# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 10:27:15 2023

@author: jcosson
"""
import os
import subprocess
from src import boundary_conditions as bc, preprocessing as pre, solvers as sol, postprocessing as post


def pimpleDyMFoam(folder_name, sweep_name,i, basepath):
    myinterval="interval{}"
    interval_name=myinterval.format(i)
    pimple_path=basepath+folder_name+"/"+sweep_name+"/"+interval_name
    print("Executing pimpleDyMFoam in "+folder_name+'/'+sweep_name+'/'+interval_name+'\n\n')
    os.chdir(pimple_path) #Entering logfile path
    
    #Open a log file and pipe the output of PimpleDyMFoam into the log        
    with open("logfile.txt","w") as logfile:
        result=subprocess.run(['pimpleDyMFoam'], stdout=logfile, stderr=subprocess.STDOUT)            
    print("Computation of "+interval_name+" is done.\n\n Writing into pimple.log ...")
    os.chdir(basepath) #back to main path
    print("Done.\n\n")
    print("End of loop for interval "+str(i)+".")
    return(result)

def startMyComputation (basepath, n, T, theta, folder_name):
    deltaT=T/n
    myinterval="interval{}"
    mysweep="sweep{}"
    for k in range(1, n+1):
        sweep_name=mysweep.format(k)
        ## COMPUTE MY INTERVAL
        print("\nStarting shooting of "+sweep_name+"\n")
        for i in range(k, n+1):
            sol.pimpleDyMFoam(folder_name, sweep_name,i, basepath)
        post.preparePostProcessing(folder_name, sweep_name, basepath, n)
        post.computePressureDropFoam(folder_name, sweep_name, basepath)
        while (k<n):
            pre.prepareMyNextSweep(k, n, folder_name, basepath, theta, deltaT)
            break
    return(myinterval, mysweep)

def computeEverything(basepath, n, T, theta, a): #change name (eg primal or adjoint+shooting method) primal_nofastpropagator_steffensen
    for s in range(a, n+1):
        print(s)
        folder_name=str(s)+"_intervals"
        os.mkdir(folder_name)
        bc.sweep_1_initialization(s, T, basepath, theta, folder_name)
        startMyComputation(basepath, s, T, theta, folder_name)