import matplotlib.pyplot as plt
import numpy as np
import utils
import pandas as pd
import seaborn as sns


def plot_solution(
		building_matrix: np.array,
		routers_placement: np.array,
		backbone_nodes: list = [],
		backbone_starting_point: tuple = (),
		ax=None
):
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

	covered_points_df = pd.DataFrame(
		[
			[point_x, point_y]
			for point_x, point_y in points_covered_by_routers
		],
		columns=["row", "column"]
	)
	plot_solution(
		building_matrix,
		routers_placement,
		ax=ax
	)
	sns.kdeplot(
		data=covered_points_df,
		x="column",
		y="row",
		cmap="inferno",
		fill=True,
		thresh=0.7,
		alpha=0.75,
		ax=ax
	)


def plot_complete(
		building_matrix: np.array,
		routers_placement: np.array,
		router_radius: int,
		backbone_nodes: list = [],
		backbone_starting_point: tuple = (),
):
	fig, (ax1, ax2) = plt.subplots(1, 2)
	fig.suptitle('Horizontally stacked subplots')
	plot_solution(
		building_matrix,
		routers_placement,
		backbone_nodes,
		backbone_starting_point,
		ax1
	)
	plot_heatmap(
		building_matrix,
		routers_placement,
		router_radius,
		ax2
	)
	plt.show()
