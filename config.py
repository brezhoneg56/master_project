# -*- coding: utf-8 -*-
"""
Created on Tue May  2 12:10:07 2023

@author: Julien
"""

####### CONFIG FILE ########
# Here, you can adapt the different paths to your structure.

#PRIMAL PATHS
#primal_path="/home/jcosson/workspace/henersj_shootingdata/calcs/moderate_deformed/primal/modef_full_20-07/" # modef + full-scheme : REF POUR ADJOINT
#primal_path="/home/jcosson/workspace/henersj_shootingdata/calcs/moderate_deformed/primal/modef_partial_05-06-23/"   # model + partial-scheme
#primal_path="/home/jcosson/workspace/henersj_shootingdata/calcs/moderate_deformed/primal/zero_init_full/"            # zero-init + full-scheme    
primal_path="/home/jcosson/workspace/henersj_shootingdata/calcs/moderate_deformed/primal/zero_init_partial_27-07/"  # zero-init + partial scheme

adjoint_path="/home/jcosson/workspace/henersj_shootingdata/calcs/moderate_deformed/adjoint/adjoint_without_newton_30-07/" #modef + partial-scheme
#adjoint_path="/home/jcosson/workspace/henersj_shootingdata/calcs/moderate_deformed/adjoint/adjoint_newton_20-07/" #modef + full-scheme
#adjoint_path="/home/jcosson/workspace/henersj_shootingdata/calcs/moderate_deformed/adjoint/coupled_newton/" #coupling modef + full-scheme

#CALCS PATHS
calcs_undeformed="/home/jcosson/workspace/henersj_shootingdata/calcs/undeformed_turbulent/"
calcs_path="/home/jcosson/workspace/henersj_shootingdata/calcs/"
#REFERENCE PATHS
ref_cases="/home/jcosson/workspace/henersj_shootingdata/reference_cases/"
postPro_cases="/home/jcosson/workspace/henersj_shootingdata/postProcessing/"
ref_cases_mod_def="/home/jcosson/workspace/henersj_shootingdata/reference_cases/moderate_deformed_SDuct/"
#MY PROJECTS PATHS
project_path="/home/jcosson/workspace/henersj_shootingdata/scripts/master_project/"
# CHOOSE YOUR BASE WORKING PATH
#basepath="/home/julien/workspace/master_project/"

## VARIABLES
# After testing is done, please uncomment the following
#n=int(input("Set the number of shooting intervals: "));
#theta=input("Define the starting time (example: 0.4): ");
n=56; #Amount of sweeps / shooting intervals
folder_name=str(n)+"_intervals_27-07-23_zero-init_primitive"
#"_intervals_20-07_primal-adjoint"#"_intervals_27-07-23_zero-init_primitive"# ## "_intervals_20-07_primal-adjoint"
theta=0.4; #Starting time in seconds
T=0.1; #Length of one period
a=n; #Amount of sweeps in the first loop
deltaT=T/n
t=0.001 #Sampling size for OpenFoam Computations
myinterval="interval{}"
mysweep="sweep{}"
maxCPU=14 #Gives the maximum amount of parallely working CPUs



#### HEADINGS #########
def headings():
    print(  '╔═════════════════════════════════════════════════════════════════╗' )
    print("""║                     .?77777777777777$.                          ║   
║                   777..777777777777$+                           ║
║                  .77    7777777777$$$                           ║
║                  .777 .7777777777$$$$                           ║
║                  .7777777777777$$$$$$                           ║
║                  ..........:77$$$$$$$                           ║
║             .77777777777777777$$$$$$$$$.=======.                ║
║             777777777777777777$$$$$$$$$$.========               ║
║             7777777777777777$$$$$$$$$$$$$.=========             ║
║             77777777777777$$$$$$$$$$$$$$$.=========             ║
║             777777777777$$$$$$$$$$$$$$$$ :========+.            ║
║             77777777777$$$$$$$$$$$$$$+..=========++~            ║
║             777777777$$..~=====================+++++            ║
║             77777777$~.~~~~=~=================+++++.            ║
║             777777$$$.~~~===================++++++.             ║
║             77777$$$$.~~==================++++++++:             ║
║             7$$$$$$$.==================++++++++++.              ║
║             .,$$$$$$.================++++++++++~.               ║
║                  .=========~.........                           ║
║                  .=============++++++                           ║
║                  .===========+++..+++                           ║
║                  .==========+++.  .++                           ║
║                   ,=======++++++,,++,                           ║
║                   ..=====+++++++++=.                            ║
║                              ..~+=...                           ║    """       )
    print('║               Launching Python Shooting Manager!                ║' )
    print('║       This program requires a working version of OpenFOAM       ║' )
    print('╚═════════════════════════════════════════════════════════════════╝' )


    