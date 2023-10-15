import numpy
import math
import random
import time

from math import gcd

from modules.taskset_set import TasksetSet
from modules.taskset import Taskset

class TasksetSetGeneration:
	def __init__(self, _matrixW, _taskset_set_number, _number_of_taskset, _period_min, _period_max, _granularity, 
				_number_of_task_in_taskset, _interference_factor, _probability_factor, _method_of_period_generation, _random_generation,
				_max_utilization):
				
		self.taskset_set_number = _taskset_set_number
		self.number_of_taskset = _number_of_taskset
		self.period_min = _period_min
		self.period_max = _period_max
		self.granularity = _granularity
		self.number_of_task_in_taskset = _number_of_task_in_taskset
		self.interference_factor = _interference_factor
		self.probability_factor = _probability_factor #TODO a quoi ça sert?
		self.method_of_period_generation = _method_of_period_generation
		self.random_generation = _random_generation
		self.max_utilization = _max_utilization

		self.matrixW = _matrixW

		self.max_lcm = 1000


	def __repr__(self):
		return ("TasksetSetGeneration("
			f"_taskset_set_number={self.taskset_set_number}, "
			f"_number_of_taskset={self.number_of_taskset}, "
			f"_period_min={self.period_min}, "
			f"_period_max={self.period_max}, "
			f"_granularity={self.granularity}, "
			f"_number_of_task_in_taskset={self.number_of_task_in_taskset}, "
			f"_interference_factor={self.interference_factor}, "
			f"_probability_factor={self.probability_factor}, "
			f"_method_of_period_generation={self.method_of_period_generation}, "
			f"_random_generation={self.random_generation}"
			f"_max_utilization={self.max_utilization}"
			")"
		)


	def setMatrix(self, _M):
		self.M = _M


	def init_taskset_set(self):
		if self.random_generation:
			utilizations = self.StaffordRandFixedSum() #génère une matrice de taille nombresets*nombredetasks par sets qui contient des 
												#self.max_utilization random dont le total arrive au u_total qu'on a donné en paramètre
		else:
			utilizations = self.max_utilization
			utilizations = numpy.array(utilizations)

		periods = self.gen_periods()
		wcets = numpy.zeros((self.number_of_taskset, self.number_of_task_in_taskset)) 
		for set_index in range(0, self.number_of_taskset): #génération de tous les wcet de tous les sets pour toutes les tâches
			for task_index in range(0, self.number_of_task_in_taskset):
				wcets[set_index][task_index] = max(1, math.floor(periods[set_index][task_index] * utilizations[set_index][task_index])) #wcet qui vient de la period * utilisation
		
		if self.random_generation:
			interferences = numpy.zeros((self.number_of_taskset, self.number_of_task_in_taskset, self.number_of_task_in_taskset)) #set d'interference de taille set*tasks*tasks 
			for _set in range(self.number_of_taskset):
				interferences[_set] = self.gen_interference(wcets[_set])
		else:
			interferences = self.interference_factor
			interferences = numpy.array(interferences)
		deadline = periods[:] #TO DO Implémenter deadline
		return [periods, deadline, utilizations, wcets, interferences]

	def StaffordRandFixedSum(self):
		# deal with self.number_of_task_in_taskset=1 case
		if self.number_of_task_in_taskset == 1:
			return numpy.tile(numpy.array([self.max_utilization]), [self.number_of_taskset, 1]) #matrice de taille self.number_of_taskset, 1 contenant que des self.max_utilization

		k = numpy.floor(self.max_utilization)
		s = self.max_utilization
		step = 1 if k < (k - self.number_of_task_in_taskset + 1) else -1
		s1 = s - numpy.arange(k, (k - self.number_of_task_in_taskset + 1) + step, step) #vecteurs qui determinent comment self.max_utilization doit s'utiliser dans le vecteur
		step = 1 if (k + self.number_of_task_in_taskset) < (k - self.number_of_task_in_taskset + 1) else -1
		s2 = numpy.arange((k + self.number_of_task_in_taskset), (k + 1) + step, step) - s #vecteurs qui determinent comment self.max_utilization doit s'utiliser dans le vecteur

		tiny = numpy.finfo(float).tiny #très petit chiffre, un seul
		huge = numpy.finfo(float).max #très grand chiffre, un seul

		w = numpy.zeros((self.number_of_task_in_taskset, self.number_of_task_in_taskset + 1)) #matrice de 0 de taille self.number_of_task_in_taskset * self.number_of_task_in_taskset+1
		w[0, 1] = huge #l'element [0][1] de la matrice w est le grand nombre
		t = numpy.zeros((self.number_of_task_in_taskset - 1, self.number_of_task_in_taskset)) #matrice de 0 de taille self.number_of_task_in_taskset-1 * self.number_of_task_in_taskset

		for i in numpy.arange(2, (self.number_of_task_in_taskset + 1)): #commence à 2 et finit à self.number_of_task_in_taskset (self.number_of_task_in_taskset+1 non-compris)
			tmp1 = w[i - 2, numpy.arange(1, (i + 1))] * s1[numpy.arange(0, i)] / float(i) #vecteur qui se remplit de valeurs au fur et a mesure jusqu'à atteindre self.number_of_task_in_taskset valeurs
			tmp2 = w[i - 2, numpy.arange(0, i)] * s2[numpy.arange((self.number_of_task_in_taskset - i), self.number_of_task_in_taskset)] / float(i)
			w[i - 1, numpy.arange(1, (i + 1))] = tmp1 + tmp2;
			#w est rempli par tmp1 et tmp2
			tmp3 = w[i - 1, numpy.arange(1, (i + 1))] + tiny;
			tmp4 = numpy.array((s2[numpy.arange((self.number_of_task_in_taskset - i), self.number_of_task_in_taskset)] > s1[numpy.arange(0, i)]))
			t[i - 2, numpy.arange(0, i)] = (tmp2 / tmp3) * tmp4 + (1 - tmp1 / tmp3) * (numpy.logical_not(tmp4))
			#t est rempli par tmp3 et tmp4

		m = self.number_of_taskset #nombre de sets
		x = numpy.zeros((self.number_of_task_in_taskset, m)) #matrice de taille self.number_of_task_in_taskset=nombre de tache m=nombre de sets
		rt = numpy.random.uniform(size=(self.number_of_task_in_taskset - 1, m))  # rand simplex type 
		rs = numpy.random.uniform(size=(self.number_of_task_in_taskset - 1, m))  # rand position in simplex
		s = numpy.repeat(s, m); #met la valeur s mfois dans la liste
		j = numpy.repeat(int(k + 1), m); #met la valeur k+1 m fois dans la liste
		sm = numpy.repeat(0, m); #met la valeur 0 m fois dans la liste
		pr = numpy.repeat(1, m); #met la valeur 1 m fois dans la liste

		for i in numpy.arange(self.number_of_task_in_taskset - 1, 0, -1):  # iterate through dimensions
			e = (rt[(self.number_of_task_in_taskset - i) - 1, ...] <= t[i - 1, j - 1])  # matrice qui contient des True or False utilisé pour décider la direction
			sx = rs[(self.number_of_task_in_taskset - i) - 1, ...] ** (1 / float(i))  # matrice de taille self.number_of_task_in_taskset (nombre de tâches)
			sm = sm + (1 - sx) * pr * s / float(i + 1) #matrice de taille self.number_of_task_in_taskset venant de la matrice précédente sx
			pr = sx * pr #copie de sx * anciennes copies de sx
			x[(self.number_of_task_in_taskset - i) - 1, ...] = sm + pr * e #encore une autre matrice aléatoire
			s = s - e
			j = j - e  # change transition table column if required

		x[self.number_of_task_in_taskset - 1, ...] = sm + pr * s #changer tous les élements de la dernière ligne de la matrice, le ... veut dire tout 
		#x est de dimension self.number_of_task_in_taskset lignes (nombre de tâches) et m colonnes (nombre de sets)
		
		for i in range(0, m): #permutation dans toutes les lignes avec les colonnes i
			x[..., i] = x[numpy.random.permutation(self.number_of_task_in_taskset), i] #c'est echangé avec avec une ligne random tout en gardant la même colonne
		return numpy.transpose(x); #on retourne une matrice de dimension m ligne (nombre de sets), self.number_of_task_in_taskset colonnes (nombre de tasks), ce qui est logique

	def gen_periods(self): 
		#self.number_of_task_in_taskset = nombre de taches, self.number_of_taskset nombre de sets de tasks, min valeur min d'une periode, max valeur max, granularite, distribution à utiliser
		if self.method_of_period_generation == "logunif": #si distribution logarithmique uniforme
			#valeur distribuée uniformément dans l'espace logarithmique
			periods = numpy.exp(numpy.random.uniform(low=numpy.log(self.period_min), high=numpy.log(self.period_max + self.granularity), size=(self.number_of_taskset, self.number_of_task_in_taskset)))
		elif self.method_of_period_generation == "unif": #si distribution uniforme
			#valeurs distribuée uniformément dans l'espace linéaire
			periods = numpy.random.uniform(low=self.period_min, high=(self.period_max + self.granularity), size=(self.number_of_taskset, self.number_of_task_in_taskset))
		elif type(self.method_of_period_generation) == list: #si on donne une liste à la place d'un nom de distribution
			if self.random_generation:
				# On choisit dans cette liste de periode prédéfinies
				assert self.number_of_taskset == 1 #condition à respecter si on donne une liste, c'est de ne générer qu'un set. Si c'est pas respecté ça renvoie error
				# avoid numpy.random.choice() because we need to be compatible with 1.6.X
				periods = [random.choice(self.method_of_period_generation) for _ in range(self.number_of_task_in_taskset)] #rempli periods de self.number_of_task_in_taskset elements qui sont des elements choisi de manière random de la liste self.method_of_period_generation
				# wrap in numpy types
			else:
				periods = self.method_of_period_generation
			periods = numpy.array(periods) #transforme en array numpy
			periods.shape = (1, self.number_of_task_in_taskset) #met sous forme de dimension mxn là où m est censé etre 1

		elif self.method_of_period_generation == "constrained_periods":
			print("SKSKSKSK\nSKSKSKSKSK\n")
			periods = self.generate_constrained_periods(self.matrixW)
			periods = numpy.array(periods)

		elif self.method_of_period_generation == "random_max_lcm":
			periods = self.gen_random_list_with_max_lcm() 
			periods = numpy.array(periods)
		else:
			return None
		periods = numpy.floor(periods / self.granularity) * self.granularity #retourne le chiffre le plus petit qui se divise par gran pour chaque elem de periods
		
		return periods

	def lcm_list(self, list_number):
	    lcm = 1
	    for i in list_number:
	        lcm = lcm*i//gcd(lcm, i)
	    return lcm

	def lcm(self, a, b):
	    return a * b // gcd(a, b)

	def gen_random_list_with_max_lcm(self):
		periods = []
		periods_before_distribution = []
		while len(periods_before_distribution) == 0:
			periods_before_distribution = self.generate_random_list_with_constraints()
		for i in range(0, len(periods_before_distribution), self.number_of_task_in_taskset):
			periods.append(periods_before_distribution[i:i+self.number_of_task_in_taskset])
		return periods

	def generate_random_list_with_constraints(self):
	    random_list = []
	    current_lcm = 1
	    loop = 0
	    
	    while len(random_list) < self.number_of_task_in_taskset*self.number_of_taskset and current_lcm <= self.max_lcm:
	        if loop == 10000: #if instance takes too much time, stop and retry
	            return []
	        number = random.randint(self.period_min, self.period_max)
	        if number not in random_list:
	            new_lcm = self.lcm(current_lcm, number)
	            
	            if new_lcm <= self.max_lcm:
	                random_list.append(number)
	                current_lcm = new_lcm
	            else:
	                if random_list:
	                    random_list.pop()  # Remove the last added number
	                    current_lcm = self.lcm_list(random_list)
	                else:
	                    break  # No more numbers to remove, exit the loop
	        loop += 1
	    return random_list

	def gen_interference(self,wcet):
		cache_interference = numpy.zeros((self.number_of_task_in_taskset, self.number_of_task_in_taskset)) #une matrice de taille nxn qui représente si une tâche a une interference sur une autre tache
		#ligne 1 = tâche 1 et toutes les colonnes seront les tâches avec lequelles y'a une interference
		for task_i in range(0, self.number_of_task_in_taskset):
			for task_j in range(task_i + 1, self.number_of_task_in_taskset):
				random_inter = numpy.random.uniform(0, 1)
				if random_inter < self.probability_factor:
					has_interference = 1
				else:
					has_interference = 0
				cache_interference[task_i][task_j] = has_interference * math.floor(
					self.interference_factor * 0.5 * min(wcet[task_i], wcet[task_j]))
				cache_interference[task_j][task_i] = cache_interference[task_i][task_j]
		for i in range(0, self.number_of_task_in_taskset):
			cache_interference[i, i] = 0 #pour que aucune tache ne fasse de l'interference sur elle-même
		return cache_interference

	def generate_taskset_set(self):
		period, deadline ,utilization, wcet, interference = self.init_taskset_set()
		taskset_set_generated = []
		for i in range(len(period)):
			print(interference[i])
			taskset_set_generated.append(Taskset(_taskset_number=i, _wcet=wcet[i], _deadline=deadline[i], _period=period[i], _interference=interference[i], 
												_utilization=utilization[i]))
		res = TasksetSet(_taskset_set_number=self.taskset_set_number, _wcet=wcet, _deadline=deadline , _period=period,
						_interference=interference , _utilization=utilization, _taskset_list=taskset_set_generated)

		return res


	def generate_constrained_periods(self, M):

		def generate_single_period(M):
		    period = 1
		    for i in M:
		        p = round(random.uniform(1, len(i)))
		        period *= i[p-1]  # -1 because list index starts from 0
		    return period

		periods = []
		for num_taskset in range(self.number_of_taskset):
			periods.append([])
			for num_task_in_taskset in range(self.number_of_task_in_taskset):
			    period = generate_single_period(M)
			    periods[-1].append(period)
		print("exmeple")
		print(periods)

		return periods

	





