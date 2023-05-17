# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 17:40:10 2023

@author: jcosson
"""
import os
import shutil
import sys
from src import boundary_conditions as bc
import subprocess
import multiprocessing
import glob
from config import primal_path, primitive_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path
from config import n, theta, T, a, t, deltaT, myinterval, mysweep
from concurrent.futures import ThreadPoolExecutor
###########################################################################

##################  PRIMAL PRIMITIVE PREPROCESSING ########################
def copyShootDirs(basepath, x, folder_name, previous_sweep_name, sweep_name):
        interval_name=myinterval.format(x)
        source_interval=basepath + folder_name + "/" + previous_sweep_name + "/" + interval_name
        destination_interval=basepath + folder_name + "/" + sweep_name
        shutil.copytree(source_interval,os.path.join(destination_interval, os.path.basename(source_interval)))

def preparenextSweepStartingFiles(basepath, folder_name, previous_sweep_name, sweep_name, i):
    interval_name=myinterval.format(i)
    destination_constant=basepath + folder_name + "/" + sweep_name + "/" + interval_name
    destination_system=basepath + folder_name + "/" + sweep_name + "/" + interval_name
    previous_interval_name=myinterval.format(i-1)
    endTime=bc.decimal_analysis(theta + deltaT*(i-1))
    source_constant=basepath + folder_name + "/" + previous_sweep_name + "/" + interval_name + '/constant'
    source_system=basepath + folder_name + "/" + previous_sweep_name + "/" + interval_name + '/system'
    source_endTime=basepath + folder_name + "/" + previous_sweep_name + "/" + previous_interval_name + '/' + str(endTime)        
    destination_endTime=basepath + folder_name + "/" + sweep_name + "/" + interval_name        
    
    shutil.copytree(source_constant,os.path.join(destination_constant, os.path.basename(source_constant)))
    shutil.copytree(source_system,os.path.join(destination_system, os.path.basename(source_system)))
    shutil.copytree(source_endTime,os.path.join(destination_endTime, os.path.basename(source_endTime)))
    print("Computing for: " + sweep_name + " and " + interval_name + ". Previous end time, that is current start time: " + str(endTime))

def prepareMyNextSweep(basepath, k, folder_name):
    #Prepare all shooting intervals of next sweep for computation 
    sweep_name=mysweep.format(k+1)#k+1
    previous_sweep_name=mysweep.format(k)#k
    os.path.join(folder_name,sweep_name)
    print("\nStarting shooting of " + sweep_name + ". ") 
    # Copy Directories that were already shoot. Warning : put that after the computations
    #Copy already shoot Directories in the next Sweep 
    for x in range(1,k+1):#k+1
        copyShootDirs(basepath, x, folder_name, previous_sweep_name, sweep_name)
    #Preparing shooting directories from sweep1 data 
    for i in range(k+1, n+1): #will become k + 1, n + 1 because of first loop being put into the big loop
        preparenextSweepStartingFiles(basepath, folder_name, previous_sweep_name, sweep_name, i)
    #with ThreadPoolExecutor() as executor:
    #    futures = [executor.submit(preparenextSweepStartingFiles, basepath,  folder_name, previous_sweep_name, sweep_name, i) for i in range(k + 1, n + 1)]
    #    for future in futures:
    #        future.result()

def seq_prepareMyNextSweep(basepath, k, folder_name): #Sequential
    myinterval="interval{}"
    mysweep="sweep{}"
    sweep_name=mysweep.format(k + 1)
    previous_sweep_name=mysweep.format(k)
    sweep_path=os.path.join(folder_name,sweep_name)
    print("\nStarting shooting of " + sweep_name + ". ") 
    # Copy Directories that were already shoot. Warning : put that after the computations
    for x in range(1,k + 1):
        interval_name=myinterval.format(x)
        source_interval=basepath + folder_name + "/" + previous_sweep_name + "/" + interval_name
        destination_interval=basepath + folder_name + "/" + sweep_name
        shutil.copytree(source_interval, os.path.join(destination_interval, os.path.basename(source_interval)))
    #pimpleDyMFoam(folder_name, sweep_name, interval_name)
    #preparePostProcessing(folder_name, sweep_name)
    #computePressureDropFoam(folder_name, sweep_name)    
    
    #Preparing shooting directories from sweep1 data 
    for i in range(k + 1,n + 1): #will become k + 1, n + 1 because of first loop being put into the big loop
        interval_name=myinterval.format(i)
        destination_constant=basepath + folder_name + "/" + sweep_name + "/" + interval_name
        destination_system=basepath + folder_name + "/" + sweep_name + "/" + interval_name
        previous_interval_name=myinterval.format(i-1)
        #startTime=decimal_analysis(theta + deltaT*(i-2))
        endTime=bc.decimal_analysis(theta + deltaT*(i-1))
        
        source_constant=basepath + folder_name + "/" + previous_sweep_name + "/" + interval_name + '/constant'
        source_system=basepath + folder_name + "/" + previous_sweep_name + "/" + interval_name + '/system'
        source_endTime=basepath + folder_name + "/" + previous_sweep_name + "/" + previous_interval_name + '/' + str(endTime)        
        destination_endTime=basepath + folder_name + "/" + sweep_name + "/" + interval_name        
        
        shutil.copytree(source_constant, os.path.join(destination_constant, os.path.basename(source_constant)))
        shutil.copytree(source_system, os.path.join(destination_system, os.path.basename(source_system)))
        shutil.copytree(source_endTime, os.path.join(destination_endTime, os.path.basename(source_endTime)))
        
        print("Computing for: " + sweep_name + " and " + interval_name + ". Previous end time, that is current start time: " + str(endTime))
###########################################################################

#################  PRIMAL STEFFENSEN PREPROCESSING  #######################
def prepareShootingUpdate(basepath, folder_name, sweep_name, k, i):#should start from sweep2, after interval2 is done
    #Copy Violet, Red, Blue, Green and Orange to prepare yellow (cf model)
    interval_name=myinterval.format(i-1)
    next_interval=myinterval.format(i)
    print('Preparing Shooting Update for ' + sweep_name + ".\n")
    next_sweep=mysweep.format(k + 1)
    if not os.path.exists(basepath + folder_name + "/" + sweep_name + "/preProcessing/"):
        #shutil.rmtree(basepath + folder_name + "/" + sweep_name + "/preProcessing/")
        os.mkdir(basepath + folder_name + "/" + sweep_name + "/preProcessing/")
        os.mkdir(basepath + folder_name + "/" + sweep_name + "/preProcessing/0/")
    zero_shootingUpdate=basepath + folder_name + "/" + sweep_name + "/preProcessing/0/"
    #print("Copy code VIOLET for " + sweep_name + " and " + interval_name + "\n")
    src_violet_folder=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + str(bc.decimal_analysis(theta + (i-2)*deltaT)) + "/"
    shutil.copy(src_violet_folder + "p", zero_shootingUpdate + "pStart_left")
    shutil.copy(src_violet_folder + "U", zero_shootingUpdate + "UStart_left")
    shutil.copy(src_violet_folder + "Uf", zero_shootingUpdate + "UfStart_left")
    shutil.copy(src_violet_folder + "phi", zero_shootingUpdate + "phiStart_left")
    print("Copy code VIOLET done.")
    #print("Copy code RED for " + sweep_name + " and " + interval_name + ".\n")
    src_red_folder=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + str(bc.decimal_analysis(theta + (i-1)*deltaT)) + "/"
    shutil.copy(src_red_folder + "p", zero_shootingUpdate + "pEnd_left")
    shutil.copy(src_red_folder + "U", zero_shootingUpdate + "UEnd_left")
    shutil.copy(src_red_folder + "Uf", zero_shootingUpdate + "UfEnd_left")
    shutil.copy(src_red_folder + "phi", zero_shootingUpdate + "phiEnd_left")
    print("Copy code RED done.")
    #print("Copy code BLUE.\n")
    shutil.copy(src_red_folder + "linU", zero_shootingUpdate + "dUdu")
    shutil.copy(src_red_folder + "linP", zero_shootingUpdate + "dPdp")
    shutil.copy(src_red_folder + "linUf", zero_shootingUpdate + "dUduf")
    print("Copy code BLUE done.")
    #print("Copy code GREEN.\n")
    src_green_folder=basepath + folder_name + "/" + next_sweep + "/" + interval_name + "/" + str(bc.decimal_analysis(theta + (i-2)*deltaT)) + "/"
    shutil.copy(src_green_folder + "p", zero_shootingUpdate + "shootingUpdateP_left") #instead of shootingUpdateP_left
    shutil.copy(src_green_folder + "U", zero_shootingUpdate + "shootingUpdateU_left")
    shutil.copy(src_green_folder + "Uf", zero_shootingUpdate + "shootingUpdateUf_left")
    shutil.copy(src_green_folder + "phi", zero_shootingUpdate + "shootingUpdatePhi_left")
    print("Copy code GREEN done.")
    #print("Copy code ORANGE.\n")
    src_orange_folder=basepath + folder_name + "/" + sweep_name + "/" + next_interval + "/" + str(bc.decimal_analysis(theta + (i-1)*deltaT)) + "/"
    shutil.copy(src_orange_folder + "p", zero_shootingUpdate + "pStart_right")
    shutil.copy(src_orange_folder + "U", zero_shootingUpdate + "UStart_right")
    shutil.copy(src_orange_folder + "Uf", zero_shootingUpdate + "UfStart_right")
    shutil.copy(src_orange_folder + "phi", zero_shootingUpdate + "phiStart_right")
    print("Copy code ORANGE done.")
    if not os.path.exists(basepath + folder_name + "/" + sweep_name + "/preProcessing/constant/"):
        src_constant=basepath + folder_name + "/" + sweep_name + "/" + myinterval.format(i) + "/constant/"
        src_system=basepath + folder_name + "/" + sweep_name + "/" + myinterval.format(i) + "/system/"
        shutil.copytree(src_constant, basepath + folder_name + "/" + sweep_name + "/preProcessing/constant/")
        shutil.copytree(src_system, basepath + folder_name+"/"+sweep_name+"/preProcessing/system/")
    print("Ready for copy code YELLOW")

###########################################################################

####################  LINEARIZATION PREPROCESSING #########################
def initializeLinearisation(basepath, folder_name, sweep_name):
    #### IS ONLY THOUGHT FOR SWEEP1
    #Copy files to prepare linearisedPimpleDyMFoam
    print("\n")
    if os.path.exists(folder_name):
        print("Preparing linearisation...\n")
    else:
        print("ERROR: No such file or directory. Exiting Shooting Manager")
        sys.exit()
    
    #Paths for variables
    linP_path=ref_cases + "/boundaryConditions/linP"
    linU_path=ref_cases + "/boundaryConditions/linU"
    fvSchemes_path=ref_cases + "/controlBib/fvSchemes"
    fvSolution_path=ref_cases + "/controlBib/fvSolution"
    
    #Copy Sweep k, interval i : preparing sweep1
    #shutil.copytree(primitive_path + folder_name + "/sweep1/" , basepath + folder_name + "/sweep1/")
    
    for i in range(1, n + 1):
        interval_name=myinterval.format(i)
        starttime_dest=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + str(bc.decimal_analysis(theta + (i-1)*deltaT))
        print(str(bc.decimal_analysis(theta + (i-1)*deltaT)))
    
        shutil.copy2(linP_path, starttime_dest)
        shutil.copy2(linU_path, starttime_dest)
        #copy fv file
        shutil.copy(fvSchemes_path, basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/system")
        shutil.copy(fvSolution_path, basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/system")

def prepareNextLinearization(basepath, folder_name, k, i):
    if k+1<=n:
        sweep_name=mysweep.format(k+1) 
        #MAINTENANT LE PROCHAIN "ACTUEL SWEEP", donc k + 1
        #if not os.path.exists(basepath + folder_name + "/" + sweep_name):
        #    os.mkdir(basepath + folder_name + "/" + sweep_name)
        #    shutil.copytree(primitive_path + folder_name + "/" + sweep_name + "/interval1/" , basepath + folder_name + "/" + sweep_name + "/interval1/")
    
        #for i in range(1, n + 1):
        interval_name=myinterval.format(i)
        #if not os.path.exists(basepath + folder_name + "/" + sweep_name + "/" + interval_name):
        #    shutil.copytree(primitive_path + folder_name + "/" + sweep_name + "/" + interval_name , basepath + folder_name + "/" + sweep_name + "/" + interval_name)
        linP_path=ref_cases + "/boundaryConditions/linP"
        linU_path=ref_cases + "/boundaryConditions/linU"
        fvSchemes_path=ref_cases + "/controlBib/fvSchemes"
        fvSolution_path=ref_cases + "/controlBib/fvSolution"
        
        #copy theta dir
        starttime_dest=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + str(bc.decimal_analysis(theta + (i-1)*deltaT))
        shutil.copy2(linP_path, starttime_dest)
        shutil.copy2(linU_path, starttime_dest)
        #copy fv file
        shutil.copy(fvSchemes_path, basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/system")
        shutil.copy(fvSolution_path, basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/system")
        print("Files successfully copied for " + interval_name + ". Ready for next linearisation.")


        
 

