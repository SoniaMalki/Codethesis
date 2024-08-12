import time


class Assignment:
    def __init__(self, assignment, success):
        self.assignment = assignment
        self.success = success
        self.computation_time = None

    def __repr__(self):
        return f"Assignment(assignment={self.assignment}, success={self.success})"

    def __str__(self):
        assignment_str = "Assignment: "
        assignment_str = "Succesfully assigned\n" if self.success else "Not successfully assigned\n"
        for core_index, tasks in enumerate(self.assignment):
            assignment_str += f"Core {core_index}: Tasks {tasks}\n"
        return assignment_str

    def __len__(self):
        return (len(self.assignment))

    def __iter__(self):
        return iter(self.assignment)

    def __next__(self):
        return next(self.assignment)

    def __getitem__(self, i):
        return self.assignment[i]

    def find_task_core(self, task_index):
        for core_index, sublist in enumerate(self.assignment):
            if task_index in sublist:
                return core_index
        return None

    def __eq__(self, other):
        if not isinstance(other, Assignment):
            return NotImplemented
        return self.assignment == other.assignment and self.success == other.success

    def add_performances(self, computation_time):
        self.computation_time = computation_time

    def items(self):
        return enumerate(self.assignment)
