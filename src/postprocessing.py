# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 10:30:18 2023

@author: jcosson
"""
import os
import sys
import re
from src import solvers as sol, preprocessing as pre, postprocessing as post, boundary_conditions as bc
import shutil
import csv
from concurrent import futures
from config import primal_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, adjoint_path
from config import n, theta, T, a, t, deltaT, myinterval, mysweep, folder_name, maxCPU
###########################################################################

#################  PRIMAL PRIMITIVE POSTPROCESSING ########################
def postProcessingCopyfiles(i, destination_file, postPro_destination):
    interval_name=myinterval.format(i)
    for filename in os.listdir(destination_file + interval_name):                
        if filename.startswith('0.') or filename.startswith(str(theta)) or filename.startswith(str(theta + deltaT*n)):
            #os.path.join(destination_file + interval_name + "/" + filename, postPro_destination)
            bc.copytree(destination_file + interval_name + "/" + filename, postPro_destination + "/" + filename + "/")

def preparePostProcessing(basepath, folder_name, sweep_name):
    destination_file=basepath + folder_name + '/' + sweep_name + '/'
    postPro_destination=destination_file + "postProcessing"
    os.chdir(destination_file)
    shutil.copytree(ref_cases_mod_def + "constant/", postPro_destination + "/constant/" )
    shutil.copytree(ref_cases_mod_def + "system/", postPro_destination + "/system/" )
    #with futures.ProcessPoolExecutor(max_workers=maxCPU) as executor:
    for i in range(1, n+1):
            #print("copyfile in loop" + str(i))
        #executor.submit(postProcessingCopyfiles, i, destination_file, postPro_destination)
        postProcessingCopyfiles(i, destination_file, postPro_destination)
    print("ready for postProcessing of " + sweep_name + "...\n")

def computePressureDropFoam(basepath, folder_name, sweep_name):
    os.chdir(basepath + folder_name + '/' + sweep_name + "/postProcessing/")
    #Open a log file for pressureDrop and timers       
    with open("pressureDrop.txt","w"):
        result=os.system('computePressureDropFoam start end > pressureDrop.txt')            
        print("\nComputation of Pressure Drop for " + sweep_name + " is done.\nWriting into pressureDrop.txt ...")
    
    #Writing the pressureDrop line into txt file
    with open("pressureDrop.txt","r") as f:
        os.chdir(basepath + folder_name)
        with open("pressureDropvalues.txt","a") as mapression:
            #mapression.write("\n\nShooting of " + sweep_name + ":\n---------------------------------\n" )
            for line in f:
                if "pressureDrop" in line:
                    pressure=mapression.write(line)
                    print(line)
        mapression.close()
    f.close()
    os.chdir(basepath) #back to main path
    print("Done.\n")
    return(pressure)

def shootingUpdateP(basepath, folder_name, sweep_name, interval_name, k, i):
    startingTime=str(bc.decimal_analysis(theta + (i-2)*deltaT))
    src_shootP=basepath + folder_name + "/" + sweep_name + "/preProcessing/0/shootingUpdateP"
    dest_shootP=basepath + folder_name + "/" + mysweep.format(k + 1) + "/" + interval_name + "/" + startingTime
    if os.path.exists(src_shootP):
        shutil.copy(src_shootP, dest_shootP)


def prepareNextNewton(basepath, folder_name, sweep_name, k, interval_name, i):
    next_sweep=mysweep.format(k+1)
    next_interval=myinterval.format(i+1)
    src_upfiles=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingUpdate/0/"
    src_p=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + str(bc.decimal_analysis(theta + (i)*deltaT)) + "/p" #correction de i-1
    dest_upfiles=basepath + folder_name + "/" + next_sweep + "/" + next_interval + "/" + str(bc.decimal_analysis(theta + (i)*deltaT))
    #print(str(bc.decimal_analysis(theta + (i-1)*deltaT)))
    shutil.copy(src_upfiles + "shootingUpdateU", dest_upfiles + "/U")
    shutil.copy(src_upfiles + "shootingUpdatePhi", dest_upfiles + "/phi")
    shutil.copy(src_upfiles + "shootingUpdateUf", dest_upfiles + "/Uf")
    shutil.copy(src_p, dest_upfiles)
    
    
### ERASING FUNCTIONS #################
def erase_system(path_files):
    for filename in os.listdir(path_files):
        the_path = os.path.join(path_files, filename)
        os.remove(the_path)        
    os.rmdir(path_files)

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

    shutil.rmtree(path_files+"/polyMesh")
    for filename in os.listdir(path_files):
        the_path = os.path.join(path_files, filename)
        try:
            os.remove(the_path)
        except:
            print("error in erase_constant line 89: os.remove(the_path)")

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
    if os.path.exists(path_files):
        os.removedirs(the_path)

def erase_shootingdefect(basepath, path_files, sweep_name, interval_name, i):
    if i!=1:
        src_shootfile=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingDefect/shooting_defect_logfile" + sweep_name + "_" + interval_name + ".txt"
        dest_shootfile=basepath + folder_name + "/" + sweep_name + "/logfiles/"
        shutil.move(src_shootfile, dest_shootfile)
        #post.erase_0(path_files)
        #post.erase_constant(path_files)
        #post.erase_system(path_files)
        
    
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
            if os.path.exists(src_log):
                shutil.move(src_log, dest_log)
            #except Exception as e4:
            #    print("Error while moving directory: " + str(e4))
            src_log=basepath+folder_name+"/"+sweep_name+"/" + interval_name + "/pimple.log"
            dest_log=basepath+folder_name+"/"+sweep_name+"/logfiles/pimple_"+interval_name+".log"
            try:
                shutil.move(src_log, dest_log)
            except Exception as error:
                print("Error while moving file: " + str(error))            
            
            erase_constant(path_files+"/constant")
            erase_system(path_files+"/system")
            erase_shootingdefect(basepath, path_files, sweep_name, interval_name, i)            
            
            shutil.rmtree(basepath + folder_name + "/" + sweep_name + "/" + interval_name)
    #PostProcessessing files
    src_log=basepath+folder_name+"/"+sweep_name+"/postProcessing/"
    dest_log=basepath+folder_name+"/"+sweep_name+"/"
    try:
        shutil.move(src_log+"pimple.log", dest_log+"/logfiles/postPro_log.log")
    except Exception:
        print("Error while moving postProlog: ")
    try:
        shutil.move(src_log+"pressureDrop.txt", dest_log+"/logfiles/pressureDrop.txt")
    except Exception:
        print("Error while moving pressureDrop: ")
    try:
        shutil.rmtree(src_log)
    except Exception as error:
        print("Error while deleting directory: " + str(error))
    
    #Preprocessing files
    src_log=basepath+folder_name+"/"+sweep_name+"/preProcessing/shooting_update_logfilesweep"+str(k)+"_"+interval_name+".txt"
    dest_log=basepath+folder_name+"/"+sweep_name+"/logfiles/shooting_update_logfilesweep"+str(k)+"_"+interval_name+".txt"
    if os.path.exists(src_log):    
        shutil.move(src_log, dest_log)
    if os.path.exists(basepath+folder_name+"/"+sweep_name+"/preProcessing/"):     
        shutil.rmtree(basepath+folder_name+"/"+sweep_name+"/preProcessing/")
    
######################################################################
## LOGTABLE


def store_for_plot_defect(basepath, sweep_name, interval_name, file):
    table = []
    ### Partie Defect :
    _, flux_value = post.fetch_values_defect(basepath, file, sweep_name, interval_name)
    velocity_value, _ = post.fetch_values_defect(basepath, file, sweep_name, interval_name)
    #with open("logtable.csv", 'a', newline='') as tab:
    #writer = csv.writer(tab)
    # Store the variables in a table or data structure of your choice
    table_defect=table.append((velocity_value, flux_value))
    # Write the row to the CSV file
    #writer.writerow([velocity_value, flux_value])
    return table_defect



def store_all_values(basepath, folder_name):
    os.chdir(basepath + folder_name)
    print("All value will be stored in a CSV file as follows:\n")
    print("Row number = Sweep Number, pressureDrop, velocity defect, continuity defect (flux), primalWallTime, SweepWallTime, AccumulatedTime")
    print("Wrinting into logtable in  " + basepath + folder_name)
    table = []
    os.chdir(basepath + folder_name)
    with open("logtable.csv", 'a', newline='') as tab:
        for k in range(1, n+1):
            sweep_name=mysweep.format(k)
            #path_file=basepath + folder_name + "/" + sweep_name + "/logfiles/pressureDrop.txt"
            #find_logfile(basepath, folder_name, "pressureDrop.txt")
            for i in range(2, n+1):
                interval_name=myinterval.format(i)
                #Write Sweep Number
                #store_for_plot(basepath, folder_name, sweep_name)
                
                #Fetch pressureDrop
                pressure_path=find_logfile(basepath + folder_name, folder_name)
                print("\n\n"+pressure_path+"\n\n")
                os.chdir(pressure_path)
                pressureDrop=post.fetch_values(basepath, "pressureDrop.txt", "pressureDrop is     ")
                
                #Fetch Velocity and Continuity Defects:
                flux_path=find_logfile(basepath, ("shooting_defect_logfile" + sweep_name + "_" + interval_name + ".txt"))
                #print(flux_path)
                
                _, flux_value = post.fetch_values_defect(basepath, sweep_name, interval_name, flux_path)
                velocity_value, _ = post.fetch_values_defect(basepath, sweep_name, interval_name, flux_path)
        
                writer = csv.writer(tab)
                # Store the variables in a table or data structure of your choice
                table.append((sweep_name, pressureDrop, velocity_value, flux_value))
                # Write the row to the CSV file
                writer.writerow([table])
    return table

def find_logfile(basepath, thefile):
    max_depth = 6  # Maximum depth to search for the file
    for root, dirs, files in os.walk(basepath):
        current_depth = root.count(os.sep) - basepath.count(os.sep)
        if current_depth <= max_depth and thefile in files:
            logfile_path = os.path.join(root, thefile)
            return logfile_path
    # If logfile is not found
    return None

def fetch_values_defect(basepath, sweep_name, interval_name, path_file):
    #path_file = basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingDefect/" + "shooting_defect_logfile" + sweep_name + "_" + interval_name + ".txt"
    with open(path_file, "r") as myfile:
        text = myfile.read()

        # Regular expression pattern to capture the value
        velocity = r"defects \(velocity\): sum local = ([\d.e+-]+)"
        fluxes = r"defects \(fluxes\): sum local = ([\d.e+-]+)"

        # Search for the pattern in each line
        for line in text.split('\n'):
            velocity_match = re.search(velocity, line)
            flux_match = re.search(fluxes, line)
            if velocity_match:
                velocity_defect = velocity_match.group(1)
                #print("defects (velocity): sum local:", velocity_defect)
            if flux_match:
                flux_defect = flux_match.group(1)
                #print("defects (fluxes): sum local:", flux_defect)
        return(velocity_defect, flux_defect)

def fetch_values(basepath, path_file, line_to_find):
    with open(path_file, "r") as myfile:
        text = myfile.read()
        # Regular expression pattern to capture the value
        #velocity = r"defects \(velocity\): sum local = ([\d.e+-]+)"
        line_to_find=line_to_find + "([\d.e+-]+)"
        # Search for the pattern in each line
        for line in text.split('\n'):
            match = re.search(line_to_find, line)
            if match:
                the_value = match.group(1)
        return(the_value)
##################################

