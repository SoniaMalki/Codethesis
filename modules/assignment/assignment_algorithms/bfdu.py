import numpy


class Bfdu:
    def __init__(self, taskset, number_of_cores, sorting_criterion):
        self.number_of_cores = number_of_cores
        self.taskset = taskset
        self.sorting_criterion = sorting_criterion
        self.period = self.taskset.period
        self.deadline = self.taskset.deadline
        self.wcet = self.taskset.wcet
        self.interference = self.taskset.interference
        self.utilization = self.taskset.utilization
        self.sorting_criterion = sorting_criterion
        self.core_utilizations = [0] * self.number_of_cores

    def sort_task(self):
        # Trie les tâches selon certains critères
        taskset = list(range(len(self.taskset)))

        if self.sorting_criterion == "wcet_ascending":
            taskset = sorted(taskset, key=lambda k: self.wcet[k])
        elif self.sorting_criterion == "wcet_descending":
            taskset = sorted(taskset, key=lambda k: self.wcet[k], reverse=True)
        elif self.sorting_criterion == "period_ascending":
            taskset = sorted(taskset, key=lambda k: self.period[k])
        elif self.sorting_criterion == "period_descending":
            taskset = sorted(
                taskset, key=lambda k: self.period[k], reverse=True)
        elif self.sorting_criterion == "utilization_ascending":
            taskset = sorted(taskset, key=lambda k: self.utilization[k])
        elif self.sorting_criterion == "utilization_descending":
            taskset = sorted(
                taskset, key=lambda k: self.utilization[k], reverse=True)
        elif self.sorting_criterion == "execution_slack_ascending":
            taskset = sorted(
                taskset, key=lambda k: self.period[k] - self.wcet[k])
        elif self.sorting_criterion == "execution_slack_descending":
            taskset = sorted(
                taskset, key=lambda k: self.period[k] - self.wcet[k], reverse=True)
        elif self.sorting_criterion == "random_order":
            numpy.random.shuffle(taskset)
        else:
            print(
                f"Invalid sorting criterion: {self.sorting_criterion}. Returning tasks in random order.")
            numpy.random.shuffle(taskset)
        return taskset

    def assign(self):
        taskset = self.sort_task()
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
