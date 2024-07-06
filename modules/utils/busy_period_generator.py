import time
from modules.scheduling.scheduling import Scheduling
from modules.utils.busy_period import BusyPeriod


class BusyPeriodGenerator:
    @staticmethod
    def generate_monocore_busy_periods_timeslice(core_schedule):
        busy_periods = []
        start = core_schedule[0][0]

        for time_t, task, job in core_schedule:
            if task is None and job is None:  
                if start is not None: 
                    busy_periods.append((start, time_t))
                    start = None
            else:
                if start is None:  
                    start = time_t

        if start is not None:
            busy_periods.append((start, time_t))

        return busy_periods


    @staticmethod
    def generate_busy_periods_timeslice(monocore_busy_periods):
        busy_periods = []  
        if monocore_busy_periods:
            monocore_busy_periods.sort(key=lambda x: x[0])

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
    def generate_busy_periods_from_schedule(scheduling, busy_period_timeslices):
        busy_period_obj = BusyPeriod()
        for start, end in busy_period_timeslices:
            core_busy_periods = []
            for core_schedule in scheduling:
                core_busy_period_solo = [item for item in core_schedule if start <= item[0] <= end]
                if core_busy_period_solo:
                    core_busy_periods.append(core_busy_period_solo)

            core_schedule_obj = Scheduling(schedule=core_busy_periods, success = scheduling.success, scheduler_name=scheduling.scheduler_name)
            busy_period_obj.add_period(scheduling=core_schedule_obj)
        return busy_period_obj

    @staticmethod
    def generate_busy_periods(scheduling):
        core_schedules = scheduling.schedule
        monocore_busy_periods_timeslices = [busy_period 
                            for core_schedule in core_schedules 
                            for busy_period in BusyPeriodGenerator.generate_monocore_busy_periods_timeslice(core_schedule)]

        busy_period_timeslices = BusyPeriodGenerator.generate_busy_periods_timeslice(monocore_busy_periods_timeslices)
        busy_period = BusyPeriodGenerator.generate_busy_periods_from_schedule(scheduling=scheduling, busy_period_timeslices=busy_period_timeslices)
        return busy_period

    def generate_shorter_scheduling(scheduling):
        busy_period = BusyPeriodGenerator.generate_busy_periods(scheduling)
        scheduling = busy_period[0]
        return scheduling
    
