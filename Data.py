

import numpy as np
import random

class Data:
    """" A class used to represent the data of the problem

    Attributes:
    
    router_range
    backbone_cost
    router_cost
    budget
    initial_backbone: touple containing the initial access point for the backbone
    matrix: a 2D numpy.array of char values 
    target_area: the number of "." in the matrix


    """

    
    
    def __init__(self, file_path : str):
        
        with open(file_path, "r") as f:
            lines = f.readlines()
            first_line = lines[0].split(" ")
            self.height = int(first_line[0])
            self.width = int(first_line[1])
            self.router_range = int(first_line[2])
            self.backbone_cost = int((lines[1].split(" "))[0])
            self.router_cost = int((lines[1].split(" "))[1])
            self.budget = int((lines[1].split(" "))[2])
            self.initial_backbone = (int((lines[2].split(" "))[0]), int((lines[2].split(" "))[1]))

            lines = lines[3:]

            python_matrix = []
            for line in lines:
                python_matrix.append([str(c) for c in line][:len(line)-1])
            
            self.matrix = np.array(python_matrix, dtype=str)
            
            self.target_area = np.count_nonzero(self.matrix == ".")
            self.coverage_mask = np.full((self.height, self.width), False, dtype=bool)
            
        """
        Random initialization of routers position.
        Routers are placed only where a target point exists.
        The initial number of router is set to the lowerbound of routers needed to cover 
        all the points in a rectangle, where the dimention is r*(r*a), where a should be the lowerbound 
        """
    def random_init(self):
        min_router = (self.target_area // self.router_range**2) + 1
        
        target_coord = []
        for i, row in enumerate(self.matrix):
            for j, item in enumerate(row):
                if item == '.':
                    target_coord.append((i,j))
                    
        router_init_list = []
        unique_randoms = random.sample(range(0, len(target_coord), min_router))
        for i in unique_randoms:
            router_init_list.append(target_coord[i])
        return router_init_list
        
        