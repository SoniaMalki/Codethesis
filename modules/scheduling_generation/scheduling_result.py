class SchedulingResult:
	def __init__(self):
		self.schedule = []

	def add_result(self, successfully_scheduled, schedule, assignment):
		res = {"successfully_scheduled":successfully_scheduled, "schedule":schedule, "assignment":assignment}
		self.schedule.append(res)

	def __str__(self):
		return str(self.schedule)

	def __len__(self):
		return(len(self.schedule))

	def __iter__(self):
		return iter(self.schedule)

	def __next__(self):
		return next(self.schedule)

	def __getitem__(self, i):
		return self.schedule[i]

