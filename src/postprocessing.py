# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 10:30:18 2023

@author: jcosson
"""
import os
from src import boundary_conditions as bc
import shutil
from config import primal_path, primitive_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path
from config import n, theta, T, a, t, deltaT, myinterval, mysweep
###########################################################################

#################  PRIMAL PRIMITIVE POSTPROCESSING ########################
def preparePostProcessing(basepath, folder_name, sweep_name):
    destination_file=basepath + folder_name + '/' + sweep_name + '/'
    postPro_destination=destination_file + "postProcessing"
    os.chdir(destination_file)
    list_dir=[]
    for x in range(1,n + 1):
        list_dir=list_dir + ["interval" + str(x)]
    for list_dir in list_dir:
        os.path.join(postPro_destination,list_dir)
        print("Copying " + list_dir + " in " + folder_name + '/' + sweep_name + '/postProcessing')
        bc.copytree(list_dir,postPro_destination)
    print("ready for postProcessing of " + sweep_name + "...\n")

def computePressureDropFoam(basepath, folder_name, sweep_name):
    os.chdir(basepath + folder_name + '/' + sweep_name + "/postProcessing")
    #Open a log file        
    with open("pressureDrop.txt","w") as logfile:
        result=os.system('computePressureDropFoam start end > pressureDrop.txt')            
        print("\nComputation of Pressure Drop for " + sweep_name + " is done.\nWriting into pressureDrop.txt ...")
    #Writing the pressureDrop line into txt file
    with open("pressureDrop.txt","r") as f:
        os.chdir(basepath + folder_name)
        with open("pressureDropvalues.txt","a") as mapression:
       # lines=f.readlines()
            for line in f:
                if "pressureDrop" in line:
                    mapression.write(line)
                    print(line)
        mapression.close()
    f.close()
    os.chdir(basepath) #back to main pa60th
    print("Done.\n")
    return(result)

def shootingUpdateP(basepath, folder_name, sweep_name, interval_name, k, i):
    startingTime=str(bc.decimal_analysis(theta + (i-2)*deltaT))
    src_shootP=basepath + folder_name + "/" + sweep_name + "/preProcessing/0/shootingUpdateP"
    dest_shootP=basepath + folder_name + "/" + mysweep.format(k + 1) + "/" + interval_name + "/" + startingTime
    shutil.copy(src_shootP, dest_shootP)

def erasefiles(basepath, folder_name, sweep_name, interval_name):
    path_files=basepath+folder_name+"/"+sweep_name+"/"+interval_name
    os.chdir(path_files)
    for filename in os.listdir(path_files):
        if filename.startswith('0.'):
            file_path = os.path.join(path_files, filename)
            try:
                shutil.rmtree(file_path)
            except Exception as e1:
                print("Error while deleting directory: " + str(e1))
                try:
                    os.remove(file_path)
                except Exception as e2:
                    print("Error while deleting file: " + str(e2))
def erase_all_files(basepath, folder_name, k):
    sweep_name=mysweep.format(k)
    for i in range(1, n+1):
            interval_name=myinterval.format(i)
            erasefiles(basepath, folder_name, sweep_name, interval_name)
            print("The files were succefully deleted. See exceptions above.")