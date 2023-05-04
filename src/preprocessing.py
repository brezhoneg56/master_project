# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 17:40:10 2023

@author: jcosson
"""
import os
import shutil
from src import boundary_conditions as bc
import subprocess
import multiprocessing
import sys
import glob
from config import primal_path, primitive_path, steffensen_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, basepath
from config import n, theta, T, a, t, deltaT, myinterval, mysweep
from concurrent.futures import ThreadPoolExecutor
########################################################################################################

################################# PRIMAL PRIMITIVE PREPROCESSING #######################################
def copyShootDirs(x, folder_name, previous_sweep_name, sweep_name):
        interval_name=myinterval.format(x)
        source_interval=basepath+folder_name+"/"+previous_sweep_name+"/"+interval_name
        destination_interval=basepath+folder_name+"/"+sweep_name
        shutil.copytree(source_interval,os.path.join(destination_interval,os.path.basename(source_interval)))

def preparenextSweepStartingFiles(folder_name, previous_sweep_name, sweep_name, i):
    interval_name=myinterval.format(i)
    destination_constant=basepath+folder_name+"/"+sweep_name+"/"+interval_name
    destination_system=basepath+folder_name+"/"+sweep_name+"/"+interval_name
    previous_interval_name=myinterval.format(i-1)
    endTime=bc.decimal_analysis(theta+deltaT*(i-1))
    source_constant=basepath+folder_name+"/"+previous_sweep_name+"/"+interval_name+'/constant'
    source_system=basepath+folder_name+"/"+previous_sweep_name+"/"+interval_name+'/system'
    source_endTime=basepath+folder_name+"/"+previous_sweep_name+"/"+previous_interval_name+'/'+str(endTime)        
    destination_endTime=basepath+folder_name+"/"+sweep_name+"/"+interval_name        
    
    shutil.copytree(source_constant,os.path.join(destination_constant,os.path.basename(source_constant)))
    shutil.copytree(source_system,os.path.join(destination_system,os.path.basename(source_system)))
    shutil.copytree(source_endTime,os.path.join(destination_endTime,os.path.basename(source_endTime)))
    print("Computing for: \n"+sweep_name+"\n"+interval_name+"\n"+"Previous end time, that is current start time: "+str(endTime))

def prepareMyNextSweep(k, folder_name):
    #Prepare all shooting intervals of next sweep for computation 
    sweep_name=mysweep.format(k+1)
    previous_sweep_name=mysweep.format(k)
    os.path.join(folder_name,sweep_name)
    print("\nStarting shooting of "+sweep_name+"\n") 
    # Copy Directories that were already shoot. Warning : put that after the computations
    #Copy already shoot Directories in the next Sweep 
    for x in range(1,k+1):
        copyShootDirs(x, folder_name, previous_sweep_name, sweep_name)
    #Preparing shooting directories from sweep1 data 
    #for i in range(k+1,n+1): #will become k+1, n+1 because of first loop being put into the big loop
    #    preparenextSweepStartingFiles(folder_name, previous_sweep_name, sweep_name, i)
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(preparenextSweepStartingFiles, folder_name, previous_sweep_name, sweep_name, i) for i in range(k+1, n+1)]
        for future in futures:
            _ = future.result()

########################################################################################################

################################# PRIMAL STEFFENSEN PREPROCESSING ######################################
def prepareShootingUpdate(folder_name, sweep_name, k, i):#should start from sweep2, after interval2 is done
    if k==0 and i==-1:
        return
    #Copy Violet, Red, Blue and Green to prepare yellow (cf model)
    interval_name=myinterval.format(i-1)
    print('Preparing Shooting Update for '+interval_name+".\n")
    next_sweep=mysweep.format(k+1)
    if not os.path.exists(steffensen_path+folder_name+"/"+sweep_name+"/preProcessing/"):
        os.mkdir(steffensen_path+folder_name+"/"+sweep_name+"/preProcessing/")
        os.mkdir(steffensen_path+folder_name+"/"+sweep_name+"/preProcessing/0/")
    zero_shootingUpdate=steffensen_path+folder_name+"/"+sweep_name+"/preProcessing/0/"
    print("Copy code VIOLET for "+sweep_name+" and "+interval_name+"\n")
    src_violet_folder=steffensen_path+folder_name+"/"+sweep_name+"/"+interval_name+"/"+str(bc.decimal_analysis(theta+(i-2)*deltaT))+"/"
    #dest_violet_folder=steffensen_path+folder_name+"/"+sweep_name+"/"+interval_name+"/"+str(startTime)
    shutil.copy(src_violet_folder+"p", zero_shootingUpdate+"pStart_left")
    shutil.copy(src_violet_folder+"U", zero_shootingUpdate+"UStart_left")
    shutil.copy(src_violet_folder+"Uf", zero_shootingUpdate+"UfStart_left")
    shutil.copy(src_violet_folder+"phi", zero_shootingUpdate+"phiStart_left")
    print("Copy code VIOLET done.\n")
    print("Copy code RED.\n"+sweep_name+" and "+interval_name)
    src_red_folder=steffensen_path+folder_name+"/"+sweep_name+"/"+interval_name+"/"+str(bc.decimal_analysis(theta+(i-1)*deltaT))+"/"
    print(src_red_folder)
    shutil.copy(src_red_folder+"p", zero_shootingUpdate+"pEnd_left")
    shutil.copy(src_red_folder+"U", zero_shootingUpdate+"UEnd_left")
    shutil.copy(src_red_folder+"Uf", zero_shootingUpdate+"UfEnd_left")
    shutil.copy(src_red_folder+"phi", zero_shootingUpdate+"phiEnd_left")
    print("Copy code RED done.\n")
    print("Copy code BLUE.\n")
    shutil.copy(src_red_folder+"linU", zero_shootingUpdate+"dUdu")
    shutil.copy(src_red_folder+"linP", zero_shootingUpdate+"dPdp")
    shutil.copy(src_red_folder+"linUf", zero_shootingUpdate+"dUduf")
    print("Copy code GREEN done.\n")
    print("Copy code GREEN.\n")
    src_green_folder=steffensen_path+folder_name+"/"+next_sweep+"/"+interval_name+"/"+str(bc.decimal_analysis(theta+(i-2)*deltaT))+"/"
    shutil.copy(src_green_folder+"p", zero_shootingUpdate+"shootingUpdateP_left")
    shutil.copy(src_green_folder+"U", zero_shootingUpdate+"shootingUpdateU_left")
    shutil.copy(src_green_folder+"Uf", zero_shootingUpdate+"shootingUpdateUf_left")
    shutil.copy(src_green_folder+"phi", zero_shootingUpdate+"shootingUpdatePhi_left")
    
    src_constant=steffensen_path+folder_name+"/"+sweep_name+"/"+myinterval.format(i)+"/constant/"
    src_system=steffensen_path+folder_name+"/"+sweep_name+"/"+myinterval.format(i)+"/constant/"
    shutil.copytree(src_constant, steffensen_path+folder_name+"/"+sweep_name+"/preProcessing/constant/")
    shutil.copytree(src_system, steffensen_path+folder_name+"/"+sweep_name+"/preProcessing/system/")

########################################################################################################

################################### LINEARIZATION PREPROCESSING ########################################
def initializeLinearisation(folder_name, sweep_name):
    #### IS ONLY THOUGHT FOR SWEEP1
    #Copy files to prepare linearisedPimpleDyMFoam
    print("\n")
    print("Preparing linearisation...\n")
    #Creating folders
    os.mkdir(steffensen_path+folder_name)
    #Paths for variables
    linP_path=ref_cases+"/boundaryConditions/linP"
    linU_path=ref_cases+"/boundaryConditions/linU"
    fvSchemes_path=ref_cases+"/controlBib/fvSchemes"
    fvSolution_path=ref_cases+"/controlBib/fvSolution"
    
    #Copy Sweep k, interval i : preparing sweep1
    shutil.copytree(primitive_path+folder_name+"/sweep1/" , steffensen_path+folder_name+"/sweep1/")
    
    for i in range(1, n+1):
        interval_name=myinterval.format(i)
        starttime_dest=steffensen_path+folder_name+"/"+sweep_name+"/"+interval_name+"/"+str(bc.decimal_analysis(theta+(i-1)*deltaT))
    
        shutil.copy2(linP_path, starttime_dest)
        shutil.copy2(linU_path, starttime_dest)
        #copy fv file
        shutil.copy(fvSchemes_path, steffensen_path+folder_name+"/"+sweep_name+"/"+interval_name+"/system")
        shutil.copy(fvSolution_path, steffensen_path+folder_name+"/"+sweep_name+"/"+interval_name+"/system")

    print("Prepartion done. Starting linearisedPimpleDyMFoam...\n")

def prepareNextLinearization(folder_name, k, i):
    if k+1<=n:
        sweep_name=mysweep.format(k+1) 
        #MAINTENANT LE PROCHAIN "ACTUEL SWEEP", donc k+1
        print("Preparing " +sweep_name+".\n")
        if not os.path.exists(steffensen_path+folder_name+"/"+sweep_name):
            os.mkdir(steffensen_path+folder_name+"/"+sweep_name)
            print("New Sweep added !")
            shutil.copytree(primitive_path+folder_name+"/"+sweep_name+"/interval1/" , steffensen_path+folder_name+"/"+sweep_name+"/interval1/")
    
        #for i in range(1, n+1):
        interval_name=myinterval.format(i)
        if not os.path.exists(steffensen_path+folder_name+"/"+sweep_name+"/"+interval_name):
            shutil.copytree(primitive_path+folder_name+"/"+sweep_name+"/"+interval_name , steffensen_path+folder_name+"/"+sweep_name+"/"+interval_name)
            print("New Interval copied !")        
        linP_path=ref_cases+"/boundaryConditions/linP"
        linU_path=ref_cases+"/boundaryConditions/linU"
        fvSchemes_path=ref_cases+"/controlBib/fvSchemes"
        fvSolution_path=ref_cases+"/controlBib/fvSolution"
        
        #copy theta dir
        starttime_dest=steffensen_path+folder_name+"/"+sweep_name+"/"+interval_name+"/"+str(bc.decimal_analysis(theta+(i-1)*deltaT))
        shutil.copy2(linP_path, starttime_dest)
        shutil.copy2(linU_path, starttime_dest)
        #copy fv file
        shutil.copy(fvSchemes_path, steffensen_path+folder_name+"/"+sweep_name+"/"+interval_name+"/system")
        shutil.copy(fvSolution_path, steffensen_path+folder_name+"/"+sweep_name+"/"+interval_name+"/system")
        print("Files successfully copied for "+interval_name+".\n")


        
 

