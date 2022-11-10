
import utils
import numpy as np
from Data import Data




def main():

    data : Data = Data("Dataset/tiny_test.in")

    print(data.matrix.shape, data.router_range)
    print(data.backbone_cost, data.router_cost, data.budget)
    print(data.initial_backbone)
    print(data.target_area)
    print(data.matrix)

    
































if __name__  == "__main__":
    main()