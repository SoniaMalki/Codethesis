import multiprocessing
import psutil
from time import perf_counter
import numpy
import time

from modules.scheduling.scheduling import Scheduling
from modules.scheduling.composite_scheduling import CompositeScheduling
from modules.scheduling.scheduling_set import SchedulingSet
from modules.scheduling.scheduling_algorithms.combined_scheduler import CombinedScheduler
from modules.scheduling.scheduling_algorithms.rhma import Rhma

from modules.scheduling.scheduling_algorithms.earliest_deadline_first import EarliestDeadlineFirst
from modules.scheduling.scheduling_algorithms.earliest_deadline_first_variant1 import EarliestDeadlineFirstVariant1
from modules.scheduling.scheduling_algorithms.earliest_deadline_first_variant2 import EarliestDeadlineFirstVariant2
from modules.scheduling.scheduling_algorithms.deadline_monotonic import DeadlineMonotonic
from modules.scheduling.scheduling_algorithms.deadline_monotonic_variant1 import DeadlineMonotonicVariant1
from modules.scheduling.scheduling_algorithms.deadline_monotonic_variant2 import DeadlineMonotonicVariant2
from modules.utils.busy_period import BusyPeriod


class MemoryLimitExceededException(Exception):
    pass


class SchedulingGenerator:
    def __init__(self, taskset_set_obj, assignment_set_obj, taskset_id, assignment_id, scheduling_id, scheduling_algorithm, scheduling_options):
        print("Initializing SchedulingGenerator")
        self.taskset_set = taskset_set_obj
        self.assignment_set = assignment_set_obj
        self.taskset_id = taskset_id
        self.assignment_id = assignment_id
        self.scheduling_id = scheduling_id
        self.scheduling_algorithm = scheduling_algorithm
        self.scheduling_options = scheduling_options
        self.number_of_cores = self.assignment_set.number_of_cores
        self.threads = self.scheduling_options.get("threads", 1)
        self.memory_threshold_theory = 8 * self.threads
        self.memory_threshold_gb = 0.95 * self.memory_threshold_theory
        self.scheduling_algorithms = [
            "EarliestDeadlineFirst",
            "EarliestDeadlineFirstVariant1",
            "EarliestDeadlineFirstVariant2",
            "DeadlineMonotonic",
            "DeadlineMonotonicVariant1",
            "DeadlineMonotonicVariant2"
        ]

        self.composite_scheduling_algorithms = [
            "CombinedScheduler",
            "Rhma"
        ]
        print(
            f"SchedulingGenerator initialized with algorithm: {self.scheduling_algorithm}")

    def monitor_memory(self, process):
        """Moniteur qui vérifie l'utilisation de la mémoire. Si l'utilisation dépasse le seuil spécifié, interrompt le processus donné."""
        psutil_process = psutil.Process(process.pid)
        while process.is_alive():
            memory_info = psutil_process.memory_info()
            memory_usage = memory_info.rss / (1024 ** 3)
            if memory_usage > self.memory_threshold_gb:
                print(
                    f"Utilisation excessive de la mémoire détectée ({memory_usage:.2f}GB/{self.memory_threshold_theory}GB). Interruption du processus de scheduling.")
                process.terminate()
                raise MemoryLimitExceededException("Memory limit exceeded")
            time.sleep(0.5)

    def run_scheduler(self, scheduler, return_dict):
        """Fonction pour exécuter le scheduler dans un processus séparé et retourner le résultat via un dictionnaire géré par Manager."""
        try:
            schedule_tuple = scheduler.schedule()
            schedule = schedule_tuple[0]
            success = schedule_tuple[1]
            actual_utilization = scheduler.actual_utilization
        except MemoryError:
            print("Mémoire insuffisante. Arrêt du scheduling.")
            print("Traceback MemoryError")
            schedule = None
            success = 0
            actual_utilization = numpy.nan

        return_dict["schedule"] = schedule
        return_dict["success"] = success
        return_dict["actual_utilization"] = actual_utilization

    def run_scheduler_composite(self, scheduler, return_dict):
        """Fonction pour exécuter le scheduler dans un processus séparé et retourner le résultat via un dictionnaire géré par Manager."""
        try:
            schedule = scheduler.schedule()
            actual_utilization = scheduler.actual_utilization

        except MemoryError:
            print("Mémoire insuffisante. Arrêt du scheduling.")
            print("Traceback MemoryError")
            schedule = None
            actual_utilization = [numpy.nan]

        return_dict["busy_periods"] = schedule
        return_dict["actual_utilization"] = actual_utilization

    def generate_scheduling_set(self):
        """Generates schedulings for each assignment within the TasksetSet."""
        print("Generating scheduling set")
        scheduling_list = []  # Store schedulings for each assignment

        # Determine the scheduling algorithm once
        if self.scheduling_algorithm not in self.scheduling_algorithms and self.scheduling_algorithm not in self.composite_scheduling_algorithms:
            print(
                f"Invalid scheduling algorithm: {self.scheduling_algorithm}. Returning None.")
            return None

        scheduler_class = globals()[self.scheduling_algorithm]

        if self.scheduling_algorithm in self.scheduling_algorithms:
            scheduling_function = self.generate_scheduling
        else:
            scheduling_function = self.generate_composite_scheduling

        # Apply the selected scheduling function to all taskset assignments
        for taskset, assignment in zip(self.taskset_set, self.assignment_set):
            if assignment.success:
                print(
                    f"Generating scheduling for taskset: {self.taskset_id} and assignment: {self.assignment_id}")
                scheduling = scheduling_function(
                    taskset=taskset, assignment=assignment, scheduler_class=scheduler_class, start_time=1, end_time=None)

                scheduling_list.append(scheduling)
                print(
                    f"Scheduling generated for taskset: {self.taskset_id} and assignment: {self.assignment_id}")

        scheduling = SchedulingSet(scheduling_id=self.scheduling_id, taskset_id=self.taskset_id, assignment_id=self.assignment_id,
                                   scheduling_algorithm=self.scheduling_algorithm, scheduling_options=self.scheduling_options, scheduling_list=scheduling_list)
        print("Scheduling set generation completed")
        return scheduling

    def generate_scheduling(self, taskset, assignment, scheduler_class, start_time=1, end_time=None):
        print(f"Generating scheduling using {scheduler_class.__name__}")
        start_time_compute = perf_counter()
        scheduler = scheduler_class(
            taskset=taskset,
            assignment=assignment,
            number_of_cores=self.number_of_cores,
            scheduling_options=self.scheduling_options,
            start_time=start_time,
            end_time=end_time,
        )

        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        scheduling_process = multiprocessing.Process(
            target=self.run_scheduler, args=(scheduler, return_dict))
        scheduling_process.start()

        memory_exceeded = False

        try:
            self.monitor_memory(scheduling_process)
        except MemoryLimitExceededException:
            print("Memory limit exceeded during scheduling. Stopping scheduling.")
            print("Traceback MemoryError")
            memory_exceeded = True

        scheduling_process.join()

        if memory_exceeded:
            if scheduling_process.is_alive():
                scheduling_process.terminate()
            schedule = None
            success = 0
            actual_utilization = numpy.nan
        else:
            schedule = return_dict["schedule"]
            success = return_dict["success"]
            actual_utilization = return_dict["actual_utilization"]

        end_time_compute = perf_counter()
        computation_time = end_time_compute - start_time_compute

        if not success or schedule is None:
            computation_time = numpy.nan
            actual_utilization = numpy.nan
            theoritical_utilization = numpy.nan
            print(
                f"Scheduling failed for taskset: {self.taskset_id} and assignment: {self.assignment_id}")
        else:
            theoritical_utilization = sum(taskset.utilization)
            print(
                f"Scheduling succeeded for taskset: {self.taskset_id} and assignment: {self.assignment_id}")

        scheduling = Scheduling(
            schedule=schedule, success=success, scheduler_name=str(scheduler))
        scheduling.add_performances(
            computation_time=computation_time, actual_utilization=actual_utilization, theoritical_utilization=theoritical_utilization)
        return scheduling

    def generate_composite_scheduling(self, taskset, assignment, scheduler_class, start_time=1, end_time=None):
        print(
            f"Generating composite scheduling using {scheduler_class.__name__}")
        start_time_compute = perf_counter()

        scheduler = scheduler_class(
            taskset=taskset,
            assignment=assignment,
            number_of_cores=self.number_of_cores,
            scheduling_options=self.scheduling_options,
            start_time=start_time,
            end_time=end_time,
        )

        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        scheduling_process = multiprocessing.Process(
            target=self.run_scheduler_composite, args=(scheduler, return_dict))
        scheduling_process.start()

        memory_exceeded = False

        try:
            self.monitor_memory(scheduling_process)
        except MemoryLimitExceededException:
            print(
                "Memory limit exceeded during composite scheduling. Stopping scheduling.")
            print("Traceback MemoryError")
            memory_exceeded = True

        scheduling_process.join()

        if memory_exceeded:
            if scheduling_process.is_alive():
                scheduling_process.terminate()
            busy_periods = None
        else:
            busy_periods = return_dict["busy_periods"]
            actual_utilization = return_dict["actual_utilization"]

        end_time_compute = perf_counter()
        computation_time = end_time_compute - start_time_compute

        scheduling = CompositeScheduling(scheduler_name=str(scheduler))

        if busy_periods is not None:
            for busy_period in busy_periods:
                scheduling.add_schedule(schedule=busy_period)

        if busy_periods is None or len(busy_periods) == 0 or not scheduling.success:
            computation_time = numpy.nan
            actual_utilization = numpy.nan
            theoritical_utilization = numpy.nan
            scheduling.success = 0
            print(
                f"Composite scheduling failed for taskset: {self.taskset_id} and assignment: {self.assignment_id}")
        else:
            actual_utilization = sum(actual_utilization)
            theoritical_utilization = sum(taskset.utilization)
            print(
                f"Composite scheduling succeeded for taskset: {self.taskset_id} and assignment: {self.assignment_id}")

        scheduling.add_performances(
            computation_time=computation_time, actual_utilization=actual_utilization, theoritical_utilization=theoritical_utilization)
        return scheduling
