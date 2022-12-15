import utils
import numpy as np
import argparse
import viz
import backbone
from Data import Data
from hill_climbing import hill_climb
from simulated_annealing import SimulatedAnnealing
from genetic_algorithm import genetic_algorithm
import matplotlib.pyplot as plt

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
                utils.get_random_router_placement(building_matrix, 5),
                utils.get_random_router_placement(building_matrix, 5)
            ],
            fitness_function=fitness_function,
            mutation_probability=0.5,
            max_iter=10,
            verbose=True
        )

    elif algorithm == "annealing":
        annealing = SimulatedAnnealing(
            data = data,
            initial_state = utils.get_random_router_placement(
                building_matrix=building_matrix,
                number_routers= int(1.2 * utils.min_routers_optimal_condition(data=data))
            ),
            number_iterations = 40,
            initial_temperature = 1000,
            fitness_function = fitness_function,
            sigma = data.router_range,
            verbose = True 
        )
        exit(0)
        #best_configuration = annealing.run()

    elif algorithm == "hill":
        best_configuration = hill_climb(data=data)

    else:
        return

    g = backbone.get_backbone_graph(
        data.initial_backbone,
        best_configuration,
        data.backbone_cost
    )

    print(f"coverage = {utils.get_number_covered_cells(best_configuration, data.matrix, data.router_range)/data.target_area}")
    print("total score", utils.compute_fitness(
        building_matrix=building_matrix,
        routers_placement=best_configuration,
        router_range=data.router_range,
        backbone_starting_point=data.initial_backbone,
        router_cost=data.router_cost,
        backbone_cost=data.backbone_cost,
        budget=data.budget
    ) )
    """
    viz.plot_solution(
        building_matrix,
        best_configuration,
        [_ for _ in g.nodes()],
        data.initial_backbone
    )
    viz.plot_heatmap(
        building_matrix,
        best_configuration,
        router_radius
    )
    """
    viz.plot_complete(
        building_matrix,
        best_configuration,
        router_radius,
        [_ for _ in g.nodes()],
        data.initial_backbone
    )
    plt.show()


if __name__  == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="Path to the dataset to use")
    parser.add_argument("algorithm", help="Algorithm to use for solving the problem")
    args = parser.parse_args()
    main(args)
