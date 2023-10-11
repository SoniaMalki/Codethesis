from modules.experience import Experience
from modules.taskset_set_generation import TasksetSetGeneration

class ExperienceGeneration:
	def __init__(self, _number_of_cores, _list_of_max_utilization, _number_of_taskset, _period_min, _period_max, _granularity, _list_of_sorting_criterion, _list_of_number_of_task_in_taskset, 
				_list_of_interference_factor, _list_of_probability_factor,
				_list_of_method_of_period_generation, _random_generation):
		#parameters that stay the same
		self.number_of_cores = _number_of_cores
		self.number_of_taskset = _number_of_taskset
		self.period_min = _period_min
		self.period_max = _period_max
		self.granularity = _granularity
		self.list_of_sorting_criterion = _list_of_sorting_criterion

		#parameters that varies
		self.list_of_number_of_task_in_taskset = _list_of_number_of_task_in_taskset
		self.list_of_interference_factor = _list_of_interference_factor
		self.list_of_probability_factor = _list_of_probability_factor
		self.list_of_method_of_period_generation = _list_of_method_of_period_generation
		self.random_generation = _random_generation


		#parameters that are generated 
		self.list_of_max_utilization = _list_of_max_utilization
		if len(self.list_of_max_utilization) == 0:
			self.u_fix = self.number_of_cores - 1
			while (self.u_fix>0.1):
				self.list_of_max_utilization.append(self.u_fix)
				self.u_fix -= 0.2


	def __repr__(self):
		return ("ExperienceGeneration("
			f"_number_of_cores={self.number_of_cores}, "
			f"_number_of_taskset={self.number_of_taskset}, "
			f"_period_min={self.period_min}, "
			f"_period_max={self.period_max}, "
			f"_granularity={self.granularity}, "
			f"_list_of_sorting_criterion={self.list_of_sorting_criterion}, "
			f"_list_of_number_of_task_in_taskset={self.list_of_number_of_task_in_taskset}, "
			f"_list_of_interference_factor={self.list_of_interference_factor}, "
			f"_list_of_probability_factor={self.list_of_probability_factor}, "
			f"_list_of_method_of_period_generation={self.list_of_method_of_period_generation}, "
			f"_random_generation={self.random_generation}"
		")"
		)

	def generate_experience(self, output_bool=False):
		taskset_set_number = 0
		experience_lenght = int(len(self.list_of_number_of_task_in_taskset)*len(self.list_of_probability_factor)*len(self.list_of_interference_factor)*len(self.list_of_method_of_period_generation)*len(self.list_of_max_utilization))
		experience_generated = []


		for number_task_in_taskset in self.list_of_number_of_task_in_taskset:
			for interference_factor in self.list_of_interference_factor:
				for probability_factor in self.list_of_probability_factor:
					for method_of_period_generation in self.list_of_method_of_period_generation: 
						for max_utilization in self.list_of_max_utilization:
							if output_bool:
								print(f"Generating taskset set {taskset_set_number+1} of {experience_lenght}")
							experience_generated.append(TasksetSetGeneration(_taskset_set_number=taskset_set_number, _number_of_taskset=self.number_of_taskset, 
																			_period_min=self.period_min, _period_max=self.period_max, _granularity=self.granularity, 
																			_number_of_task_in_taskset=number_task_in_taskset, _interference_factor=interference_factor, 
																			_probability_factor=probability_factor, _method_of_period_generation=method_of_period_generation,
																			_random_generation=self.random_generation, _max_utilization=max_utilization
																			).generate_taskset_set())
							taskset_set_number += 1
		
		res = Experience(_number_of_cores=self.number_of_cores, _number_of_taskset=self.number_of_taskset, _period_min=self.period_min, _period_max=self.period_max, 
						_granularity=self.granularity, _list_of_sorting_criterion=self.list_of_sorting_criterion,
						_list_of_number_of_task_in_taskset=self.list_of_number_of_task_in_taskset, _list_of_interference_factor=self.list_of_interference_factor, 
						_list_of_probability_factor=self.list_of_probability_factor, _list_of_method_of_period_generation=self.list_of_method_of_period_generation,  
						_list_of_max_utilization=self.list_of_max_utilization, 
						_experience_lenght=experience_lenght, _taskset_set_list=experience_generated)
		return res