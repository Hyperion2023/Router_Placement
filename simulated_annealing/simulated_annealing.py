import math
import random as rm
import utils
import numpy as np

__all__ = ["simulated_annealing"]


def random_variation(current_state : np.array, building_matrix : np.array):
    
    rows = current_state.shape[0]
    columns = current_state.shape[1]

    random = rm.randrange(1, 3) # TODO add the router movement

    if random == 1: # add one router
        target_coords = np.nonzero(building_matrix == ".") #returns a touple of arrays for the row and column coordinates
        if len(target_coords[0]) == 0:
            return current_state
        random_coord = rm.randrange(0, len(target_coords[0]))
        rand_row = target_coords[0][random_coord]
        rand_column = target_coords[1][random_coord]

        new_state = np.copy(current_state)
        new_state[rand_row][rand_column] = 1
        return new_state

    elif random == 2: # remove one router
        router_coords = current_state.nonzero()
        if len(router_coords[0]) == 0:
            return current_state
        
        random_coord = rm.randrange(0, len(router_coords[0]))
        rand_row = router_coords[0][random_coord]
        rand_column = router_coords[1][random_coord]

        new_state = np.copy(current_state)
        new_state[rand_row][rand_column] = 0
        return new_state

    #elif random == 3: # move one router


def simulated_annealing(
        initial_state : np.array, 
        number_iterations : int, 
        initial_temperature : int, 
        building_matrix : np.array, 
        fitness_function,
        sigma
    ) -> np.array:

    """" pseudocode of simulated annealing

    initial_state: rappresentation of the current state of the solution
        initial_state.fitness(): returns an evaluation of the state, we want to maximize it
        initial_state.get_random_variation(): a random variation of the current state, for example the router placement or number 
    
    number_iterations : the max number of iterations
    initial_temperature: the starting temperature

    returns: the final configuration
    """

    rm.seed(a=None, version=2)

    curret_temperature = initial_temperature
    current_state = initial_state

    for i in range(number_iterations): # the termination condition could be also related to the temperature

        new_state = random_variation(current_state = current_state, building_matrix=building_matrix)

        delta_fitness = fitness_function(new_state) - fitness_function(current_state)
       
        if delta_fitness >= 0: # new state is better
            current_state = new_state # set the new state
        
        elif rm.uniform(0,1) < np.exp(delta_fitness / curret_temperature): # delta_fitness < 0, so this is equivalent to 1 / e^ sigma * (|delta_fitness|/current_temperature)
            print("Iteration", i, "delta fitness", delta_fitness, "prob of accept bad fitness:", np.exp(sigma * delta_fitness / curret_temperature))
            current_state = new_state
        
        else:
            pass


        curret_temperature -= 1 # also more compex decreasing 
        


    return current_state