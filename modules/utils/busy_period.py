class BusyPeriod:
    def __init__(self):
        self.periods = []

    def add_period(self, scheduling):
        self.periods.append(scheduling)

    def __str__(self):
        return "\n".join([f"Busy Period from {scheduling.start_time} to {scheduling.end_time}, Schedule: {scheduling.scheduler_name}"
                          for scheduling in self.periods])
