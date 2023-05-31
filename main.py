# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 09:42:28 2023

@author: jcosson
"""
import os
import time
import config as c
import subprocess
from concurrent import futures

from config import primal_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, adjoint_path;
from config import n, theta, T, a, t, deltaT, myinterval, mysweep, folder_name;
from src import solvers as sol, preprocessing as pre, postprocessing as post, boundary_conditions as bc, adjoint_solvers as adsol
import sys
import shutil
import concurrent.futures

################                  PATH                     ################
c.headings()
################           CHOICE OF COMPUTATION           ################
#Primitive shooting :
basepath=primal_path
os.chdir(adjoint_path)
    
####################

#The big Solver
#sol.primal_shooting_stef_update(primal_path, "yes")
#adsol.computeAdjoint()
#sol.the_shooting_manager()
#for k in range(1, n+1):
#    sweep_name=mysweep.format(k)
#    sol.computeAdjointDefect(basepath, sweep_name, k)

sol.primal_shooting_stef_update(basepath, "yes")