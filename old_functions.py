# -*- coding: utf-8 -*-
"""
Created on Tue May 23 11:01:38 2023

@author: jcosson
"""

# OLD SOLVER FUNCTIONS

def seq_computeSteffensenMethod(basepath, folder_name): #Sequential reolsution for linearisation and Shooting Update
    start_time=time.time()
    print("\n\nStarting Steffensen's Method for " + folder_name + ".\n")
    #Initialisation of Sweep 1  
    sweep_name="sweep1"
    pre.initializeLinearisation(folder_name, sweep_name)
    #Linearisation preparation and cmputation from Sweep 2 to n
    for k in range (1, n + 1):
        sweep_name=mysweep.format(k)
        for i in range (1, n + 1):
            interval_name=myinterval.format(i)  
            sol.linearisedPimpleDyMFoam(basepath, folder_name, sweep_name, i)
            pre.prepareNextLinearization(folder_name, k, i)
    # Preparation and Computation of shootingUpdate
    for k in range (1, n + 1):
        for i in range (2, n + 1):
            sweep_name=mysweep.format(k)
            #if not k==n:
            m=1
            print("Starting shooting update process for " + sweep_name + ".\n")
            #for i in range(2, n + 1):
            interval_name=myinterval.format(i)
            pre.prepareShootingUpdate(basepath, folder_name, sweep_name, k, i)
            interval_name=myinterval.format(m)
            sol.computeShootingUpdate(folder_name, sweep_name, interval_name)
            post.shootingUpdateP(folder_name, sweep_name, interval_name, k, m)
            m=m + 1
            if k==n-1:
                print("Steffensen's Method terminated. Sweep " + str(k) + "updated.")
                return(0)
    end_time = time.time()
    elapsed_time = end_time - start_time
    num_minutes=int(elapsed_time/60)
    num_seconds=elapsed_time%60
    print("Elapsed time:",num_minutes, "minutes and" , num_seconds, "seconds")

########################################### OLD
def OLD_computeSteffensenMethod(basepath, folder_name): #Works in Steffensens path. Now we want everything in the same folder
    start_time=time.time()
    print("\n\nStarting Steffensen's Method for " + folder_name + ".\n")
    #Initialisation of Sweep 1  
    sweep_name="sweep1"
    pre.initializeLinearisation(folder_name, sweep_name)
    #Linearisation preparation and cmputation from Sweep 2 to n
    for k in range (1, n + 1):
        sweep_name=mysweep.format(k)
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = []
            for i in range (1, n + 1):
                futures.append(executor.submit(linearisedPimpleDyMFoam, basepath, folder_name, sweep_name, i))
                concurrent.futures.wait(futures)
                pre.prepareNextLinearization(folder_name, k, i)
    # Preparation and Computation of shootingUpdate
    for k in range (1, n + 1):
        for i in range (2, n + 1):
            sweep_name=mysweep.format(k)
            #if not k==n:
            m=1
            print("Starting shooting update process for " + sweep_name + ".\n")
            #for i in range(2, n + 1):
            interval_name=myinterval.format(i)
            pre.prepareShootingUpdate(basepath, folder_name, sweep_name, k, i)
            interval_name=myinterval.format(m)
            sol.computeShootingUpdate(steffensen_path, folder_name, sweep_name, interval_name)
            post.shootingUpdateP(folder_name, sweep_name, interval_name, k, m)
            m=m + 1
            if k==n-1:
                print("Steffensen's Method terminated. Sweep " + str(k) + "updated.")
                return(0)
    end_time = time.time()
    elapsed_time = end_time - start_time
    num_minutes=int(elapsed_time/60)
    num_seconds=elapsed_time%60
    print("Elapsed time:",num_minutes, "minutes and" , num_seconds, "seconds")


def VERY_OLDloop_pimpleDyMFoam(basepath, folder_name): #sequential Version of primal shooting without update
    for k in range(1, n + 1):
        sweep_name=mysweep.format(k)
        ## COMPUTE MY INTERVAL
        print("\nStarting shooting of " + sweep_name + "\n")
        for i in range(k, n + 1):
            sol.pimpleDyMFoam(basepath, folder_name, sweep_name,i)
        post.preparePostProcessing(folder_name, sweep_name)
        post.computePressureDropFoam(folder_name, sweep_name)
        while (k<n):
            pre.prepareMyNextSweep(k, folder_name)
            break
    return(myinterval, mysweep)

def OLD_loop_pimpleDyMFoam(basepath, folder_name): #Version V1 : Parallel call for all intervals within one sweep
    start_time=time.time()
    #with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []
        for k in range(1, n + 1):
            sweep_name = mysweep.format(k)
            print("\nStarting shooting of " + sweep_name + "\n")
            for i in range(k, n+1):
                futures.append(executor.submit(pimpleDyMFoam, basepath, folder_name, sweep_name, i))
            concurrent.futures.wait(futures)
            post.preparePostProcessing(basepath, folder_name, sweep_name)
            post.computePressureDropFoam(basepath, folder_name, sweep_name)
            if (k<n): #instead of while
                pre.prepareMyNextSweep(basepath, k, folder_name)
                #break
        for future in concurrent.futures.as_completed(futures):
            future.result()
    bc.time(start_time)
    #return(myinterval, mysweep)
    
    
def BASH_loop_pimpleDyMFoam(basepath, folder_name, sweep_name, k): #Version V1 : Parallel call for all intervals within one sweep
    #with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
    print("\nStarting shooting of " + sweep_name + "\n")
    print("Starting EXECUTOR ... \n")
    
    os.chdir(project_path+"sh/")
    #pass k and n+1 to bash + pfade 
   
    
    subprocess.run(["chmod",  "u+x",  "./executor_pimpleDyMFoam.sh"])    
    subprocess.run(["./executor_pimpleDyMFoam.sh", basepath, folder_name, sweep_name, str(k), str(n)])    
    os.chdir(basepath)
#    with futures.ProcessPoolExecutor() as executor:
#        
#        for i in range(k, n+1):
#            executor.submit(pimpleDyMFoam, basepath, folder_name, sweep_name, i)
#            print("Starting pimpleDyMFoam for interval " + str(i) +"\n")
#        
#        print("Started all simulations and wait \n")
#    print("EXECUTOR terminated \n")
##   concurrent.futures.wait(futures)
    post.preparePostProcessing(basepath, folder_name, sweep_name)
    post.computePressureDropFoam(basepath, folder_name, sweep_name)
    if (k<n): #instead of while
        pre.prepareMyNextSweep(basepath, k, folder_name)

def OLD_loop_linearisedPimpleDyMFoam(basepath, folder_name, sweep_name, k): #Version V1 : Parallel call for all intervals within one sweep
    #with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
    print("\nStarting linearisation of " + sweep_name + "\n")
    print("Starting LIN EXECUTOR ... \n")
    
    with futures.ThreadPoolExecutor(max_workers=13) as executor:        
        for i in range(k, n+1):
            executor.submit(linearisedPimpleDyMFoam, basepath, folder_name, sweep_name, i)
            print("Starting linearisedPimpleDyMFoam for interval " + str(i))
            pre.prepareNextLinearization(basepath, folder_name, k, i)
        
        print("\n\nAll Linearisations started, Waiting... \n")
    print("LIN EXECUTOR terminated \n\n")  
    
    
    
    #PREPROCESSING FUNCTIONS

def seq_initializeLinearisation(basepath, folder_name, sweep_name):
    #### IS ONLY THOUGHT FOR SWEEP1
    #Copy files to prepare linearisedPimpleDyMFoam
    if not os.path.exists(folder_name):
        print("ERROR: No such file or directory. Exiting Shooting Manager")
        sys.exit()
    
    #Paths for lin and fv files
    linP_path=ref_cases + "/boundaryConditions/linP"
    linU_path=ref_cases + "/boundaryConditions/linU"
    fvSchemes_path=ref_cases + "/controlBib/fvSchemes"
    fvSolution_path=ref_cases + "/controlBib/fvSolution"

    #Copy lin and fv files in every subinterval
    for i in range(1, n + 1):
        interval_name=myinterval.format(i)
        starttime_dest=basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/" + str(bc.decimal_analysis(theta + (i-1)*deltaT))
        
        #Copy lin files
        shutil.copy2(linP_path, starttime_dest)
        shutil.copy2(linU_path, starttime_dest)
        
        #Copy fv files
        shutil.copy(fvSchemes_path, basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/system")
        shutil.copy(fvSolution_path, basepath + folder_name + "/" + sweep_name + "/" + interval_name + "/system")
        bc.check_existence(ref_cases + "/boundaryConditions/", "linU")

def seq2_prepareMyNextSweep(basepath, k, folder_name):
    #Prepare all shooting intervals of next sweep for computation 
    sweep_name=mysweep.format(k+1)#k+1
    previous_sweep_name=mysweep.format(k)#k
    os.path.join(folder_name,sweep_name)
    print("\nPreparing shooting of " + sweep_name + ". ") 
    # Copy Directories that were already shoot. Warning : put that after the computations
    #Copy already shoot Directories in the next Sweep 
    for x in range(1,k+1):#k+1
        copyShootDirs(basepath, x, folder_name, previous_sweep_name, sweep_name)
    #Preparing shooting directories from sweep1 data 
    for i in range(k+1, n+1): #will become k + 1, n + 1 because of first loop being put into the big loop
        preparenextSweepStartingFiles(basepath, folder_name, previous_sweep_name, sweep_name, i)
    sweep_name=mysweep.format(k)

def seq_prepareMyNextSweep(basepath, k, folder_name): #Sequential
    myinterval="interval{}"
    mysweep="sweep{}"
    sweep_name=mysweep.format(k + 1)
    previous_sweep_name=mysweep.format(k)
    sweep_path=os.path.join(folder_name,sweep_name)
    print("\nStarting shooting of " + sweep_name + ". ") 
    # Copy Directories that were already shoot. Warning : put that after the computations
    for x in range(1,k + 1):
        interval_name=myinterval.format(x)
        source_interval=basepath + folder_name + "/" + previous_sweep_name + "/" + interval_name
        destination_interval=basepath + folder_name + "/" + sweep_name
        shutil.copytree(source_interval, os.path.join(destination_interval, os.path.basename(source_interval)))    
    
    #Preparing shooting directories from sweep1 data 
    for i in range(k+1,n+1):
        interval_name=myinterval.format(i)
        destination_constant=basepath + folder_name + "/" + sweep_name + "/" + interval_name
        destination_system=basepath + folder_name + "/" + sweep_name + "/" + interval_name
        previous_interval_name=myinterval.format(i-1)
        endTime=bc.decimal_analysis(theta + deltaT*(i-1))
        
        source_constant=basepath + folder_name + "/" + previous_sweep_name + "/" + interval_name + '/constant'
        source_system=basepath + folder_name + "/" + previous_sweep_name + "/" + interval_name + '/system'
        source_endTime=basepath + folder_name + "/" + previous_sweep_name + "/" + previous_interval_name + '/' + str(endTime)        
        destination_endTime=basepath + folder_name + "/" + sweep_name + "/" + interval_name        
        
        shutil.copytree(source_constant, os.path.join(destination_constant, os.path.basename(source_constant)))
        shutil.copytree(source_system, os.path.join(destination_system, os.path.basename(source_system)))
        shutil.copytree(source_endTime, os.path.join(destination_endTime, os.path.basename(source_endTime)))
        
    print("The " + sweep_name + " is ready to be shoot. Waiting for " + previous_sweep_name + " to terminate...")

# BOUNDARY CONDITIONS

def seq_sweep_1_initialization(basepath, folder_name):
#Fetch all the files from src directories and modify them for the specific case : constant, system, start_time_dir, polyMesh, controlDict
    #k=1
    os.chdir(basepath) 
    os.mkdir(folder_name)
    sweep_name=mysweep.format(1)
    sweep_path=os.path.join(folder_name,sweep_name)
    os.mkdir(sweep_path)
    print("\nThe directory " + folder_name + " has been created at this place: \n" + basepath + "\n\n")
    for i in range(1,n + 1):
        interval_name=myinterval.format(i)
            
        # Fetching Directory constant
        source_constant=calcs_undeformed + 'constant'
        destination_constant=basepath + folder_name + "/" + sweep_name + "/" + interval_name
        shutil.copytree(source_constant,os.path.join(destination_constant,os.path.basename(source_constant)))
        
        # Fetching Directory system
        source_system=calcs_undeformed + 'system'
        destination_system=basepath + folder_name + "/" + sweep_name + "/" + interval_name
        shutil.copytree(source_system,os.path.join(destination_system,os.path.basename(source_system)))
        
        # Fetching Directory with starting time
        startTime=decimal_analysis(theta + deltaT*(i-1))
        endTime=decimal_analysis(theta + deltaT*i)
        source_startTime=calcs_undeformed + str(startTime)
        destination_startTime=basepath + folder_name + "/" + sweep_name + "/" + interval_name
        shutil.copytree(source_startTime,os.path.join(destination_startTime,os.path.basename(source_startTime)))
        
        # Deleting wrong polyMesh/points in the starting time directory
        polyMesh_path=basepath + folder_name + "/" + sweep_name + "/" + interval_name + '/constant/polyMesh/points'
        print('The file ' + folder_name + '/' + sweep_name + '/' + interval_name + '/constant/polyMesh/points has been succefully removed.')
        os.remove(polyMesh_path)
        file=destination_startTime + '/' + str(startTime) + '/polyMesh/points'
        if os.path.exists(file):
            shutil.rmtree(destination_startTime + '/' + str(startTime) + '/polyMesh')
        
        #Fetching the right polyMesh
        source_newPolyMesh=ref_cases_mod_def + "constant/polyMesh/points"
        destination_newPolyMesh=basepath + folder_name + "/" + sweep_name + "/" + interval_name + '/constant/polyMesh'
        shutil.copy(source_newPolyMesh,destination_newPolyMesh)

        #Modify the controlDict file to ajust startTime and endTime        
        controlDict_path=folder_name + '/' + sweep_name + '/' + interval_name + '/system/controlDict'
        for line in fileinput.input(controlDict_path, inplace=True):
            if line.startswith('startTime'):
                line = 'startTime       {};\n'.format(startTime)
            elif line.startswith('endTime'):
                line = 'endTime         {};\n'.format(endTime)
            print(line)
    print("Sweep 1 initialization is done.")
    os.chdir(basepath + folder_name)
    with open("pressureDropvalues.txt","w") as mytime:
        mytime.write("\n\n=============================================================================\n\n" + "                         LOGFILE " + folder_name + "\n\n=============================================================================\n\n")
    mytime.close()
    return(folder_name)