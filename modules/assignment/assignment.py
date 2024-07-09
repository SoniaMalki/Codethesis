import time


class Assignment:
    def __init__(self, assignment, success):
        self.assignment = assignment
        self.success = success

    def __str__(self):
        return str(self.assignment)

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
