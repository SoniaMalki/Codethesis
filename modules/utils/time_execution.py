class TimeExecution:
	def __init__(self, _time, _task_index=-1, _job_index=-1):
		self.time =_time
		self.job_index = _job_index
		self.task_index = _task_index
		if _task_index == -1 and _job_index==-1:
			self.executing = "Idle"
		else:
			self.executing = f"T{_task_index}J{_job_index}"

	def __repr__(self):
		return ("TimeExecution("
			f"_time={self.time}, "
			f"_job_index={self.job_index}, "
			f"_task_index={self.task_index}"
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


