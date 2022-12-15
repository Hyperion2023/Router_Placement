import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Data
from copy import copy

from search import Policy
from search import Search
from utils import get_number_covered_cells 
from utils import print_routers

def hill_climb(data:Data, random_init=10, max_step=10, policy="best"):
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
        print("-------------------RANDOM INIT, iteration: {}------------------".format(j))
        data.random_init(num_routers=1)
        router_mask = data.initial_routers_placement()
        print("STARTING CONFIGURATION:")
        print_routers(data.matrix, data.router_list)
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
        
        if(policy == "best"):
            policy = Policy.BEST
        else:
            policy = Policy.GREEDY
        
        while i < max_step:
            improved = search.optimization_step(policy, verbose=1)
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
            max_score = temp_score
            best_routers_settings = copy(map_mask)
            break
        if temp_score > max_score:
            # todo
            # here we should take in consideration also the cost
            max_score = temp_score
            best_routers_settings = copy(map_mask)
        print("ITERATION: {} \n FINAL SCORE: {}".format(j, temp_score))
            
    # print("FINAL CONFIGURATION: ")
    return best_routers_settings
    # print_routers(data.matrix, best_routers_settings)