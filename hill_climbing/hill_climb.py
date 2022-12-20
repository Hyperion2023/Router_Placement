import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from classes.Data import Data
from copy import copy
import numpy as np
from hill_climbing.search import Policy
from hill_climbing.search import Search
from utils import get_number_covered_cells 
from utils import print_routers

def hill_climb(
        data: Data,
        random_init=10,
        max_step=10,
        policy="best"
):
    """the hill climbing algorithm for router placement

    Args:
        data (Data): data for the router placement
        random_init (int, optional): numebr of random initialization of the hill climbing. Defaults to 10.
        max_step (int, optional): max non improvement step. Defaults to 10.
        policy (str, optional): the policy for the improving. Defaults to "best".

    Returns:
        list: a list of routers coordinates
    """
    for j in range(random_init):
        print(f"-------------------RANDOM INIT, iteration: {j}------------------")
        data.random_init(num_routers=1)
        router_mask = data.initial_routers_placement()
        print("STARTING CONFIGURATION:")
        #print_routers(data.matrix, data.router_list)
        starting_score = get_number_covered_cells(router_mask, data.matrix, data.router_range)
        print("STARTING SCORE: ", starting_score)
        max_score = 0
        best_routers_settings = None
        i = 0
        
        map_mask = data.initial_routers_placement()
        building_matrix = data.matrix
        router_list = data.router_list
        router_range = data.router_range
        target_coords = data.target_coords
        
        search = Search(map_mask=map_mask, 
                        building_matrix=building_matrix,
                        router_list=router_list, 
                        target_coords=target_coords, 
                        range=router_range)
        
        if policy == "best":
            policy = Policy.BEST
        else:
            policy = Policy.GREEDY
        
        while i < max_step:
            improved = search.optimization_step(policy, verbose=True)
            print("\tnew score: {}".format(starting_score+improved))
            starting_score += improved
            if improved == 0:
                i += 1
            else:
                i = 0
            if starting_score ==  len(data.target_coords):
                break
        temp_score = get_number_covered_cells(router_mask, data.matrix, data.router_range)
        if temp_score == data.target_area :
            best_routers_settings = copy(data.router_list)
            break
        if temp_score > max_score:
            best_routers_settings = copy(data.router_list)
        print(f"ITERATION: {j} \n FINAL SCORE: {temp_score}")

    matrix = np.zeros(shape=data.building_matrix.shape)
    for elem in best_routers_settings:
        matrix[elem[0]][elem[1]] = 1

    #return best_routers_settings
    return matrix