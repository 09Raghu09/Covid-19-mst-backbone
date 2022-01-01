from covid_abs.graphics import *
from covid_abs.abs import *
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from matplotlib import animation, rc
from IPython.display import HTML

warnings.simplefilter('ignore')

##### Scenario 1: Hamburg with 3 Supermarkets + 1 School #####
sim = Simulation(
    # Percentage of infected in initial population
    initial_infected_perc=0.02,
    # Percentage of immune in initial population
    initial_immune_perc=0.01,
    # Length of simulation environment
    length=1000,
    # Height of simulation environment
    height=1000,
    # Size of population
    population_size=2438,
    # Minimal distance between agents for contagion
    contagion_distance=5.,
    # Maximum percentage of population which Healthcare System can handle simutaneously
    critical_limit=0.05,
    # Mobility ranges for agents, by Status
    amplitudes={
        Status.Susceptible: 5,
        Status.Recovered_Immune: 5,
        Status.Infected: 5
    }
)
anim = execute_simulation(sim, iterations=10)
rc('animation', html='html5')
anim
save_gif(anim, 'hamburg_3supermarkets_1school_no_restrictions.gif')


##### Scenario 2: Hamburg with 3 Supermarkets + 1 School and LOCKDOWN #####
sim = Simulation(
    # Percentage of infected in initial population
    initial_infected_perc=0.02,
    # Percentage of immune in initial population
    initial_immune_perc=0.01,
    # Length of simulation environment
    length=1000,
    # Height of simulation environment
    height=1000,
    # Size of population
    population_size=2438,
    # Minimal distance between agents for contagion
    contagion_distance=5.,
    # Maximum percentage of population which Healthcare System can handle simutaneously
    critical_limit=0.05,
    # Mobility ranges for agents, by Status
    amplitudes={
        Status.Susceptible: 0.5,
        Status.Recovered_Immune: 0.5,
        Status.Infected: 0.5,
    }
)

# anim = execute_simulation(sim, iterations=90)
# rc('animation', html='html5')
# anim
# save_gif(anim, 'hamburg_3supermarkets_1school_lockdown.gif')
