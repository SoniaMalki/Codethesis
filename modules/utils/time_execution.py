class TimeExecution:
	def __init__(self, time, task_index=None, job_index=None):
		self.time = time
		self.job_index = job_index
		self.task_index = task_index
		if task_index == None and job_index==None:
			self.executing = "Idle"
		else:
			self.executing = f"T{task_index}J{job_index}"

	def __repr__(self):
		return ("TimeExecution("
			f"time={self.time}, "
			f"job_index={self.job_index}, "
			f"task_index={self.task_index}"
			")"
			)

	def __str__(self):
		return f"Time = {self.time}: {self.executing}"

	def is_idle(self):
		return self.executing == "Idle"


	def __sub__(self, other):
		return self.time - other.time

	def __add__(self, other):
		return self.time - other.time


