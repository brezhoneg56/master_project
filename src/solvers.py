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
from src import boundary_conditions as bc, preprocessing as pre, solvers as sol, postprocessing as post
from config import primal_path, primitive_path, steffensen_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path
from config import n, theta, T, a, deltaT, myinterval, mysweep, folder_name
###########################################################################

#########################   PRIMITIVE SHOOTING    #########################
def pimpleDyMFoam(basepath, folder_name, sweep_name, i):
    interval_name=myinterval.format(i)
    pimple_path=basepath + folder_name + "/" + sweep_name + "/" + interval_name
    print("Executing pimpleDyMFoam in " + folder_name + '/' + sweep_name + '/' + interval_name + '.')
    #print(basepath)
    #print(folder_name)
    #print(sweep_name)
    #print(str(i))    
    os.chdir(pimple_path) #Entering logfile path
    
    #Open a log file and pipe the output of PimpleDyMFoam into the log        
#    with open("PDFlogfile"+sweep_name+"_"+interval_name+".txt","w") as logfile:
#        #result=subprocess.run(['pimpleDyMFoam'], stdout=logfile, stderr=subprocess.STDOUT)
#        result=subprocess.run(['pimpleDyMFoam'], stdout=logfile)
#        #result=subprocess.run(['pimpleDyMFoam']) 
    os.system('pimpleDyMFoam >pimple.log 2>&1')                
    print("Computation of " + interval_name + " is done. Writing into pimple.log ...")
    os.chdir(basepath) #back to main path
    return(0)

def loop_pimpleDyMFoam(basepath, folder_name, sweep_name, k): #Version V1 : Parallel call for all intervals within one sweep
    print("\nStarting shooting of " + sweep_name + "\n")
    print("Starting EXECUTOR ... \n")
    with futures.ProcessPoolExecutor() as executor:
        for i in range(k, n+1):
            executor.submit(pimpleDyMFoam, basepath, folder_name, sweep_name, i)
            print("Starting pimpleDyMFoam for interval " + str(i))
        
        print("\n\nAll simulations started. Waiting... \n")
    print("EXECUTOR pimpleDyMFoam terminated.")
    post.preparePostProcessing(basepath, folder_name, sweep_name)
    post.computePressureDropFoam(basepath, folder_name, sweep_name)
    if k<n: #instead of while
        pre.prepareMyNextSweep(basepath, k, folder_name)


#########################      LINEARIZATION      #########################

def linearisedPimpleDyMFoam(basepath, folder_name, sweep_name, i):
    #Executing linearisedPimpleDyMFoam for sweep k interval i
    interval_name=myinterval.format(i)
    lin_pimple_path=basepath + folder_name + "/" + sweep_name + "/" + interval_name
    #if not os.path.exists(basepath + folder_name + "/" + sweep_name):    
    #    os.mkdir(basepath + folder_name + "/" + sweep_name)
    print("Executing linearisedPimpleDyMFoam in " + folder_name + '/' + sweep_name + '/' + interval_name + ".")
    #if not os.path.exists(lin_pimple_path):    
    #    os.mkdir(lin_pimple_path)
    os.chdir(lin_pimple_path)
    with open("lin_logfile"+sweep_name+"_"+interval_name+".txt","w") as logfile:
        subprocess.run(['linearisedPimpleDyMFoam'], stdout=logfile, stderr=subprocess.STDOUT)
        #subprocess.run(['linearisedPimpleDyMFoam'])
    print("Computation of " + interval_name + " is done. Writing into pimple.log ...")
    os.chdir(basepath) #back to main path

def loop_linearisedPimpleDyMFoam(basepath, folder_name, sweep_name, k): #Version V1 : Parallel call for all intervals within one sweep
    #with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
    print("\nStarting linearisation of " + sweep_name + "\n")
    print("Starting LIN EXECUTOR ... \n")
    with futures.ThreadPoolExecutor(max_workers=13) as executor:
        
        for i in range(k, n+1):
            executor.submit(linearisedPimpleDyMFoam, basepath, folder_name, sweep_name, i)
            print("Starting linearisedPimpleDyMFoam for interval " + str(i) +"\n")
            pre.prepareNextLinearization(basepath, folder_name, k, i)
        print("\n\nAll Linearisations started, Waiting... \n")
    print("LIN EXECUTOR terminated \n\n")  


def computeShootingUpdate(basepath, folder_name, g, interval_name):
    sweep_name=mysweep.format(g)
    # Calls compute shootingupdate from openfoam
    print("Computing Shooting Update for " + interval_name + "in" + sweep_name + ".\n")
    os.chdir(basepath + folder_name + "/" + sweep_name + "/preProcessing/")
    with open("shooting_update_logfile"+sweep_name+"_"+interval_name+".txt","w") as logfile:
        subprocess.run(['computeShootingUpdate'], stdout=logfile, stderr=subprocess.STDOUT)
    #subprocess.run(['computeShootingUpdate'])    
###########################################################################

###################### FUNCTIONS FOR MAIN EXECUTION #######################

def primal_nofastpropagator_seq(basepath): #change name (eg primal or adjoint + shooting method) primal_nofastpropagator_steffensen
    start_time=time.time()
    for s in range(a, n + 1):
        print(s)
        #folder_name=str(s) + "_intervals_parallel"
        if os.path.exists(folder_name):
            ans=input("WARNING: Directory " + folder_name + " already exists. Do you want to replace it ? (Y/N)     \n   \n")
            if ans=="Y" or ans=="y":
                for g in range(1, n + 1):
                    if os.path.exists("sweep" + str(g)):
                        shutil.rmtree("sweep" + str(g))
                shutil.rmtree(folder_name)
            else:
                sys.exit()
        os.mkdir(folder_name)
        bc.sweep_1_initialization(basepath, folder_name)
        loop_pimpleDyMFoam(basepath, folder_name)
    end_time = time.time()
    elapsed_time = end_time - start_time
    num_minutes=int(elapsed_time/60)
    num_seconds=elapsed_time%60
    print("Elapsed time:",num_minutes, "minutes and" , num_seconds, "seconds")
    bc.time(start_time)
    return(folder_name)

def computeSteffensenMethod(basepath, folder_name):
    start_time=time.perf_counter()
    print("\n\nStarting Steffensen's Method for " + folder_name + ".\n")
    #Initialisation of Sweep 1  
    sweep_name="sweep1"
    pre.initializeLinearisation(basepath, folder_name, sweep_name)
    #Linearisation preparation and cmputation from Sweep 2 to n
    for k in range (1, n+1):
        sweep_name=mysweep.format(k)
        with concurrent.futures.ProcessPoolExecutor() as executor:
            for i in range (1, n+1):
                executor.submit(linearisedPimpleDyMFoam, basepath, folder_name, sweep_name, i)
                pre.prepareNextLinearization(basepath, folder_name, k, i)
    # Preparation and Computation of shootingUpdate
    for k in range (1, n):
        for i in range (2, n+1):
            sweep_name=mysweep.format(k)
            #if not k==n:
            m=1
            print("Starting shooting update process for " + sweep_name + ".\n")
            #for i in range(2, n + 1):
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
    print(bc.time(start_time))

def primal_shooting(basepath): #Initialize the case and launch the primal Shooting with linearization
    for s in range(a, n + 1):
        print(s)
        #folder_name=str(s) + "_intervals_parallel"
        if os.path.exists(folder_name):
            ans=input("WARNING: Directory " + folder_name + " already exists. Do you want to replace it ? (Y/N)     \n   \n")
            if ans=="Y" or ans=="y":
                for g in range(1, n + 1):
                    if os.path.exists("sweep" + str(g)):
                        shutil.rmtree("sweep" + str(g))
                shutil.rmtree(folder_name)
            else:
                sys.exit()
        os.mkdir(folder_name)
        bc.sweep_1_initialization(basepath, folder_name)
        primal_shooting_stef_update(basepath)        

def WORKONprimal_shooting_stef_update(basepath): #Prinmal Shooting with Linearization
    g=0
    start_time_ALL=time.time()
    for k in range(1, n + 1):
        start_time=time.perf_counter()
        sweep_name = mysweep.format(k)
        print("\nStarting shooting of " + sweep_name + "\n")
        for i in range(k, n+1):
            interval_name=myinterval.format(i)
            pimple_path=basepath + folder_name + "/" + sweep_name + "/" + interval_name
            print("Executing pimpleDyMFoam in " + folder_name + '/' + sweep_name + '/' + interval_name + '.')
            os.chdir(pimple_path) #Entering logfile path
    
        #Open a log file and pipe the output of PimpleDyMFoam into the log        
            with open("PDFlogfile"+sweep_name+"_"+interval_name+".txt","w") as logfile:
                #result=subprocess.run(['pimpleDyMFoam'], stdout=logfile, stderr=subprocess.STDOUT)
                subprocess.Popen(['pimpleDyMFoam'], stdout=logfile, stderr=subprocess.STDOUT)
                #result=subprocess.run(['pimpleDyMFoam'])                 
            print("Computation of " + interval_name + " is done. Writing into pimple.log ...")
            os.chdir(basepath) #back to main path
        post.preparePostProcessing(basepath, folder_name, sweep_name)
        post.computePressureDropFoam(basepath, folder_name, sweep_name)   




########################## OLD FUNCTIONS ######################


def OLD_NOT_WORKINGprimal_shooting_stef_update(basepath):
    g=0
    start_time_ALL=time.time()
    for k in range(1, n + 1):
        sweep_name = mysweep.format(k)
        #loop_pimpleDyMFoam(basepath, folder_name)
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures_1 = []
            for k in range(1, n + 1):
                start_time=time.perf_counter()
                sweep_name = mysweep.format(k)
                print("\nStarting shooting of " + sweep_name + "\n")
                for i in range(k, n+1):
                    futures_1.append(executor.submit(pimpleDyMFoam, basepath, folder_name, sweep_name, i))
                concurrent.futures.wait(futures_1)
                post.preparePostProcessing(basepath, folder_name, sweep_name)
                post.computePressureDropFoam(basepath, folder_name, sweep_name)
                if k==1:
                    pre.initializeLinearisation(basepath, folder_name, sweep_name)
                if (k<n): #instead of while
                    pre.prepareMyNextSweep(basepath, k, folder_name)
                #break
                futures_2 = []
                for i in range (1, n+1):
                    futures_2.append(executor.submit(linearisedPimpleDyMFoam, basepath, folder_name, sweep_name, i))
                    pre.prepareNextLinearization(basepath, folder_name, k, i)
                for future in concurrent.futures.as_completed(futures_2):
                    future.result()
                #if k>2: 
                g=g+1
                for i in range (2, n+1):
                    sweep_name=mysweep.format(k)
                    #if not k==n:
                    m=1
                    print("Starting shooting update process for " + sweep_name + ".\n")
                    #for i in range(2, n + 1):
                    interval_name=myinterval.format(i)
                    pre.prepareShootingUpdate(basepath, folder_name, sweep_name, k, i)
                    interval_name=myinterval.format(m)
                    sol.computeShootingUpdate(basepath, folder_name, sweep_name, interval_name)
                    post.shootingUpdateP(basepath, folder_name, sweep_name, interval_name, k, m)
                    m=m + 1
                if k==n-1:
                    print("Steffensen's Method terminated. Sweep " + str(k) + " updated.")
                    return(0)
                #post.erase_all_files(basepath, folder_name, g)
                end_time = time.time()
                elapsed_time = end_time - start_time
                num_minutes=int(elapsed_time/60)
                num_seconds=elapsed_time%60
                print("Elapsed time:",num_minutes, "minutes and" , num_seconds, "seconds")
        total_time=end_time-start_time_ALL
        num_minutes=int(total_time/60)
        num_seconds=total_time%60
        print("Elapsed time:",num_minutes, "minutes and" , num_seconds, "seconds")
        
def seq_computeSteffensenMethod(basepath, folder_name): #Sequential reolsution for linearisation and Shooting Update
    start_time=time.time()
    print("\n\nStarting Steffensen's Method for " + folder_name + ".\n")
    #Initialisation of Sweep 1  
    sweep_name="sweep1"
    pre.initializeLinearisation(folder_name, sweep_name)
    #Linearisation preparation and cmputation from Sweep 2 to n
    for k in range (1, n + 1):
        sweep_name=mysweep.format(k)
        for i in range (1, n + 1):
            interval_name=myinterval.format(i)  
            sol.linearisedPimpleDyMFoam(basepath, folder_name, sweep_name, i)
            pre.prepareNextLinearization(folder_name, k, i)
    # Preparation and Computation of shootingUpdate
    for k in range (1, n + 1):
        for i in range (2, n + 1):
            sweep_name=mysweep.format(k)
            #if not k==n:
            m=1
            print("Starting shooting update process for " + sweep_name + ".\n")
            #for i in range(2, n + 1):
            interval_name=myinterval.format(i)
            pre.prepareShootingUpdate(basepath, folder_name, sweep_name, k, i)
            interval_name=myinterval.format(m)
            sol.computeShootingUpdate(folder_name, sweep_name, interval_name)
            post.shootingUpdateP(folder_name, sweep_name, interval_name, k, m)
            m=m + 1
            if k==n-1:
                print("Steffensen's Method terminated. Sweep " + str(k) + "updated.")
                return(0)
    end_time = time.time()
    elapsed_time = end_time - start_time
    num_minutes=int(elapsed_time/60)
    num_seconds=elapsed_time%60
    print("Elapsed time:",num_minutes, "minutes and" , num_seconds, "seconds")

########################################### OLD
def OLD_computeSteffensenMethod(basepath, folder_name): #Works in Steffensens path. Now we want everything in the same folder
    start_time=time.time()
    print("\n\nStarting Steffensen's Method for " + folder_name + ".\n")
    #Initialisation of Sweep 1  
    sweep_name="sweep1"
    pre.initializeLinearisation(folder_name, sweep_name)
    #Linearisation preparation and cmputation from Sweep 2 to n
    for k in range (1, n + 1):
        sweep_name=mysweep.format(k)
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = []
            for i in range (1, n + 1):
                futures.append(executor.submit(linearisedPimpleDyMFoam, basepath, folder_name, sweep_name, i))
                #interval_name=myinterval.format(i)  
                #sol.linearisedPimpleDyMFoam(basepath, folder_name, sweep_name, i)
                concurrent.futures.wait(futures)
                pre.prepareNextLinearization(folder_name, k, i)
    # Preparation and Computation of shootingUpdate
    for k in range (1, n + 1):
        for i in range (2, n + 1):
            sweep_name=mysweep.format(k)
            #if not k==n:
            m=1
            print("Starting shooting update process for " + sweep_name + ".\n")
            #for i in range(2, n + 1):
            interval_name=myinterval.format(i)
            pre.prepareShootingUpdate(basepath, folder_name, sweep_name, k, i)
            interval_name=myinterval.format(m)
            sol.computeShootingUpdate(steffensen_path, folder_name, sweep_name, interval_name)
            post.shootingUpdateP(folder_name, sweep_name, interval_name, k, m)
            m=m + 1
            if k==n-1:
                print("Steffensen's Method terminated. Sweep " + str(k) + "updated.")
                return(0)
    end_time = time.time()
    elapsed_time = end_time - start_time
    num_minutes=int(elapsed_time/60)
    num_seconds=elapsed_time%60
    print("Elapsed time:",num_minutes, "minutes and" , num_seconds, "seconds")


def VERY_OLDloop_pimpleDyMFoam(basepath, folder_name): #sequential Version of primal shooting without update
    for k in range(1, n + 1):
        sweep_name=mysweep.format(k)
        ## COMPUTE MY INTERVAL
        print("\nStarting shooting of " + sweep_name + "\n")
        for i in range(k, n + 1):
            sol.pimpleDyMFoam(basepath, folder_name, sweep_name,i)
        post.preparePostProcessing(folder_name, sweep_name)
        post.computePressureDropFoam(folder_name, sweep_name)
        while (k<n):
            pre.prepareMyNextSweep(k, folder_name)
            break
    return(myinterval, mysweep)

def OLD_loop_pimpleDyMFoam(basepath, folder_name): #Version V1 : Parallel call for all intervals within one sweep
    start_time=time.time()
    #with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []
        for k in range(1, n + 1):
            sweep_name = mysweep.format(k)
            print("\nStarting shooting of " + sweep_name + "\n")
            for i in range(k, n+1):
                futures.append(executor.submit(pimpleDyMFoam, basepath, folder_name, sweep_name, i))
            concurrent.futures.wait(futures)
            post.preparePostProcessing(basepath, folder_name, sweep_name)
            post.computePressureDropFoam(basepath, folder_name, sweep_name)
            if (k<n): #instead of while
                pre.prepareMyNextSweep(basepath, k, folder_name)
                #break
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
    bc.time(start_time)
    #return(myinterval, mysweep)
    
    
def BASH_loop_pimpleDyMFoam(basepath, folder_name, sweep_name, k): #Version V1 : Parallel call for all intervals within one sweep
    #with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
    print("\nStarting shooting of " + sweep_name + "\n")
    print("Starting EXECUTOR ... \n")
    
    os.chdir(project_path+"sh/")
    #pass k and n+1 to bash + pfade 
   
    
    subprocess.run(["chmod",  "u+x",  "./executor_pimpleDyMFoam.sh"])    
    subprocess.run(["./executor_pimpleDyMFoam.sh", basepath, folder_name, sweep_name, str(k), str(n)])    
    os.chdir(basepath)
#    with futures.ProcessPoolExecutor() as executor:
#        
#        for i in range(k, n+1):
#            executor.submit(pimpleDyMFoam, basepath, folder_name, sweep_name, i)
#            print("Starting pimpleDyMFoam for interval " + str(i) +"\n")
#        
#        print("Started all simulations and wait \n")
#    print("EXECUTOR terminated \n")
##   concurrent.futures.wait(futures)
    post.preparePostProcessing(basepath, folder_name, sweep_name)
    post.computePressureDropFoam(basepath, folder_name, sweep_name)
    if (k<n): #instead of while
        pre.prepareMyNextSweep(basepath, k, folder_name)
