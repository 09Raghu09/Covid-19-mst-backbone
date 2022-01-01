from covid_abs.graphics import *


def No_Restriction() -> Simulation:
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
        population_size=2348,
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
    return sim


def Lockdown() -> Simulation:
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
            Status.Susceptible: .5,
            Status.Recovered_Immune: .5,
            Status.Infected: .5
        })

    return sim


def Moderate_Reduction_in_Social_Contact() -> Simulation:
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
        })
    # when more than 5% infected implement lockdown
    sim.append_trigger_simulation(lambda a: a.get_statistics()['Infected'] >= .05,
                                  'amplitudes', lambda a: {
        Status.Susceptible: 1.5,
        Status.Recovered_Immune: 1.5,
        Status.Infected: 1.5
    })

    # when 95% infected
    sim.append_trigger_simulation(lambda a: a.get_statistics()['Infected'] <= .05,
                                  'amplitudes', lambda a: {
        Status.Susceptible: 5,
        Status.Recovered_Immune: 5,
        Status.Infected: 5
    })

    return sim


def Moderate_Reduction_in_Social_Contact_and_wearing_Masks() -> Simulation:
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
        # mask reduce by 16%
        contagion_rate=0.9*.16,
        # Mobility ranges for agents, by Status
        amplitudes={
            Status.Susceptible: 5,
            Status.Recovered_Immune: 5,
            Status.Infected: 5
        })
    # when more than 10% infected implement lockdown
    sim.append_trigger_simulation(lambda a: a.get_statistics()['Infected'] >= .1,
                                  'amplitudes', lambda a: {
        Status.Susceptible: 1.5,
        Status.Recovered_Immune: 1.5,
        Status.Infected: 1.5
    })

    # when 95% infected
    sim.append_trigger_simulation(lambda a: a.get_statistics()['Infected'] <= .05,
                                  'amplitudes', lambda a: {
        Status.Susceptible: 5,
        Status.Recovered_Immune: 5,
        Status.Infected: 5
    })

    return sim


SCENARIOS = [No_Restriction, Lockdown, Moderate_Reduction_in_Social_Contact,
             Moderate_Reduction_in_Social_Contact_and_wearing_Masks]

for scen_func in SCENARIOS:
    file_name = f'{scen_func.__name__}' + '_supermarket_only.gif'
    titlename = f'{scen_func.__name__}'.replace(
        '_', ' ') + ' with central locations'
    anim = execute_simulation(scen_func(), iterations=80, third_plot='R',
                              fig_tit=f'{scen_func.__name__}'.replace('_', ' '))
    print(f'{scen_func.__name__}')
    rc('animation', html='html5')
    save_gif(anim, file_name)
