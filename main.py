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
import fileinput

######### PATHS ########################## 
basepath="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/moderate_deformed/primal/"
calcs_undeformed="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/undeformed_turbulent/"
ref_cases_mod_def="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/reference_cases/moderate_deformed_SDuct/"
project_path="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/scripts/master_project/"
os.chdir(basepath)

############## FUNCTIONS ####################################

def decimal_analysis(number):  ##analysis of how many decimals my number has : 1, 2 ou 3 décimales
        if number * 10 % 10 == 0:
            return round(number,2)
        else:
            return round(number,3)

def copytree(src, dst, symlinks=False, ignore=None):
    """
    This is an improved version of shutil.copytree which allows writing to
    existing folders and does not overwrite existing files but instead appends
    a ~1 to the file name and adds it to the destination path.
    """

    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    if not os.path.exists(dst):
        os.makedirs(dst)
        shutil.copystat(src, dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        i = 1
        while os.path.exists(dstname) and not os.path.isdir(dstname):
            parts = name.split('.')
            file_name = ''
            file_extension = parts[-1]
            # make a new file name inserting ~1 between name and extension
            for j in range(len(parts)-1):
                file_name += parts[j]
                if j < len(parts)-2:
                    file_name += '.'
            suffix = file_name + '~' + str(i) + '.' + file_extension
            dstname = os.path.join(dst, suffix)
            i+=1
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                shutil.copy2(srcname, dstname)
        except (IOError, os.error) as why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except BaseException as err:
            errors.extend(err.args[0])
    try:
        shutil.copystat(src, dst)
    except WindowsError:
        # can't copy file access times on Windows
        pass
    except OSError as why:
        errors.extend((src, dst, str(why)))
    if errors:
        raise BaseException(errors)

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
        copytree(list_dir,postPro_destination)
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
                with open("pressureDropvalues.txt","w") as mapression:
                    mapression.write(line)
                    print(line)
                mapression.close()
    os.chdir(basepath) #back to main path
    print("Done.\n\n")
    return(result)

def prepareMyNextSweep(k):
    sweep_name=mysweep.format(k+1)
    previous_sweep_name=mysweep.format(k)
    sweep_path=os.path.join(folder_name,sweep_name)
    print("Starting shooting of "+sweep_name+"\n") 
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
        endTime=decimal_analysis(theta+deltaT*(i-1))
        
        source_constant=basepath+folder_name+"/"+previous_sweep_name+"/"+interval_name+'/constant'
        source_system=basepath+folder_name+"/"+previous_sweep_name+"/"+interval_name+'/system'
        source_endTime=basepath+folder_name+"/"+previous_sweep_name+"/"+previous_interval_name+'/'+str(endTime)        
        destination_endTime=basepath+folder_name+"/"+sweep_name+"/"+interval_name        
        
        shutil.copytree(source_constant,os.path.join(destination_constant,os.path.basename(source_constant)))
        shutil.copytree(source_system,os.path.join(destination_system,os.path.basename(source_system)))
        shutil.copytree(source_endTime,os.path.join(destination_endTime,os.path.basename(source_endTime)))
        
        print("Computing for: \n"+sweep_name+"\n"+interval_name+"\n"+"Previous end time, that is current start time: "+str(endTime))


def sweep_1_initialization(n):
#Fetch all the files from src directories and modify them for the specific case : constant, system, start_time_dir, polyMesh, controlDict
    k=1
    os.mkdir(folder_name)
    print("\nThe directory "+folder_name+" has been created at this place: \n"+basepath+"\n\n")
    sweep_name=mysweep.format(k)
    sweep_path=os.path.join(folder_name,sweep_name)
    os.mkdir(sweep_path)
    for i in range(1,n+1):
        interval_name=myinterval.format(i)
            
        # Fetching Directory constant
        source_constant=calcs_undeformed+'constant'
        destination_constant=basepath+folder_name+"/"+sweep_name+"/"+interval_name
        shutil.copytree(source_constant,os.path.join(destination_constant,os.path.basename(source_constant)))
        
        # Fetching Directory system
        source_system=calcs_undeformed+'system'
        destination_system=basepath+folder_name+"/"+sweep_name+"/"+interval_name
        shutil.copytree(source_system,os.path.join(destination_system,os.path.basename(source_system)))
        
        # Fetching Directory with starting time
        startTime=decimal_analysis(theta+deltaT*(i-1))
        endTime=decimal_analysis(theta+deltaT*i)
        source_startTime=calcs_undeformed+str(startTime)
        destination_startTime=basepath+folder_name+"/"+sweep_name+"/"+interval_name
        shutil.copytree(source_startTime,os.path.join(destination_startTime,os.path.basename(source_startTime)))
        
        # Deleting wrong polyMesh/points in the starting time directory
        polyMesh_path=basepath+folder_name+"/"+sweep_name+"/"+interval_name+'/constant/polyMesh/points'
        print('The file '+folder_name+'/'+sweep_name+'/'+interval_name+'/constant/polyMesh/points has been succefully removed.\n\n')
        os.remove(polyMesh_path)
        
        #Fetching the right polyMesh
        source_newPolyMesh=ref_cases_mod_def+"constant/polyMesh/points"
        destination_newPolyMesh=basepath+folder_name+"/"+sweep_name+"/"+interval_name+'/constant/polyMesh'
        shutil.copy(source_newPolyMesh,destination_newPolyMesh)

        #Modify the controlDict file to ajust startTime and endTime        
        controlDict_path=folder_name+'/'+sweep_name+'/'+interval_name+'/system/controlDict'
        for line in fileinput.input(controlDict_path, inplace=True):
            if line.startswith('startTime'):
                line = 'startTime       {};\n'.format(startTime)
            elif line.startswith('endTime'):
                line = 'endTime         {};\n'.format(endTime)
            print(line)
    return("Sweep 1 initialization is done.")

################################        INITIALIZATION      ################################
#folder_name=input("Name your folder: ")

folder_name="test_intervals"
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

sweep_1_initialization(n)

################################        COMPUTE MY SWEEP : sweep k in [1-n]       ################################
for k in range(1,n+1):
    sweep_name=mysweep.format(k)
    print("Starting shooting of "+sweep_name+"\n")

    ## COMPUTE MY INTERVAL     
    for i in range(k, n+1):
        pimpleDyMFoam(folder_name, sweep_name, i)
    preparePostProcessing(folder_name, sweep_name)
    computePressureDropFoam(folder_name, sweep_name)    
    prepareMyNextSweep(k)
