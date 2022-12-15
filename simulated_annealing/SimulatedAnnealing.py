import math
import random as rm
import utils
import numpy as np
import Data

__all__ = ["SimulatedAnnealing"]


class Cell:
    def __init__(self, position, coverage_level = 0) -> None:
        self.position = position
        self.coverage_level = coverage_level
        pass


class FastPriorityDict:
    def __init__(self) -> None:
        self.inner_dict = {}
        self.inner_list = []
        self.approximate_higer_index = 0
        self.approximate_lower_index = len(self.inner_list)
        self.edits_since_ordered = 0
        pass

    def add_element(self, position : tuple(int, int)):
        new_cell = Cell(position)
        self.inner_dict[position] = new_cell
        self.inner_list.append(new_cell)
    
    def edit_element(self, position : tuple(int, int), delta):
        cell = self.inner_dict[position]
        cell.coverage_level += delta
    
    def order(self):
        self.inner_list.sort(key=lambda x : x.coverage_level, reverse=True)
        self.approximate_higer_index = 0
        self.approximate_lower_index = len(self.inner_list)
    
    def get_higer(self):
        cell = self.inner_list[self.approximate_higer_index]
        self.approximate_higer_index +=1
        return cell.position
    
    def get_lower(self):
        cell = self.inner_list[self.approximate_lower_index]
        self.approximate_higer_index -=1
        return cell.position
    
    


class SimulatedAnnealing:

    def __init__(self, 
        data, 
        initial_state,
        number_iterations : int, 
        initial_temperature : int,  
        fitness_function,
        sigma,
        verbose=True
    ) -> None:

        self.data = data
        self.initial_state = initial_state
        self.number_iterations = number_iterations
        self.initial_temperature = initial_temperature
        self.fitness_function = fitness_function
        self.sigma = sigma
        self.verbose = verbose
    


        


    def state_neighbor(
        current_state : np.array, 
        building_matrix : np.array, 
        move_type : str, 
        router_range : int,
        verbose : bool):
        
        supported_moves = ["smart_add", "remove"] # TODO add the router movement

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

        elif move_type == "smart_add":
            uncovered = utils.get_uncovered(current_state, building_matrix, router_range)

            lets_cover = rm.choice(uncovered)
            new_state[lets_cover[0]][lets_cover[1]] = 1


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
                router_range= data.router_range,
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