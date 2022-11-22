import matplotlib.pyplot as plt
import numpy as np


def plot_solution(
		building_matrix: np.array,
		routers_placement: np.array,
		backbone_nodes: list,
		backbone_starting_point: tuple
):
	# creating matrix for plot
	plot_matrix = np.zeros(shape=building_matrix.shape)

	n, m = building_matrix.shape
	for i in range(n):
		for j in range(m):
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
	x, y = backbone_starting_point
	plot_matrix[x][y] = 50

	plt.matshow(plot_matrix)
	plt.show()
