# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 17:40:10 2023

@author: jcosson
"""
import os
import shutil
from src import boundary_conditions as bc

def prepareMyNextSweep(k, n, folder_name, basepath, theta, deltaT):
    myinterval="interval{}"
    mysweep="sweep{}"
    sweep_name=mysweep.format(k+1)
    previous_sweep_name=mysweep.format(k)
    sweep_path=os.path.join(folder_name,sweep_name)
    print("\nStarting shooting of "+sweep_name+"\n") 
    # Copy Directories that were already shoot. Warning : put that after the computations
    for x in range(1,k+1):
        interval_name=myinterval.format(x)
        source_interval=basepath+folder_name+"/"+previous_sweep_name+"/"+interval_name
        destination_interval=basepath+folder_name+"/"+sweep_name
        shutil.copytree(source_interval,os.path.join(destination_interval,os.path.basename(source_interval)))
    #pimpleDyMFoam(folder_name, sweep_name, interval_name)
    #preparePostProcessing(folder_name, sweep_name)
    #computePressureDropFoam(folder_name, sweep_name)    
    
    #Preparing shooting directories from sweep1 data 
    for i in range(k+1,n+1): #will become k+1, n+1 because of first loop being put into the big loop
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

def prepareNextSweepSteffenson(k, n, folder_name, steffensen_path, primitive_path):
    for i in range(k+1,n+1):
        myinterval="interval{}"
        mysweep="sweep{}"
        sweep_name=mysweep.format(k+1)
        interval_name=myinterval.format(i+1)
        os.chdir(steffensen_path)
        #previous_sweep_name=mysweep.format(k)
        sweep_path=os.path.join(folder_name,sweep_name)
        primitive_interval_path=primitive_path+'/'+sweep_name+'/'+interval_name
        print("\nStarting shooting of "+sweep_name+" with Steffensen's method.\n")
        #Copy directories of refcases
        linP_var_path="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/reference_cases/boundary/linP"
        linU_var_path="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/reference_cases/boundary/linU"
        #Copy of interval1 file
        shutil.copytree(primitive_interval_path,os.path.join(steffensen_path+sweep_name,os.path.basename(primitive_interval_path)))
        #Copy of lin varaible from refcases
        startTime=decimal_analysis(theta+deltaT*(i-2)) ##vérif la valeur
        start_time_path=steffensen_path+'/'+sweep_name+'/'+interval_name+'/'+str(startTime)
        os.copy(linP_var_path, start_time_path)
        os.copy(linU_var_path, start_time_path)
        
        fvSchemes_path="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/reference_cases/controlBib/fvSchemes"
        fvSolutions_path="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/reference_cases/controlBib/fvSolutions"
        os.copy(fvSchemes_path, steffensen_path+'/'+sweep_name+'/'+interval_name+'/')
        os.copy(fvSolutions_path, steffensen_path+'/'+sweep_name+'/'+interval_name+'/')
        print("Copy Done. Starting linearisedPimpleDyMFoam...\n")




