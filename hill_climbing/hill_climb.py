import copy
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Data


from search import Policy
from search import Search
from utils import get_number_covered_cells 
from utils import print_routers


def hill_climb(data:Data):
    data.random_init()
    router_mask = data.initial_routers_placement()
    print("STARTING CONFIGURATION:")
    print_routers(data.matrix, data.router_list)

    
    random_init = 10
    max_step = 50
    max_score = 0
    best_routers_settings = None
    i = 0
    
    map_mask = data.initial_router_placement()
    building_matrix = data.matrix
    router_list = data.router_list
    router_range = data.router_range
    
    search = search.Search(map_mask, building_matrix, router_list, router_range)
    
    for j in range(random_init):
        print("-------------------RANDOM INIT, iteration: {}------------------".format(j))
        while i < 50:
            improved = search.optimization_step(router_mask, data.matrix, data.router_list, data.router_range, Policy.BEST, verbose=True)
            if improved == 0:
                i += 1
        temp_score = get_covered_cells(router_mask, data.matrix, data.router_range)
        if temp_score == data.target_area :
            max_score = temp_score
            best_routers_settings = copy(data.router_list)
            break
        if temp_score > max_score:
            # todo
            # here we should take in consideration also the cost
            max_score = temp_score
            best_routers_settings = copy(data.router_list)
        data.random_init()
        router_mask = data.initial_routers_placement()
            
    print("FINAL CONFIGURATION: ")
    print_routers(data.matrix, best_routers_settings)