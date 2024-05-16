class AssignmentResult:
	def __init__(self):
		self.assignment = []


	def add_result(self, taskset_assignment_success, taskset_assignment, taskset):
		res = {"taskset_assignment_success":taskset_assignment_success, "taskset_assignment":taskset_assignment, "taskset":taskset}
		self.assignment.append(res)

	def __str__(self):
		return str(self.assignment)

	def show_experiment_result(experiment_index):
		pass #faire un print

	def __len__(self):
		return(len(self.assignment))

	def __iter__(self):
		return iter(self.assignment)

	def __next__(self):
		return next(self.assignment)

	def __getitem__(self, i):
		return self.assignment[i]


