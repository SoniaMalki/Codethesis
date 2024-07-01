from modules.assignment.assignment import Assignment

class AssignmentSet:
    def __init__(self, assignment_id, taskset_id, assignment_method, citta_criteria, number_of_cores, assignment_list):
        self.assignment_id = assignment_id
        self.taskset_id = taskset_id
        self.assignment_method = assignment_method
        self.citta_criteria = citta_criteria
        self.number_of_cores = number_of_cores
        self.assignment_list = assignment_list

    def __repr__(self):
        return ("AssignmentSet("
                f"assignment_id={self.assignment_id}, "
                f"taskset_id={self.taskset_id}, "
                f"assignment_method={self.assignment_method}, "
                f"citta_criteria={self.citta_criteria}, "
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
        return self.taskset_list[i]

    def __str__(self):
        res = (f"Assignment id: {self.assignment_id}\n"
               f"Taskset ID: {self.taskset_id}\n"
               f"Assignment Method: {self.assignment_method}\n"
               f"CITTA criteria: {self.citta_criteria}\n"
               f"Core Number: {self.number_of_cores}\n"
               f"Assignment List: {self.assignment_list}\n"
               )

        return res