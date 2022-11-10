import numpy as np
import utils

class State:
	def __init__(
			self,
			routers_placement: np.array
		):
		self.routers_placement = routers_placement

	@staticmethod
	def compute_fitness(
			building_matrix: np.array,
			routers_placement: np.array,
			configuration
		) -> float:
		router_range = configuration.router_range

		# compute number of cells covered by router signal
		covered_cells = utils.get_covered_cells(routers_placement, building_matrix, router_range)

		# compute number of routers
		number_routers = utils.get_number_routers(routers_placement)

		# compute cost of backbone connecting routers
		# maybe here add backbone as a router in the matrix
		backbone_starting_point = configuration.initial_backbone
		backbone_length = utils.get_backbone_length(backbone_starting_point, routers_placement)

		router_cost = configuration.router_cost
		backbone_cost = configuration.backbone_cost
		budget = configuration.budget

		return 1000*covered_cells + (budget - number_routers*router_cost - backbone_length*backbone_cost)

	def compute_fitness(
			self,
			building_matrix: np.array,
			configuration
		) -> float:
		return State.compute_fitness(building_matrix, self.routers_placement, configuration)
