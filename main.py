import utils
import numpy as np
import argparse
import viz
import backbone
from Data import Data
from simulated_annealing import simulated_annealing
from genetic_algorithm import genetic_algorithm


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
    router_radius = data.router_range

    if algorithm == "genetic":
        best_configuration = genetic_algorithm(
            building_matrix=building_matrix,
            population=[
                utils.get_random_router_placement(building_matrix, 10),
                utils.get_random_router_placement(building_matrix, 10)
            ],
            fitness_function=fitness_function,
            mutation_probability=0.5,
            max_iter=5,
            verbose=True
        )
    elif algorithm == "annealing":
        best_configuration = simulated_annealing(
            data=data,
            initial_state=np.zeros(building_matrix.shape),
            number_iterations=10,
            initial_temperature=500,
            building_matrix=building_matrix,
            fitness_function=fitness_function,
            sigma=router_radius,
            verbose=True
        )
    elif algorithm == "hill_climbing":
        pass
    else:
        return

    g = backbone.get_backbone_graph(
        data.initial_backbone,
        best_configuration,
        data.backbone_cost
    )
    viz.plot_solution(building_matrix, best_configuration, [_ for _ in g.nodes()])


if __name__  == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="Path to the dataset to use")
    parser.add_argument("algorithm", help="Algorithm to use for solving the problem")
    args = parser.parse_args()
    main(args)
