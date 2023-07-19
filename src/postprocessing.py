# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 10:30:18 2023

@author: jcosson
"""
import os
import sys
import re
import subprocess
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
            bc.copytree(destination_file + interval_name + "/" + filename, postPro_destination + "/" + filename + "/") #avant bc.copytree

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
                    pressure=mapression.write("\n" + str(line)) #avant : juste line
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

#################  ADJOINT POSTPROCESSING ########################
def prepare_adjoint_fixed_primal(basepath, folder_name, sweep_name, k, interval_name, i):
    print("START prepare_adjoint_fixed_primal")
    next_sweep=mysweep.format(k+1)    
    
    src_sweep=adjoint_path + folder_name + "/" + sweep_name + "/" + interval_name + "/"
    dest_sweep=adjoint_path + folder_name + "/" + next_sweep + "/" + interval_name + "/"
    shutil.copytree(src_sweep, dest_sweep)    

def copy_adjoint_variables(basepath, folder_name, sweep_name, k, interval_name, i):
    next_sweep=mysweep.format(k+1)
    next_interval=myinterval.format(i-1)
    
    dest_upfiles=basepath + folder_name + "/" + next_sweep + "/" + next_interval + "/" + str(-bc.decimal_analysis(theta + (i-1)*deltaT)) + "/"
    src_pa=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + str(-bc.decimal_analysis(theta + (i-1)*deltaT)) + "/"
    shutil.copy(src_pa + "pa", dest_upfiles + "pa")
    shutil.copy(src_pa + "Ua", dest_upfiles + "Ua")
    shutil.copy(src_pa + "phia", dest_upfiles + "phia")
    shutil.copy(src_pa + "Uaf", dest_upfiles + "Uaf")


    
    
    
    #if i>1:
    #    src_upfiles=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/adjointShootingUpdate/0/"
    #    shutil.copy(src_upfiles + "shootingUpdateUa", dest_upfiles + "Ua")
    #    shutil.copy(src_upfiles + "shootingUpdatePhia", dest_upfiles + "phia")
    #    shutil.copy(src_upfiles + "shootingUpdateUaf", dest_upfiles + "Uaf")
    
    


def prepareNextAdjointNewton(basepath, folder_name, sweep_name, k, interval_name, i):
    next_sweep=mysweep.format(k+1)
    next_interval=myinterval.format(i-1)
    src_upfiles=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/adjointShootingUpdate/0/"
    src_p=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + str(-bc.decimal_analysis(theta + (i-1)*deltaT)) + "/pa" #correction de i-1
    dest_upfiles=basepath + folder_name + "/" + next_sweep + "/" + next_interval + "/" + str(-bc.decimal_analysis(theta + (i-1)*deltaT))
    #print(str(bc.decimal_analysis(theta + (i-1)*deltaT)))
        
    
    
    if k<n:
        pre.prepareMyNextAdjointSweep(basepath, k, folder_name)
            
        #Renaming Time folder with "-"
        pre.prepareTimeFolders(folder_name, next_sweep, k)
        
        
    
    shutil.copy(src_upfiles + "shootingUpdateUa", dest_upfiles + "/Ua")
    shutil.copy(src_upfiles + "shootingUpdatePhia", dest_upfiles + "/phia")
    shutil.copy(src_upfiles + "shootingUpdateUaf", dest_upfiles + "/Uaf")
    shutil.copy(src_p, dest_upfiles)

def computeAdjointPressureDropFoam(basepath, folder_name, sweep_name):
    os.chdir(basepath + folder_name + '/' + sweep_name + "/adjoint_postProcessing/")
    #Open a log file for pressureDrop and timers       
    with open("adjointPressureDrop.txt","w"):
        os.system('computeAdjointPressureDropFoam start end > "adjointPressureDrop.txt"')            
        print("\nComputation of Pressure Drop for " + sweep_name + " is done.\nWriting into adjoint_pressureDrop.txt ...")
    
    #Writing the pressureDrop line into txt file
    with open("adjointPressureDrop.txt","r") as f:
        os.chdir(basepath + folder_name)
        with open("pressureDropvalues.txt","a") as mapression:
            #mapression.write("\n\nShooting of " + sweep_name + ":\n---------------------------------\n" )
            for line in f:
                if "adjointPressureDrop" in line:
                    mapression.write(line)
                    print(line)
        mapression.close()
    f.close()
    os.chdir(basepath) #back to main path
    print("Done.\n")


def adjointPostProcessingCopyfiles(i, destination_file, postPro_destination):
    interval_name=myinterval.format(i)
    for filename in os.listdir(destination_file + interval_name):                
        if filename.startswith('-0.') or filename.startswith(str(-theta)) or filename.startswith(str(-(theta + deltaT*n))):
            #os.path.join(destination_file + interval_name + "/" + filename, postPro_destination)
            #bc.copytree(destination_file + interval_name + "/" + filename, postPro_destination + "/" + filename + "/")
            shutil.copytree(destination_file + interval_name + "/" + filename, postPro_destination + "/" + filename + "/")

def prepareAdjointPostProcessing(basepath, folder_name, sweep_name):
    destination_file=basepath + folder_name + '/' + sweep_name + '/'
    postPro_destination=destination_file + "adjoint_postProcessing"
    os.chdir(destination_file)
    shutil.copytree(ref_cases_mod_def + "constant/", postPro_destination + "/constant/" )
    shutil.copytree(ref_cases_mod_def + "system/", postPro_destination + "/system/" )
    #with futures.ProcessPoolExecutor(max_workers=maxCPU) as executor:
    for i in range(1, n+1):
            #print("copyfile in loop" + str(i))
            #executor.submit(adjointPostProcessingCopyfiles, i, destination_file, postPro_destination)
        post.adjointPostProcessingCopyfiles(i, destination_file, postPro_destination)
    print("ready for postProcessing of " + sweep_name + "...\n")

#################    ERASING FUNCTIONS    #################
    
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
        try:
            os.removedirs(the_path)
        except Exception as e:
            print(e)

def erase_shootingdefect(basepath, path_files, sweep_name, interval_name, i):
    if i!=1:
        src_shootfile=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/shootingDefect/shooting_defect_logfile" + sweep_name + "_" + interval_name + ".txt"
        dest_shootfile=basepath + folder_name + "/" + sweep_name + "/logfiles/"
        shutil.move(src_shootfile, dest_shootfile)
        #post.erase_0(path_files)
        #post.erase_constant(path_files)
        #post.erase_system(path_files)
def erase_adjointShootingdefect(basepath, path_files, sweep_name, interval_name, i):
    #if i!=n:
        src_shootfile=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/adjointShootingDefect/shooting_defect_logfile" + sweep_name + "_" + interval_name + ".txt"
        dest_shootfile=basepath + folder_name + "/" + sweep_name + "/logfiles/"
        try:
            shutil.move(src_shootfile, dest_shootfile)
        except Exception as e:
            print(e)
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
    except Exception as epost:
        print("Error while moving postProlog: " + str(epost))
    try:
        shutil.move(src_log+"pressureDrop.txt", dest_log+"/logfiles/pressureDrop" + str(k) + ".txt")
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
    
def erase_all_adjoint_files(basepath, folder_name, k):
    sweep_name=mysweep.format(k)
    #Interval time files   
    os.makedirs(basepath+folder_name+"/"+sweep_name+"/logfiles")
    for i in range(1, n+1):
            interval_name=myinterval.format(i)
            path_files=basepath+folder_name+"/"+sweep_name+"/"+interval_name
            erase_time_files(path_files)
            
            #Lin logilfe
            src_log=basepath+folder_name+"/"+sweep_name+"/"+interval_name+"/adjoint_lin_logfilesweep"+str(k)+"_"+interval_name+".txt"
            dest_log=basepath+folder_name+"/"+sweep_name+"/logfiles/adjoint_lin_logfilesweep"+str(k)+"_"+interval_name+".txt"
            if os.path.exists(src_log):
                shutil.move(src_log, dest_log)
            
            #Pimple Logfile
            src_log=basepath+folder_name+"/"+sweep_name+"/" + interval_name + "/adjoint_pimple.log"
            dest_log=basepath+folder_name+"/"+sweep_name+"/logfiles/pimple_"+interval_name+".log"
            try:
                shutil.move(src_log, dest_log)
            except Exception as error:
                print("Error while moving file: " + str(error))            
            #Shooting logfile
            src_log=basepath+folder_name+"/"+sweep_name+"/" + interval_name + "/adjoint_shooting_defect_logfilesweep" + str(k) + "_" + interval_name + ".txt"
            dest_log=basepath+folder_name+"/"+sweep_name+"/logfiles/adjoint_shooting_defect_logfilesweep" + str(k) + "_" + interval_name + ".txt"
            try:
                shutil.move(src_log, dest_log)
            except Exception as error:
                print("Error while moving file: " + str(error)) 
                
            erase_constant(path_files+"/constant")
            erase_system(path_files+"/system")
            erase_adjointShootingdefect(basepath, path_files, sweep_name, interval_name, i)            
            
            shutil.rmtree(basepath + folder_name + "/" + sweep_name + "/" + interval_name)
    #PostProcessessing files
    src_log=basepath+folder_name+"/"+sweep_name+"/adjoint_postProcessing/"
    dest_log=basepath+folder_name+"/"+sweep_name+"/"
    #try:
    #    shutil.move(src_log+"pimple.log", dest_log+"/logfiles/postPro_log.log")
    #except Exception as epost:
    #    print("Error while moving postProlog: " + str(epost))
    try:
        shutil.move(src_log+"adjointPressureDrop.txt", dest_log+"/logfiles/adjointPressureDrop" + str(k) + ".txt")
    except Exception:
        print("Error while moving adjointPressureDrop: ")
    try:
        shutil.rmtree(src_log)
    except Exception as error:
        print("Error while deleting directory: " + str(error))
    
    #Preprocessing files
#    src_log=basepath+folder_name+"/"+sweep_name+"/preProcessing/shooting_update_logfilesweep"+str(k)+"_"+interval_name+".txt"
#    dest_log=basepath+folder_name+"/"+sweep_name+"/logfiles/shooting_update_logfilesweep"+str(k)+"_"+interval_name+".txt"
#    if os.path.exists(src_log):    
#        shutil.move(src_log, dest_log)
#    if os.path.exists(basepath+folder_name+"/"+sweep_name+"/preProcessing/"):     
#        shutil.rmtree(basepath+folder_name+"/"+sweep_name+"/preProcessing/")

def erase_primal_adjoint_files(the_primal_path, the_adjoint_path, folder_name, k):
    erase_all_files(the_primal_path, folder_name, k)
    erase_all_adjoint_files(the_adjoint_path, folder_name, k)

#################  LOGTABLE FUNCTIONS  #################


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
    print("Row number = Sweep Number, pressureDrop, velocity defect, continuity defect (flux), primalWallTime, SweepWallTime, AccumulatedTime\n")
    print("Wrinting into logtable in  " + basepath + folder_name + "\n")
    table = []
    primalWallTime = []
    acc_time=0.0
    os.chdir(basepath + folder_name)
    with open("logtable.csv", 'a', newline='') as tab:
        writer = csv.writer(tab)
        for k in range(1, n+1):
            sweep_name=mysweep.format(k)
            velocity=0.0;
            flux=0.0;
            
            #Fetch pressureDrop
            pressureDrop=fetchPressureDrop(basepath, sweep_name, k)
            
            for i in range(2, n+1):
                interval_name=myinterval.format(i)
                _, flux_value = post.fetch_values_defect(basepath, sweep_name, interval_name, "shooting_defect_logfile" + sweep_name + "_" + interval_name + ".txt")
                velocity_value, _ = post.fetch_values_defect(basepath, sweep_name, interval_name, "shooting_defect_logfile" + sweep_name + "_" + interval_name + ".txt")
                velocity=velocity+float(velocity_value)
                flux=flux+float(flux_value)

            os.chdir(basepath + folder_name)
            with open("pimpleDyMFoam_times.txt", "r") as timefile:
                for y in timefile:
                    y = y.strip()
                    primalWallTime.append(float(y))
            timefile.close()
            with open("subintervals_times.txt", "r") as timefile:
                for index, y in enumerate(timefile):
                    if index == k-1:  # Read the line corresponding to the current round (k)
                        y = y.strip()
                        acc_time+=float(y)
                        #print(y)
                        break

            # Store the variables in a table or data structure of your choice
            table.append([str(k) + "    " + str(pressureDrop) + "    " + str(round(velocity, 3)) + "    " + str(round(flux, 3)) + "    " + str(round(primalWallTime[k-1],3)) + "    " + str(round(acc_time, 3))])
        
        # Write the row to the CSV file
        writer.writerows(table)

def store_all_adjoint_values(basepath, folder_name):
    os.chdir(basepath + folder_name)
    print("All value will be stored in a CSV file as follows:\n")
    print("Row number = Sweep Number, pressureDrop, velocity defect, continuity defect (flux), primalWallTime, SweepWallTime, AccumulatedTime\n")
    print("Wrinting into logtable in  " + basepath + folder_name + "\n")
    table = []
    primalWallTime = []
    acc_time=0.0
    os.chdir(basepath + folder_name)
    with open("adjointlogtable.csv", 'a', newline='') as tab:
        writer = csv.writer(tab)
        for k in range(1, n+1):
            sweep_name=mysweep.format(k)
            velocity=0.0;
            flux=0.0;
            
            #Fetch pressureDrop
            pressureDrop=fetchAdjointPressureDrop(basepath, sweep_name, k)
            
            for i in range(1, n):
                interval_name=myinterval.format(i)
                try:
                    _, flux_value = post.fetch_adjoint_values_defect(basepath, sweep_name, interval_name, "adjoint_shooting_defect_logfile" + sweep_name + "_" + interval_name + ".txt")
                except Exception as e:
                    print("flux value problem")
                    print(e)
                try:
                    velocity_value, _ = post.fetch_adjoint_values_defect(basepath, sweep_name, interval_name, "adjoint_shooting_defect_logfile" + sweep_name + "_" + interval_name + ".txt")
                except Exception as e:
                    print("velocity value problem ")
                    print(e)                
                try:
                    velocity=velocity+float(velocity_value)
                    flux=flux+float(flux_value)
                except Exception as e:
                    print("summing problem")
                    print(e)
            os.chdir(basepath + folder_name)
            with open("adjointPimpleDyMFoam_times.txt", "r") as timefile:
                for y in timefile:
                    y = y.strip()
                    primalWallTime.append(float(y))
            timefile.close()
            with open("adjoint_subintervals_times.txt", "r") as timefile:
                for index, y in enumerate(timefile):
                    if index == k-1:  # Read the line corresponding to the current round (k)
                        y = y.strip()
                        acc_time+=float(y)
                        #print(y)
                        break

            # Store the variables in a table or data structure of your choice
            table.append([str(k) + "    " + str(pressureDrop) + "    " + str(round(velocity, 3)) + "    " + str(round(flux, 3)) + "    " + str(round(primalWallTime[k-1],3)) + "    " + str(round(acc_time, 3))])
        
        # Write the row to the CSV file
        writer.writerows(table)
        print("Done.\n\n\n")




def find_logfile(basepath, sweep_name, thefile):
    try:
        file_path = basepath + folder_name + "/" + sweep_name + "/logfiles/"
        for root, dirs, files in os.walk(file_path):
            if thefile in files:
                logfile_path = os.path.join(root, thefile)
                return (logfile_path)
            else:
                print(thefile + " not found")
    except Exception:
        try:
            file_path = basepath + folder_name + "/" + sweep_name
            for root, dirs, files in os.walk(file_path):
                if thefile in files:
                    logfile_path = os.path.join(root, thefile)
                    return (logfile_path)
                else:
                    print(thefile + " not found")
        except Exception as e:
            print(str(e))

def fetchPressureDrop(basepath, sweep_name, k):
    #print(basepath + folder_name + "/" + sweep_name + "/adjointPostProcessing/")
    if os.path.exists(basepath + folder_name + "/" + sweep_name + "/logfiles/"):
        pressure_path= basepath + folder_name + "/" + sweep_name + "/logfiles/pressureDrop" + str(k) + ".txt"
        pressureDrop=post.fetch_values(basepath, pressure_path, "pressureDrop is")
    elif os.path.exists(basepath + folder_name + "/" + sweep_name + "/postProcessing/"):
        pressure_path= basepath + folder_name + "/" + sweep_name + "/postProcessing/pressureDrop.txt"
        pressureDrop=post.fetch_values(basepath, pressure_path, "pressureDrop is")
    else:
        print("Pressure Drop not found ")
        pressureDrop=0
    return(pressureDrop)
    
def fetchAdjointPressureDrop(basepath, sweep_name, k):
    if os.path.exists(basepath + folder_name + "/" + sweep_name + "/logfiles/"):
        pressure_path= basepath + folder_name + "/" + sweep_name + "/logfiles/adjointPressureDrop" + str(k) + ".txt"
        pressureDrop=post.fetch_values(basepath, pressure_path, "adjointPressureDrop is")
    elif os.path.exists(basepath + folder_name + "/" + sweep_name + "/adjoint_postProcessing/"):
        pressure_path= basepath + folder_name + "/" + sweep_name + "/adjoint_postProcessing/adjointPressureDrop.txt"
        pressureDrop=post.fetch_values(basepath, pressure_path, "adjointPressureDrop is")  
    else:
        print("Pressure Drop not found ")
        pressureDrop=0
    return(pressureDrop)

def fetch_values_defect(basepath, sweep_name, interval_name, thefile):
# Regular expression pattern to capture the value
    velocity = r"defects \(velocity\): sum local = ([\d.e+-]+)"
    fluxes = r"defects \(fluxes\): sum local = ([\d.e+-]+)"    
    
    if os.path.exists(basepath + folder_name + "/" + sweep_name + "/" + interval_name +  "/shootingDefect/"):
        path_file=basepath + folder_name + "/" + sweep_name + "/" + interval_name +  "/shootingDefect/"        
        os.chdir(path_file)
    #path_file = #shooting_defect_logfile" + sweep_name + "_" + interval_name + ".txt"
    elif os.path.exists(basepath + folder_name + "/" + sweep_name + "/logfiles/"):
        path_file =basepath + folder_name + "/" + sweep_name + "/logfiles/"
        os.chdir(path_file)
        #with open(thefile, "r") as myfile:
         #   text = myfile.read()
    
    if os.path.exists(basepath + folder_name + "/" + sweep_name + "/" + interval_name +  "/shootingDefect/"):
        path_file=basepath + folder_name + "/" + sweep_name + "/" + interval_name +  "/shootingDefect/"        
        os.chdir(path_file)
    
    with open(thefile, "r") as myfile:
        text = myfile.read()
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

def fetch_adjoint_values_defect(basepath, sweep_name, interval_name, thefile):
    # Regular expression pattern to capture the value
    velocity = r"defects \(adjoint velocity\): sum local = [-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?"  ### r"[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?"      ([\d.e+-]+)
    fluxes = r"defects \(adjoint fluxes\): sum local = [-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?"#([\d.e+-]+)"    
    if os.path.exists(basepath + folder_name + "/" + sweep_name + "/logfiles/"):
        path_file =basepath + folder_name + "/" + sweep_name + "/logfiles/"
        os.chdir(path_file)
        print(path_file)
    elif os.path.exists(basepath + folder_name + "/" + sweep_name + "/" + interval_name +  "/"):
        path_file=basepath + folder_name + "/" + sweep_name + "/" + interval_name +  "/"        
        os.chdir(path_file)
    if os.path.exists(path_file + thefile):
        with open(thefile, "r") as myfile:
            text = myfile.read()
            # Search for the pattern in each line
            for line in text.split('\n'):
                velocity_match = re.search(velocity, line)
                flux_match = re.search(fluxes, line)
                if velocity_match:
                    velocity_defect = velocity_match.group(1)
                    #print("defects (adjoint velocity): sum local:", velocity_defect)
                if flux_match:
                    flux_defect = flux_match.group(1)
                    #print("defects (adjoint fluxes): sum local:", flux_defect)
                    return(float(velocity_defect), float(flux_defect))

def fetch_values(basepath, path_file, line_to_find):
    value = None

    with open(path_file, "r") as file:
        for line in file:
            if line_to_find in line:
                value = line.split()[-1]
                return(value)
                break

    if value is not None:
        print("Extracted value:", value)
    else:
        print("Value not found in the file.")

#################    PLOT FUNCTIONS    #################

def plot_my_data(basepath, filename, x_axis, y_axis, new_folder, k):
    os.chdir(basepath + new_folder + "/")
    print(basepath + new_folder)
    # Read the first and last lines of logtable.csv
    with open("logtable.csv", 'r') as file:
        first_line = file.readline().strip().split('    ')
        last_line = file.readlines()[-1].strip().split('    ')

    # Get the column values based on x_axis and y_axis
    num_columns = len(first_line)
    x_min = float(first_line[min(x_axis - 1, num_columns - 1)])
    x_max = float(last_line[min(x_axis - 1, num_columns - 1)])
    y_min = float(first_line[min(y_axis - 1, num_columns - 1)])
    y_max = float(last_line[min(y_axis - 1, num_columns - 1)])

    axis_labels = {
        1: "Sweep [-]",
        2: "Pressure Drop [Nm, E-7]",
        3: "Impuls Defect [kg.m.s⁻¹]",
        4: "Continuity Defect [kg.m.s⁻¹]",
        5: "Wall Time Primal [s]",
        6: "Total Accumulated Time [s]"
    }
    xrange_values = {
        1: "[{}:{}]\n".format(0,k+1),
        2: "[{}:{}]\n".format(0,x_max),
        3: "[{}:{}]\n".format(0,x_max),
        4: "[{}:{}]\n".format(0,x_max),
        5: "[{}:{}]\n".format(0,x_max),
        6: "[{}:{}]\n".format(0,x_max),
    }
    yrange_values = {
        1: "[0:{}]\n".format(k+1),
        2: "[0:1.5]\n",
        3: "[{}:{}]\n".format(y_max,y_min),
        4: "[{}:{}]\n".format(y_max,y_min),
        5: "[{}:{}]\n".format(0,y_max + 50),
        6: "[{}:{}]\n".format(0,y_max),
    }

    with open(filename, 'r') as file:
        lines = file.readlines()

    modified_lines = []
    for line in lines:
        if line.startswith('set title'):
            #new_title="Plot for " + str(n) + " subintervals"
            new_title = "Plot for {} subintervals".format(k)
            modified_lines.append("set title '" + new_title + "'\n")
        elif line.startswith("set xlabel"):
            modified_lines.append("set xlabel '" + axis_labels[x_axis] + "'\n")
        elif line.startswith("set ylabel"):
            modified_lines.append("set ylabel '" + axis_labels[y_axis] + "'\n")
        elif line.startswith("set xrange"):
            modified_lines.append("set xrange " + xrange_values[x_axis])
        elif line.startswith("set yrange"):
            modified_lines.append("set yrange " + yrange_values[y_axis])
        elif line.startswith("plot 'logtable.csv'"):
            parts = line.split("using ")
            parts[1] = str(x_axis) + ":" + str(y_axis)
            if y_axis == 2:
                parts[1] = str(x_axis) + ":(${}*10e6)".format(y_axis)
            modified_lines.append("using ".join(parts) + " with linespoints ls 1 title 'Primal Shooting',")
        elif line.startswith("set output "):
            
            # Construct the plot filename based on the given options
            #plot_filename = "plot_{}_{}_{}.eps".format(x_axis, y_axis, title)
            plot_filename = "plot_{}_{}_{}_intervals.eps".format(x_axis, y_axis, k)
            modified_lines.append("set output '" + plot_filename + "'\n")
        else:
            modified_lines.append(line)

    with open(filename, 'w') as file:
        file.writelines(modified_lines)

    
    # Execute the bash command to generate the plot
    subprocess.run(["gnuplot", filename])
    # # Example usage:
        # filename = 'path/to/file'
        # modify_plot_code_in_file(filename, 6, 2, "Custom Plot Title")

def all_plots_new(basepath):
    bash_path="/home/jcosson/workspace/henersj_shootingdata/scripts/gnuplot/shootingManagerOutput.plot"
    intervals=[2,3,5,7,10,14,28,56,100]
    for intervals in intervals:
        new_folder=str(intervals)+"_intervals_05-06-23"
        dest_bash=basepath + new_folder + "/shootingManagerOutput.plot"
        shutil.copyfile(bash_path, dest_bash)
        print("Plotting in " + basepath + new_folder + " ...\n")        
        os.chdir(basepath + new_folder + "/")
        plot_my_data(basepath, "shootingManagerOutput.plot", 6, 2, new_folder, intervals)
        plot_my_data(basepath, "shootingManagerOutput.plot", 6, 1, new_folder, n)
        plot_my_data(basepath, "shootingManagerOutput.plot", 1, 2, new_folder, n)
        plot_my_data(basepath, "shootingManagerOutput.plot", 1, 3, new_folder, n)
        plot_my_data(basepath, "shootingManagerOutput.plot", 1, 4, new_folder, n)
        plot_my_data(basepath, "shootingManagerOutput.plot", 1, 5, new_folder, n)
    print("Data has been plotted.")


def multiple_plots(basepath, filename, x_axis, y_axis, intervals):
    os.chdir(basepath)
    bash_path="/home/jcosson/workspace/henersj_shootingdata/scripts/gnuplot/multiplePlotShooting.plot"
    dest_bash=basepath + "/multiplePlotShooting" + str(x_axis) + str(y_axis) + ".plot"
    shutil.copyfile(bash_path, dest_bash)
    filename="multiplePlotShooting" + str(x_axis) + str(y_axis) + ".plot"
    print("Plotting in " + basepath + " ...\n")       
    for interval in intervals:
        with open(str(interval) + "_intervals_05-06-23" + "/logtable" + str(interval) + ".csv", 'r') as file:
            first_line = file.readline().strip().split('    ')
            last_line = file.readlines()[-1].strip().split('    ')

        # Get the column values based on x_axis and y_axis
        num_columns = len(first_line)
        x_min = float(first_line[min(x_axis - 1, num_columns - 1)])
        x_max = float(last_line[min(x_axis - 1, num_columns - 1)])
        y_min = float(first_line[min(y_axis - 1, num_columns - 1)])
        y_max = float(last_line[min(y_axis - 1, num_columns - 1)])            

        axis_labels = {
            1: "Sweep [-]",
            2: "Pressure Drop [Nm, E-7]",
            3: "Impuls Defect [kg.m.s⁻¹]",
            4: "Continuity Defect [kg.m.s⁻¹]",
            5: "Wall Time Primal [s]",
            6: "Total Accumulated Time [s]"
            }
        xrange_values = {
            1: "[{}:{}]\n".format(0,interval),
            2: "[{}:{}]\n".format(0, x_max*10e5),
            3: "[{}:{}]\n".format(x_max,x_min),
            4: "[{}:{}]\n".format(0,x_max),
            5: "[{}:{}]\n".format(0,x_max),
            6: "[{}:{}]\n".format(0,x_max),
            }
        yrange_values = {
            1: "[0:{}]\n".format(interval),
            2: "[0:{}]\n".format(y_max, 10e-5),
            3: "[{}:{}]\n".format(y_max,y_min),
            4: "[{}:{}]\n".format(y_max,y_min),
            5: "[{}:{}]\n".format(0,y_max + 50),
            6: "[{}:{}]\n".format(0,y_max),
            }
    with open(filename, 'r') as file:
        lines = file.readlines()
    modified_lines = []
    num=1
    for line in lines:
        if line.startswith('set title'):
            new_title = "Plot Comparison over {} subintervals".format(intervals)
            modified_lines.append("set title '" + new_title + "'\n")
        elif line.startswith("set xlabel"):
            modified_lines.append("set xlabel '" + axis_labels[x_axis] + "'\n")
        elif line.startswith("set ylabel"):
            modified_lines.append("set ylabel '" + axis_labels[y_axis] + "'\n")
        elif line.startswith("set xrange"):
            modified_lines.append("set xrange " + xrange_values[x_axis])
        elif line.startswith("set yrange"):
            modified_lines.append("set yrange " + yrange_values[y_axis])
        elif line.startswith("set output "):
            plot_filename = "plot_{}_{}_{}_intervals.eps".format(x_axis, y_axis, "Comparison")
            modified_lines.append("set output '" + plot_filename + "'\n")
        
        elif line.endswith("' , \\\n"):
            print(line)
            #Delete existing lines
            del lines[num-1]
        else:
            modified_lines.append(line)
        num+=1
        print(line)

    plot_commands = []
    for interval in intervals:
        #plot_command = "'{}_intervals_05-06-23/logtable{}.csv' using 6:($2*10e6) with linespoints ls 1 title '{} intervals' ".format(interval, interval, interval)
        plot_command = "'{}_intervals_05-06-23/logtable{}.csv' using {}:{} with linespoints title '{} intervals' ".format(interval, interval, x_axis, y_axis, interval)
        plot_commands.append(plot_command)
    
    # Join the plot commands using a comma and a line continuation character \
    plot_command_string = ", \\\n".join(plot_commands)
    
    # Final plot command
    final_plot_command = "plot " + plot_command_string
    
    # Append the final_plot_command to modified_lines
    modified_lines.append(final_plot_command)       
        
    with open(filename, 'w') as file:
        file.writelines(modified_lines)
    
    # Execute the bash command to generate the plot
    subprocess.run(["gnuplot", filename])