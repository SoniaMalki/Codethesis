class Bfdu:
    def __init__(self, taskset, number_of_cores):
        self.number_of_cores = number_of_cores
        self.taskset = taskset
        self.utilization = self.taskset.utilization
        self.core_utilizations = [0] * self.number_of_cores  

    def assign(self):
        taskset = sorted(range(len(self.utilization)), key=lambda k: self.utilization[k], reverse=True)
        task_in_core = [[] for _ in range(self.number_of_cores)]
        taskset_not_assigned = []

        for task_index in taskset:
            core_index = self.find_best_fit_core(task_in_core, task_index)
            if core_index is not None:
                task_in_core[core_index].append(task_index)
                self.core_utilizations[core_index] += self.utilization[task_index]
            else:
                taskset_not_assigned.append(task_index)

        # Vérifier s'il reste des tâches non assignées
        if not taskset_not_assigned:
            return task_in_core, 1
        else:
            return task_in_core, 0

    def find_best_fit_core(self, task_in_core, task_index):
        """Trouve le cœur avec l'utilisation la plus élevée qui peut accueillir la nouvelle tâche."""
        best_fit_core = None
        min_remaining_utilization = float('inf')

        for core_index in range(self.number_of_cores):
            remaining_utilization = 1 - self.core_utilizations[core_index]

            if self.utilization[task_index] <= remaining_utilization and remaining_utilization < min_remaining_utilization:
                min_remaining_utilization = remaining_utilization
                best_fit_core = core_index

        return best_fit_core
