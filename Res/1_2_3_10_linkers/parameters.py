# gillespie parameter
Nlinker = 2
ell_tot = 10**3
V = 4/3*np.pi*(ell_tot/6)**1.5
kdiff = 1/(V) # for 1D
Energy = -15
Nprocess = 1000
args = [[ell_tot,Energy,kdiff,np.random.randint(1000000),Nlinker,1] for _ in range(Nprocess)]

# Simulation parameters
step_tot = 10000
compute_steps = 10
