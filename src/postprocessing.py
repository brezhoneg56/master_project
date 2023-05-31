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
from config import basepath, primal_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, adjoint_path
from config import n, theta, T, a, t, deltaT, myinterval, mysweep, folder_name
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
    #with futures.ProcessPoolExecutor(max_workers=14) as executor:
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

def the_shooting_update_for_all(sweep_name, k, i, j):
    m=1 #Counter for Shooting update is always i-1
    #print("Starting shooting update process for " + sweep_name + ".\n")
    interval_name=myinterval.format(i)
    #print("j="+str(j))
    #print("n="+str(n))
    if j<=n:
        #print("Shooting Update process started from " + interval_name + " for " + sweep_name)
        pre.prepareShootingUpdate(basepath, folder_name, sweep_name, k, j)
    interval_name=myinterval.format(m)    
    sol.computeShootingUpdate(basepath, folder_name, k, i)
    post.shootingUpdateP(basepath, folder_name, sweep_name, interval_name, k, m)
    m=m+1 #Counter for Shooting Update

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

def erase_shootingdefect(path_files, sweep_name, interval_name, i):
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
            erase_shootingdefect(path_files, sweep_name, interval_name, i)            
            
            shutil.rmtree(basepath + folder_name + "/" + sweep_name + "/" + interval_name)
            
            
    
    #PostProcessessing files
    src_log=basepath+folder_name+"/"+sweep_name+"/postProcessing/"
    dest_log=basepath+folder_name+"/"+sweep_name+"/"
    try:
        shutil.move(src_log+"pimple.log", dest_log+"/logfiles/postPro_log.log")
        shutil.move(src_log+"pressureDrop.txt", dest_log+"/logfiles/pressureDrop.txt")
    except Exception:
        print("Error while moving directory: ")
    #erase_files(src_log)
    try:
        shutil.rmtree(src_log)
    except Exception as error:
        print("Error while deleting directory: " + str(error))
    
    #Preprocessing files
    src_log=basepath+folder_name+"/"+sweep_name+"/preProcessing/shooting_update_logfilesweep"+str(k)+"_"+interval_name+".txt"
    dest_log=basepath+folder_name+"/"+sweep_name+"/logfiles/shooting_update_logfilesweep"+str(k)+"_"+interval_name+".txt"
    if os.path.exists(src_log):    
        shutil.move(src_log, dest_log)
    #except Exception as e4:
     #           print("Error while moving directory: " + str(e4))
    
    #erase_files(basepath+folder_name+"/"+sweep_name+"/preProcessing/")
    if os.path.exists(basepath+folder_name+"/"+sweep_name+"/preProcessing/"):     
    #try:
        shutil.rmtree(basepath+folder_name+"/"+sweep_name+"/preProcessing/")
    #except Exception as error:
    #    print("Error while deleting file: " + str(error))

def store_for_plot2(filename):
    table = []
#    with open(filename, 'r') as file:
#        reader = csv.reader(file, delimiter='    ')
#        next(reader)  # Skip header line
#        
#        for row in reader:
#            sweep_number = int(row[0])
#            timer = float(row[1])
#            pressure_drop = float(row[2])
#            
#            # Store the variables in a table or data structure of your choice
#            table.append((sweep_number, timer, pressure_drop))
#    
#    return table
# Option 2
def store_for_plot3(filename):
    table = []
    with open(filename, 'r') as file:
        lines = file.readlines()
        os.chdir(basepath + folder_name)
        with open("logtable.csv", 'a') as tab:
            with open("pressureDropvalues.txt","r") as mapression:
                for line in mapression:
                    sweep_number = int(match.group(1))
                    if "pressureDrop" in line:
                        pressure_drop = float(group(3))
                    if "Elapsed time for pimpleDyMFoam" in line:
                        timer = float(match.group(2))
                    # Store the variables in a table or data structure of your choice
                    table.append((sweep_number, timer, pressure_drop))
    return table


def store_for_plot(filename):
    table = []
    with open(filename, 'r') as file:
        lines = file.readlines()

        # Assuming basepath and folder_name are defined somewhere in your code
        os.chdir(basepath + folder_name)

        with open("logtable.csv", 'a', newline='') as tab:
            writer = csv.writer(tab)

            with open("pressureDropvalues.txt", "r") as mapression:
                for line in mapression:
                    # Use regex to search for the desired information
                    match = re.search(r'Sweep Number: (\d+), Timer: (\d+\.\d+), Pressure Drop: (\d+\.\d+)', line)
                    if match:
                        sweep_number = int(match.group(1))
                        timer = float(match.group(2))
                        pressure_drop = float(match.group(3))

                        # Store the variables in a table or data structure of your choice
                        table.append((sweep_number, timer, pressure_drop))

                        # Write the row to the CSV file
                        writer.writerow([sweep_number, timer, pressure_drop])

    return table
