# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 17:40:10 2023

@author: jcosson
"""
import os
import shutil
import sys
from src import boundary_conditions as bc, postprocessing as post
import subprocess
import multiprocessing
from concurrent import futures
import glob
from config import basepath, primal_path, primitive_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, postPro_cases
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
    print("Preparing for: " + sweep_name + " and " + interval_name + ". Previous end time, that is new start time: " + str(endTime))

def prepareMyNextSweep(basepath, k, folder_name):
    
    #Prepare all shooting intervals of next sweep for computation 
    sweep_name=mysweep.format(k+1)#k+1
    previous_sweep_name=mysweep.format(k)#k
    os.path.join(folder_name,sweep_name)
    print("\nPreparing shooting of " + sweep_name + ". ") 
    
    # Copy Directories that were already shoot. Warning : put that after the computations
    for x in range(1,k+1):#k+1
        copyShootDirs(basepath, x, folder_name, previous_sweep_name, sweep_name)
    #Preparing shooting directories from sweep1 data 
    with futures.ProcessPoolExecutor(max_workers=13) as executor:    
        for i in range(k+1, n+1): #will become k + 1, n + 1 because of first loop being put into the big loop
            executor.submit(preparenextSweepStartingFiles, basepath, folder_name, previous_sweep_name, sweep_name, i)
        sweep_name=mysweep.format(k)

###########################################################################

#################  PRIMAL STEFFENSEN PREPROCESSING  #######################
def prepareShootingUpdate(basepath, folder_name, sweep_name, k, i):#should start from sweep2, after interval2 is done
    
    #Copy Violet, Red, Blue, Green and Orange to prepare yellow (cf model)
    interval_name=myinterval.format(i-1)
    next_interval=myinterval.format(i)
    next_sweep=mysweep.format(k + 1)
    if not os.path.exists(basepath + folder_name + "/" + sweep_name + "/preProcessing/"):
        os.mkdir(basepath + folder_name + "/" + sweep_name + "/preProcessing/")
        os.mkdir(basepath + folder_name + "/" + sweep_name + "/preProcessing/0/")
    zero_shootingUpdate=basepath + folder_name + "/" + sweep_name + "/preProcessing/0/"
    
    #Copy codes, see master_script
    src_violet_folder=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + str(bc.decimal_analysis(theta + (i-2)*deltaT)) + "/"
    shutil.copy(src_violet_folder + "p", zero_shootingUpdate + "pStart_left")
    shutil.copy(src_violet_folder + "U", zero_shootingUpdate + "UStart_left")
    shutil.copy(src_violet_folder + "Uf", zero_shootingUpdate + "UfStart_left")
    shutil.copy(src_violet_folder + "phi", zero_shootingUpdate + "phiStart_left")
    #print("Copy code VIOLET done.")

    src_red_folder=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + str(bc.decimal_analysis(theta + (i-1)*deltaT)) + "/"
    shutil.copy(src_red_folder + "p", zero_shootingUpdate + "pEnd_left")
    shutil.copy(src_red_folder + "U", zero_shootingUpdate + "UEnd_left")
    shutil.copy(src_red_folder + "Uf", zero_shootingUpdate + "UfEnd_left")
    shutil.copy(src_red_folder + "phi", zero_shootingUpdate + "phiEnd_left")
    #print("Copy code RED done.")

    shutil.copy(src_red_folder + "linU", zero_shootingUpdate + "dUdu")
    shutil.copy(src_red_folder + "linP", zero_shootingUpdate + "dPdp")
    shutil.copy(src_red_folder + "linUf", zero_shootingUpdate + "dUduf")
    #print("Copy code BLUE done.")

    src_green_folder=basepath + folder_name + "/" + next_sweep + "/" + interval_name + "/" + str(bc.decimal_analysis(theta + (i-2)*deltaT)) + "/"
    shutil.copy(src_green_folder + "p", zero_shootingUpdate + "shootingUpdateP_left") #instead of shootingUpdateP_left
    shutil.copy(src_green_folder + "U", zero_shootingUpdate + "shootingUpdateU_left")
    shutil.copy(src_green_folder + "Uf", zero_shootingUpdate + "shootingUpdateUf_left")
    shutil.copy(src_green_folder + "phi", zero_shootingUpdate + "shootingUpdatePhi_left")
    #print("Copy code GREEN done.")

    src_orange_folder=basepath + folder_name + "/" + sweep_name + "/" + next_interval + "/" + str(bc.decimal_analysis(theta + (i-1)*deltaT)) + "/"
    shutil.copy(src_orange_folder + "p", zero_shootingUpdate + "pStart_right")
    shutil.copy(src_orange_folder + "U", zero_shootingUpdate + "UStart_right")
    shutil.copy(src_orange_folder + "Uf", zero_shootingUpdate + "UfStart_right")
    shutil.copy(src_orange_folder + "phi", zero_shootingUpdate + "phiStart_right")
    #print("Copy code ORANGE done.")
    
    ###New linU and linP (Defect Update)
    src_linU=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingDefect/0/linUDefect"
    src_linP=ref_cases + "/boundaryConditions/linP0"
    dest_linU= basepath + folder_name + "/" + next_sweep + "/" + interval_name + "/" + str(bc.decimal_analysis(theta + (i-2)*deltaT)) + "/linU"
    dest_linP= basepath + folder_name + "/" + next_sweep + "/" + interval_name + "/" + str(bc.decimal_analysis(theta + (i-2)*deltaT)) + "/linP"
    shutil.copy(src_linU, dest_linU)
    shutil.copy(src_linP, dest_linP)

    #Copy of constant and system files
    if not os.path.exists(basepath + folder_name + "/" + sweep_name + "/preProcessing/constant/"):
        src_constant=basepath + folder_name + "/" + sweep_name + "/" + myinterval.format(i) + "/constant/"
        src_system=basepath + folder_name + "/" + sweep_name + "/" + myinterval.format(i) + "/system/"
        shutil.copytree(src_constant, basepath + folder_name + "/" + sweep_name + "/preProcessing/constant/")
        shutil.copytree(src_system, basepath + folder_name+"/"+sweep_name+"/preProcessing/system/")
    print(interval_name + " ready for copy code YELLOW")

###########################################################################

####################  LINEARIZATION PREPROCESSING #########################
def initializeLinearisation(basepath, folder_name, sweep_name):
    #### IS ONLY THOUGHT FOR SWEEP1
    #Copy files to prepare linearisedPimpleDyMFoam
    if not os.path.exists(folder_name):
        print("ERROR: No such file or directory. Exiting Shooting Manager")
        sys.exit()
    
    #Paths for lin and fv files
    linP_path=ref_cases + "/boundaryConditions/linP"
    linU_path=ref_cases + "/boundaryConditions/linU"
    fvSchemes_path=ref_cases + "/controlBib/fvSchemes"
    fvSolution_path=ref_cases + "/controlBib/fvSolution"
    with futures.ProcessPoolExecutor(max_workers=13) as executor:    
        for i in range(1, n + 1): #will become k + 1, n + 1 because of first loop being put into the big loop
            executor.submit(copy_linearization, folder_name, sweep_name, i, linP_path, linU_path, fvSchemes_path, fvSolution_path)

def copy_linearization(folder_name, sweep_name, i, linP_path, linU_path, fvSchemes_path, fvSolution_path):    
        interval_name=myinterval.format(i)
        starttime_dest=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + str(bc.decimal_analysis(theta + (i-1)*deltaT))
        
        #Copy lin files
        shutil.copy2(linP_path, starttime_dest + "/linP")
        shutil.copy2(linU_path, starttime_dest + "/linU")
        
        #Copy fv files
        shutil.copy(fvSchemes_path, basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/system")
        shutil.copy(fvSolution_path, basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/system")
        
        bc.check_existence(ref_cases + "/boundaryConditions/", "linU")

def prepareNextLinearization(basepath, folder_name, k, i):
    interval_name=myinterval.format(i)
    if not os.path.exists(folder_name):
        print("ERROR: No such file or directory. Exiting Shooting Manager")
        sys.exit()    
    #if k<=n:
    sweep_name=mysweep.format(k)
        
    #Paths for lin and fv files, OLD paths without Newton Update 
#   linP_path=ref_cases + "/boundaryConditions/linP"
#   linU_path=ref_cases + "/boundaryConditions/linU"
    fvSchemes_path=ref_cases + "/controlBib/fvSchemes"
    fvSolution_path=ref_cases + "/controlBib/fvSolution"
        
    #New Paths for linP and linU, taking the Newton Update into account:
    linP_path=ref_cases + "/boundaryConditions/linP0"
    linU_path=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingDefect/0/linUDefect"
        
    with futures.ProcessPoolExecutor(max_workers=13) as executor:    
        for i in range(2, n + 1): #avant c'était
            executor.submit(copy_linearization, folder_name, sweep_name, i, linP_path, linU_path, fvSchemes_path, fvSolution_path)

def prepareNewtonUpdate(basepath, folder_name, sweep_name, k, interval_name, i): #on st int2 et on prepare int3
    #Fetch shooting Update folder from postPro cases
    src_shootUpdate=ref_cases+"shootingDefect/"
    dest_shootUpdate=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingUpdate/" 
    if os.path.exists(dest_shootUpdate):
        print("Replacing file")
        post.erase_files(dest_shootUpdate)   
    shutil.copytree(src_shootUpdate, dest_shootUpdate)
    
    #Fetch data from EndTime folder
    src_data=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + str(bc.decimal_analysis(theta + (i)*deltaT))
    #print(str(bc.decimal_analysis(theta + (i)*deltaT)))
    dest_data=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingUpdate/0/"
    shutil.copy(src_data+"/linU", dest_data+"dUdu")
    shutil.copy(src_data+"/linUf", dest_data+"dUduf")
    shutil.copy(src_data+"/linP", dest_data+"dPdp")
    shutil.copy(src_data+"/U", dest_data+"UEnd_left")
    shutil.copy(src_data+"/p", dest_data+"pEnd_left")
    shutil.copy(src_data+"/phi", dest_data+"phiEnd_left")
    shutil.copy(src_data+"/Uf", dest_data+"UfEnd_left")
    shutil.copy(src_data+"/U", dest_data+"shootingUpdateU")
    shutil.copy(src_data+"/p", dest_data+"shootingUpdateP")
    shutil.copy(src_data+"/phi", dest_data+"shootingUpdatePhi")
    shutil.copy(src_data+"/Uf", dest_data+"shootingUpdateUf")


    