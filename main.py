# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 09:42:28 2023

@author: jcosson
"""
import os
import time
import config as c
from config import primal_path, primitive_path, steffensen_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path;
from config import n, theta, T, a, t, deltaT, myinterval, mysweep, folder_name;
from src import solvers as sol, preprocessing as pre, postprocessing as post
import sys
import shutil
################                  PATH                     ################
c.headings()
################           CHOICE OF COMPUTATION           ################
#Primitive shooting :
basepath=primitive_path
os.chdir(basepath)
#sol.primal_nofastpropagator_seq(basepath)

sol.computeSteffensenMethod(basepath, folder_name)
################################################################
#for k in range (1, n):
#    start_sweep=time.time()
#    for i in range (2, n + 1):
#        sweep_name=mysweep.format(k)
#        #if not k==n:
#        m=1
#        print("Starting shooting update process for " + sweep_name + ".\n")
#        #for i in range(2, n + 1):
#        interval_name=myinterval.format(i)
#        pre.prepareShootingUpdate(basepath, folder_name, sweep_name, k, i)
#        interval_name=myinterval.format(m)
#        sol.computeShootingUpdate(steffensen_path, folder_name, sweep_name, interval_name)
#        post.shootingUpdateP(steffensen_path, folder_name, sweep_name, interval_name, k, m)
#        m=m + 1
#        if k==n-1:
#            print("Steffensen's Method terminated. Sweep " + str(k) + "updated.")
#            #return(0)
#    end_time = time.time()
#    print(end_time-start_sweep)
    #elapsed_time = end_time - start_time
    #num_minutes=int(elapsed_time/60)
    #num_seconds=elapsed_time%60
    #print("Elapsed time:",num_minutes, "minutes and" , num_seconds, "seconds")


###########################################################################

