import random as rm
import utils
import numpy as np
from classes import Data
import random
from classes.PriorityDict import PriorityDict

class PrioritySolution:
	"""
	Soulution to the problem with a priprity ordered dictionary
	"""

	def __init__(self,
				 data : Data,
				 initial_state,
				 fitness_function,
				 verbose=True
				 ) -> None:

		self.data = data
		self.state = initial_state
		self.verbose = verbose
		self.fitness_function = fitness_function
		self.pri_dic = self.init_pri_dic(
			data.building_matrix,
			initial_state,
			data.router_range
		)

	@staticmethod
	def init_pri_dic(
			building_matrix: np.array,
			routers_placement: np.array,
			router_range: int
	) -> PriorityDict:
		"""
		Initialize the dictionary with the order on the values such that for each target cell of the matrix there is an entry in the dictionary
		"""
		# we want to add each cell of the grid and then update the coverage level
		pri_dict = PriorityDict()

		# add all the target coords to the priority dict
		target_coords = np.nonzero(building_matrix == ".")
		for (i, j) in zip(target_coords[0], target_coords[1]):
			pri_dict.add_element((i, j))

		# iterate the router and update the nearby cells
		router_coords = routers_placement.nonzero()
		for (i, j) in zip(router_coords[0], router_coords[1]):  # for each router

			# filter points covered by walls and void cells
			points_covered_by_router = utils.filter_non_target_points(
				building_matrix=building_matrix,
				router_coords=(i, j),
				points=utils.get_points_around_router(
					matrix=building_matrix,
					router_coords=(i, j),
					router_radius=router_range
				)
			)

			for (x, y) in points_covered_by_router:  # for each point (cell) covered by the router
				pri_dict.edit_element((x, y), 1)

		pri_dict.shuffle()
		pri_dict.order()

		return pri_dict

	@staticmethod
	def _update_neighbor(
			pri_dic: PriorityDict,
			building_matrix: np.array,
			router: tuple[int, int],
			router_range: int,
			delta: int
	):
		"""
		Given a router position and a delta value, update the coverage value of all the cells covered by the router with the delta, the walls are taken into account
		:param router: tuple of two int, the position of the router
		:param delta: int, the delta to apply to the near cells
		"""
		x, y = router

		points_covered_by_router = utils.filter_non_target_points(
			building_matrix=building_matrix,
			router_coords=(x, y),
			points=utils.get_points_around_router(
				matrix=building_matrix,
				router_coords=(x, y),
				router_radius=router_range
			)
		)
		for (x, y) in points_covered_by_router:  # for each point (cell) covered by the router
			pri_dic.edit_element((x, y), delta=delta)  # edit the point

	@staticmethod
	def _state_neighbor(
			pri_dic: PriorityDict,
			building_matrix: np.array,
			routers_placement: np.array,
			router_range: int,
			move_type: str
	) -> np.array:
		"""
		Given a move type, returns the new state in the solution space.
		If the move is 'add' a new router will be add in the less covered cell,
		if the move is 'remove' the nearest router to the most covered cell will be removed
		:param move_type: string, the type of move to perform, if it is not supported, a random move will be performed
		:returns: np.array, the new state
		"""

		supported_moves = ["add", "remove"]
		new_state = np.copy(routers_placement)

		if move_type not in supported_moves:
			move_type = random.choice(supported_moves)

		if move_type == "add":  # add one router
			while True:
				x, y = pri_dic.get_lower()  # the cell with less coverage
				if routers_placement[x][y] == 0:  # there is not another router in that cell
					new_state[x][y] = 1
					break

			# we have to update the near cells
			PrioritySolution._update_neighbor(
				pri_dic=pri_dic,
				building_matrix=building_matrix,
				router=(x, y),
				router_range=router_range,
				delta=+1
			)

		elif move_type == "remove":  # remove one router
			target = pri_dic.get_higer()  # the cell with most coverage
			to_remove = utils.get_nearest_router(cell=target, routers=routers_placement)
			x, y = to_remove
			new_state[x][y] = 0

			# we have to update the near cells
			PrioritySolution._update_neighbor(
				pri_dic=pri_dic,
				building_matrix=building_matrix,
				router=(x, y),
				router_range=router_range,
				delta=-1
			)
		else:
			pass

		return new_state


	def run(
			self,
			num_iterations : int,
			evaluation_delay: int
	) -> np.array:

		""""
		run the algorithm

		:param num_iterations: int, the number of iterations, note: if the solution is out of budget other iterations will be performed
		:param evaluation_delay: int, how often perform the fitness evaluation, the shuffling and reordering of the inner dict and the coverage evaluation, that are all computational intensive


		returns: the final configuration as a np.array
		"""

		rm.seed(a=None, version=2)

		if self.verbose:
			print(f"evaluation step")
		fitness, out_budget = self.fitness_function(self.state) # calculate fitness function and out of budget
		coverage = utils.get_number_covered_cells(self.state, self.data.matrix, self.data.router_range) / self.data.target_area #calculate coverage
		self.pri_dic.shuffle() #shuffle priority dict
		self.pri_dic.order() #ordinate priority dict
		if self.verbose:
			print(f"out_budget: {out_budget}, coverage: {coverage}")

		i=1
		while num_iterations > 0 or out_budget:
			if self.verbose:
				print(f"Iteration {i},", end=" ")

			if(not out_budget) and (coverage == 1.0):
				if self.verbose:
					print("end because full coverage")
				break

			if out_budget:
				if self.verbose:
					print(f"move: remove")
				self.state = self._state_neighbor(
					self.pri_dic,
					self.data.building_matrix,
					self.state,
					self.data.router_range,
					move_type="remove"
				)
			else:
				if self.verbose:
					print(f"move: add")
				self.state = self._state_neighbor(
					self.pri_dic,
					self.data.building_matrix,
					self.state,
					self.data.router_range,
					move_type="add"
				)

			if(i % evaluation_delay == 0) or out_budget:

				if self.verbose:
					print(f"evaluation step")
				fitness, out_budget = self.fitness_function(self.state) # calculate fitness function and out of budget
				coverage = utils.get_number_covered_cells(self.state, self.data.matrix, self.data.router_range) / self.data.target_area #calculate coverage
				self.pri_dic.shuffle() #shuffle priority dict
				self.pri_dic.order() #ordinate priority dict
				if self.verbose:
					print(f"out_budget: {out_budget}, coverage: {coverage}")

			i+=1
			num_iterations -= 1

		return np.copy(self.state)