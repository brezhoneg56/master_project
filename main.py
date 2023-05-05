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
import shutil
#########                  PATH                        ###########################################################################################
c.headings()
os.chdir(basepath)
####         AUTOMATIC FILE DELETION/CREATIION           #########################################################################################

if os.path.exists(folder_name):
    shutil.rmtree(folder_name)
    print("Previous directory named "+folder_name+" has been replaced.")

######             CHOICE OF COMPUTATION                ##########################################################################################

#Primitive shooting :
#sol.primal_nofastpropagator_seq()

#Steffensen shooting :
#sol.computeSteffensenMethod(folder_name)
for k in range (1, n+1):
    for i in range (2, n+1):
        sweep_name=mysweep.format(k)
        #if not k==n:
        m=1
        print("Starting shooting update process for "+sweep_name+".\n")
        #for i in range(2, n+1):
        interval_name=myinterval.format(i)
        pre.prepareShootingUpdate(folder_name, sweep_name, k, i)
        interval_name=myinterval.format(m)
        sol.computeShootingUpdate(folder_name, sweep_name, interval_name)
        post.shootingUpdateP(folder_name, sweep_name, interval_name, k, m)
        m=m+1
        if k==n-1:
            print("Steffensen's Method terminated. Sweep "+k+"updated.")
            return
##################################################################################################################################################
