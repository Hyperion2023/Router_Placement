import numpy as np
import random
from concurrent.futures import ProcessPoolExecutor


__all__ = ["genetic_algorithm"]


def flip_matrix(matrix: np.array, flip_p: float) -> np.array:
	# generate a matrix with the positions to flip
	flipped_positions_matrix = np.random.choice([0,1], matrix.shape, p=[1-flip_p, flip_p])

	# flip the matrix (equivalent to a xor operation)
	return np.where(np.logical_xor(matrix, flipped_positions_matrix), 1, 0)

def mutate(
		building_matrix: np.array,
		routers_placement: np.array,
		flip_cell_prob: float = 0.05
) -> np.array:
	"""
	Flips randomly the routers, keeping only the routers in target cells (thus not placing
	routers in void and walls)

	:param building_matrix: array of arrays, indicates where are void, wall and target cells
	:param routers_placement: array of arrays, a mask which indicates where are the routers in the original matrix;
		cell is 1 if there is a router, else 0
	:param flip_cell_prob: float, probability that a cell is flipped
	:return: the new routers placement
	"""
	# generate new routers placement
	new_routers_placement = np.array(routers_placement, dtype=int)

	# flips the new routers placement
	flip_matrix(new_routers_placement, flip_cell_prob)

	# eliminate routers where there are walls and voids
	mask = np.where(building_matrix == ".", 1, 0)
	return new_routers_placement & mask

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

def get_weight_population_by_fitness(population: list, fitness_function) -> list:
	"""
	Computes for each configuration the probability to be selected (according to the fitness function)
	and returns the configurations (ordered in ascending order)

	:param population: list, list of routers placement
	:param fitness_function: function that, taken a routers placement as its parameter, returns its value
	:return: list of tuples, for each tuple the first element contains the routers placement, while the second element
		corresponds to its value according to the fitness function
	"""
	# computing for each configuration the probability to be selected, according to the fitness function
	with ProcessPoolExecutor(initializer=worker_init, initargs=(fitness_function,)) as executor:
		weighted_population = [
			(configuration, configuration_fitness[0])
			for (configuration, configuration_fitness) in zip(population, executor.map(worker, population))
		]

	# order by the fitness of configuration
	weighted_population.sort(key=lambda x: x[1], reverse=True)

	return weighted_population


def choose_parents_population(population: list, fitness_function) -> tuple:
	"""
	Choose 2 parents in the population. A member of the population probability to be picked is proportional to its
	value according to the fitness function.

	:param population: list, list of routers placement
	:param fitness_function: function that, taken a routers placement as its parameter, returns its value
	:return: tuple, a couple of randomly selected configurations weighted by their fitness value
	"""
	weighted_population = get_weight_population_by_fitness(population, fitness_function)

	# selected 2 parents with a probabity proportial to the configuration fitness
	configurations = []
	fitnesses = []
	for (configuration, configuration_fitness) in weighted_population:
		configurations.append(configuration)
		fitnesses.append(configuration_fitness)

	picked_parents = (random.choices(configurations, weights=fitnesses, k=2))

	return picked_parents[0], picked_parents[1]


def genetic_algorithm(
		building_matrix: np.array,
		population: list,
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
	for i in range(max_iter):  # iterate until some individual is fit enough, or enough time has elapsed
		if verbose:
			print(f"ITERATION {i}")

		new_population = []
		for _ in range(len(population)):
			# select randomly two individuals in the population, preferring these with better fitness
			parent1, parent2 = choose_parents_population(population, fitness_function)

			# let the parents reproduce
			child = reproduce(parent1, parent2)

			# do a mutation
			if random.random() < mutation_probability:
				child = mutate(
					building_matrix,
					child,
					flip_cell_probability
				)

			# add new child to population
			new_population.append(child)

		population = new_population

	# return best individual found according to fitness
	weighted_population = get_weight_population_by_fitness(population, fitness_function)

	return weighted_population[0][0]
