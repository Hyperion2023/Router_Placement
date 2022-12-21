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
	# parsing command line arguments
	filepath = args.filepath
	algorithm = args.algorithm
	num_iterations = args.iterations
	verbose = args.verbose

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
			mutation_probability=args.mutation,
			max_iter=num_iterations,
			verbose=verbose
		)
	elif algorithm == "priority":
		best_configuration = priority(
			data = data,
			initial_state=utils.get_grid_router_placement(data=data, rescale_range_factor=0.6),
			fitness_function=fitness_function,
			num_iterations=num_iterations,
			evaluation_delay=args.evaluation_delay,
			verbose=verbose
		)
	elif algorithm == "annealing":
		best_configuration = simulated_annealing(
			initial_state=utils.get_random_router_placement(
				building_matrix=building_matrix,
				number_routers= int(1.2 * utils.min_routers_optimal_condition(data=data))
			),
			number_iterations=num_iterations,
			initial_temperature=args.temperature,
			building_matrix=building_matrix,
			fitness_function=fitness_function,
			sigma=router_radius,
			verbose=verbose
		)
	elif algorithm == "hill":
		best_configuration = hill_climb(
			data=data,
            fitness_function=fitness_function,
			random_init=args.random_init,
			max_step=args.max_step,
			policy="best" if args.best_policy else "",
            verbose=verbose
		)
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

	viz.plot_complete(
		building_matrix,
		best_configuration,
		router_radius,
		[_ for _ in g.nodes()],
		data.initial_backbone
	)
	plt.show()

def check_args(args) -> bool:
	if args.algorithm not in ["hill", "annealing", "genetic", "priority"]:
		print("The selected algorithm does not exist!")
		return False

	if args.iterations <= 0:
		print("Number of iterations must be positive")
		return False

	if args.mutation < 0 or args.mutation > 1:
		print("Mutation probability must be a float number between 0.0 and 1.0")
		return False

	if args.temperature <= 0:
		print("Temperature must be a positive value")
		return False

	if args.evaluation_delay <= 0:
		print("Evaluation delay must be a positive value")
		return False

	if args.random_init <= 0:
		print("Number of random initializations must be a positive value")
		return False

	if args.max_step <= 0:
		print("Maximum number of non improvement steps must be a positive value")
		return False

	return True

if __name__  == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("filepath", help="Path to the dataset to use")
	parser.add_argument(
		"algorithm",
		help="Algorithm to use for solving the problem; the possible algorithms are {genetic, priority, annealing, hill}"
	)
	parser.add_argument(
		"-i",
		"--iterations",
		help="""Number of iterations that the algorithm has to perform.
			 This parameter is useful only for the following algorithms: {genetic, priority, annealing}
			 """,
		type=int,
		default=10
	)
	parser.add_argument(
		"--mutation",
		help="""Probability thar a random mutation occurs in the genetic algorithm;
			This parameter is a number between 0.0 and 1.0 and is useful only for the {genetic} algorithm
			""",
		type=float,
		default=0.5
	)
	parser.add_argument(
		"-t",
		"--temperature",
		help="""Initial temperature for the simulated annealing algorithm;
				This parameter is a positive value and is useful only for the {annealing} algorithm
				""",
		type=float,
		default=1000
	)
	parser.add_argument(
		"-d",
		"--evaluation_delay",
		help="""How often perform the internal operations to compute the coverage evaluation;
				This parameter is a positive value and is useful only for the {priority} algorithm
				""",
		type=int,
		default=3
	)
	parser.add_argument(
		"-r",
		"--random_init",
		help="""Number of random initialization of the hill climbing;
				This parameter is a positive value and is useful only for the {hill} algorithm
				""",
		type=int,
		default=1
	)
	parser.add_argument(
		"--max_step",
		help="""Maximum number of non improvement step;
				This parameter is a positive value and is useful only for the {hill} algorithm
				""",
		type=int,
		default=1
	)
	parser.add_argument(
		"-b",
		"--best_policy",
		help="""Select the "best movement" as policy for the improving in each iteration:
				This parameter is useful only for the {hill} algorithm
				""",
		action="store_true"
	)
	parser.add_argument("--verbose", help="increase output verbosity", action="store_true")

	args = parser.parse_args()

	if check_args(args):
		main(args)
