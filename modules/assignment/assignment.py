class Assignment:
	def __init__(self, assignment, success):
		self.assignment = assignment
		self.success = success

	def __str__(self):
		return str(self.assignment)

	def __len__(self):
		return(len(self.assignment))

	def __iter__(self):
		return iter(self.assignment)

	def __next__(self):
		return next(self.assignment)

	def __getitem__(self, i):
		return self.assignment[i]


