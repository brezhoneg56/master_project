# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 10:30:18 2023

@author: jcosson
"""
import os
from src import boundary_conditions as bc
import sys
import shutil
from config import primal_path, primitive_path, steffensen_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, basepath
from config import n, theta, T, a, t, deltaT, myinterval, mysweep
########################################################################################################

################################ PRIMAL PRIMITIVE POSTPROCESSING #######################ä###############
def preparePostProcessing(folder_name, sweep_name):
    destination_file=basepath+folder_name+'/'+sweep_name+'/'
    postPro_destination=destination_file+"postProcessing"
    os.chdir(destination_file)
    print("Preparing for postProcessing of "+sweep_name+"\n")
    list_dir=[]
    for x in range(1,n+1):
        list_dir=list_dir+["interval"+str(x)]
    for list_dir in list_dir:
        os.path.join(postPro_destination,list_dir)
        bc.copytree(list_dir,postPro_destination)
    print("ready for postProcessing ...")

def computePressureDropFoam(folder_name, sweep_name):
    os.chdir(basepath+folder_name+'/'+sweep_name+"/postProcessing")
    #Open a log file        
    with open("pressureDrop.txt","w") as logfile:
        result=os.system('computePressureDropFoam start end > pressureDrop.txt')            
        print("\nComputation of Pressure Drop for "+sweep_name+" is done.\n\nWriting into pressureDrop.txt ...")
    #Writing the pressureDrop line into txt file
    with open("pressureDrop.txt","r") as f:
        os.chdir(basepath+folder_name)
        with open("pressureDropvalues.txt","a") as mapression:
       # lines=f.readlines()
            for line in f:
                if "pressureDrop" in line:
                    mapression.write(line)
                    print(line)
        mapression.close()
    f.close()
    os.chdir(basepath) #back to main path
    print("Done.\n\n")
    return(result)

def shootingUpdateP(folder_name, sweep_name, interval_name, k, i, pressure):
    startingTime=str(bc.decimal_analysis(theta+(i-2)*deltaT))
    src_shootP=steffensen_path+folder_name+"/"+sweep_name+"/preProcessing/0/"+pressure
    dest_shootP=steffensen_path+folder_name+"/"+mysweep.format(k+1)+"/"+interval_name+"/"+startingTime
    shutil.copy(src_shootP, dest_shootP)
    return("Shooting Update done. Preparing for next loop...\n")