import numpy as np
import networkx as nx
import itertools


__all__ = [
	"get_backbone_length",
	"get_backbone_graph"
]


def get_chebyshev_distance(point1: tuple, point2: tuple):
	x1, y1 = point1
	x2, y2 = point2
	return max(abs(x1 - x2), abs(y1 - y2))


def get_backbone_graph(
		backbone_starting_point: tuple,
		routers_placement: np.array,
		backbone_unit_cost: int
) -> nx.Graph:
	"""
	Finds an approximation of the minimum sized graph connecting all the routers and the backbone starting point.

	:param backbone_starting_point: tuple of ints, the x,y coordinates of the backbone starting point inside the matrix
	:param routers_placement: array of arrays, the matrix describing the placement of routers inside the building
	:param backbone_unit_cost: int, cost of a single unit of backbone
	:return: the minimum sized graph that connects all the routers and the starting point
	"""
	# creating the equivalent grid graph for the routers placement
	n, m = routers_placement.shape
	g = nx.grid_2d_graph(n, m)

	# adding edges to the graph
	g.add_edges_from(
		[
			((x, y), (x + 1, y + 1))
			for x in range(n-1)
			for y in range(m-1)
		] +
		[
			((x + 1, y), (x, y + 1))
			for x in range(n-1)
			for y in range(m-1)
		],
		weight=backbone_unit_cost
	)

	# finding routers coordinates inside the matrix
	rows, columns = np.nonzero(routers_placement)
	routers_coords = [
		(x, y)
		for (x, y) in zip(rows, columns)
	]

	# setting the weight of each edge to the cost of a backbone unit
	for edge in g.edges():
		g.edges()[edge]["weight"] = backbone_unit_cost

	# for each router, searching the shortest path
	for router in routers_coords:
		# use a-star to found the shortest past
		path = nx.astar_path(
			g,
			backbone_starting_point,
			router,
			heuristic=get_chebyshev_distance,
			weight="weight"
		)
		# reducing the cost of found edges
		for path_edge in itertools.pairwise(path):
			g.edges()[path_edge]["weight"] = 0

	# cutting off the edges not used
	edges_to_remove = [edge for edge in g.edges() if g.edges()[edge]["weight"] != 0]
	g.remove_edges_from(edges_to_remove)

	# cutting off nodes with degree zero
	nodes_to_remove = [node for node in g.nodes() if g.degree[node] == 0]
	g.remove_nodes_from(nodes_to_remove)

	return g


def get_backbone_length(
		backbone_starting_point: tuple,
		routers_placement: np.array,
		backbone_unit_cost: int
) -> int:
	"""
	Returns the length of the minimum sized graph connecting all the routers and the backbone starting points

	:param backbone_starting_point: tuple of ints, the x,y coordinates of the backbone starting point inside the matrix
	:param routers_placement: array of arrays, the matrix describing the placement of routers inside the building
	:param backbone_unit_cost: int, cost of a single unit of the backbone
	:return: the len of the minimum sized graph that connects all the routers and the starting point
	"""
	return len(
		get_backbone_graph(
			backbone_starting_point,
			routers_placement,
			backbone_unit_cost
		)
	)
