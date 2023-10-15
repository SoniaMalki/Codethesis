import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches


class SchedulePlan:
	def __init__(self, number_of_cores):
		self.schedule = {}
		for i in range(number_of_cores):
			self.schedule[i] = []

	def add_core_scheduling(self, core_index, schedule_plan, schedule_algorithm_name):
		self.schedule[core_index] = [{"schedule_algorithm_name": schedule_algorithm_name, "schedule_plan":schedule_plan}]


	def draw_task_schedule(self):
		"""
		Dessine un diagramme gradué pour chaque tâche sur chaque cœur.
		"""
		# Regrouper les tâches par cœur et par identifiant de tâche


		task_schedule = []
		for key in self.schedule.keys():
			schedule = self.schedule[key]
			core_index = key + 1
			for a in schedule:
				for timeExecution in a['schedule_plan']:
					task_schedule.append((timeExecution.task_index + 1, timeExecution.time, 1, core_index))


		total_time = 15  # Temps total pour l'axe des x

		grouped_tasks = {}
		for task in task_schedule:
			key = (task[3], task[0])  # core, task_name
			if key not in grouped_tasks:
				grouped_tasks[key] = []  # Créez une nouvelle liste si la clé n'existe pas
			grouped_tasks[key].append(task)

		# Compter le nombre total de graphiques nécessaires
		total_plots = len(grouped_tasks)

		# Créer une figure et des axes
		fig, axs = plt.subplots(total_plots, 1, figsize=(10, total_plots * 2), squeeze=False)

		# Hauteur de chaque barre (tâche)
		height = 1

		# Espacement entre les barres
		pad = 0.3

		# Dessiner chaque groupe de tâches dans son propre graphique
		for plot_counter, ((core, task_name), tasks) in enumerate(grouped_tasks.items()):
			for task in tasks:
				_, start, duration, _ = task
				rect = patches.Rectangle((start, pad), duration, height - 2 * pad, 
										 linewidth=1, edgecolor='black', facecolor='skyblue')
				axs[plot_counter, 0].add_patch(rect)
				axs[plot_counter, 0].text(start + 0.1, height / 2, f'Task {task_name}', va='center', fontsize=8, color='black')

			# Configurer les axes et les labels
			axs[plot_counter, 0].set_xlim(0, total_time)
			axs[plot_counter, 0].set_ylim(0, height)
			axs[plot_counter, 0].set_yticks([])
			axs[plot_counter, 0].set_title(f'Core {core} - Task {task_name}')
			axs[plot_counter, 0].grid(True)

		plt.xlabel('Time')
		plt.tight_layout()
		plt.show()


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