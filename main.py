
import numpy as np
from copy import copy
from Data import Data
from search import *
from utils import *




def main():

    data = Data.Data("Dataset/tiny_test.in")

    print(data.matrix.shape, data.router_range)
    print(data.backbone_cost, data.router_cost, data.budget)
    print(data.initial_backbone)
    print(data.target_area)
    # print(data.matrix)
    
    data.random_init()
    router_mask = data.initial_routers_placement()
    print("STARTING CONFIGURATION:")
    print_routers(data.matrix, data.router_list)

    
    random_init = 10
    max_step = 50
    max_score = 0
    best_routers_settings = None
    i = 0
    for j in range(random_init):
        print("-------------------RANDOM INIT, iteration: {}------------------".format(j))
        while i < 50:
            improved = optimization_step(router_mask, data.matrix, data.router_list, data.router_range, Policy.BEST, verbose=True)
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































if __name__  == "__main__":
    main()