import numpy as np
import itertools

__all__ = [
	"get_number_routers",
	"get_number_routers",
	"get_backbone_length"
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
	coords = []
	for i in np.arange(start=-router_radius, stop=router_radius+1, step=1):
		for j in np.arange(start=-router_radius, stop=router_radius + 1, step=1):
			# check if location is within boundary
			if 0 <= r + i < m and 0 <= c + j < n:
				coords.append((r + i, c + j))
	return coords


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


def get_covered_cells(
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
		routers_placement: np.array
) -> int:
	return 0



