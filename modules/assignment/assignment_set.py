from modules.assignment.assignment import Assignment


class AssignmentSet:
    def __init__(self, assignment_id, taskset_id, assignment_method, sorting_criterion, number_of_cores, assignment_list):
        self.assignment_id = assignment_id
        self.taskset_id = taskset_id
        self.assignment_method = assignment_method
        self.sorting_criterion = sorting_criterion
        self.number_of_cores = number_of_cores
        self.assignment_list = assignment_list

    def __repr__(self):
        return ("AssignmentSet("
                f"assignment_id={self.assignment_id}, "
                f"taskset_id={self.taskset_id}, "
                f"assignment_method={self.assignment_method}, "
                f"sorting_criterion={self.sorting_criterion}, "
                f"number_of_cores={self.number_of_cores}, "
                f"assignment_list={self.assignment_list}, "
                ")"
                )

    def __len__(self):
        return len(self.assignment_list)

    def __iter__(self):
        return iter(self.assignment_list)

    def __next__(self):
        return next(self.assignment_list)

    def __getitem__(self, i):
        return self.assignment_list[i]

    def __str__(self):
        res = (f"Assignment id: {self.assignment_id}\n"
               f"Taskset ID: {self.taskset_id}\n"
               f"Assignment Method: {self.assignment_method}\n"
               f"CITTA criteria: {self.sorting_criterion}\n"
               f"Core Number: {self.number_of_cores}\n"
               f"Assignment List: {self.assignment_list}\n"
               )

        return res

    def __eq__(self, other):
        if not isinstance(other, AssignmentSet):
            return NotImplemented
        return (self.assignment_id == other.assignment_id and
                self.taskset_id == other.taskset_id and
                self.assignment_method == other.assignment_method and
                self.sorting_criterion == other.sorting_criterion and
                self.number_of_cores == other.number_of_cores and
                self.assignment_list == other.assignment_list)
