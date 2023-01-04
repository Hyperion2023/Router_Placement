import matplotlib.pyplot as plt
import numpy as np
import utils
from os.path import splitext, basename

def plot_solution(
		building_matrix: np.array,
		routers_placement: np.array,
		backbone_nodes: list = [],
		backbone_starting_point: tuple = (),
		ax=None
):
	"""
	Plots the building planimetry and routers placement

	:param building_matrix: array of arrays, the matrix describing the building (voids, targets, walls)
	:param routers_placement: array of arrays, the matrix describing the placement of the routers inside the building
	:param backbone_nodes: list of tuples, the list of nodes belonging to the backbone
	:param backbone_starting_point: tuple, the backbone initial starting point coordinates
	:param ax: axis on which place the plot
	"""
	# creating matrix for plot
	plot_matrix = np.zeros(shape=building_matrix.shape)

	n, m = building_matrix.shape
	for i in range(n):
		for j in range(m):
			# filling the matrix with voids/walls/targets
			if building_matrix[i][j] == "#":  # adding wall
				plot_matrix[i][j] = 10
			elif building_matrix[i][j] == "-":  # adding void
				plot_matrix[i][j] = 20

			# adding routers
			if routers_placement[i][j] == 1:
				plot_matrix[i][j] = 30

	# adding backbone
	for (i, j) in backbone_nodes:
		if plot_matrix[i][j] == 0 or plot_matrix[i][j] == 20:
			plot_matrix[i][j] = 40

	# adding backbone starting point
	if backbone_starting_point != ():
		x, y = backbone_starting_point
		plot_matrix[x][y] = 50

	ax.matshow(plot_matrix)


def plot_heatmap(
	building_matrix: np.array,
	routers_placement: np.array,
	router_radius: int,
	ax=None
):
	"""
	Plots a heatmap where lighter areas corresponds to cells covered by the routers

	:param building_matrix: array of arrays, the matrix describing the building (voids, targets, walls)
	:param routers_placement: array of arrays, the matrix describing the placement of the routers inside the building
	:param router_radius: int, the range of a router
	:param ax: axis on which place the plot
	"""
	# finding all the points covered by the routers
	points_covered_by_routers = []
	for router_coords in np.transpose(np.nonzero(routers_placement)):
		router_row, router_column = tuple(router_coords)

		covered_points = utils.filter_non_target_points(
			building_matrix,
			(router_row, router_column),
			utils.get_points_around_router(
				building_matrix,
				(router_row, router_column),
				router_radius
			)
		)
		for covered_point in covered_points:
			points_covered_by_routers.append(covered_point)

	# creating matrix for plot
	plot_matrix = np.zeros(shape=building_matrix.shape)

	n, m = building_matrix.shape
	for i in range(n):
		for j in range(m):
			# filling the matrix with voids/walls/targets
			if building_matrix[i][j] == "#":  # adding wall
				plot_matrix[i][j] = 10
			elif building_matrix[i][j] == "-":  # adding void
				plot_matrix[i][j] = 20

			# adding routers
			if routers_placement[i][j] == 1:
				plot_matrix[i][j] = 30

	# adding coverage points
	for (i, j) in points_covered_by_routers:
		if plot_matrix[i][j] == 0 or plot_matrix[i][j] == 20:
			plot_matrix[i][j] = 40

	ax.matshow(plot_matrix)

def plot_complete(
		building_matrix: np.array,
		routers_placement: np.array,
		router_radius: int,
		backbone_nodes: list = [],
		backbone_starting_point: tuple = (),
		filepath : str = None,
		algorithm : str = None
):
	"""
	Plots the building planimetry (and routers placement) alongside the covered area of the building

	:param building_matrix: array of arrays, the matrix describing the building (voids, targets, walls)
	:param routers_placement: array of arrays, the matrix describing the placement of the routers inside the building
	:param router_radius: int, the range of a router
	:param backbone_nodes: list of tuples, the list of nodes belonging to the backbone
	:param backbone_starting_point: tuple, the backbone initial starting point coordinates
	"""
	# creating figure with 2 subplots
	fig, (ax1, ax2) = plt.subplots(1, 2)
	fig.suptitle("Results")

	# plotting the solution
	plot_solution(
		building_matrix,
		routers_placement,
		backbone_nodes,
		backbone_starting_point,
		ax1
	)

	# plotting the coverage of the solution
	plot_heatmap(
		building_matrix,
		routers_placement,
		router_radius,
		ax2
	)

	if filepath and algorithm:
		plt.savefig(f"./{splitext(basename(filepath))[0]}_{algorithm}.png", format="png", dpi=500)

	plt.show()
