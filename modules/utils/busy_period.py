class BusyPeriod:
    def __init__(self):
        self.periods = []

    def add_period(self, scheduling):
        self.periods.append(scheduling)

    def __str__(self):
        return "\n".join([f"Busy Period {index} from {scheduling.start_time} to {scheduling.end_time}, Schedule: {scheduling.scheduler_name}"
                          for index, scheduling in enumerate(self.periods)
                          ])

    def __len__(self):
        return (len(self.periods))

    def __iter__(self):
        return iter(self.periods)

    def __next__(self):
        return next(self.periods)

    def __getitem__(self, i):
        return self.periods[i]

    def __setitem__(self, i, value):
        self.periods[i] = value


def __eq__(self, other):
    if not isinstance(other, BusyPeriod):
        return NotImplemented
    return self.periods == other.periods
