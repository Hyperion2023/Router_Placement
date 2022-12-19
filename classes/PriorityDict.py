from .Cell import Cell
import random
import sys

class PriorityDict:
	def __init__(self) -> None:
		self.inner_dict = {}
		self.inner_list = []
		self.approximate_higer_index = 0
		self.approximate_lower_index = len(self.inner_list) - 1
		self.edits_since_ordered = sys.maxsize
		pass

	def add_element(self, position: tuple[int, int]):
		new_cell = Cell(position, coverage_level=0)
		self.inner_dict[position] = new_cell
		self.inner_list.append(new_cell)

	def edit_element(self, position: tuple[int, int], delta):
		cell = self.inner_dict[position]
		cell.coverage_level += delta

	def order(self):
		self.inner_list.sort(key=lambda x: x.coverage_level, reverse=True)
		self.approximate_higer_index = 0
		self.approximate_lower_index = len(self.inner_list) - 1
		self.edits_since_ordered = 0

	def get_higer(self):
		if self.edits_since_ordered >= len(self.inner_list) / 2:  # euristic to reorder the list
			self.order()

		cell = self.inner_list[self.approximate_higer_index]
		self.approximate_higer_index += 1
		return cell.position

	def get_lower(self):
		if self.edits_since_ordered >= len(self.inner_list) / 2:  # euristic to reorder the list
			self.order()

		cell = self.inner_list[self.approximate_lower_index]
		self.approximate_lower_index -= 1
		return cell.position

	def shuffle(self):
		random.shuffle(self.inner_list)