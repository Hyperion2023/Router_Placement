import utils
import numpy as np
import argparse
from Data import Data
from genetic_algorithm import genetic_algorithm
from simulated_annealing import simulated_annealing
import os

def main(args):
    filepath = args.filepath
    algorithm = args.algorithm

    data = Data(filepath)

    fitness_function = lambda routers: utils.compute_fitness(
        building_matrix=building_matrix,
        routers_placement=routers,
        router_range=data.router_range,
        backbone_starting_point=data.initial_backbone,
        router_cost=data.router_cost,
        backbone_cost=data.backbone_cost,
        budget=data.budget
    )

    building_matrix = data.matrix
    best_configuration = None

    if algorithm == "genetic":
        best_configuration = genetic_algorithm(
        building_matrix=building_matrix,
        population=[
            np.zeros(building_matrix.shape),
            np.zeros(building_matrix.shape),
            np.zeros(building_matrix.shape),
            np.zeros(building_matrix.shape)
        ],
        fitness_function=fitness_function,
        mutation_probability=0.4,
        max_iter=10,
        verbose=True
        )
        pass
    
    elif algorithm == "annealing":
        best_configuration = simulated_annealing(
            initial_state = np.zeros(building_matrix.shape),
            building_matrix = building_matrix,
            number_iterations = 100,
            initial_temperature = 500,
            fitness_function=fitness_function,
            sigma=data.router_range
            )
    
    elif algorithm == "hill_climbing":
        pass

    building_matrix = data.matrix
    router_radius = 7


    coverage = utils.get_number_covered_cells(best_configuration, building_matrix, data.router_range) / data.target_area
    print("coverge:", coverage)
    utils.save_output_matrix(
        building_matrix=building_matrix, 
        state=best_configuration, 
        score=coverage,
        path="./result_"+os.path.basename(filepath))


if __name__  == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="Path to the dataset to use")
    parser.add_argument("algorithm", help="Algorithm to use for solving the problem")
    args = parser.parse_args()
    main(args)
