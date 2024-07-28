from modules.scheduling.scheduling import Scheduling


class CompositeScheduling:
    def __init__(self, scheduler_name):
        self.scheduler_name = scheduler_name
        self.success = True
        self.schedules = []

        self.computation_time = None
        self.actual_utilization = None
        self.theoritical_utilization = None

    def add_schedule(self, schedule):
        if isinstance(schedule, Scheduling):
            self.schedules.append(schedule)
            self.success = self.success & schedule.success
        else:
            raise TypeError("Only Scheduling objects can be added")

    def __repr__(self):
        return f"CompositeScheduling(scheduler_name={self.scheduler_name}, success={self.success}, schedules={len(self.schedules)})"

    def __str__(self, end_time=None):
        composite_str = f"Composite Scheduling scheduled by: {self.scheduler_name}\n"
        for schedule_index, schedule in enumerate(self.schedules):
            schedule_str = schedule.__str__(end_time=end_time)
            if schedule_str != '':
                composite_str += f'Schedule {schedule_index} by '
                composite_str += schedule_str + '\n'
        return composite_str

    def __len__(self):
        return len(self.schedules)

    def __getitem__(self, i):
        return self.schedules[i]

    def __eq__(self, other):
        if not isinstance(other, CompositeScheduling):
            return NotImplemented
        return (self.scheduler_name == other.scheduler_name and
                self.success == other.success and
                self.schedules == other.schedules)

    def add_performances(self, computation_time, actual_utilization, theoritical_utilization):
        self.computation_time = computation_time
        self.actual_utilization = actual_utilization
        self.theoritical_utilization = theoritical_utilization
