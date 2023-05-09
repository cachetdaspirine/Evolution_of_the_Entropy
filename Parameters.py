import numpy as np
import math
import  sys

def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

if sys.argv.__len__()<2:
    print("please give a simulation name when executing this script")
    sys.exit()

Nlinker = 2
ell_tot = 10**3
kdiff = Nlinker/ (4/3 * np.pi * (ell_tot /2)**1.5)
Energy = [-10. for _ in range(10)]#np.linspace(-50,-10,10)
seeds = [np.random.randint(0,1000000) for _ in range(10)]

step_tot = 10**4
dump_step = 10**3
measurement_step = 10**2

gillespie_params =  {'ell_tot':ell_tot,'rho0':0.,'BindingEnergy':Energy,'kdiff':kdiff,'seed':seeds,'sliding':False,'Nlinker':Nlinker,'old_gillespie':None,'dimension':1}
simulation_param = {'step_tot' : step_tot,'min_dump_step':0, 'dump_step':dump_step,'label_key':'seed','Simulation_Name':sys.argv[1],'measurement_steps':measurement_step}
cpu_param = {'Nnodes':10}

names = [str(truncate(e,5)) for e in seeds]
steps = [str(step*dump_step) for step in range(simulation_param['min_dump_step']+1,step_tot//dump_step+1)]

