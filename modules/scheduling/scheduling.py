class Scheduling:
    def __init__(self, success, schedule):
        self.success = success
        self.schedule = schedule  # This is the actual schedule data

    def __str__(self):
        return str(self.schedule)

    def __len__(self):
        return(len(self.schedule))

    def __iter__(self):
        return iter(self.schedule)

    def __next__(self):
        return next(self.schedule)

    def __getitem__(self, i):
        return self.schedule[i]