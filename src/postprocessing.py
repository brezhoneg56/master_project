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
            pressure_path=post.find_logfile(basepath, sweep_name, "pressureDrop" + str(k) + ".txt")
            try:
                pressureDrop=post.fetch_values(basepath, pressure_path, "pressureDrop is     ")
            except Exception:
                print("Pressure Drop not found")
                pressureDrop=0
            
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

def find_logfile(basepath, sweep_name, thefile):
    file_path = basepath + folder_name + "/" + sweep_name + "/logfiles/"
    for root, dirs, files in os.walk(file_path):
        if thefile in files:
            logfile_path = os.path.join(root, thefile)
            return (logfile_path)
        else:
            print(thefile + " not found")

def fetch_values_defect(basepath, sweep_name, interval_name, thefile):
    path_file = basepath + folder_name + "/" + sweep_name + "/logfiles/"#shooting_defect_logfile" + sweep_name + "_" + interval_name + ".txt"
    os.chdir(path_file)
    with open(thefile, "r") as myfile:
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

def plot_my_data(basepath, filename, x_axis, y_axis, title):
    os.chdir(basepath + folder_name)
    with open(filename, 'r') as file:
        lines = file.readlines()

    modified_lines = []
    for line in lines:
        if line.startswith('set title'):
            modified_lines.append("set title '" + title + "'\n")
        elif line.startswith("plot 'logtable.csv'"):
            parts = line.split("using ")
            parts[1] = str(x_axis) + ":" + str(y_axis)
            modified_lines.append("using ".join(parts))
        else:
            modified_lines.append(line)

    with open(filename, 'w') as file:
        file.writelines(modified_lines)

    # Example usage:
        #filename = 'path/to/file'
        #modify_plot_code_in_file(filename, 6, 2, "Custom Plot Title")



#def plot_results(basepath):
#    os.chdir(basepath + folder_name)
#    line_2 = []
#    line_last = []
#    
#    with open("logtable.csv", "r") as file:
#        for line in file:
#            data = line.split()
#            line_2.append(float(data[1]))
#            line_last.append(float(data[-1]))
#
#    # Plotting
#    plt.plot(line_last, line_2, 'bo-')  # 'bo-' represents blue color, marker 'o', and solid line
#    plt.xlabel('Last Line')
#    plt.ylabel('Second Line')
#    plt.title('Second Line as a Function of Last Line')
#    plt.grid(True)
#    plt.show()

