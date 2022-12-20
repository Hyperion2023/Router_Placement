import random as rm
import utils
import numpy as np
import Data

__all__ = ["simulated_annealing"]


def state_neighbor(current_state : np.array, building_matrix : np.array, move_type : str, verbose : bool):
    
    supported_moves = ["add", "remove"]

    new_state = new_state = np.copy(current_state)

    if (move_type not in supported_moves):
        move_type = rm.choice(supported_moves)

    if verbose:
        print("\t\tnew state type: ", move_type)

    if move_type == "add": # add one router
        target_coords = np.nonzero(building_matrix == ".") #returns a touple of arrays for the row and column coordinates
        if len(target_coords[0]) == 0:
            return current_state
        random_coord = rm.randrange(0, len(target_coords[0]))
        rand_row = target_coords[0][random_coord]
        rand_column = target_coords[1][random_coord]
        new_state[rand_row][rand_column] = 1

    elif move_type == "remove": # remove one router
        router_coords = current_state.nonzero()
        if len(router_coords[0]) == 0:
            return current_state
        random_coord = rm.randrange(0, len(router_coords[0]))
        rand_row = router_coords[0][random_coord]
        rand_column = router_coords[1][random_coord]
        new_state[rand_row][rand_column] = 0

    else:
        pass
        
    return new_state


def simulated_annealing(
        data: Data,
        initial_state : np.array, 
        number_iterations : int, 
        initial_temperature : int, 
        building_matrix : np.array, 
        fitness_function,
        sigma,
        verbose=True
    ) -> np.array:

    """" simulated annealing

    initial_state: rappresentation of the current state of the solution, is a 2D np.array with the same shape of building_matrix, is 1 where there is a router, 0 elsewhere
    number_iterations : the max number of iterations
    initial_temperature: the starting temperature
    building matrix: the matrix of the buildings
    fitness function: a function that takes as input a matrix representing the state
    sigma: a parameter for the temperature decay
    
    returns: the final configuration as a np.array
    """

    rm.seed(a=None, version=2)

    curret_temperature = initial_temperature
    current_state = initial_state
    currennt_fitness , out_budget = fitness_function(current_state)

    for i in range(number_iterations): # the termination condition could be also related to the temperature
        if verbose:
            print(f"ITERAZIONE {i}")
        
        new_state = state_neighbor(
            current_state = current_state, 
            building_matrix=building_matrix,
            move_type="random",
            verbose=verbose
            )

        new_fitness, out_budget = fitness_function(new_state)
        if out_budget:
            print("out of budget")
        delta_fitness = new_fitness - currennt_fitness
       
        if delta_fitness >= 0: # new state is better
            current_state = new_state # set the new state
            currennt_fitness = new_fitness
        
        elif rm.uniform(0,1) < np.exp(delta_fitness / curret_temperature): # delta_fitness < 0, so this is equivalent to 1 / e^ sigma * (|delta_fitness|/current_temperature)
            if verbose:
                print("\t\taccepted negative change")
            current_state = new_state
            currennt_fitness = new_fitness
        
        else:
            pass
        
        if verbose:
            print("\t\tdelta fitness", delta_fitness, ", the probability of accept negative changes was:", np.exp(sigma * delta_fitness / curret_temperature))
            

        curret_temperature -= 1 # also more compex decreasing 
        


    return current_state