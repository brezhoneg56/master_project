# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 09:42:28 2023

@author: jcosson
"""
import os
import re
import time
import config as c
import subprocess
from concurrent import futures
import csv
from config import primal_path, calcs_undeformed, ref_cases, ref_cases_mod_def, project_path, adjoint_path;
from config import n, theta, T, a, t, deltaT, myinterval, mysweep, folder_name, maxCPU;
from src import solvers as sol, preprocessing as pre, postprocessing as post, boundary_conditions as bc, adjoint_solvers as adsol
import sys
import shutil
import threading
import concurrent.futures
c.headings()
################           CHOICE OF COMPUTATION           ################

sol.primal_shooting_stef_update(primal_path, "no", "no")
adsol.computeAdjoint(adjoint_path, "no", "yes")


#for k in range(1,n+1):
    #post.erase_primal_adjoint_files(primal_path, adjoint_path, folder_name, k)
    #erase_all_files(the_primal_path, folder_name, k)
    #post.erase_all_adjoint_files(adjoint_path, folder_name, k)
#post.store_all_adjoint_values(adjoint_path, folder_name)
#post.store_all_values(primal_path, folder_name)