

import numpy as np

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

            self.router_range = int((lines[0].split(" "))[2])
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