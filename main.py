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
 
basepath="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/moderate_deformed/primal/"
calcs_undeformed="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/undeformed_turbulent/"
ref_cases_mod_def="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/reference_cases/moderate_deformed_SDuct/"
#import module-run.py
############## FUNCTIONS ####################################

def decimal_analysis(number):  ##On analyse les décimales pour avoir des périodes cohérentes avec les dossiers : 1, 2 ou 3 décimales
        if number * 10 % 10 == 0:
            return round(number,2)
        else:
            return round(number,3)

def pimpleMyFoam(folder_name,sweep_name,interval_name):
    pimple_path=basepath+folder_name+"/"+sweep_name+"/"+interval_name
    command='pimpleDyMFoam >pimple.log 2>&1 &'
    #result=subprocess.run(command, shell=True, cwd=pimple_path,capture_output=True, text=True)
    #return(result.stdout)
    
def computePressureDrop(folder_name,sweep_name):
    pressure_path=basepath+folder_name+"/"+sweep_name+"/postProcessing"    
    command='computePressureDropFoam start end > pressureDrop.txt'
    #result=subprocess.run(command, shell=True, cwd=pressure_path,capture_output=True, text=True)
    #return(result.stdout)
    #with open("pressureDrop.txt", "r") as f:
    #    log_data = f.read()
    #pressure_drop_index = log_data.find("pressureDrop is")
    #pressure_drop_str = log_data[pressure_drop_index:].split()[2]
    #pressure_drop = float(pressure_drop_str)
    #print("The pressure drop for "+sweep_name+" is "+pressure_drop)
#######################################################
#########INITIALIZATION################################
#folder_name=input("Name your folder: ")
folder_name="four_intervals"
os.mkdir(folder_name)
# After testing is done, please uncomment the following
#n=int(input("Set the number of shooting intervals: "));
#theta=input("Define the starting time (example: 0.4): ");

# For the testing we can uncomment the following
n=4;
theta=0.4;
T=0.1;
deltaT=T/n

########## SET THE SWEEP FOLDERS ##############################

#sweep="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/moderate_deformed/primal/"
myinterval="interval{}"
mysweep="sweep{}"

############## SWEEP 1 INITIALIZATION ##################################
for k in range(1,2): ##je laisse le loop pour l'instant pour ma rappeler pour après, mais ensuite pour k=1, je dois le supprimer puisque c'est juste sweep1  
    sweep_name=mysweep.format(k)
    sweep_path=os.path.join(folder_name,sweep_name)
    os.mkdir(sweep_path)
    
##########  ALL INTERVALS IN SWEEP1 ###################################
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
        print('The directory '+polyMesh_path+' has not been deleted because we outcommented the command line.')
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
        
        #Executing PimpleMyFoam
        pimpleMyFoam(folder_name,sweep_name,interval_name)
        
        #Prepare postProcessing
        source_file="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/scripts/primitiveShooting/primal"
        destination_file=folder_name+'/'+sweep_name
        subprocess.run(['chmod','u+x','preparePostProcessing.sh'])
        #subprocess.run(['preparePostProcessing.sh'])        
        
        #Prepare computePressureDrop      
        computePressureDrop(folder_name,sweep_name)
        
        
        
###############################################################

##########  FOR LOOP FOR SWEEP FROM 2-n ###################################
for k in range(2,n+1):  
    sweep_name=mysweep.format(k)
    previous_sweep_name=mysweep.format(k-1)
    sweep_path=os.path.join(folder_name,sweep_name)
    os.mkdir(sweep_path)
##########  ALL INTERVALS IN SWEEPk ###################################
    # Copy Directories that were already shoot
    for x in range(1,k):
        interval_name=myinterval.format(x)
        source_interval=basepath+folder_name+"/"+previous_sweep_name+"/"+interval_name
        destination_interval=basepath+folder_name+"/"+sweep_name
        shutil.copytree(source_interval,os.path.join(destination_interval,os.path.basename(source_interval)))
    #Preparing shooting directories from sweep1 data
    for i in range(k,n+1):
        interval_name=myinterval.format(i)
        destination_constant=basepath+folder_name+"/"+sweep_name+"/"+interval_name
        destination_system=basepath+folder_name+"/"+sweep_name+"/"+interval_name
        previous_interval_name=myinterval.format(i-1)
        startTime=decimal_analysis(theta+deltaT*(i-2))
        endTime=decimal_analysis(theta+deltaT*(i-1))
        
        source_constant=basepath+folder_name+"/"+previous_sweep_name+"/"+interval_name+'/constant'
        source_system=basepath+folder_name+"/"+previous_sweep_name+"/"+interval_name+'/system'
        source_endTime=basepath+folder_name+"/"+previous_sweep_name+"/"+previous_interval_name+'/'+str(endTime)        
        destination_endTime=basepath+folder_name+"/"+sweep_name+"/"+interval_name        
        
        shutil.copytree(source_constant,os.path.join(destination_constant,os.path.basename(source_constant)))
        shutil.copytree(source_system,os.path.join(destination_system,os.path.basename(source_system)))
        #shutil.copytree(source_endTime,os.path.join(destination_endTime,os.path.basename(source_endTime)))
        
        #pimpleMyFoam(basepath,folder_name,sweep_name,interval_name)
    ## Prepare computePressure
       # computePressureDrop(folder_name,sweep_name)
        
        
        
        
        
#cp -r ../sweep2/preparePostProcessing.sh .
 #1458  ./preparePostProcessing.sh 
 #1459  computePressureDropFoam start end
 #1460  ls
 #1461  cd postProcessing/
 #1462  computePressureDropFoam start end
 #1463  cd ..
 #1464  ls
        
        
