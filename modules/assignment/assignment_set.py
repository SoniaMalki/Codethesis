from modules.assignment.assignment import Assignment


class AssignmentSet:
    def __init__(self, assignment_id, taskset_id, assignment_method, sorting_criterion, number_of_cores, assignment_list):
        self.assignment_id = assignment_id
        self.taskset_id = taskset_id
        self.assignment_method = assignment_method
        self.sorting_criterion = sorting_criterion
        self.number_of_cores = number_of_cores
        self.assignment_list = assignment_list

        self.mean_success = self.calculate_mean_success()
        self.mean_computation_time = self.calculate_mean_computation_time()

    def __repr__(self):
        return (
            f"AssignmentSet(assignment_id={self.assignment_id}, taskset_id={self.taskset_id}, "
            f"assignment_method={self.assignment_method}, sorting_criterion={self.sorting_criterion}, "
            f"number_of_cores={self.number_of_cores}, assignment_list={len(self.assignment_list)})"
        )

    def __str__(self):
        assignment_str = "\n".join(repr(assignment)
                                   for assignment in self.assignment_list)
        return (
            f"Assignment ID: {self.assignment_id}\n"
            f"Taskset ID: {self.taskset_id}\n"
            f"Method: {self.assignment_method}\n"
            f"Criterion: {self.sorting_criterion}\n"
            f"Cores: {self.number_of_cores}\n"
            f"Assignments:\n{assignment_str}"
        )

    def __len__(self):
        return len(self.assignment_list)

    def __iter__(self):
        return iter(self.assignment_list)

    def __next__(self):
        return next(self.assignment_list)

    def __getitem__(self, i):
        return self.assignment_list[i]

    def __eq__(self, other):
        if not isinstance(other, AssignmentSet):
            return NotImplemented
        return (self.assignment_id == other.assignment_id and
                self.taskset_id == other.taskset_id and
                self.assignment_method == other.assignment_method and
                self.sorting_criterion == other.sorting_criterion and
                self.number_of_cores == other.number_of_cores and
                self.assignment_list == other.assignment_list)
    

    def calculate_mean_success(self):
        return sum(assignment.success for assignment in self.assignment_list) / len(self.assignment_list)

    def calculate_mean_computation_time(self):
        return sum(assignment.computation_time for assignment in self.assignment_list) / len(self.assignment_list)
