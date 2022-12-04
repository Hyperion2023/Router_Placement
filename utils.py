import random
import numpy as np
import Data
import math
import backbone
import itertools


__all__ = [
	"get_number_routers",
	"get_number_covered_cells",
	"compute_fitness",
	"get_random_router_placement"
]


def get_points_around_router(
    matrix: np.array,
    router_coords: tuple,
    router_radius: int
) -> list:
	"""
	Given the position of a router inside the building, returns the number of cells covered by that
	router, without considering the wall and void cells.

	:param matrix: array of arrays, matrix of cells
	:param router_coords: tuple, contains the (x,y) coordinates of a router in the matrix
	:param router_radius: int, the radius of cells covered by the router
	"""
	r, c = router_coords
	m, n = matrix.shape

	return [
		(r + i, c + j)
		for i in np.arange(start=-router_radius, stop=router_radius+1, step=1)
		for j in np.arange(start=-router_radius, stop=router_radius + 1, step=1)
		if 0 <= r + i < m and 0 <= c + j < n
	]


def filter_non_target_points(
    building_matrix: np.array,
    router_coords: tuple,
    points: list
) -> list:
    """
    Given the coordinate of a router and a set of cells covered by the router, filters the cells
    keeping only the cells which aren't covered by walls and aren't void

    :param building_matrix: array of arrays, the matrix describing the building (voids, targets, walls)
    :param router_coords: tuple, the (x,y) coordinates of a router in the building
    :param points: list, list of the cells (described with (x,y) coordinates) covered by the router without
            considering the walls
    :return: filtered points
    """
    def is_wall(c): return c == "#"
    def is_void(c): return c == "-"
    filtered_points = list()

    a, b = router_coords
    # iterate over all the points to evaluate
    for (x, y) in points:
        # check if point is void
        if not is_void(building_matrix[x, y]):
            # check if point is covered by wall
            w_lower = min(a, x)
            w_upper = max(a, x)
            v_lower = min(b, y)
            v_upper = max(b, y)

            # generate all the points inside the smallest enclosing rectangle between
            # the point and the router
            cells_to_check = itertools.product(
                range(w_lower, w_upper + 1), range(v_lower, v_upper + 1))

            # evaluate if inside this rectangle there is a wall
            for (w, v) in cells_to_check:
                # if there is a wall, don't insert the point
                if is_wall(building_matrix[w][v]):
                    break
            else:  # branch executed if we didn't break
                # insert the point
                filtered_points.append((x, y))

    return filtered_points


def get_number_covered_cells(
		routers_placement: np.array,
		building_matrix: np.array,
		router_range: int
) -> int:
    """
    Given a placement of routers and the matrix of the building returns the number of unique target
    cells covered, considering voids and walls.

    :param routers_placement: the mask of the position of routers in the building
    :param building_matrix: array of arrays, the matrix describing the building (voids, targets, walls)
    :param router_range: range of the router
    :return: the number of unique target cells covered
    """
    covered_cells = set()
    # iterate over routers (non zero cells)
    for router_coords in zip(*routers_placement.nonzero()):
        # compute points covered by the router
        points_covered_by_router = get_points_around_router(
            routers_placement,
            router_coords,
            router_range
        )
        # filter points covered by walls and void cells
        points_covered_by_router = filter_non_target_points(
            building_matrix,
            router_coords,
            points_covered_by_router
        )

        for covered_cell in points_covered_by_router:
            covered_cells.add(covered_cell)

    return len(covered_cells)


def get_number_routers(
    routers_placement: np.array
) -> int:
    """
    :param routers_placement: array of arrays, matrix which indicates the cells where routers are
            placed. If a cell contains a router its value is 1, otherwise 0
    :return: the number of routers
    """
    return np.count_nonzero(routers_placement)


def compute_fitness(
		building_matrix: np.array,
		routers_placement: np.array,
		router_range: int,
		backbone_starting_point: tuple,
		router_cost: int,
		backbone_cost: int,
		budget: int
	) -> tuple:

	"""
		Compute the fitness value of a routers placement

		:param building_matrix: array of arrays, matrix which indicates the presence of voids/targers/walls
		:param routers_placement: array of arrays, matrix which indicates the cells where routers are
            placed. If a cell contains a router its value is 1, otherwise 0
		:param router_range: int, the range of a router
		:param backbone_starting_point: tuple, 
		:param router_cost:
		:param backbone_cost:
		:param budget:
		:return: tuple, the first value is the fitness score, while the second is equal to True if the solution
			cost is greater than the budget, False otherwise.
	"""
	# compute number of cells covered by router signal
	number_covered_cells = get_number_covered_cells(routers_placement, building_matrix, router_range)

	# compute number of routers
	number_routers = get_number_routers(routers_placement)

	# compute cost of backbone connecting routers
	backbone_length = backbone.get_backbone_length(
		backbone_starting_point,
		routers_placement,
		backbone_cost
	)
	
	total_cost = number_routers*router_cost + backbone_length*backbone_cost

	score = 1000 * number_covered_cells + (budget - total_cost )
	
	return score, total_cost > budget


def get_random_router_placement(
		building_matrix: np.array,
		number_routers: int
) -> np.array:
	"""
	Generates a random placement of the routers inside the building, considering the condition that
	a router can't be placed in a wall and leveraging the fact that a router inside a void cell is unuseful

	:param building_matrix: array of arrays, the matrix which describers the building structure
	:param number_routers: int, number of routers to generate.
	:return: returns a placement of routers containing the number of required routers
	"""
	n, m = building_matrix.shape
	routers_placement = np.zeros(shape=(n, m))

	generate_router_position = lambda width, height: (
		random.randint(0, width-1),
		random.randint(0, height-1)
	)
	is_target = lambda c: c == "."
	contains_router = lambda c: c == 1

	number_routers_created = 0
	while number_routers_created < number_routers:
		# generate a couple of random coordinates inside the building
		i, j = generate_router_position(n, m)

		# verify if the random position is suitable for containing a router; this means
		# that the cell should be a target and must not contain a router

		if is_target(building_matrix[i][j]) and not contains_router(routers_placement[i][j]):
			routers_placement[i][j] = 1
			number_routers_created += 1

	return routers_placement


def save_output_matrix(path, building_matrix, state, score):
	_building_matrix = np.copy(building_matrix)
	router_coords = [ (i,j) for (i,j) in zip(*state.nonzero())]
	for (i, j) in router_coords:
		_building_matrix[i][j] = 1
	np.savetxt(path,_building_matrix, fmt="%c", delimiter='')

	f = open(path,'r+')
	lines = f.readlines() # read old content
	f.seek(0) # go back to the beginning of the file
	f.write("Score: "+str(score)+"\n\n") # write new content at the beginning
	for line in lines: # write old content after new
		f.write(line)
	f.close()


def min_routers_optimal_condition(data : Data) -> int:
    """
    get the number of routers needed to obtain a full coverage in a perfect scenario
    """

    target_area = data.target_area
    router_range = data.router_range

    router_coverage = router_range*router_range
    num_router = math.ceil(target_area/router_coverage)
    return num_router


