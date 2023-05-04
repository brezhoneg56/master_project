# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 17:05:09 2023

@author: jcosson
"""
import os
import shutil
#import subprocess
import fileinput
import sys
#sys.path.append('../')

from config import primal_path, primitive_path, steffensen_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, basepath
from config import n, theta, T, a, t, deltaT, myinterval, mysweep
def decimal_analysis(number):  ##analysis of how many decimals my number has : 1, 2 ou 3 décimales
        if number * 10 % 10 == 0:
            return round(number,2)
        else:
            return round(number,3)
        
def sweep_1_initialization(folder_name):
#Fetch all the files from src directories and modify them for the specific case : constant, system, start_time_dir, polyMesh, controlDict
    k=1
    os.chdir(basepath)    
    sweep_name=mysweep.format(k)
    sweep_path=os.path.join(folder_name,sweep_name)
    os.mkdir(sweep_path)
    print("\nThe directory "+folder_name+" has been created at this place: \n"+basepath+"\n\n")
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
        file=destination_startTime+'/'+str(startTime)+'/polyMesh/points'
        if os.path.exists(file):
            shutil.rmtree(destination_startTime+'/'+str(startTime)+'/polyMesh')
        
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
    print("Sweep 1 initialization is done.")
    return(folder_name)


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