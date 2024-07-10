class Scheduling:
    def __init__(self, schedule, success, scheduler_name):
        self.schedule = schedule
        self.success = success
        self.scheduler_name = scheduler_name
        if self.schedule:
            self.start_time = min(
                time for core_schedule in self.schedule for time, *_ in core_schedule)
            self.end_time = max(
                time for core_schedule in self.schedule for time, *_ in core_schedule)

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
            len(f" T{task}J{job} ") if task is not None and job is not None else len(
                " Idle ")
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
        return (self.end_time-self.start_time)

    def __iter__(self):
        return iter(self.schedule)

    def __next__(self):
        return next(self.schedule)

    def __getitem__(self, i):
        return self.schedule[i]
