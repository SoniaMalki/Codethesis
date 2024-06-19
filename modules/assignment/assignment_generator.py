from modules.assignment_generation.citta import Citta
from modules.assignment_generation.wfdu import Wfdu
from modules.assignment_generation.ffdu import Ffdu

import time
class TasksetAssignment:
	def __init__(self, _assignment_algorithm, _number_of_cores):
		self.assignment_algorithm = _assignment_algorithm
		self.number_of_cores = _number_of_cores
		
	def assign(self, taskset, sorting_criterion):
		if self.assignment_algorithm.lower() == "citta":
			assigned_cores, successfully_assigned = self.citta_assignment(taskset, self.number_of_cores, sorting_criterion)
		elif  self.assignment_algorithm.lower() == "wmin":
			assigned_cores, successfully_assigned = self.wmin_assignment(taskset, self.number_of_cores, sorting_criterion)
		elif self.assignment_algorithm.lower() == "wfdu":
			assigned_cores, successfully_assigned = self.wfdu_assignment(taskset, self.number_of_cores, sorting_criterion)
		elif self.assignment_algorithm.lower() == "ffdu":
			assigned_cores, successfully_assigned = self.ffdu_assignment(taskset, self.number_of_cores, sorting_criterion)
		elif self.assignment_algorithm.lower() == "custom":
			assigned_cores, successfully_assigned = [[0,1],[2,3]], 1


		task_assignment_list = [[] for core in range(self.number_of_cores)]
		if successfully_assigned:
			for core_index, core in enumerate(assigned_cores):
				for task_index in core:
					task_assignment_list[core_index].append(taskset[task_index])

		# task_assignment_list=[]
		# if successfully_assigned: #else return empty list
		# 	for core_index, core in enumerate(assigned_cores):
		# 		for task_index in core:
		# 			task_assignment = TaskAssignment(_task=taskset[task_index], _assigned_core=core_index) #revoir cet objet
		# 			task_assignment_list.append(task_assignment)
		return task_assignment_list, successfully_assigned

	def citta_assignment(self, taskset, num_cores, sort_crit):
		citta_instance = Citta(taskset, num_cores, sort_crit) 
		assigned_cores, tra ,successfully_assigned = citta_instance.assign()
		return assigned_cores, successfully_assigned

	def wfdu_assignment(self, taskset, num_cores, sort_crit):
		wfdu_instance = Wfdu(taskset, num_cores, sort_crit) 
		assigned_cores, tra ,successfully_assigned = wfdu_instance.assign()
		return assigned_cores, successfully_assigned

	def ffdu_assignment(self, taskset, num_cores, sort_crit):
		ffdu_instance = Ffdu(taskset, num_cores, sort_crit) 
		assigned_cores, tra ,successfully_assigned = ffdu_instance.assign()
		return assigned_cores, successfully_assigned

	def wmin_assignment(self, taskset):
		wmin_instance = Wmin()
		assigned_cores = wmin_instance.assign(taskset)
		return assigned_cores

