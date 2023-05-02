# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 10:30:18 2023

@author: jcosson
"""
import os
from src import boundary_conditions as bc
import sys
#sys.path.append('../')
from .. import primal_path, primitive_path, steffensen_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, basepath
from .. import n, theta, T, a, deltaT, myinterval, mysweep
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
        os.chdir(basepath+folder_name)
        with open("pressureDropvalues.txt","a") as mapression:
       # lines=f.readlines()
            for line in f:
                if "pressureDrop" in line:
                    #os.chdir(basepath+folder_name)
                    mapression.write(line)
                    print(line)
        mapression.close()
    f.close()
    os.chdir(basepath) #back to main path
    print("Done.\n\n")
    return(result)