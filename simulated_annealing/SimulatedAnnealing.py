import random as rm
import utils
import numpy as np
import Data
from .FastPriorityDict import FastPriorityDict



class SimulatedAnnealing:

    def __init__(self, 
        data : Data, 
        initial_state,
        number_iterations : int, 
        initial_temperature : int,  
        fitness_function,
        sigma,
        verbose=True
    ) -> None:

        self.data = data
        self.state = initial_state
        self.number_iterations = number_iterations
        self.initial_temperature = initial_temperature
        self.fitness_function = fitness_function
        self.sigma = sigma
        self.verbose = verbose

        self.pri_dic = self.init_pri_dic()
  

    def init_pri_dic(self) -> FastPriorityDict:
        if self.verbose:
            print("Initializing priority dict")
        
        # we want to add each cell of the grid and then update the coverage level
        pri_dict = FastPriorityDict()

        #add all the target coords to the priority dict
        target_coords = np.nonzero(self.data.building_matrix == ".")
        for  (i, j) in zip(target_coords[0], target_coords[1]):
            pri_dict.add_element( (i, j))
        
        #iterate the router and update the nearby cells
        router_coords = self.state.nonzero()
        for  (i, j) in zip(router_coords[0], router_coords[1]): # for each router
           
            # filter points covered by walls and void cells
            points_covered_by_router = utils.filter_non_target_points(
                building_matrix = self.data.building_matrix,
                router_coords = (i, j),
                points = utils.get_points_around_router(
                    matrix = self.data.building_matrix,
                    router_coords = (i, j),
                    router_radius= self.data.router_range
                )
            )

            for (x, y) in points_covered_by_router: #for each point (cell) covered by the router
                pri_dict.edit_element((x, y), 1)

        pri_dict.order()
        
        if self.verbose:
            print("Priority dict initialized")

        return pri_dict


    def state_neighbor(
        self,
        move_type : str
        ) -> np.array:

        supported_moves = ["add", "remove"] 

        new_state = new_state = np.copy(self.current_state)

        if (move_type not in supported_moves):
            move_type = rm.choice(supported_moves)

        if self.verbose:
            print("\t\tnew state type: ", move_type)

        if move_type == "add": # add one router
            target = self.pri_dic.get_lower() # the cell with less coverage
            #TODO how can i know that it is not a router?

        elif move_type == "remove": # remove one router
            router_coords = self.current_state.nonzero()
            if len(router_coords[0]) == 0:
                return self.current_state
            random_coord = rm.randrange(0, len(router_coords[0]))
            rand_row = router_coords[0][random_coord]
            rand_column = router_coords[1][random_coord]
            new_state[rand_row][rand_column] = 0

        elif move_type == "smart_add":
            uncovered = utils.get_uncovered(self.current_state, self.building_matrix, self.router_range)

            lets_cover = rm.choice(uncovered)
            new_state[lets_cover[0]][lets_cover[1]] = 1

        else:
            pass
            
        return new_state

    def run(
        self, 
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

        curret_temperature = self.initial_temperature
        current_state = self.initial_state
        currennt_fitness , out_budget = self.fitness_function(current_state)

        for i in range(self.number_iterations): # the termination condition could be also related to the temperature
            if self.verbose:
                print(f"ITERAZIONE {i}")
            
            new_state = self.state_neighbor(
                current_state = current_state, 
                building_matrix=self.building_matrix,
                move_type="random",
                router_range= self.data.router_range,
                verbose=self.verbose
                )

            new_fitness, out_budget = self.fitness_function(new_state)
            if out_budget:
                print("out of budget")
            delta_fitness = new_fitness - currennt_fitness
        
            if delta_fitness >= 0: # new state is better
                current_state = new_state # set the new state
                currennt_fitness = new_fitness
            
            elif rm.uniform(0,1) < np.exp(delta_fitness / curret_temperature): # delta_fitness < 0, so this is equivalent to 1 / e^ sigma * (|delta_fitness|/current_temperature)
                if self.verbose:
                    print("\t\taccepted negative change")
                current_state = new_state
                currennt_fitness = new_fitness
            
            else:
                pass
            
            if self.verbose:
                print("\t\tdelta fitness", delta_fitness, ", the probability of accept negative changes was:", np.exp(self.sigma * delta_fitness / curret_temperature))
                

            curret_temperature -= 1 # also more compex decreasing 
            


        return current_state