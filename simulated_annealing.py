import math
import random

def simulated_annealing_skeleton(initial_state, number_iterations, initial_temperature):
    """" pseudocode of simulated annealing

    initial_state: rappresentation of the current state of the solution
        initial_state.fitness(): returns an evaluation of the state, we want to maximize it
        initial_state.get_random_variation(): a random variation of the current state, for example the router placement or number 
    
    number_iterations : the max number of iterations
    initial_temperature: the starting temperature
    """

    curret_temperature = initial_temperature
    current_state = initial_state

    for i in range(number_iterations): # the termination condition could be also related to the temperature

        new_state = current_state.get_random_variation()

        delta_fitness = new_state.fitness() - current_state.fitness()
       
        if delta_fitness > 0: # new state is better
            current_state = new_state # set the new state
        
        elif random.uniform(0,1) < math.exp(delta_fitness / curret_temperature): # delta_fitness < 0, so this is equivalent to 1 / e^(|delta_fitness|/current_temperature)
            current_state = new_state
        
        else:
            pass

        curret_temperature -= 1 # also more compex decreasing 