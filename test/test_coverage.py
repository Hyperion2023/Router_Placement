import unittest
import numpy as np
import utils


class TestCoverage(unittest.TestCase):
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
		return building_matrix

	def test_no_router(self):
		building_matrix = TestCoverage.init_building_matrix()

		routers_placement = np.zeros(building_matrix.shape)

		router_range = 3

		self.assertEqual(
			utils.get_number_covered_cells(routers_placement, building_matrix, router_range),
			0
		)

	def test_single_router(self):
		building_matrix = TestCoverage.init_building_matrix()

		routers_placement = np.zeros(building_matrix.shape)
		routers_placement[3][7] = 1

		router_range = 3

		self.assertEqual(
			utils.get_number_covered_cells(routers_placement, building_matrix, router_range),
			27
		)

	def test_partially_overlapping_routers(self):
		building_matrix = TestCoverage.init_building_matrix()

		routers_placement = np.zeros(building_matrix.shape)
		routers_placement[3][7] = 1
		routers_placement[3][9] = 1

		router_range = 3

		self.assertEqual(
			utils.get_number_covered_cells(routers_placement, building_matrix, router_range),
			51
		)

	def test_fully_overlapping_routers(self):
		building_matrix= TestCoverage.init_building_matrix()

		routers_placement = np.zeros(building_matrix.shape)
		routers_placement[3][7] = 1
		routers_placement[6][6] = 1

		router_range = 3

		self.assertEqual(
			utils.get_number_covered_cells(routers_placement, building_matrix, router_range),
			27
		)
