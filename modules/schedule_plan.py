import time

class SchedulePlan:
	def __init__(self, number_of_cores):
		self.schedule = {}
		for i in range(number_of_cores):
			self.schedule[i] = []

	def add_core_scheduling(self, core_index, schedule_plan, schedule_algorithm_name):
		self.schedule[core_index] = [{"schedule_algorithm_name": schedule_algorithm_name, "schedule_plan":schedule_plan}]

	def __add__(self, other):
		for core_index in  range(len(other)):
			self.schedule[core_index].extend(other[core_index])

	def __str__(self):
		total_res = []
		for core_index in self.schedule.keys():
			res = []
			for period_index in range(len(self.schedule[core_index])):
				res.append(f"Algorithm : {self.schedule[core_index][period_index]['schedule_algorithm_name']}")
				res.append(f"Core {core_index}") 
				for timef in self.schedule[core_index][period_index]["schedule_plan"]:
					res.append(str(timef))
				res.append("\n")
			total_res.append(res)

		string = self.print_matrix_with_aligned_columns(total_res)
		return string

	def print_matrix_with_aligned_columns(self, matrix):
		rows = len(matrix)
		cols = len(matrix[0])

		col_widths = [max(len(str(matrix[j][i])) for i in range(cols)) for j in range(rows)] 
		string = ""

		for j in range(cols):
			for i in range(rows):
				if matrix[i][j] != "\n":
					cell_value = str(matrix[i][j]).ljust(col_widths[i])
					string += cell_value
					if i < rows - 1:
						string += " | "
				else:
					string += ""
			if j < cols-1:
				string += "\n"
				
		return string

	def __len__(self):
		return(len(self.schedule))

	def __iter__(self):
		return iter(self.schedule)

	def __next__(self):
		return next(self.schedule)

	def __getitem__(self, i):
		return self.schedule[i]