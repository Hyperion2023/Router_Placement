import utils
import argparse
import viz
import backbone
from classes.Data import Data
from hill_climbing import hill_climb
from priority_solution import priority
from genetic_algorithm import genetic_algorithm
import matplotlib.pyplot as plt
from simulated_annealing import simulated_annealing

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
				utils.get_grid_router_placement(data=data, rescale_range_factor=0.6),
				utils.get_grid_router_placement(data=data, rescale_range_factor=0.6)
			],
			data=data,
			fitness_function=fitness_function,
			mutation_probability=0.5,
			max_iter=10,
			verbose=True
		)
	elif algorithm == "priority":
		best_configuration = priority(
			data = data,
			initial_state=utils.get_grid_router_placement(data=data, rescale_range_factor=0.6),
			fitness_function=fitness_function,
			num_iterations=10,
			evaluation_delay=3,
			verbose=True
		)
	elif algorithm == "annealing":
		best_configuration = simulated_annealing(
			data=data,
			initial_state=utils.get_random_router_placement(
				building_matrix=building_matrix,
				number_routers= int(1.2 * utils.min_routers_optimal_condition(data=data))
			),
			number_iterations=40,
			initial_temperature=1000,
			building_matrix=building_matrix,
			fitness_function=fitness_function,
			sigma=router_radius,
			verbose=True
		)
	elif algorithm == "hill":
		best_configuration = hill_climb(
			data=data,
            fitness_function=fitness_function,
			random_init=1,
			max_step=5,
			policy="best",
            verbose=True
		)
	else:
		print("The selected algorithm does not exist!")
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
