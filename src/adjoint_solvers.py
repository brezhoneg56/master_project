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
from config import n, theta, T, a, deltaT, myinterval, mysweep, folder_name, maxCPU

def prepareAdjointDefectComputation(basepath, sweep_name, interval_name, previous_interval, i): #for computeDefect
    
    #Fetch shootingDefect from ref_Cases    
    src_shootingDefect = ref_cases + "shootingDefect/"
    dest_shootingDefect = basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingDefect/"
    try:
        shutil.copytree(src_shootingDefect, dest_shootingDefect)
    except Exception as e:
        print(e)
    startingTime=str(bc.decimal_analysis(theta + (i)*deltaT))
    endingTime=str(bc.decimal_analysis(theta + (i)*deltaT))
    adjointStartingTime=str(bc.decimal_analysis(-(theta + (i)*deltaT)))
    adjointEndingTime=str(bc.decimal_analysis(-(theta + (i)*deltaT))) #avant i

    #Fetch U, p, phi from current interval
    src_U=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + adjointStartingTime + "/Ua" ##Starts with -0.5
    src_p=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + adjointStartingTime + "/pa"
    src_phi=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + adjointStartingTime + "/phia"
    
    dest_U=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingDefect/0/UaInit_right"
    dest_p=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingDefect/0/paInit_right"
    dest_phi=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingDefect/0/phiaInit_right"

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

def postProcessingCopyfiles(i, destination_file, postPro_destination):
    interval_name=myinterval.format(i)
    for filename in os.listdir(destination_file + interval_name):                
        if filename.startswith('-0.') or filename.startswith(str(-theta)) or filename.startswith(str(-(theta + deltaT*n))):
            #os.path.join(destination_file + interval_name + "/" + filename, postPro_destination)
            bc.copytree(destination_file + interval_name + "/" + filename, postPro_destination + "/" + filename + "/")

def prepareAdjointPostProcessing(basepath, folder_name, sweep_name):
    destination_file=basepath + folder_name + '/' + sweep_name + '/'
    postPro_destination=destination_file + "adjoint_postProcessing"
    os.chdir(destination_file)
    shutil.copytree(ref_cases_mod_def + "constant/", postPro_destination + "/constant/" )
    shutil.copytree(ref_cases_mod_def + "system/", postPro_destination + "/system/" )
    #with futures.ProcessPoolExecutor(max_workers=maxCPU) as executor:
    for i in range(1, n+1):
            #print("copyfile in loop" + str(i))
        #executor.submit(postProcessingCopyfiles, i, destination_file, postPro_destination)
        postProcessingCopyfiles(i, destination_file, postPro_destination)
    print("ready for postProcessing of " + sweep_name + "...\n")

def computeAdjointPressureDropFoam(basepath, folder_name, sweep_name):
    os.chdir(basepath + folder_name + '/' + sweep_name + "/adjoint_postProcessing/")
    #Open a log file for pressureDrop and timers       
    with open("adjoint_pressureDrop.txt","w"):
        result=os.system('computeAdjointPressureDropFoam start end > "adjoint_pressureDrop.txt')            
        print("\nComputation of Pressure Drop for " + sweep_name + " is done.\nWriting into adjoint_pressureDrop.txt ...")
    
    #Writing the pressureDrop line into txt file
    with open("adjoint_pressureDrop.txt","r") as f:
        os.chdir(basepath + folder_name)
        with open("pressureDropvalues.txt","a") as mapression:
            #mapression.write("\n\nShooting of " + sweep_name + ":\n---------------------------------\n" )
            for line in f:
                if "adjointPressureDrop" in line:
                    pressure=mapression.write(line)
                    print(line)
        mapression.close()
    f.close()
    os.chdir(basepath) #back to main path
    print("Done.\n")


def computeAdjointDefect(basepath, sweep_name, k):
    #int1_Defect(basepath, sweep_name)
    print("\nComputing Adjoint Defect ...")
    for i in range(n-1, 0, -1): # avant n-1 
        interval_name=myinterval.format(i)
        previous_interval=myinterval.format(i+1) #avant i-1 mais on va à l'envers
        prepareAdjointDefectComputation(adjoint_path, sweep_name, interval_name, previous_interval, i)
        os.chdir(adjoint_path + folder_name + "/" + sweep_name + "/" + interval_name)
        with open("adjoint_shooting_defect_logfile"+sweep_name+"_"+interval_name+".txt","w") as logfile:
            os.chdir(adjoint_path + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingDefect")
            subprocess.run(['computeAdjointShootingDefect'], stdout=logfile, stderr=subprocess.STDOUT)        
    os.chdir(basepath)

def adjointPimpleDyMFoam(folder_name, sweep_name, i):
    interval_name=myinterval.format(i)
    pimple_path=adjoint_path + folder_name + "/" + sweep_name + "/" + interval_name   
    os.chdir(pimple_path) #Entering logfile path
    #print(pimple_path)    
    os.system('adjointPimpleDyMFoam >adjoint_pimple.log 2>&1')                
    print("Adjoint computation of " + interval_name + " is done. Writing into pimple.log ...")
    os.chdir(adjoint_path) #back to main path
    return(0)
    
def loop_adjoint_pimpleDyMFoam(folder_name, sweep_name, k): #Version V1 : Parallel call for all intervals within one sweep
    print("\nStarting shooting of " + sweep_name + "\n")
    print("Starting ADJ EXECUTOR ... \n")
    with futures.ProcessPoolExecutor(max_workers=maxCPU) as executor:
        for i in range(n, k-1, -1): #(n, k-1, -1)
            executor.submit(adjointPimpleDyMFoam, folder_name, sweep_name, i)
        #adjointPimpleDyMFoam(folder_name, sweep_name, i)
            print("Starting adjointPimpleDyMFoam for interval " + str(i))
        print("\n\nAll simulations started. Waiting... \n")
    print("ADJ EXECUTOR adjointPimpleDyMFoam terminated.\n\n")
    #A priori inutiale:
    prepareAdjointPostProcessing(adjoint_path, folder_name, sweep_name)
    computeAdjointPressureDropFoam(adjoint_path, folder_name, sweep_name)
    

def copy_adjointlinearization(basepath, folder_name, sweep_name, i, fvSchemes_path, fvSolution_path):    
        interval_name=myinterval.format(i)
        #New Paths for linP and linU, taking the Newton Update into account:
        interval_name=myinterval.format(i)
        linP_path=ref_cases + "/boundaryConditions/linPa0"
        linU_path=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingDefect/0/linUaDefect"        
        
        starttime_dest=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + str(-(bc.decimal_analysis(theta + (i)*deltaT)))
        print("Start for LIN COPY:" + str(starttime_dest))
        #Copy lin files
        shutil.copy2(linP_path, starttime_dest + "/linPa")
        shutil.copy2(linU_path, starttime_dest + "/linUa")
        
        #Copy fv files
        shutil.copy(fvSchemes_path, basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/system")
        shutil.copy(fvSolution_path, basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/system")
        
        #bc.check_existence(ref_cases + "/boundaryConditions/", "linU")

def prepareNextAdjointLinearization(basepath, folder_name, k):
    if not os.path.exists(folder_name):
        print("ERROR: No such file or directory. Exiting Shooting Manager")
        sys.exit()    
    #if k<=n:
    sweep_name=mysweep.format(k)
        
    #Paths for lin and fv files, OLD paths without Newton Update 
    fvSchemes_path=ref_cases + "/controlBib/fvSchemes"
    fvSolution_path=ref_cases + "/controlBib/fvSolution"

    #with futures.ProcessPoolExecutor(max_workers=maxCPU) as executor:    
    for i in range(n, 0, -1): #avant n-1
            #executor.submit(copy_adjointlinearization, basepath, folder_name, sweep_name, i, fvSchemes_path, fvSolution_path)
        copy_adjointlinearization(basepath, folder_name, sweep_name, i, fvSchemes_path, fvSolution_path)

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
    print("linfor " + sweep_name)
    
    #with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
    print("\nStarting adjoint linearisation of " + sweep_name + "\n")
    print("Starting LIN ADJ EXECUTOR ... \n")
    #if k==1:
    #    pre.initializeLinearisation(basepath, folder_name, sweep_name)
    #for i in range(1, n+1):#k, essayer 2
    prepareNextAdjointLinearization(adjoint_path, folder_name, k)
    with futures.ProcessPoolExecutor(max_workers=maxCPU) as executor:        
        for i in range(1, n+1):#k.essayer 2, on ne lin pas dans 1
            executor.submit(adjointLinearisedPimpleDyMFoam, adjoint_path, folder_name, sweep_name, i)
            print("Starting adjointLinearisedPimpleDyMFoam for interval " + str(i))
        
        print("\n\nAll Adjoint linearisations started, Waiting... \n")
    print("LIN ADJ EXECUTOR terminated \n\n")
    
def computeAdjointNewtonUpdate(basepath, sweep_name, i, k):
    interval_name=myinterval.format(i)
    pre.prepareAdjointNewtonUpdate(basepath, folder_name, sweep_name, k, interval_name, i)
    os.chdir(basepath + folder_name + "/" + sweep_name + "/" + interval_name)     
    with open("rel_adj_newton_update_logfile"+sweep_name+"_"+interval_name+".txt","w") as logfile:
        os.chdir(basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingUpdate")
        subprocess.run(['relaxedComputeAdjointNewtonUpdate'], stdout=logfile, stderr=subprocess.STDOUT)  #before : computeNewtonUpdate
    os.chdir(basepath)
    if i<n and k<n:
        post.prepareNextAdjointNewton(basepath, folder_name, sweep_name, k, interval_name, i)

def loop_computeAdjointNewtonUpdate(basepath, folder_name, sweep_name, k):
    print("\nComputing Adjoint Newton Update...")
    with futures.ProcessPoolExecutor(max_workers=maxCPU) as executor:
        for i in range(n-k-1, 0, -1): #déart à n au lieu de n-1
             executor.submit(computeAdjointNewtonUpdate, basepath, sweep_name, i, k)
        #computeAdjointNewtonUpdate (basepath, sweep_name, i, k)


#def computeAdjoint(basepath):
#    #Starting Timer for entire Process
#    start_time=time.time()
#    
#    #Verify if folder_name exists, and offers to delete it if so
#    bc.checking_existence(basepath, folder_name)
#    print("Preparing files for adjoint computation...\n")
#    
#    #Preparing files for adjoint computation
#    #pre.prepareTimeFolders(folder_name, "sweep1")
#    pre.initializeMyAdjoint(folder_name, "sweep1")
#    print("done")
#    #Initialization loop over all Sweeps    
#    for k in range (1, n+1):
#        sweep_name=mysweep.format(k)
#        
#        #Renaming Time folder with "-"
#        pre.prepareTimeFolders(folder_name, sweep_name)
#    
#        #Intermediate Timer
#        elapsed_time = time.time() - start_time        
#        bc.timer_and_write(basepath, elapsed_time, "copying files", "adjoint folder")
#    
#  
#        sweep_name=mysweep.format(k)
#        loop_adjoint_pimpleDyMFoam(folder_name, sweep_name, k)
#        
#        #Computing Adjoint Defect
#        print("\nADJOINT DEFECT...\n")
#        computeAdjointDefect(adjoint_path, sweep_name, k)
#        
#        #Computing Adjoint Linearization
#        print("\nADJOINT LINEARIZATION...\n")
#        loop_linearised_adjoint_pimpleDyMFoam(folder_name, sweep_name, k)
#        
#        #Starting Adjoint Newton Update
#        loop_computeAdjointNewtonUpdate(basepath, folder_name, sweep_name, k)
#        
#        #Renaming Time folder with "-"
#        sweep_name=mysweep.format(k+1)
#        #pre.prepareTimeFolders(folder_name, sweep_name)
#        
#        if k<n: #A FAIRE !!!
#            pre.prepareMyNextAdjointSweep(basepath, k, folder_name)
#       
#    #Final Timer
#    elapsed_time = time.time() - start_time        
#    bc.timer_and_write(elapsed_time, "adjointPimpleDyMFoam", folder_name)


def combined_shooting_stef_update():
    basepath=primal_path
    #Verify if primal folder_name exists, and offers to delete it if so
    bc.checking_existence(primal_path, folder_name)
    
    #Verify if adjoint folder_name exists, and offers to delete it if so
    bc.checking_existence(adjoint_path, folder_name)

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

        #Newline for defect
        sol.loop_computeDefect(basepath, sweep_name, k)

        #Starting intermediate timer

        #Starting linearisation for Sweep k over all subintervals
        sol.loop_linearisedPimpleDyMFoam(basepath, folder_name, sweep_name, k) #One sync version

        #Starting Newton Update
        sol.loop_computeNewtonUpdate(basepath, folder_name, sweep_name, k)
        
        ###### Adjoint
        start_time=time.time()
        
        basepath=adjoint_path

        sweep_name=mysweep.format(k)
        
        #Renaming Time folder with "-"
        pre.prepareTimeFolders(folder_name, sweep_name)
        
        #Preparing files for adjoint computation
        if sweep_name=="sweep1":
            pre.initializeMyAdjoint(folder_name, sweep_name)
        
        sweep_name=mysweep.format(k)
        loop_adjoint_pimpleDyMFoam(folder_name, sweep_name, k)
        
        #Computing Adjoint Defect
        print("\nADJOINT DEFECT...\n")
        computeAdjointDefect(adjoint_path, sweep_name, k)
        
        #Computing Adjoint Linearization
        print("\nADJOINT LINEARIZATION...\n")
        loop_linearised_adjoint_pimpleDyMFoam(folder_name, sweep_name, k)
        
        #Starting Adjoint Newton Update
        loop_computeAdjointNewtonUpdate(basepath, folder_name, sweep_name, k)
        
        
        ###############
        basepath=primal_path
        erasing="no"
        # Deleting Files after Sweep k Done    
        if erasing=="yes":
            print("Deleting files...\n")
            post.erase_all_files(basepath, folder_name, k)
            print("The files were succefully deleted. See exceptions above.")
        
        #Stopping intermediate timer and writing into logfile
        elapsed_time = time.time() - start_time
        bc.timer_and_write(basepath, elapsed_time, "subintervals", sweep_name)
        
    print("Steffensen's Method terminated. Sweep " + str(k) + " updated.")

    #Stopping timer and writing into logfile
    total_time=time.time()-start_time_ALL
    bc.timer_and_write(basepath, total_time, folder_name, sweep_name)
    post.store_all_values(basepath, folder_name)