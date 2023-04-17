# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 09:42:28 2023

@author: jcosson
"""
## $pvd . a quoi sert cette commande?
#os.system("cp -r /home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/undeformed_turbulent/constant /home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/moderate_deformed/primal/four_intervals/sweep1")
import os
import shutil
import subprocess
#import fileinput
from src import boundary_conditions as bc, preprocessing as pre
#decimal_analysis, sweep_1_initialization, copytree
######### PATHS ########################## 
basepath="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/moderate_deformed/primal/"
calcs_undeformed="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/undeformed_turbulent/"
ref_cases_mod_def="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/reference_cases/moderate_deformed_SDuct/"
project_path="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/scripts/master_project/"
os.chdir(basepath)

############## FUNCTIONS ####################################



def pimpleDyMFoam(folder_name, sweep_name,i):
    interval_name=myinterval.format(i)
    pimple_path=basepath+folder_name+"/"+sweep_name+"/"+interval_name
    print("Executing pimpleDyMFoam in "+folder_name+'/'+sweep_name+'/'+interval_name+'\n\n')
    os.chdir(pimple_path) #Entering logfile path
    
    #Open a log file and pipe the output of PimpleDyMFoam into the log        
    with open("logfile.txt","w") as logfile:
        result=subprocess.run(['pimpleDyMFoam'], stdout=logfile, stderr=subprocess.STDOUT)            
    print("Computation of "+interval_name+" is done.\n\n Writing into pimple.log ...")
    os.chdir(basepath) #back to main path
    print("Done.\n\n")
    print("End of loop for interval "+str(i)+".")
    return(result)

def preparePostProcessing(folder_name, sweep_name):
    destination_file=basepath+folder_name+'/'+sweep_name+'/'
    postPro_destination=destination_file+"postProcessing"
    os.chdir(destination_file)
    print("Preparing for postProcessing of "+sweep_name+"\n")
    list_dir=[]
    for x in range(1,n+1):
        list_dir=list_dir+["interval"+str(x)]
    for list_dir in list_dir:
        dest_dir=os.path.join(postPro_destination,list_dir)
        bc.copytree(list_dir,postPro_destination)
    print("ready for postProcessing ...")

def computePressureDropFoam(folder_name, sweep_name):
    os.chdir(basepath+folder_name+'/'+sweep_name+"/postProcessing")
    #Open a log file        
    with open("pressureDrop.txt","w") as logfile: ###Erreor openfoam vient de la à priori car on ouvre deux fois le logfile
        result=os.system('computePressureDropFoam start end > pressureDrop.txt')            
        print("\nComputation of Pressure Drop for "+sweep_name+" is done.\n\nWriting into pressureDrop.txt ...")
    #os.chdir(basepath)     
    #Writing the pressureDrop line into txt file
    with open("pressureDrop.txt","r") as f:
        lines=f.readlines()
        for line in lines:
            if "pressureDrop" in line:
                os.chdir(basepath+folder_name)
                with open("pressureDropvalues.txt","a") as mapression:
                    mapression.write(line)
                    print(line)
                mapression.close()
    os.chdir(basepath) #back to main path
    print("Done.\n\n")
    return(result)




################################        INITIALIZATION      ################################
#folder_name=input("Name your folder: ")

folder_name="new_intervals"
n=4;
theta=0.4;
T=0.1;
deltaT=T/n
myinterval="interval{}"
mysweep="sweep{}"
# After testing is done, please uncomment the following
#n=int(input("Set the number of shooting intervals: "));
#theta=input("Define the starting time (example: 0.4): ");

################################        SWEEP 1 INITIALIZATION      ################################

bc.sweep_1_initialization(n, folder_name, basepath, calcs_undeformed, theta, deltaT, ref_cases_mod_def)

################################        COMPUTE MY SWEEP : sweep k in [1-n]       ################################
for k in range(1,n+1):
    sweep_name=mysweep.format(k)
    print("Starting shooting of "+sweep_name+"\n")

    ## COMPUTE MY INTERVAL     
    for i in range(k, n+1):
        pimpleDyMFoam(folder_name, sweep_name, i)
    preparePostProcessing(folder_name, sweep_name)
    computePressureDropFoam(folder_name, sweep_name)    
    pre.prepareMyNextSweep(k, n, folder_name, basepath, theta, deltaT)
