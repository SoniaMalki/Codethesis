from modules.homogeneous_scheduler import HomogeneousScheduler
from modules.mixed_scheduler import MixedScheduler
class Scheduler:
	def __init__(self, _assignment, _scheduling_algorithm_name, _number_of_cores, _current_time=0):
		self.assignment = _assignment
		self.number_of_cores = _number_of_cores
		self.scheduling_algorithm_name = _scheduling_algorithm_name
		self.current_time = _current_time #TODO A VOIR 

		if self.scheduling_algorithm_name.lower() == "edf":
			self.scheduler = HomogeneousScheduler(self.assignment, self.scheduling_algorithm_name, self.number_of_cores, self.current_time)
		elif self.scheduling_algorithm_name.lower() == "dm":
			self.scheduler = HomogeneousScheduler(self.assignment, self.scheduling_algorithm_name, self.number_of_cores, self.current_time)
		elif self.scheduling_algorithm_name.lower() == "mixed":
			self.scheduler = MixedScheduler(self.assignment, self.scheduling_algorithm_name, self.number_of_cores, self.current_time)

	def schedule(self):
		schedule, successfully_scheduled = self.scheduler.schedule()
		return schedule, successfully_scheduled
