import numpy as np
import itertools
import Data
import networkx as nx
import math
import matplotlib.pyplot as plt

__all__ = [
	"get_number_routers",
	"get_number_covered_cells",
	"get_backbone_length",
	"compute_fitness"
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
	is_wall = lambda c: c == "#"
	is_void = lambda c: c == "-"
	filtered_points = list()

	a, b = router_coords
	# iterate over all the points to evaluate
	for (x, y) in points:
		# check if point is void
		if not is_void(building_matrix[x][y]):
			# check if point is covered by wall
			w_lower = min(a, x)
			w_upper = max(a, x)
			v_lower = min(b, y)
			v_upper = max(b, y)

			# generate all the points inside the smallest enclosing rectangle between
			# the point and the router
			cells_to_check = itertools.product(range(w_lower, w_upper + 1), range(v_lower, v_upper + 1))

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

	:param routers_placement:
	:param building_matrix:
	:param router_range:
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


def get_backbone_length(
		backbone_starting_point: tuple,
		routers_placement: np.array,
		building_matrix: np.array
) -> int:

	return 0

	G = nx.Graph()

	shape = building_matrix.shape


	# create a "full connectet" network with the same shape as the building matrix, exluding the void cells
	for i in range(shape[0]): #rows
		for j in range(shape[1]): #columns
			
			if (building_matrix[i][j] == "-"):
				continue # skip this iteration

			G.add_node((i, j), type=building_matrix[i][j])
			if (j != 0) and (building_matrix[i][j-1] != "-"): #not the first column and the left one is not void
				G.add_edge( (i, j-1) , (i  , j) , weight=1) # edge with the left one
			if (i != 0) and (building_matrix[i-1][j] != "-"): #not the first row and the above one is not void
				G.add_edge( (i-1, j ) , (i, j), weight=1) # edge with the above one
	
	router_coords = routers_placement.nonzero()

	router_coords = [(i, j) for (i, j) in zip(router_coords[0], router_coords[1]) ]

	router_coords.append(backbone_starting_point)

	print("calculating steiner")

	tree = nx.approximation.steiner_tree(G, terminal_nodes=router_coords)

	backbone = tree.size(weight="weight")
	print(backbone)

	return backbone


def compute_fitness(
		building_matrix: np.array,
		routers_placement: np.array,
		router_range: int,
		backbone_starting_point: tuple,
		router_cost: int,
		backbone_cost: int,
		budget: int
	) -> float:
	# compute number of cells covered by router signal
	number_covered_cells = get_number_covered_cells(routers_placement, building_matrix, router_range)

	# compute number of routers
	number_routers = get_number_routers(routers_placement)

	# compute cost of backbone connecting routers
	backbone_length = get_backbone_length(backbone_starting_point, routers_placement, building_matrix=building_matrix)

	return 1000*number_covered_cells + (budget - number_routers*router_cost - backbone_length*backbone_cost)


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


