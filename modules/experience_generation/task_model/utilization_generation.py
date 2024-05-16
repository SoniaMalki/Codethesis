# utilization_generation.py

import numpy

class UtilizationGeneration:
    def __init__(self, number_of_taskset, number_of_task_in_taskset, max_utilization):
        self.number_of_taskset = number_of_taskset
        self.number_of_task_in_taskset = number_of_task_in_taskset
        self.max_utilization = max_utilization

    def StaffordRandFixedSum(self):
        if self.number_of_task_in_taskset == 1:
            return numpy.tile(numpy.array([self.max_utilization]), [self.number_of_taskset, 1])

        k = numpy.floor(self.max_utilization)
        s = self.max_utilization
        step = 1 if k < (k - self.number_of_task_in_taskset + 1) else -1
        s1 = s - numpy.arange(k, (k - self.number_of_task_in_taskset + 1) + step, step)
        step = 1 if (k + self.number_of_task_in_taskset) < (k - self.number_of_task_in_taskset + 1) else -1
        s2 = numpy.arange((k + self.number_of_task_in_taskset), (k + 1) + step, step) - s

        tiny = numpy.finfo(float).tiny
        huge = numpy.finfo(float).max

        w = numpy.zeros((self.number_of_task_in_taskset, self.number_of_task_in_taskset + 1))
        w[0, 1] = huge
        t = numpy.zeros((self.number_of_task_in_taskset - 1, self.number_of_task_in_taskset))

        for i in numpy.arange(2, (self.number_of_task_in_taskset + 1)):
            tmp1 = w[i - 2, numpy.arange(1, (i + 1))] * s1[numpy.arange(0, i)] / float(i)
            tmp2 = w[i - 2, numpy.arange(0, i)] * s2[numpy.arange((self.number_of_task_in_taskset - i), self.number_of_task_in_taskset)] / float(i)
            w[i - 1, numpy.arange(1, (i + 1))] = tmp1 + tmp2;
            tmp3 = w[i - 1, numpy.arange(1, (i + 1))] + tiny;
            tmp4 = numpy.array((s2[numpy.arange((self.number_of_task_in_taskset - i), self.number_of_task_in_taskset)] > s1[numpy.arange(0, i)]))
            t[i - 2, numpy.arange(0, i)] = (tmp2 / tmp3) * tmp4 + (1 - tmp1 / tmp3) * (numpy.logical_not(tmp4))

        m = self.number_of_taskset
        x = numpy.zeros((self.number_of_task_in_taskset, m))
        rt = numpy.random.uniform(size=(self.number_of_task_in_taskset - 1, m))
        rs = numpy.random.uniform(size=(self.number_of_task_in_taskset - 1, m))
        s = numpy.repeat(s, m)
        j = numpy.repeat(int(k + 1), m)
        sm = numpy.repeat(0, m)
        pr = numpy.repeat(1, m)

        for i in numpy.arange(self.number_of_task_in_taskset - 1, 0, -1):
            e = (rt[(self.number_of_task_in_taskset - i) - 1, ...] <= t[i - 1, j - 1])
            sx = rs[(self.number_of_task_in_taskset - i) - 1, ...] ** (1 / float(i))
            sm = sm + (1 - sx) * pr * s / float(i + 1)
            pr = sx * pr
            x[(self.number_of_task_in_taskset - i) - 1, ...] = sm + pr * e
            s = s - e
            j = j - e

        x[self.number_of_task_in_taskset - 1, ...] = sm + pr * s
        
        for i in range(0, m):
            x[..., i] = x[numpy.random.permutation(self.number_of_task_in_taskset), i]
        return numpy.transpose(x)
