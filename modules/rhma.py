import math
import logging
import numpy 
from time import sleep
from pulp import *

from modules.homogeneous_scheduler import HomogeneousScheduler
from modules.earliest_deadline_first import EarliestDeadlineFirst
from modules.deadline_monotonic import DeadlineMonotonic
from modules.schedule_plan import SchedulePlan
from modules.time_execution import TimeExecution

import matplotlib.pyplot as plt
import matplotlib.patches as patches

class Rhma:
	def __init__(self):
		self.algorithm_list = ["EDF", "EDFV1", "DM", "DMV1"]


	
	def schedule(self, busy_period_list, number_of_cores, assignment, hyperperiod):

		busy_period_list = busy_period_list[0:2] #TODO enlever to do
		print(busy_period_list)


		hyperperiod = busy_period_list[-1][-1] #TODO enlever to do TODO
		taskset = assignment["taskset"]
		core_assignment =  assignment["taskset_assignment"]
		rhma_schedule_plan = SchedulePlan(number_of_cores)

		#define parameters, I did it outside of the bp loop because it will be repettitive (attention it is not the same in the paper, it is inside)
		for task in taskset:
			task.create_jobs(0, hyperperiod)

		c_i_param = taskset.wcet
		d_i_param = taskset.deadline

		d_i_a_param = []
		for task in taskset: 
			temp = []
			for job in task:
				temp.append(job.absolute_deadline)
			d_i_a_param.append(temp)
		

		t_i_param = taskset.period
		i_i_param = taskset.interference
		n_i_param = [math.ceil(hyperperiod / taskset[i].period) for i in range(len(taskset))]

		o_i_j_param = []
		for task in taskset:
			temp = [0 for _ in range(len(core_assignment))]
			for k, core in enumerate(core_assignment):
				if task in core:
					temp[k] = 1
				else:
					temp[k] = 0
			o_i_j_param.append(temp)

		s_i_h_param = []
		for task in taskset:
			temp = []
			for busy_period in busy_period_list:
				temp_h = []
				for t in range(busy_period[0], busy_period[1]+1):
					if t % task.period == 0:
						temp_h.append(int(t//task.period))
				temp.append(temp_h)
			s_i_h_param.append(temp)

		r_i_a_h_param = []
		print(s_i_h_param)


		print("period", d_i_param)
		for i in range(len(s_i_h_param)):
			temp = []
			for h in range(len(s_i_h_param[i])):
				temp_h = []
				for a in s_i_h_param[i][h]:

					print([a*taskset[i].period, min((a+1)*taskset[i].period,busy_period_list[h][-1]+1)])

					temp_h.append([a*taskset[i].period, min((a+1)*taskset[i].period,busy_period_list[h][-1]+1)])

				temp.append(temp_h)
			r_i_a_h_param.append(temp)
		print(r_i_a_h_param)

		[
			[[0], [1, 2]], 
			[[0], [1]], 
			[[0], [1, 2]], 
			[[0], [1]]
		]



		t_h_param = [[t for t in range(busy_period[0], busy_period[1]+1)] for busy_period in busy_period_list]
		lcm = hyperperiod
		maxI = sum(taskset.interference)


		"""
		print("c_param", c_i_param)
		print("")
		print("d_param", d_i_param)
		print("")
		print("d_i_a_param", d_i_a_param)
		print("")
		print("t_param ",t_i_param)
		print("")
		print("i_param" ,i_i_param)
		print("")
		print("n_param", n_i_param)
		print("")
		print("o_i_j_param", o_i_j_param)
		print("")
		print("s_i_h_param", s_i_h_param)
		print("")
		print("r_i_a_h_param")
		for elem in r_i_a_h_param:
			print(elem)
		print("")
		print("t_h_param", t_h_param)
		print("")
		print("lcm", lcm)
		print("")
		print("maxI", maxI)
		print('////')
		"""

		#defining the decision variable
		for h, busy_period in enumerate(busy_period_list): 
			total_period = busy_period[1] - busy_period[0] + 1
			prob = LpProblem("MILPscheduling", LpMinimize)
			
			x = {}
			m = {}
			w = {}

			for i in range(len(s_i_h_param)):
				x[i] = {}
				m[i] = {}
				w[i] = {}
				for a_index, a in enumerate(s_i_h_param[i][h]):
					x[i][a] = {}
					m[i][a] = {}
					w_variable_name = f'w_{i}_{a}'
					w[i][a] = LpVariable(w_variable_name, 0, taskset[i].deadline, LpInteger)
					for j in range(number_of_cores):
						x[i][a][j] = {}
						for t in range(int(r_i_a_h_param[i][h][a_index][0]), int(r_i_a_h_param[i][h][a_index][1])):
							
							x_variable_name = f'x_{i}_{a}_{j}_{t}'
							x[i][a][j][t] = LpVariable(x_variable_name, 0, 1, LpBinary)
							#print("--------- check this")
							#print(r_i_a_h_param[i][h][a_index])
							

					for k in range(len(s_i_h_param)):
						m[i][a][k] = {}
						for b in s_i_h_param[k][h]:
							m_variable_name = f'm_{i}_{a}_{k}_{b}'
							m[i][a][k][b] = LpVariable(m_variable_name, 0, 1, LpBinary)
			

			#defining the constraint
			for i in range(len(s_i_h_param)):
				for a_index, a in enumerate(s_i_h_param[i][h]):
					for j in range(number_of_cores):
						for t in range(int(r_i_a_h_param[i][h][a_index][0]), int(r_i_a_h_param[i][h][a_index][1])):
							if o_i_j_param[i][j] == 0:
								prob += x[i][a][j][t] == 0 

			for i in range(len(s_i_h_param)):
				for a_index, a in enumerate(s_i_h_param[i][h]):
					for k in range(len(s_i_h_param)):
						for b_index, b in enumerate(s_i_h_param[k][h]):
							if k > i and not self.has_intersection(r_i_a_h_param[i][h][a_index], r_i_a_h_param[k][h][b_index]):
								prob += m[i][a][k][b] == 0  



			#pas trop sure
			for i in range(len(s_i_h_param)):
				for j in range(number_of_cores):
					left = lpSum(x[i][a][j][t] for a_index, a in enumerate(s_i_h_param[i][h]) for t in range(int(r_i_a_h_param[i][h][a_index][0]), int(r_i_a_h_param[i][h][a_index][1])))
					num_activations_S_i_h = len(s_i_h_param[i][h])
					right1 = num_activations_S_i_h * c_i_param[i] * o_i_j_param[i][j]
					for k in range(len(s_i_h_param)):
							if k != i and o_i_j_param[i][j] != o_i_j_param[k][j] and i_i_param[i] != 0 and i_i_param[k] != 0:
								num_activations_S_k_h = len(s_i_h_param[k][h])
								right2 = lpSum(m[i][a][k][b]*i_i_param[k]*o_i_j_param[i][j] for a in s_i_h_param[i][h] for b in s_i_h_param[k][h])
								
								# Add the constraint
								if num_activations_S_i_h > 0 and num_activations_S_k_h > 0:
									prob += left == right1 + right2

			for i in range(len(s_i_h_param)):
				for j in range(number_of_cores):
					for a_index, a in enumerate(s_i_h_param[i][h]):
						left = lpSum(x[i][a][j][t] for t in range(int(r_i_a_h_param[i][h][a_index][0]), int(r_i_a_h_param[i][h][a_index][1])))
						right1 = c_i_param[i] * o_i_j_param[i][j]
						right2 = lpSum(m[i][a][k][b] * i_i_param[k] * o_i_j_param[i][j] for k in range(len(s_i_h_param)) if k != i for b in s_i_h_param[k][h])
						# Add the constraint
						prob += left == right1 + right2

			for i in range(len(s_i_h_param)):
				for a_index, a in enumerate(s_i_h_param[i][h]):
						for t in t_h_param[h]:
							if t in x[i][a][j]:
								left_side = t * lpSum(x[i][a][j][t] for j in range(number_of_cores))
								right_side = d_i_a_param[i][a] - 1
								prob += left_side <= right_side


		

			for i in range(len(s_i_h_param)):
				for a_index, a in enumerate(s_i_h_param[i][h]):
					for k in range(len(s_i_h_param)):
						if k != i:
							for b in s_i_h_param[k][h]:
								for j in range(number_of_cores):
									for l in range(number_of_cores):
										if j != l:
											for t in t_h_param[h]:
												if t in x[i][a][j] and t in x[k][b][l]:
													left_side = m[i][a][k][b]
													right_side = x[i][a][j][t] + x[k][b][l][t]-1
													prob += left_side >= right_side

			for i in range(len(s_i_h_param)):
				for a_index, a in enumerate(s_i_h_param[i][h]):
					for k in range(len(s_i_h_param)):
						if k != i:
							for b_index, b in enumerate(s_i_h_param[k][h]):
								prob += m[i][a][k][b] == m[k][b][i][a]

			for i in range(len(s_i_h_param)):
				for a_index, a in enumerate(s_i_h_param[i][h]):
					for j in range(number_of_cores):
						for t in t_h_param[h]:
							if t in x[i][a][j]:
								left_side = w[i][a]
								right_side = t * x[i][a][j][t] - a * t_i_param[i] + 1 #pas sure pour t_i_param 
								prob += left_side >= right_side

			# Define the objective function
			maxI = sum(taskset.interference)  # You need to calculate maxI
			objective = (1 / maxI) * lpSum(m[i][a][k][b] for i in range(len(s_i_h_param))
										   for k in range(len(s_i_h_param))
										   for a in s_i_h_param[i][h]
										   for b in s_i_h_param[k][h]) + lpSum(w[i][a]) * lpSum(1/d_i_param[i] for i in range(len(s_i_h_param))
																				for a in range(len(s_i_h_param[i][h])))
			prob += objective

			# Solve the problem
			status = prob.solve()
			if LpStatus[status] == 'Optimal':
				print("Optimal yes")
			else:
				print(f"An optimal solution was not found! Status: {LpStatus[status]}")

			# Get the optimal solution and objective value
			optimal_solution = [(v.name, v.varValue) for v in prob.variables()]
			objective_value = value(prob.objective)
			
			# Print the results
			print("Optimal Solution:")
			for var, val in optimal_solution:
				print(f"{var} = {val}")
			print("Objective Value:", objective_value)

			print(optimal_solution)
			
			# Assuming optimal_solution contains the solution of your MILP problem

			x_values = {}

			for var_name, var_value in optimal_solution:
				# Check if the variable name starts with 'x_' to identify x variables
				if var_name.startswith('x_'):
					# Parse the variable name to get the indices
					_, i, a, j, t = var_name.split('_')
					i, a, j, t = int(i), int(a), int(j), int(t)
					# Store the value in the x_values dictionary
					x_values[(i, a, j, t)] = var_value

			schedule_plan_total = SchedulePlan(number_of_cores)
			time_executions = [[] for core in range(number_of_cores)]

			"""
			# Iterate through time steps
			for t in range(total_period):  # Adjust max_time accordingly
				for i in range(len(taskset)):  # Adjust num_tasks accordingly
					for a in s_i_h_param[i][h]:  # Adjust num_activations accordingly
						for j in range(number_of_cores):  # Adjust num_cores accordingly
							# Check if x[i][a][j][t] is 1
							if x_values.get((i, a, j, t), 0) == 1:
								print("TEST")
								# Create a TimeExecution object and append it to the list
								job_identifier = taskset[i].job_list[a].job_identifier
								time_execution = TimeExecution(_time=t, _task_index=i, _job_index=job_identifier)
								time_executions[j].append(time_execution)
			"""
			print(x_values)	
			for key in x_values:
				if x_values[key] == 1.0:
					time_execution = TimeExecution(_time=key[3], _task_index=key[0], _job_index=1)
					time_executions[key[2]].append(time_execution)
				

			for core_index, core in enumerate(time_executions):
				print(time_executions[core_index])
				schedule_plan_total.add_core_scheduling(core_index, core, "rhma")


			#print(repr(schedule_plan_total))

	

			schedule_plan_total.draw_task_schedule()

		return [], 1


	def has_intersection(self, interval1, interval2):
		# Check if the intervals have common elements
		if interval1[0] <= interval2[1] and interval2[0] < interval1[1]:
			return True
		else:
			return False




