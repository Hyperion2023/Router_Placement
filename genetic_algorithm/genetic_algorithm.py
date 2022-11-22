import numpy as np
import random

__all__ = ["genetic_algorithm"]


def mutate(building_matrix: np.array, routers_placement: np.array) -> np.array:
	"""
	Mutation consists in flipping a random position for each row

	:param building_matrix: array of arrays, indicates where are void, wall and target cells
	:param routers_placement: array of arrays, a mask which indicates where are the routers in the original matrix;
		cell is 1 if there is a router, else 0
	"""
	is_wall = lambda c: c == "#"
	is_void = lambda c: c == "-"
	flip_cell = lambda c: 1 if c == 0 else 0

	new_routers_placement = np.array(routers_placement)

	for (row_index, row) in enumerate(building_matrix):  # iterate over all rows
		# if the row is all invalid cells (void/walls) then skip to next_row
		if "." not in row:
			continue

		# generate a random (valid) position inside row
		invalid_cell_to_flip = True
		while invalid_cell_to_flip:
			flipping_position = random.randint(0, len(row)-1)
			cell = building_matrix[row_index][flipping_position]
			# checks if it is a wall or void
			if not is_wall(cell) and not is_void(cell):
				invalid_cell_to_flip = False

		# flip cell
		new_routers_placement[row_index][flipping_position] = flip_cell(new_routers_placement[row_index][flipping_position])

	return new_routers_placement


def reproduce(routers_placement1: np.array, routers_placement2: np.array) -> np.array:
	"""
	"""
	matrix_width, matrix_height = routers_placement1.shape

	starting_point = 0
	end_point = matrix_width - 1

	split_point = random.randint(starting_point, end_point)

	# extracting sub-matrices
	parent1_left, parent1_right = routers_placement1[:, 0:split_point], routers_placement1[:, split_point:]
	parent2_left, parent2_right = routers_placement2[:, 0:split_point], routers_placement2[:, split_point:]

	# composing submatrices
	new_routers_placement = np.concatenate((parent1_left, parent2_right), axis=1)

	return new_routers_placement


def get_weight_population_by_fitness(population: list, fitness_function) -> list:
	# computing for each configuration the probability to be selected, according to the fitness function
	weighted_population = [
		(configuration, configuration_fitness)
		for (configuration, configuration_fitness) in zip(population, map(fitness_function, population))
	]

	# order by the fitness of configuration
	weighted_population.sort(key=lambda x: x[1])

	return weighted_population


def choose_parents_population(population: list, fitness_function) -> tuple:
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
		mutation_probability: float = None,
		max_iter: int = 1000,
		verbose: bool = False
) -> np.array:
	"""
	:param building_matrix: array of arrays, indicates where are void, wall and target cells
	:param population: list, list of configurations to use as a starting points
	:param fitness_function: function, function used to evaluate the fitness of a configuration
	:param mutation_probability: float, probability of a random mutation. If not specified, a random
		probability is generated for every reproduction cycle
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
				child = mutate(building_matrix, child)

			# add new child to population
			new_population.append(child)

		population = new_population

	# return best individual found according to fitness
	weighted_population = get_weight_population_by_fitness(population, fitness_function)

	return weighted_population[0][0]
