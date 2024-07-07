class Scheduling:
    def __init__(self, schedule, success, scheduler_name):
        self.schedule = schedule 
        self.success = success
        self.scheduler_name = scheduler_name
        if self.schedule:
            self.start_time = min(time for core_schedule in self.schedule for time, *_ in core_schedule)
            self.end_time = max(time for core_schedule in self.schedule for time, *_ in core_schedule)

    def __strs__(self):
        return str(self.schedule)
    
    def __str__(self, end_time=None):
        # Trouver les variables les plus grandes pour le temps (lignes) et core (colonnes)
        num_cores = len(self.schedule)
        
        # Limiter end_time au maximum disponible dans le schedule si end_time est spécifié
        if end_time is not None:
            end_time = min(end_time, self.end_time)
        else:
            end_time = self.end_time

        if end_time < self.start_time:
            return ''
        
        # Calculer la largeur des colonnes (pour l'alignement)
        max_time_width = len(str(end_time))
        time_column_width = len(f"Time = {end_time:{max_time_width}d} : ")
        max_core_header_width = len(f" Core {num_cores - 1} ")
        core_width = max(
            len(f" T{task}J{job} ") if task is not None and job is not None else len(" Idle ")
            for core_schedule in self.schedule for _, task, job in core_schedule
        )
        core_width = max(core_width, max_core_header_width)
        
        # Construction du header
        header_line = []
        for core in range(num_cores):
            header_line.append(f" {f'Core {core}':{core_width}}")
        header = f"{self.scheduler_name}:\n"
        header += " " * (time_column_width) + " | ".join(header_line)

        # Construction du tableau
        output = header + "\n"
        for t in range(self.start_time, end_time+1):
            line = f"Time = {t:{max_time_width}d} : "
            for i, core_schedule in enumerate(self.schedule):
                for time, task, job in core_schedule:
                    if time == t:
                        if task is not None and job is not None:
                            line += f" {f'T{task}J{job}':{core_width}} | "
                        else:
                            line += f" {'Idle':{core_width}} | "
                        break
                else:
                    line += f" {'Idle':{core_width}} | "
            output += line.rstrip(" | ") + "\n"

        return output

    def __len__(self):
        return(self.end_time-self.start_time)

    def __iter__(self):
        return iter(self.schedule)

    def __next__(self):
        return next(self.schedule)

    def __getitem__(self, i):
        return self.schedule[i]

    def get_time_units(self):
        """Returns a list of time units within this Scheduling object."""
        return list(range(self.start_time, self.end_time + 1))

    def get_activations(self, len_taskset):
        """Returns a list of lists, where each sublist contains the activation IDs for each task."""
        activations = [[] for _ in range(len_taskset)]
        for core_schedule in self.schedule:
            for time_unit, task_id, job_id in core_schedule:
                if task_id is not None and job_id not in activations[task_id]:
                    activations[task_id].append(job_id)
        return activations

    def get_execution_intervals(self, taskset):
        """Returns a list of dictionaries, where each dictionary represents a task 
        and maps activation IDs to lists of time units for that activation.
        """
        activations = self.get_activations(len_taskset=len(taskset))
        execution_intervals = [{} for _ in range(len(taskset))]
        for core_schedule in self.schedule:
            for time_unit, task_id, activation_id in core_schedule:
                if task_id is not None:
                    if activation_id in activations[task_id]:  # Check if this activation is relevant
                        if activation_id not in execution_intervals[task_id]:
                            execution_intervals[task_id][activation_id] = []
                        execution_intervals[task_id][activation_id].append(time_unit)
        return execution_intervals