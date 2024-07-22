from modules.taskset.taskset_set import TasksetSet
from modules.taskset.taskset import Taskset
from modules.taskset.taskset_set_generator import TasksetSetGenerator


class TasksetSetManual:
    def __init__(self, taskset_id, wcet_list, deadline_list, period_list, interference_list, utilization_list):
        self.taskset_id = taskset_id
        self.wcet_list = wcet_list
        self.deadline_list = deadline_list
        self.period_list = period_list
        self.interference_list = interference_list
        self.single_interference = [9 for _ in range(len(self.wcet_list))]
        self.utilization_list = utilization_list

    def create_taskset_set(self):
        """Crée un TasksetSet à partir des paramètres donnés."""
        hyperperiods = TasksetSetGenerator.generate_hyperperiods(
            periods=[self.period_list])
        N = TasksetSetGenerator.generate_N(
            periods=[self.period_list], hyperperiods=hyperperiods)
        activations = TasksetSetGenerator.generate_activations(
            periods=[self.period_list], N=N)
        absolute_deadlines = TasksetSetGenerator.generate_absolute_deadline(
            periods=[self.period_list], deadlines=[self.deadline_list], activations=activations)
        taskset_list = [
            Taskset(
                taskset_number=0,
                wcet=self.wcet_list,
                deadline=self.deadline_list,
                period=self.period_list,
                interference=self.interference_list,
                single_interference=self.single_interference,
                utilization=self.utilization_list,
                hyperperiod=hyperperiods[0],
                N=N[0],
                activation=activations[0],
                absolute_deadline=absolute_deadlines[0]
            )
        ]
        return TasksetSet(
            taskset_id=self.taskset_id,
            wcet=self.wcet_list,
            deadline=self.deadline_list,
            period=self.period_list,
            interference=self.interference_list,
            single_interference=self.single_interference,
            utilization=self.utilization_list,
            taskset_list=taskset_list,
        )
