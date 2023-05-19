# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 09:42:28 2023

@author: jcosson
"""
import os
import time
import config as c
import subprocess
from concurrent import futures

from config import primal_path, primitive_path, steffensen_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path;
from config import n, theta, T, a, t, deltaT, myinterval, mysweep, folder_name;
from src import solvers as sol, preprocessing as pre, postprocessing as post, boundary_conditions as bc
import sys
import shutil
import concurrent.futures

################                  PATH                     ################
c.headings()
################           CHOICE OF COMPUTATION           ################
#Primitive shooting :
basepath=primitive_path
os.chdir(basepath)

def checking_existence(folder_name):
    if os.path.exists(folder_name):
            ans=input("WARNING: Directory " + folder_name + " already exists. Do you want to replace it ? (Y/N)     \n   \n")
            if ans=="Y" or ans=="y":
                print("Deleting files...\n")
                for g in range(1, n + 1):
                    if os.path.exists("sweep" + str(g)):
                        shutil.rmtree("sweep" + str(g))
                shutil.rmtree(folder_name)
                #os.mkdir(folder_name)
                
            else:
                sys.exit()
    return(folder_name)


def the_shooting_update_for_all(sweep_name, k, i, j):
    m=1 #Counter for Shooting update is always i-1
    print("Starting shooting update process for " + sweep_name + ".\n")
    #for i in range(2, n + 1):
    interval_name=myinterval.format(i)
    print("j="+str(j))
    print("n="+str(n))
    if j<=n:
        print("Shooting Update process started from " + interval_name + " for " + sweep_name)
        pre.prepareShootingUpdate(basepath, folder_name, sweep_name, k, j)
    interval_name=myinterval.format(m)
    #if k>1:
    
    sol.computeShootingUpdate(basepath, folder_name, k, i)
    post.shootingUpdateP(basepath, folder_name, sweep_name, interval_name, k, m)
    m=m+1 #Counter for Shooting Update
    

def primal_shooting_stef_update(basepath):
    g=1
    countershooting=1
##Function:
    checking_existence(folder_name)
##
    start_time_ALL=time.time()
    bc.sweep_1_initialization(basepath, folder_name)

# STARTING MAIN LOOP
    for k in range(1, n+1):
        start_time=time.time()
        sweep_name = mysweep.format(k)
        
        #sol.loop_pimpleDyMFoam(basepath, folder_name, sweep_name, k)
        ## here its the function above:
        print("\nStarting shooting of " + sweep_name + "\n")
        print("Starting EXECUTOR ... \n")
        with futures.ProcessPoolExecutor(max_workers=13) as executor:
            for i in range(k, n+1):
                executor.submit(sol.pimpleDyMFoam, basepath, folder_name, sweep_name, i)
                print("Starting pimpleDyMFoam for interval " + str(i))
            print("\n\nAll simulations started. Waiting... \n")
        print("EXECUTOR pimpleDyMFoam terminated.\n\n")
        post.preparePostProcessing(basepath, folder_name, sweep_name)
        post.computePressureDropFoam(basepath, folder_name, sweep_name)
        if k<n: #instead of while
            pre.prepareMyNextSweep(basepath, k, folder_name)
        ###########
        elapsed_time = time.time() - start_time
        num_minutes=int(elapsed_time / 60)
        num_seconds=elapsed_time % 60
        print("Elapsed time for primitive Shooting: " + str(round((num_minutes),2)) + " minutes and " + str(num_seconds) + " seconds.")
        ## Function write_time        
        os.chdir(basepath + folder_name)
        with open("pressureDropvalues.txt","a") as mytime:
            time_pimple="Elapsed time for pimpleDyMFoam in " + sweep_name + ": " + str(round((num_minutes),2)) + " minutes and " + str(num_seconds) + " seconds." 
            mytime.write(time_pimple)
            print(time_pimple)
        mytime.close()
        os.chdir(basepath) #back to main pa60th
        lin_time=time.time()

        sol.loop_linearisedPimpleDyMFoam(basepath, folder_name, sweep_name, k)
        
        elapsed_time = time.time() - lin_time
        num_minutes=int(elapsed_time / 60)
        num_seconds=elapsed_time % 60
        print("Elapsed time for linearisation: " + str(num_minutes) + " minutes and " + str(num_seconds) + " seconds.")
        os.chdir(basepath + folder_name)
        with open("pressureDropvalues.txt","a") as mytime:
       # lines=f.readlines()
            time_pimple="Elapsed time for linearisedPimpleDyMFoam in " + sweep_name + ": " + str(round((num_minutes),2)) + " minutes and " + str(num_seconds) + " seconds." 
            mytime.write(time_pimple)
            print(time_pimple)
        mytime.close()
        os.chdir(basepath) #back to main pa60th
        countershooting=countershooting+1
        print("g="+str(g))
        print("countershooting="+str(countershooting))
        for i, j in zip(range(2, n+1),range(countershooting, n+n)):
             the_shooting_update_for_all(sweep_name, k, i, j)
        if k==n-1:
            print("Steffensen's Method terminated. Sweep " + str(k) + " updated.")
        
        # Deleting Files after Sweep k Done        
        #ans=input("Do you want to delete useless files? (Y/N)     \n   \n")
        #if ans=="Y" or ans=="y":
        print("Deleting files...\n")
        post.erase_all_files(basepath, folder_name, k)
        elapsed_time = time.time() - start_time
        num_minutes=int(elapsed_time / 60)
        num_seconds=elapsed_time % 60
        print("Elapsed time for " + sweep_name + ": " + str(num_minutes) + " minutes and " + str(num_seconds) + " seconds.")
        os.chdir(basepath + folder_name)
        with open("pressureDropvalues.txt","a") as mytime:
            time_pimple="Elapsed time for " + sweep_name + ": " + str(round((num_minutes),2)) + " minutes and " + str(num_seconds) + " seconds." 
            mytime.write(time_pimple)
            print(time_pimple)
        mytime.close()
        os.chdir(basepath) #back to main path
    #Delete 2 last dirs:
    if k==n:
        try:
            for k in range(n-1, n+1):
                sweep_name=mysweep.format(k)
                for i in range(1, n+1):
                    interval_name=myinterval.format(i)
                    path_files=basepath+folder_name+"/"+sweep_name+"/"+interval_name
                    post.erasefiles(path_files)
        except:
            print("Problem deleting last files.")
    total_time=time.time()-start_time_ALL
    num_minutes=int(total_time / 60)
    num_seconds=total_time % 60
    print("Elapsed time: " + str(num_minutes) + " minutes and " + str(num_seconds) + " seconds.")
    os.chdir(basepath + folder_name)
    with open("pressureDropvalues.txt","a") as mytime:
        time_pimple="Elapsed time for " + sweep_name + ": " + str(round((num_minutes),2)) + " minutes and " + str(num_seconds) + " seconds." 
        mytime.write(time_pimple)
        print(time_pimple)
    mytime.close()
    os.chdir(basepath) #back to main pa60th
####################

primal_shooting_stef_update(basepath)
