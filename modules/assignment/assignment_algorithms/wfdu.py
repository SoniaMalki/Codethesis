class Wfdu:
    def __init__(self, taskset, number_of_cores):
        self.number_of_cores = number_of_cores
        self.taskset = taskset
        self.utilization = self.taskset.utilization
        self.core_utilizations = [0] * self.number_of_cores  

    def assign(self):
        taskset = sorted(range(len(self.utilization)), key=lambda k: self.utilization[k], reverse=True)
        print(taskset)
        task_in_core = [[] for _ in range(self.number_of_cores)]
        taskset_not_assigned = []

        for task_index in taskset:
            core_index = self.find_worst_fit_core(task_in_core, task_index)
            if core_index is not None:
                task_in_core[core_index].append(task_index)
                self.core_utilizations[core_index] += self.utilization[task_index]
                print(f"taskindex: {task_index} core ut: {self.core_utilizations}")
            else:
                taskset_not_assigned.append(task_index)

        # Vérifier s'il reste des tâches non assignées
        if not taskset_not_assigned:
            return task_in_core, 1
        else:
            return task_in_core, 0

    def find_worst_fit_core(self, task_in_core, task_index):
        """Trouve le cœur avec l'utilisation la moins élevée (pour WFDU) et vérifie la limite d'utilisation."""
        min_utilization = 1
        worst_fit_core = None
        for core_index in range(self.number_of_cores):
            # Vérifie si la tâche rentre dans la limite d'utilisation du cœur
            if self.core_utilizations[core_index] + self.utilization[task_index] <= 1 and self.core_utilizations[core_index] < min_utilization:
                min_utilization = self.core_utilizations[core_index]
                worst_fit_core = core_index
        return worst_fit_core
    
