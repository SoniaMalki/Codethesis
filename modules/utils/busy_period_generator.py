class BusyPeriodGenerator:
    @staticmethod
    def detect_monocore_busy_periods(core_schedule):
        busy_periods = []
        start = None

        for time, task, job in core_schedule:
            if task is None and job is None:  
                if start is not None: 
                    busy_periods.append((start, time))
                    start = None
            else:
                if start is None:  
                    start = time
        
        if start is not None:
            busy_periods.append((start, time))

        return busy_periods


    @staticmethod
    def detect_busy_periods(monocore_busy_periods):
        busy_periods = []  
        if monocore_busy_periods:
            monocore_busy_periods.sort(key=lambda x: x[1])

            current_start, current_end = monocore_busy_periods[0]
            for start, end in monocore_busy_periods[1:]:
                if current_end >= start:  
                    current_end = max(current_end, end)
                else:
                    busy_periods.append((current_start, current_end))
                    current_start, current_end = start, end
            
            # Add the last period
            busy_periods.append((current_start, current_end))

        return busy_periods


    @staticmethod
    def generate_busy_periods(scheduling):
        core_schedules = scheduling.schedule

        monocore_busy_periods = [busy_period 
                            for core_schedule in core_schedules 
                            for busy_period in BusyPeriodGenerator.detect_monocore_busy_periods(core_schedule)]

        busy_period = BusyPeriodGenerator.detect_busy_periods(monocore_busy_periods)

        return busy_period


   