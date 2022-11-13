import utils
import numpy as np
import argparse
from Data import Data
from genetic_algorithm import genetic_algorithm


def main(args):
    filepath = args.filepath
    algorithm = args.algorithm

    data = Data(filepath)

    if algorithm == "genetic":
        # genetic_algorithm()
        pass
    elif algorithm == "annealing":
        pass
    elif algorithm == "hill_climbing":
        pass

    building_matrix = data.matrix
    router_radius = 7

    """
    routers_to_generate = 700
    i = 0
    while i < routers_to_generate:
        m, n = building_matrix.shape
        x = random.randint(0, m-1)
        y = random.randint(0, n-1)

        if building_matrix[x][y] == "." and routers_placement[x][y] == 0:
            routers_placement[x][y] = 1
            i += 1

    print(utils.get_number_covered_cells(routers_placement, building_matrix, router_radius))
    """
    fitness_function = lambda routers: utils.compute_fitness(
        building_matrix=building_matrix,
        routers_placement=routers,
        router_range=data.router_range,
        backbone_starting_point=data.initial_backbone,
        router_cost=data.router_cost,
        backbone_cost=data.backbone_cost,
        budget=data.budget
    )
    best_configuration = genetic_algorithm(
        building_matrix=building_matrix,
        population=[
            utils.get_random_router_placement(building_matrix, 10),
            utils.get_random_router_placement(building_matrix, 20)
        ],
        fitness_function=fitness_function,
        mutation_probability=0.4,
        max_iter=10,
        verbose=True
    )
    print(utils.get_number_covered_cells(best_configuration, building_matrix, router_radius))


if __name__  == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="Path to the dataset to use")
    parser.add_argument("algorithm", help="Algorithm to use for solving the problem")
    args = parser.parse_args()
    main(args)
