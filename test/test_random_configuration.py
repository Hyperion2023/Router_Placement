import unittest
import numpy as np
import itertools
from utils import get_random_router_placement, get_number_routers


class TestRandomConfiguration(unittest.TestCase):
	@staticmethod
	def init_building_matrix():
		building_matrix = np.empty(shape=(7, 16), dtype=str)
		building_matrix.fill(".")
		building_matrix[0][1] = "#"
		building_matrix[1][1] = "#"
		building_matrix[2][1:5] = "#"
		building_matrix[3][4] = "#"
		building_matrix[4][4] = "#"
		building_matrix[5][4] = "#"
		building_matrix[6][4] = "#"
		building_matrix[1][8] = "#"
		building_matrix[2][8] = "#"
		building_matrix[5][8] = "#"
		building_matrix[6][8] = "#"
		for i in range(7):
			building_matrix[i][13] = "-"
			building_matrix[i][14] = "-"
			building_matrix[i][15] = "-"
		return building_matrix

	def test_empty_random_configuration(self):
		building_matrix = self.init_building_matrix()
		expected_routers = 0

		routers_placement = get_random_router_placement(building_matrix, expected_routers)

		# checking if the desidered number of routers have been generated
		self.assertEqual(get_number_routers(routers_placement), expected_routers)

		# checking if the wall/void constraints are satisfied
		n, m = building_matrix.shape
		is_wall = lambda c: c == "#"
		is_void = lambda c: c == "."
		contains_router = lambda c: c == 1

		for i, j in itertools.product(range(n), range(m)):
			cell = routers_placement[i][j]
			if contains_router(cell):
				self.assertTrue(not is_void(cell) and not is_wall(cell))

	def test_random_configuration(self):
		building_matrix = self.init_building_matrix()
		expected_routers = 4

		routers_placement = get_random_router_placement(building_matrix, expected_routers)

		# checking if the desidered number of routers have been generated
		self.assertEqual(get_number_routers(routers_placement), expected_routers)

		# checking if the wall/void constraints are satisfied
		n, m = building_matrix.shape
		is_wall = lambda c: c == "#"
		is_void = lambda c: c == "."
		contains_router = lambda c: c == 1

		for i, j in itertools.product(range(n), range(m)):
			cell = routers_placement[i][j]
			if contains_router(cell):
				self.assertTrue(not is_void(cell) and not is_wall(cell))


	def test_full_random_configuration(self):
		building_matrix = self.init_building_matrix()
		expected_routers = 77

		routers_placement = get_random_router_placement(building_matrix, expected_routers)

		# checking if the desidered number of routers have been generated
		self.assertEqual(get_number_routers(routers_placement), expected_routers)

		# checking if the wall/void constraints are satisfied
		n, m = building_matrix.shape
		is_wall = lambda c: c == "#"
		is_void = lambda c: c == "."
		contains_router = lambda c: c == 1

		for i, j in itertools.product(range(n), range(m)):
			cell = routers_placement[i][j]
			if contains_router(cell):
				self.assertTrue(not is_void(cell) and not is_wall(cell))
