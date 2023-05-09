import numpy as np
import sys
from Parameters import *
sys.path.append('/home/hcleroy/PostDoc/aging_condensates/Simulation/Aging_Condensate/Analysis_cluster/Analysis_object')
import Simulate as Sim
import os

class Simulation(Sim.ParallelSimulation):
    def __init__(self,gillespie_param,simulation_param,cpu_param):
        super().__init__(gillespie_param,simulation_param,cpu_param)
        self.R = dict()
        self.move = dict()
        self.time=0
        self.Fmes = 0
        self.time_of_measurement=0
        if os.path.exists('Res/'+self.Simulation_Name):
            print("the output file already exists, do you want to override it ? This will delete the data contained (Y/y/yes or N/n/no)")
            answer = input()
            Positive = {"y","Y","Yes","yes","YES"}
            if answer in Positive:
                os.system('rm -rf  Res/'+self.Simulation_Name)
            else:
                print("cancel the execution : no file to write the results")
                sys.exit()
        os.system('mkdir Res/'+self.Simulation_Name)
    def extract_parameter(self, gillespie, moves, time,step,name):
        F_to_return = self.Fmes/self.time_of_measurement
        self.Fmes = 0.
        self.time_of_measurement = 0.
        #return {"Ell_"+name+"_"+str(step):gillespie.get_ell_coordinates(),"F_"+name+"_"+str(step):F_to_return,"R_"+name+"_"+str(step):gillespie.get_R(),"time_"+name+"_"+str(step):np.sum(time),"move_"+name+"_"+str(step):moves}
        return {"F_"+name+"_"+str(step):F_to_return,
                    "time_"+name+"_"+str(step):np.sum(time),
                    "R_"+name+"_"+str(step):gillespie.get_R()}
    def state_b4(self,gillespie,time):
        """ this function save what has to be saves before an evolution step"""
        self.nrg_b4 = gillespie.get_F()
    def state_after(self,gillespie,time):
        """ this function save what has to be saved after an evolution step"""
        self.Fmes += self.nrg_b4*(time[-1])
        self.time_of_measurement +=time[-1] # total time of the measurement.
    def unpack_res(self, res):
        return res


sim = Simulation(gillespie_params,simulation_param,cpu_param)

ResList = sim.Parallel_Run()
Res= {key: value for dictionary in ResList for key, value in dictionary.items()}

for name in names:
    FreeNRG,moves,time = [],[],[]
    for step in steps:
        time.append(Res["time_"+name+"_"+step])
        #moves.extend(Res["move_"+name+"_"+step])
        FreeNRG.append(Res["F_"+name+"_"+step])
        np.save("Res/"+simulation_param['Simulation_Name']+"/R_"+name+"_"+step+".npy",Res["R_"+name+"_"+step],allow_pickle=True)
        #np.save("Res/"+simulation_param['Simulation_Name']+"/Ell_"+name+"_"+step+".npy",Res["Ell_"+name+"_"+step],allow_pickle=True)
    #np.save("Res/"+simulation_param['Simulation_Name']+"/moves_"+name+".npy",moves)
    np.save("Res/"+simulation_param['Simulation_Name']+"/time_"+name+".npy",time)
    np.save("Res/"+simulation_param['Simulation_Name']+"/FreeNRG_"+name+".npy",FreeNRG)
# copy the parameter file to keep track of what happened
os.system('cp /home/hcleroy/PostDoc/aging_condensates/Simulation/Effect_of_Binding_Energy/Parameters.py Res/'+simulation_param['Simulation_Name']+'/')
    