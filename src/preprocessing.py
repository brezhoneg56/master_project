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
#from .. import main
import sys
import glob
#sys.path.append('../')
from config import primal_path, primitive_path, steffensen_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, basepath
from config import n, theta, T, a, deltaT, myinterval, mysweep
from concurrent.futures import ThreadPoolExecutor

#### Primal Primitive

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
    #startTime=decimal_analysis(theta+deltaT*(i-2))
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
    sweep_path=os.path.join(folder_name,sweep_name)
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

#### Linearised
def prepareShootingUpdate(folder_name, sweep_name, interval_name, k, i):#should start from sweep2, after interval2 is done
    #Copy Violet, Red, Blue and Green to prepare yellow (cf model)
    print('Preparing Shooting Update for '+interval_name+".\n")
    next_sweep=mysweep.format(k)
    next_interval=myinterval.format(i)
    shootingUpdate=os.mkdir(steffensen_path+folder_name+"/"+sweep_name+"/shootingUpdate/")
    zero_shootingUpdate=os.mkdir(steffensen_path+folder_name+"/"+sweep_name+"/shootingUpdate/0/")
    current_sweep_current_interval=steffensen_path+folder_name+"/"+sweep_name+"/"+interval_name+"/"
    current_sweep_next_interval=steffensen_path+folder_name+"/"+sweep_name+"/"+next_interval+"/"
    next_sweep_current_interval=steffensen_path+folder_name+"/"+next_sweep+"/"+interval_name+"/"
    next_sweep_next_interval=steffensen_path+folder_name+"/"+next_sweep+"/"+next_interval+"/"
    print("Copy code VIOLET.\n")
    shutil.copy(current_sweep_current_interval+"p" , zero_shootingUpdate)
    print("Copy code RED.\n")

    print("Copy code BLUE.\n")

    print("Copy code GREEN.\n")

def initializeLinearisation(folder_name, sweep_name):
    #Copy files to prepare linearisedPimpleDyMFoam
    print("\n")
    print("Preparing linearisation...\n")
    #Creating folders
    os.mkdir(steffensen_path+folder_name)
    os.mkdir(steffensen_path+folder_name+"/sweep1/")
    #Paths for variables
    linP_path=ref_cases+"/boundaryConditions/linP"
    linU_path=ref_cases+"/boundaryConditions/linU"
    fvSchemes_path=ref_cases+"/controlBib/fvSchemes"
    fvSolution_path=ref_cases+"/controlBib/fvSolution"
    
    #Copy Sweep k, interval 1 : preparing sweep1/int1
    shutil.copytree(primitive_path+folder_name+"/sweep1/interval1/" , steffensen_path+folder_name+"/sweep1/interval1/")
    
    shutil.copy(linP_path, steffensen_path+folder_name+"/sweep1/interval1/"+str(theta)+"/")
    shutil.copy(linU_path, steffensen_path+folder_name+"/sweep1/interval1/"+str(theta)+"/")
    shutil.copy(fvSchemes_path, steffensen_path+folder_name+"/sweep1/interval1/system/")
    shutil.copy(fvSolution_path, steffensen_path+folder_name+"/sweep1/interval1/system/")
    print("Prepartion done. Starting linearisedPimpleDyMFoam...\n")

def prepareLinearization(folder_name, sweep_name, interval_name, i): ##WORKS
    #Paths for variables
    linP_path=ref_cases+"/boundaryConditions/linP"
    linU_path=ref_cases+"/boundaryConditions/linU"
    fvSchemes_path=ref_cases+"/controlBib/fvSchemes"
    fvSolution_path=ref_cases+"/controlBib/fvSolution"
    #Copy of constant and system files
    src_system=primitive_path+folder_name+"/"+sweep_name+"/"+interval_name+"/system/"
    dest_system=steffensen_path+folder_name+"/"+sweep_name+"/"+interval_name+"/system"
    src_constant=primitive_path+folder_name+"/"+sweep_name+"/"+interval_name+"/constant/"
    dest_constant=steffensen_path+folder_name+"/"+sweep_name+"/"+interval_name+"/constant"
    shutil.copytree(src_constant , dest_constant)
    shutil.copytree(src_system, dest_system)
    #copy theta dir
    starttime_source=primitive_path+folder_name+"/"+sweep_name+"/"+interval_name+"/"+str(bc.decimal_analysis(theta+(i-1)*deltaT))+"/"
    starttime_dest=steffensen_path+folder_name+"/"+sweep_name+"/"+interval_name+"/"+str(bc.decimal_analysis(theta+(i-1)*deltaT))+"/"
    time_source=glob.glob(primitive_path+folder_name+"/"+sweep_name+"/"+interval_name+"/0.*")
    time_dest=steffensen_path+folder_name+"/"+sweep_name+"/"+interval_name+"/"
    print(str(starttime_dest))
    shutil.copytree(time_source, time_dest)
    #copy lin files
    shutil.copy(linP_path, starttime_dest)
    shutil.copy(linU_path, starttime_dest)
    #copy fv files
    shutil.copy(fvSchemes_path, steffensen_path+folder_name+"/"+sweep_name+"/"+interval_name+"/system")
    shutil.copy(fvSolution_path, steffensen_path+folder_name+"/"+sweep_name+"/"+interval_name+"/system")
    print("Files successfully copied for "+interval_name+".\n")












def WRONGprepareSteffensen(folder_name,):
    #Pour l'implementation on considère n=4, on entre dans k=1
    print("Steffensen Preparation: copy of interval1 folders...")
    #Path from other sweep
    constant_next_sweep_int1=primitive_path+folder_name+"/sweep2/interval1/constant"
    system_next_sweep_int1=primitive_path+folder_name+"/sweep2/interval1/system"
    time_next_sweep_int1=primitive_path+folder_name+"/sweep2/interval1/"+str(theta)
    
    #Paths from actual sweep
    #current_sweep_path=steffensen_path+folder_name+"sweep1/"
    int1_steffensen=steffensen_path+folder_name+"/sweep1/interval1/"
    linP_path=ref_cases+"/boundaryConditions/linP"
    linU_path=ref_cases+"/boundaryConditions/linU"
    
    fvSchemes_path=ref_cases+"/controlBib/fvSchemes"
    fvSolution_path=ref_cases+"/controlBib/fvSolution"
    
    #Creating folders
    os.mkdir(steffensen_path+folder_name)
    #os.mkdir(steffensen_path+folder_name+"/sweep1")
    #os.mkdir(steffensen_path+folder_name+"/sweep1/interval1")

    #Copy of constant, system, starttime, from primitive folder
    shutil.copytree(constant_next_sweep_int1,os.path.join(int1_steffensen,os.path.basename(constant_next_sweep_int1)))
    shutil.copytree(system_next_sweep_int1,os.path.join(int1_steffensen,os.path.basename(system_next_sweep_int1)))
    shutil.copytree(time_next_sweep_int1,os.path.join(int1_steffensen,os.path.basename(time_next_sweep_int1)))
    #Copy of lin Variables and fv Folders
    shutil.copy(linP_path, int1_steffensen+str(theta)+"/")
    shutil.copy(linU_path, int1_steffensen+str(theta)+"/")
    shutil.copy(fvSchemes_path, int1_steffensen+"/system/")
    shutil.copy(fvSolution_path, int1_steffensen+"/system/")
    os.mkdir(steffensen_path+folder_name+"/sweep1/interval1/0")
    print("Copy Done. Starting linearisedPimpleDyMFoam...\n")
    #os.chdir(steffensen_path+folder_name+"/sweep1/interval1/")
    #with open("logfile.txt","w") as logfile:
    #    result=subprocess.run(['linearisedPimpleDyMFoam'], stdout=logfile, stderr=subprocess.STDOUT)            
    #    return(result)

def prepareNextSweepSteffenson(k, folder_name):
    for k in range(1,n+1): #LOOP for all sweeps in folder_name
        for i in range(1,n+1):
            myinterval="interval{}"
            mysweep="sweep{}"
            sweep_name=mysweep.format(k)
            next_sweep=mysweep.format()
            interval_name=myinterval.format(i)
            previous_interval=myinterval.format(i-1)
            os.chdir(steffensen_path)
            #previous_sweep_name=mysweep.format(k)
            
            #Paths from actual sweep
            #current_sweep_path=steffensen_path+folder_name+"sweep1/"
            int_steffensen=steffensen_path+folder_name+"/"+sweep_name+"/"+interval_name
            linP_path=ref_cases+"/boundaryConditions/linP"
            linU_path=ref_cases+"/boundaryConditions/linU"
            fvSchemes_path=ref_cases+"/controlBib/fvSchemes"
            fvSolution_path=ref_cases+"/controlBib/fvSolution"
            if i==1:
                #Creating folders
                os.mkdir(steffensen_path+folder_name)
                int1_steffensen=steffensen_path+folder_name+"/sweep1/interval1/"
                constant_next_sweep_int=primitive_path+folder_name+"/"+next_sweep+"/"+interval_name+"/constant"
                system_next_sweep_int=primitive_path+folder_name+"/"+next_sweep+"/"+interval_name+"/system"
                time_next_sweep_int=primitive_path+folder_name+"/"+next_sweep+"/"+interval_name+"/"+str(theta)

                #Copy of constant, system, starttime, from primitive folder
                shutil.copytree(constant_next_sweep_int,os.path.join(int1_steffensen,os.path.basename(constant_next_sweep_int)))
                shutil.copytree(system_next_sweep_int,os.path.join(int1_steffensen,os.path.basename(system_next_sweep_int)))
                shutil.copytree(time_next_sweep_int,os.path.join(int1_steffensen,os.path.basename(time_next_sweep_int)))
                #Copy of lin Variables and fv Folders
                shutil.copy(linP_path, int1_steffensen+str(theta)+"/")
                shutil.copy(linU_path, int1_steffensen+str(theta)+"/")
                shutil.copy(fvSchemes_path, int1_steffensen+"/system/")
                shutil.copy(fvSolution_path, int1_steffensen+"/system/")
                os.mkdir(steffensen_path+folder_name+"/sweep1/interval1/0")
                print("Copy Done for interval1. \n")
            
            elif i>1:
                int_steffensen_path=steffensen_path+folder_name+"/"+sweep_name+"/"+interval_name
                constant_next_sweep_int=primitive_path+folder_name+"/"+next_sweep+"/"+previous_interval+"/constant"
                system_next_sweep_int=primitive_path+folder_name+"/"+next_sweep+"/"+previous_interval+"/system"
                time_next_sweep_int=primitive_path+folder_name+"/"+next_sweep+"/"+previous_interval+"/"+str(theta)
                
                
                
                sweep_path=os.path.join(folder_name,sweep_name)
                primitive_interval_path=primitive_path+'/'+sweep_name+'/'+interval_name
                print("\nStarting shooting of "+sweep_name+" with Steffensen's method.\n")
                
                
                #Copy of lin varaible from refcases
                startTime=bc.decimal_analysis(theta+deltaT*(i-2)) ##vérif la valeur
                start_time_path=steffensen_path+'/'+sweep_name+'/'+interval_name+'/'+str(startTime)
                #os.copy(linP_var_path, start_time_path)
                #os.copy(linU_var_path, start_time_path)
                
                fvSchemes_path="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/reference_cases/controlBib/fvSchemes"
                fvSolutions_path="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/reference_cases/controlBib/fvSolutions"
                os.copy(fvSchemes_path, steffensen_path+'/'+sweep_name+'/'+interval_name+'/')
                os.copy(fvSolutions_path, steffensen_path+'/'+sweep_name+'/'+interval_name+'/')
                print("Copy Done. Starting linearisedPimpleDyMFoam...\n")



