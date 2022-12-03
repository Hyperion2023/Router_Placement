import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Data
from copy import copy

from search import Policy
from search import Search
from utils import get_number_covered_cells 
from utils import print_routers

def hill_climb(data:Data, random_init=10, max_step=50):    
    for j in range(random_init):
        print("-------------------RANDOM INIT, iteration: {}------------------".format(j))
        data.random_init()
        router_mask = data.initial_routers_placement()
        print("STARTING CONFIGURATION:")
        print_routers(data.matrix, data.router_list)
        print("STARTING SCORE: ",get_number_covered_cells(router_mask, data.matrix, data.router_range))
        max_score = 0
        best_routers_settings = None
        i = 0
        
        map_mask = data.initial_routers_placement()
        building_matrix = data.matrix
        router_list = data.router_list
        router_range = data.router_range
        
        search = Search(map_mask, building_matrix, router_list, router_range)
        
        while i < 50:
            improved = search.optimization_step(Policy.BEST, verbose=True)
            if improved == 0:
                i += 1
        temp_score = get_number_covered_cells(router_mask, data.matrix, data.router_range)
        if temp_score == data.target_area :
            max_score = temp_score
            best_routers_settings = copy(data.router_list)
            break
        if temp_score > max_score:
            # todo
            # here we should take in consideration also the cost
            max_score = temp_score
            best_routers_settings = copy(data.router_list)
        print("ITERATION: {} \n FINAL SCORE: {}".format(j, temp_score))
            
    # print("FINAL CONFIGURATION: ")
    return best_routers_settings
    # print_routers(data.matrix, best_routers_settings)