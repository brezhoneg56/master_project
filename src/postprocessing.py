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

def erase_system(path_files):
    for filename in os.listdir(path_files):
        the_path = os.path.join(path_files, filename)
        os.remove(the_path)
def erase_0(path_files):  
    for filename in os.listdir(path_files):
        the_path = os.path.join(path_files, filename)                    
        shutil.rmtree(path_files)                
    try:
        os.remove(the_path)
    except Exception as e2:
        print("Error while deleting file: " + str(e2))
def erase_constant(path_files):
    for filename in os.listdir(path_files+"/polyMesh/sets"):
        the_path = os.path.join(path_files+"/polyMesh/sets", filename)
        try:
            shutil.rmtree(path_files+"/polyMesh/sets")
        except Exception as sets:
            print("sets deleting problem: " + str(sets))
        for filename in os.listdir(path_files+"/polyMesh"):
            the_path = os.path.join(path_files+"/polyMesh", filename)
            try:
                shutil.rmtree(path_files+"/polyMesh")
            except Exception as polymesh:
                print("rmtree polymesh:" + str(polymesh))
            try:  
                os.remove(path_files+"/polyMesh")
            except Exception as polymesh:
                print("Error:"+ str(polymesh))
            for filename in os.listdir(path_files):
                the_path = os.path.join(path_files, filename)
                os.remove(the_path)
                try:
                    shutil.rmtree(the_path)
                except:
                    return(0)

def erase_time_files(path_files):
    for filename in os.listdir(path_files):
        if filename.startswith('0.'):
            the_path = os.path.join(path_files, filename)
            try:
                shutil.rmtree(the_path)
            except Exception as e1:
                try:
                    os.remove(the_path)
                except Exception as e1:
                    print("Error while deleting directory: " + str(e1))

def erase_files(path_files):
    for filename in os.listdir(path_files):
        for filename in os.listdir(path_files):
            the_path = os.path.join(path_files, filename)
            try:
                os.remove(the_path)
            except:
                try:
                    shutil.rmtree(the_path)
                except:
                    print("Failed to erase")

def erase_all_files(basepath, folder_name, k):
    sweep_name=mysweep.format(k)
    #Interval time files   
    os.makedirs(basepath+folder_name+"/"+sweep_name+"/logfiles")
    for i in range(1, n+1):
            interval_name=myinterval.format(i)
            path_files=basepath+folder_name+"/"+sweep_name+"/"+interval_name
            erase_time_files(path_files)
            
            src_log=basepath+folder_name+"/"+sweep_name+"/"+interval_name+"/lin_logfilesweep"+str(k)+"_"+interval_name+".txt"
            dest_log=basepath+folder_name+"/"+sweep_name+"/logfiles/lin_logfile_"+interval_name+".txt"
            try:
                shutil.move(src_log, dest_log)
            except Exception as e4:
                print("Error while moving directory: " + str(e4))
            src_log=basepath+folder_name+"/"+sweep_name+"/" + interval_name + "/pimple.log"
            dest_log=basepath+folder_name+"/"+sweep_name+"/logfiles/pimple_"+interval_name+".log"
            try:
                shutil.move(src_log, dest_log)
            except Exception as error:
                print("Error while moving file: " + str(error))            
            try:
                erase_constant(path_files+"/constant")
            except Exception as cte:
                print("Problem with constant: " + str(cte))  
            try:
                erase_system(path_files+"/system")
            except Exception as sys:
                print("Problem with system: " + str(sys))
            try:
                erase_0(path_files+"/preProcessing/0")
            except Exception as e0:
                print("Problem with 0:" + str(e0))
    #PostProcessessing files
    src_log=basepath+folder_name+"/"+sweep_name+"/postProcessing/"
    dest_log=basepath+folder_name+"/"+sweep_name+"/"
    try:
        shutil.move(src_log+"pimple.log", dest_log+"/logfiles/postPro_log.log")
        shutil.move(src_log+"pressureDrop.txt", dest_log+"/logfiles/pressureDrop.txt")
    except Exception as e4:
        print("Error while moving directory: " + str(e4))
    erase_files(src_log)
    try:
        shutil.rmtree(src_log)
    except Exception as error:
        print("Error while deleting directory: " + str(error))
    
    #Preprocessing files
    src_log=basepath+folder_name+"/"+sweep_name+"/preProcessing/shooting_update_logfilesweep"+str(k)+"_"+interval_name+".txt"
    dest_log=basepath+folder_name+"/"+sweep_name+"/logfiles/shooting_update_logfilesweep"+str(k)+"_"+interval_name+".txt"
    try:
        shutil.move(src_log, dest_log)
    except Exception as e4:
                print("Error while moving directory: " + str(e4))
    erase_files(basepath+folder_name+"/"+sweep_name+"/preProcessing/")
    try:
        shutil.rmtree(basepath+folder_name+"/"+sweep_name+"/preProcessing/")
    except Exception as error:
        print("Error while deleting file: " + str(error))
    print("The files were succefully deleted. See exceptions above.")

    