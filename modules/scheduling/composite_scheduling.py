import numpy
from modules.scheduling.scheduling import Scheduling


class CompositeScheduling:
    def __init__(self, scheduler_name):
        self.scheduler_name = scheduler_name
        self.success = True
        self.schedules = []

        self.computation_time = numpy.nan
        self.actual_utilization = numpy.nan
        self.theoretical_utilization = numpy.nan

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
        scheduler_name_same = self.scheduler_name == other.scheduler_name
        success_same = self.success == other.success
        schedule_same = self.schedules == other.schedules
        return (scheduler_name_same and
                success_same and
                schedule_same)

    def add_performances(self, computation_time, actual_utilization, theoretical_utilization):
        self.computation_time = computation_time
        self.actual_utilization = actual_utilization
        self.theoretical_utilization = theoretical_utilization
        self.overutilization = (
            (
                self.actual_utilization
                - self.theoretical_utilization
            )
            / self.theoretical_utilization
        ) * 100
