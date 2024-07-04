from modules.scheduling.scheduling import Scheduling

class CompositeScheduling:
    def __init__(self, scheduler_name):
        self.scheduler_name = scheduler_name
        self.success = True
        self.schedules = []

    def add_schedule(self, schedule):
        if isinstance(schedule, Scheduling):
            self.schedules.append(schedule)
            self.success = self.success & schedule.success
        else:
            raise TypeError("Only Scheduling objects can be added")

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

