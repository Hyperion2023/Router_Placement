import numpy as np
import random
from concurrent.futures import ProcessPoolExecutor
from classes import PriorityDict, Cell
import utils
import Data


__all__ = ["genetic_algorithm"]


def init_pri_dic(
		building_matrix: np.array,
		routers_placement: np.array,
		router_range: int
) -> PriorityDict:
	"""
	Initialize the dictionary with the order on the values such that for each target cell of the matrix there is an entry in the dictionary
	"""
	# we want to add each cell of the grid and then update the coverage level
	pri_dict = PriorityDict()

	# add all the target coords to the priority dict
	target_coords = np.nonzero(building_matrix == ".")
	for (i, j) in zip(target_coords[0], target_coords[1]):
		pri_dict.add_element((i, j))

	# iterate the router and update the nearby cells
	router_coords = routers_placement.nonzero()
	for (i, j) in zip(router_coords[0], router_coords[1]):  # for each router

		# filter points covered by walls and void cells
		points_covered_by_router = utils.filter_non_target_points(
			building_matrix=building_matrix,
			router_coords=(i, j),
			points=utils.get_points_around_router(
				matrix=building_matrix,
				router_coords=(i, j),
				router_radius=router_range
			)
		)

		for (x, y) in points_covered_by_router:  # for each point (cell) covered by the router
			pri_dict.edit_element((x, y), 1)

	pri_dict.shuffle()
	pri_dict.order()

	return pri_dict


def _update_neighbor(
		pri_dic: PriorityDict,
		building_matrix: np.array,
		router: tuple[int, int],
		router_range: int,
		delta: int
):
	"""
	Given a router position and a delta value, update the coverage value of all the cells covered by the router with the delta, the walls are taken into account
	:param router: tuple of two int, the position of the router
	:param delta: int, the delta to apply to the near cells
	"""
	x, y = router

	points_covered_by_router = utils.filter_non_target_points(
		building_matrix=building_matrix,
		router_coords=(x, y),
		points=utils.get_points_around_router(
			matrix=building_matrix,
			router_coords=(x, y),
			router_radius=router_range
		)
	)
	for (x, y) in points_covered_by_router:  # for each point (cell) covered by the router
		pri_dic.edit_element((x, y), delta=delta)  # edit the point


def _state_neighbor(
		pri_dic: PriorityDict,
		building_matrix: np.array,
		routers_placement: np.array,
		router_range: int,
		move_type: str
) -> np.array:
	"""
	Given a move type, returns the new state in the solution space.
	If the move is 'add' a new router will be add in the less covered cell,
	if the move is 'remove' the nearest router to the most covered cell will be removed
	:param move_type: string, the type of move to perform, if it is not supported, a random move will be performed
	:returns: np.array, the new state
	"""

	supported_moves = ["add", "remove"]

	new_state = np.copy(routers_placement)

	if move_type not in supported_moves:
		move_type = random.choice(supported_moves)

	if move_type == "add":  # add one router
		while True:
			x, y = pri_dic.get_lower()  # the cell with less coverage
			if routers_placement[x][y] == 0:  # there is not another router in that cell
				new_state[x][y] = 1
				break

		# we have to update the near cells
		_update_neighbor(
			pri_dic=pri_dic,
			building_matrix=building_matrix,
			router=(x, y),
			router_range=router_range,
			delta=+1
		)

	elif move_type == "remove":  # remove one router
		target = pri_dic.get_higer()  # the cell with most coverage
		to_remove = utils.get_nearest_router(cell=target, routers=routers_placement)
		x, y = to_remove
		new_state[x][y] = 0

		# we have to update the near cells
		_update_neighbor(
			pri_dic=pri_dic,
			building_matrix=building_matrix,
			router=(x, y),
			router_range=router_range,
			delta=-1
		)
	else:
		pass

	return new_state

def mutate(
		building_matrix: np.array,
		routers_placement: np.array,
		router_range: int,
		fitness_function
) -> np.array:
	"""

	:return: the new routers placement
	"""
	pri_dic = init_pri_dic(building_matrix, routers_placement, router_range)
	pri_dic.shuffle()  # shuffle priority dict
	pri_dic.order()  # ordinate priority dict

	# evaluate child
	_, out_of_budget = fitness_function(routers_placement)

	move_type = "remove" if out_of_budget else "add"
	return _state_neighbor(
		pri_dic=pri_dic,
		building_matrix=building_matrix,
		routers_placement=routers_placement,
		router_range=router_range,
		move_type=move_type
	)

def reproduce(routers_placement1: np.array, routers_placement2: np.array) -> np.array:
	"""
	Given 2 parents computes the child by extracting the submatrices for each parent and then merging
	them.

	:param routers_placement1: array of arrays, the first parent matrix
	:param routers_placement2: array of arrays, the second parent matrix
	:return: array of arrays, the child matrix
	"""
	matrix_rows, matrix_columns = routers_placement1.shape

	# computing splitting points
	rows_mid = round(matrix_rows / 2)
	columns_mid = round(matrix_columns / 2)

	# extracting sub-matrices
	matrix1_upper_left = routers_placement1[0:rows_mid, 0:columns_mid]
	matrix1_down_right = routers_placement1[rows_mid:, columns_mid:]
	matrix2_upper_right = routers_placement2[0:rows_mid, columns_mid:]
	matrix2_down_left = routers_placement2[rows_mid:, 0:columns_mid]

	# composing submatrices
	merged_matrix_upper = np.concatenate((matrix1_upper_left, matrix2_upper_right), axis=1)
	merged_matrix_down = np.concatenate((matrix2_down_left, matrix1_down_right), axis=1)

	return np.concatenate((merged_matrix_upper, merged_matrix_down), axis=0)


_func = None

def worker_init(func):
	global _func
	_func = func


def worker(x):
	return _func(x)

def get_weight_population_by_fitness(population: list, fitness_function) -> tuple:
	"""
	Computes for each configuration the probability to be selected (according to the fitness function)
	and returns the configurations (ordered in descending order)

	:param population: list, list of routers placement
	:param fitness_function: function that, taken a routers placement as its parameter, returns its value
	:return: tuple, the first element is the best individual in the population, the latter is a list of tuples,
	for each tuple the first element contains the routers placement, while the second element corresponds to its value
	according to the fitness function
	"""
	# computing for each configuration the probability to be selected, according to the fitness function
	with ProcessPoolExecutor(initializer=worker_init, initargs=(fitness_function,)) as executor:
		weighted_population = [
			(configuration, configuration_fitness[0])
			for (configuration, configuration_fitness) in zip(population, executor.map(worker, population))
		]

	# order by the fitness of configuration
	weighted_population.sort(key=lambda x: x[1], reverse=True)

	return weighted_population[0], weighted_population


def choose_parents_population(
		weighted_population: list
) -> tuple:
	"""
	Choose 2 parents in the population. A member of the population probability to be picked is proportional to its
	value according to the fitness function.

	:param weighted_population: list, a list containing tuples in the form (configuration, fitness value of configuration)
	:return: tuple, a couple of randomly selected configurations
	"""
	# selected 2 parents with a probabity proportial to the configuration fitness
	configurations, fitnesses = zip(*weighted_population)
	picked_parents = random.choices(configurations, weights=fitnesses, k=2)

	return picked_parents[0], picked_parents[1]


def genetic_algorithm(
		building_matrix: np.array,
		population: list,
		data: Data,
		fitness_function,
		mutation_probability: float,
		flip_cell_probability: float = 0.05,
		max_iter: int = 1000,
		verbose: bool = False
) -> np.array:
	"""
	:param building_matrix: array of arrays, indicates where are void, wall and target cells
	:param population: list, list of configurations to use as a starting points
	:param fitness_function: function, function used to evaluate the fitness of a configuration
	:param mutation_probability: float, probability of a random mutation.
	:param flip_cell_probability: float, the probability that during a mutation cell is flipped
	:param max_iter: int, maximum number of iterations cycles
	:param verbose: bool
	:return: the best individual in population, according to fitness
	"""
	avg = lambda l: sum(l)/len(l) if len(l) != 0 else 0
	best_individual_found = None

	for i in range(max_iter):  # iterate until some individual is fit enough, or enough time has elapsed
		if verbose:
			print(f"ITERATION {i}")

		# weight each population member by fitness function
		best_individual_in_population, weighted_population = get_weight_population_by_fitness(population, fitness_function)
		if best_individual_found is None:
			best_individual_found = best_individual_in_population
		else:
			if best_individual_in_population[1] > best_individual_found[1]:
				best_individual_found = best_individual_in_population

		if verbose:
			_, fitness_values = zip(*weighted_population)
			# print fitnesses
			print(f"Fitnesses = {fitness_values}")
			# print max, min, average of fitness value
			print(f"Population fitness min/max/avg = {min(fitness_values)}/{max(fitness_values)}/{avg(fitness_values)}")

		new_population = []
		for _ in range(len(population)):
			# select randomly two individuals in the population, preferring these with better fitness
			parent1, parent2 = choose_parents_population(weighted_population)

			# let the parents reproduce
			child = reproduce(parent1, parent2)

			# do a mutation
			if random.random() < mutation_probability:
				if verbose:
					print("A random mutation occurred in a child!")

				child = mutate(
					building_matrix,
					child,
					data.router_range,
					fitness_function
				)

			# add new child to population
			new_population.append(child)

		population = new_population

	# return best individual found according to fitness
	best_individual_in_population, weighted_population = get_weight_population_by_fitness(population, fitness_function)

	if best_individual_found is None:
		return best_individual_in_population[0]
	else:
		if best_individual_in_population[1] > best_individual_found[1]:
			return best_individual_in_population[0]
		else:
			return best_individual_found[0]

