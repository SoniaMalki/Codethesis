class Schedule:
    def __init__(self, success, schedule):
        self.success = success
        self.schedule = schedule  # This is the actual schedule data

    def __str__(self):
        # You can format the schedule data nicely here
        # For example, you can print it in a table format
        return str(self.schedule)  # Or just return the raw schedule data