# -*- coding: utf-8 -*-
"""
Created on Tue May  2 12:10:07 2023

@author: Lucie
"""
#import colorama
#from colorama import Fore, Style
####### CONFIG FILE ########
# Here, you can adapt the different paths to your structure.

#PRIMAL PATHS
primal_path="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/moderate_deformed/primal/"
primitive_path="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/moderate_deformed/primal/primitive_shooting/"
steffensen_path="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/moderate_deformed/primal/steffenssens_method/"
#CALCS PATHS
calcs_undeformed="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/calcs/undeformed_turbulent/"
#REFERENCE PATHS
ref_cases="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/reference_cases/"
ref_cases_mod_def="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/reference_cases/moderate_deformed_SDuct/"
#MY PROJECTS PATHS
project_path="/home/jcosson/workspace/henersj-shootingdata-3b74bb73f55e/scripts/master_project/"
# CHOOSE YOUR BASE WORKING PATH
basepath=primitive_path

## VARIABLES
# After testing is done, please uncomment the following
#n=int(input("Set the number of shooting intervals: "));
#theta=input("Define the starting time (example: 0.4): ");
n=7; #Amount of sweeps / shooting intervals
folder_name=str(n)+"_intervals"
theta=0.4; #Starting time in seconds
T=0.1; #Length of one period
a=n; #Amount of sweeps in the first loop
deltaT=T/n
t=0.001 #Sampling size for OpenFoam Computations
myinterval="interval{}"
mysweep="sweep{}"




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


    