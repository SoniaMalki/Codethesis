class BusyPeriod:
    def __init__(self):
        self.periods = []

    def add_period(self, scheduling):
        self.periods.append(scheduling)

    def __repr__(self):
        return f"BusyPeriod(periods={len(self.periods)})"

    def __str__(self):
        busy_period_str = "Busy Periods:\n"
        for index, scheduling in enumerate(self.periods):
            busy_period_str += (
                f"Period {index}: {scheduling.start_time} - {scheduling.end_time} "
                f"({scheduling.scheduler_name})\n"
            )
        return busy_period_str

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
