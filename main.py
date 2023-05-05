# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 09:42:28 2023

@author: jcosson
"""
import os
import config as c
from config import primal_path, primitive_path, steffensen_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, basepath;
from config import n, theta, T, a, t, deltaT, myinterval, mysweep, folder_name;
from src import solvers as sol, preprocessing as pre, postprocessing as post
import sys
import shutil
#########                  PATH                        ###########################################################################################
c.headings()
os.chdir(basepath)
####         AUTOMATIC FILE DELETION/CREATIION           #########################################################################################

if os.path.exists(folder_name):
    ans=input(print("WARNING: Directory "+folder_name+" already exists. Do you want to replace it ? (Y/N)     \n   \n"))
    if ans=="Y" or ans=="y":
        shutil.rmtree(folder_name)
    else:
        sys.exit()
    

######             CHOICE OF COMPUTATION                ##########################################################################################

#Primitive shooting :
#sol.primal_nofastpropagator_seq()

#Steffensen shooting :
sol.computeSteffensenMethod(folder_name)

##################################################################################################################################################
