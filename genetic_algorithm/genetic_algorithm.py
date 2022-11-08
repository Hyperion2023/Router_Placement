"""
-select 2 patterns for reproduction, one possibility is to select from all individuals with probability proportional to their fitness score. Another possibility is to select them randomly
-randomly select a crossover point to split each of the parent data, and recombine the parts to form two children, one with the first part of parent 1 and the second part of parent 2;
the other with the second part of parent 1 and the first part of parent 2.
-mutation phase: once a son has been generated, every part in its composition is flipped with probability equal to the mutation rate
"""

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
	flip_cell = lambda c: 1 if c == 0 else 0

	new_routers_placement = np.array(routers_placement)

	for (row_index, row) in enumerate(new_routers_placement):  # iterate over all rows
		# generate a random (valid) position inside row
		invalid_cell_to_flip = True
		while invalid_cell_to_flip:
			flipping_position = random.randint(0, len(row)-1)

			# checks if it is a wall
			invalid_cell_to_flip = True if is_wall(building_matrix[row_index][flipping_position]) else False

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


def choose_parents_population(population: list, fitness_function) -> tuple:
	# computing for each configuration the probability to be selected, according to the fitness function
	weighted_population = [
		(configuration, configuration_fitness)
		for (configuration, configuration_fitness) in zip(population, map(fitness_function, population))
	]

	# order by the fitness of configuration
	weighted_population.sort(key=lambda x: x[1])

	return weighted_population[0][0], weighted_population[1][0]


def genetic_algorithm(
		building_matrix: np.array,
		population: list,
		fitness_function,
		mutation_probability: float = None,
		max_iter: int = 1000
) -> np.array:
	"""
	:param building_matrix: array of arrays, indicates where are void, wall and target cells
	:param population: list, list of configurations to use as a starting points
	:param fitness_function: function, function used to evaluate the fitness of a configuration
	:param mutation_probability: float, probability of a random mutation. If not specified, a random
		probability is generated for every reproduction cycle
	:param max_iter: int, maximum number of iterations cycles
	:return: the best individual in population, according to fitness
	"""
	for _ in range(max_iter):  # iterate until some individual is fit enough, or enough time has elapsed
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
	weighted_population = [
		(configuration, configuration_fitness)
		for (configuration, configuration_fitness) in zip(population, map(fitness_function, population))
	]
	weighted_population.sort(key=lambda x: x[1])

	return weighted_population[0][0]
