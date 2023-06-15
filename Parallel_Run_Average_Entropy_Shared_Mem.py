import numpy as np
import multiprocessing as mp
from multiprocessing import shared_memory
import sys
import queue
import copy
sys.path.append('/home/hcleroy/PostDoc/aging_condensates/Simulation/Gillespie/Gillespie_backend/')
sys.path.append('/home/hugo/PostDoc/aging_condensates/Gillespie/Gillespie_backend/')
sys.path.append('/home/hcleroy/aging_condensate/Gillespie/Gillespie_backend')
import Gillespie_backend as gil
sys.path.append('/home/hcleroy/PostDoc/aging_condensates/Simulation/Gillespie/Analysis/')
sys.path.append('/home/hugo/PostDoc/aging_condensates/Gillespie/Analysis/')
sys.path.append('/home/hcleroy/aging_condensate/Gillespie/Analysis')
from ToolBox import *
def weighted_average_energy(Gil, step_tot, compute_steps):
    """
    Compute the evolution of a Gillespie object over `step_tot` steps, and 
    compute the weighted average of the energy every `compute_steps`.
    
    Parameters:
    Gil (Gillespie): The Gillespie object to evolve
    step_tot (int): The total number of steps to evolve the object
    compute_steps (int): The number of steps for computing the weighted average

    Returns:
    array: a 2D numpy array of shape (step_tot//compute_steps,2) where the first column is the time drawn, and the second 
        is the energy averaged over the compute_steps steps.
    float: The percentage of moves where move == 1
    """
    current_time = 0
    total_weight = 0
    prev_energy = Gil.get_F()
    bound_linkers = 0
    results = np.zeros((step_tot//compute_steps,2),dtype=float)
    move_1_count = 0
    weighted_energy = 0

    for step in range(1, step_tot + 1):
        move, time = Gil.evolve()
        move = move[0]
        time=time[0]
        current_time += time
        if move == 1:
            move_1_count += 1
        #weighted_entropy += (prev_entropy-Gil.ell_tot*np.log(np.pi*4)) * time
        #weighted_energy += ((prev_energy-(Gil.binding_energy * Gil.Nlinker- Gil.ell_tot*np.log(np.pi*4)))/
        #                                        (-MinEnt(Gil.Nlinker,Gil.ell_tot)+Gil.ell_tot*np.log(4*np.pi))) * time
        weighted_energy+=prev_energy*time
        total_weight += time
        prev_energy = Gil.get_F()
        if step % compute_steps == 0:
            weighted_energy = weighted_energy/total_weight
            results[(step-1)//compute_steps] = [current_time, weighted_energy]
            weighted_energy =0.
            total_weight = 0.

    return results, (move_1_count / step_tot) * 100
def run_simulation_with_shared_results(q, shared_mem_array, shape,shared_count, step_tot, compute_steps,lock):
    """
    Runs the weighted_average_entropy function with the provided seed and stores the results
    in the shared_results and shared_move_1_percentage_count variables.

    Parameters:
    seed (int): The seed for the Gillespie object
    shared_results (List): A shared list to store the results
    shared_move_1_percentage_count (Value): A shared variable to store the move_1_percentage count
    step_tot (int): The total number of steps to evolve the object
    compute_steps (int): The number of steps for computing the weighted average
    """
    while True:
        try:
            # the block = False means that the process wont wait for a argument to com in the queue
            args =q.get(block=False) # extract an element from the queue to run the simulation
        except queue.Empty: # once the queue is empty break the loop
            break

        Nlinker = args[4]
        ell_tot = args[0]
        kdiff = args[2]
        Energy = args[1]
        seed = args[3]
        dimension = args[5]
        # create the gillespie object
        Gil = gil.Gillespie(ell_tot=ell_tot, rho0=0., BindingEnergy=Energy, kdiff=kdiff,
                            seed=seed, sliding=False, Nlinker=Nlinker, old_gillespie=None, dimension=dimension)
        # make the simulation and store the resutls
        results, move_1_percentage = weighted_average_energy(Gil, step_tot, compute_steps)

        # Access the shared memory and wrap it as a numpy array
        shared_mem = shared_memory.SharedMemory(name=shared_mem_array.name)
        shared_results = np.ndarray(shape, dtype=np.float64, buffer=shared_mem.buf)

        with lock:
            shared_results += results
            shared_count.value += move_1_percentage

def average_simulations( args, step_tot, compute_steps):
    """
    Averages the simulation results for the specified number of simulations using the provided seeds.
    Each simulation is run in parallel using multiprocessing.

    Parameters:
    args (2D array): a list of array of arguments for each running gillespie. The order is : ell_tot, Energy,kdiff,seed,Nlinker,dimension
    step_tot (int): The total number of steps to evolve the object
    compute_steps (int): The number of steps for computing the weighted average
    num_simulations (int): The number of simulations to run
    
    Returns:
    np.ndarray: The averaged results of all simulations
    float: The average move_1_percentage across all simulations
    """
    # initialize a shared memory
    shape = (step_tot//compute_steps,2)
    shared_mem_array = shared_memory.SharedMemory(create=True, size=shape[0]*shape[1] * 8)  # Double precision float is 8 bytes
    shared_array = np.ndarray(shape, dtype=np.float64, buffer=shared_mem_array.buf)
    shared_array[:] = 0  # Initialize the shared array with zeros
    shared_count = mp.Value('d',0.0) # initialize the count

    # initialize a lock
    lock = mp.Lock()
    
    # transfer all the args into a queue
    # this is use to execute the code with 12 cpu, irrespective of the size of args
    q = mp.Queue()
    for arg in args:
        q.put(arg)


    processes = []
    for _ in range(mp.cpu_count()):
        p = mp.Process(target=run_simulation_with_shared_results, args=(q, shared_mem_array, shape,shared_count, step_tot, compute_steps, lock))
        p.daemon = True
        p.start()
        processes.append(p)
    for p in processes:
        p.join()

    shared_array /= args.__len__()
    shared_count.value /= args.__len__()

    print(shared_count.value)


    copyarray = copy.copy(shared_array)
    shared_mem_array.unlink()
    shared_mem_array.close()

    return copyarray
    