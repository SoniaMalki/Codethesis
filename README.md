## Documentation du code

### 1. Génération de Tasksets

Le processus de génération de tasksets vise à créer des ensembles de tâches réalistes pour tester les algorithmes d'assignation et d'ordonnancement. 

#### 1.1. Paramètres de génération

Les paramètres clés pour la génération de tasksets sont définis dans le fichier `experience.json`.  Ils sont ensuite utilisés par la classe `TasksetSetGenerator` pour créer les tasksets. 

- **`taskset_repetition`**:  Nombre de tasksets à générer. Permet de répéter une expérience plusieurs fois avec les même paramètre de génération, pour faire des moyennes. (choix entre : 1, 2, 4, 8 ou 16)
- **`tasks_per_taskset`**:  Nombre de tâches dans chaque taskset. (choix entre: 10 ou 20)
- **`interference_factor`**: Facteur utilisé pour calculer l'interférence entre les tâches. L'interférence est défini comme un pourcentage du WCET. (choix entre: 0.2 ou 0.8)
- **`probability_factor`**: Probabilité qu'une interférence se produise entre deux tâches. (choix entre: 0.1 ou 0.4)
- **`max_utilization`**:  Utilisation maximale autorisée pour chaque taskset. (choix entre: 0.2 à 1 par incrément de 0.2. Cela est multiplié par le nombre de coeurs disponibles)
- **`taskset_options`** Options spécifiques à l'algorithme de generation de taskset si nécessaire.
    - **`deadline_option`**: Option pour la génération des deadlines.
        - `eq_period`:  La deadline est égale à la période de la tâche.
        - `leq_period`: La deadline est un nombre aléatoire entre le WCET et la période de la tâche.
    - **`max_hyperperiod`**:  Hyperpériode maximale autorisée pour les tasksets générés. Permet de ne pas avoir une explosion de paramètres. (choix entre: différentes puissances de 10 jusqu'à limite raisonnable)
    - **`max_prime`**:  Nombre premier maximal utilisé pour générer les périodes des tâches. (choix entre: différents premiers jusque 23)
    - **`gen_limit_exponent`**: Exposant utilisé pour limiter l'hyperpériode maximale lors de la génération de la matrice de nombres premiers. (choix entre: 2, 3, 4 ou 5)

#### 1.2. Génération des paramètres des tâches

Les paramètres de chaque tâche (`wcet`, `deadline`, `period`, `interference`, `single_interference`, `utilization`, `hyperperiod`, `N`, `activation`, `absolute_deadline`) sont générés par les modules suivants :

- **`UtilizationGenerator`**: Génère les utilisations des tâches en s'assurant que la somme des utilisations des tâches d'un même taskset ne dépasse pas l'utilisation maximale spécifiée (`max_utilization`). Utilise la méthode décrite dans [1] (Emberson, Stafford, & Davis, 2010)
- **`PrimeMatrixGenerator`**: Génère une matrice de nombres premiers utilisée pour créer des périodes de tâches uniques et éviter les explosions d'hyperpériode.  Utilise la méthode décrite dans [2] (Goossens & Macq, 2001). Les matrices sont générés si elles n'existent pas, elles sont ensuite sauvegardées pour être réutilisées. On différencie les différentes matrice par leur paramètres qui sont ajoutés au nom du fichier.
- **`PeriodGenerator`**:  Utilise la matrice de nombres premiers pour générer les périodes des tâches. Utilise la méthode décrite dans [2] (Goossens & Macq, 2001). 
- **`WCETCalculator`**:  Calcule le WCET de chaque tâche en fonction de sa période et de son utilisation. (WCET = utilization * period) 
- **`DeadlineGenerator`**: Génère les deadlines des tâches en fonction de l'option spécifiée `deadline_option`.
- **`InterferenceGenerator`**:  Génère les interférences entre les tâches d'un même taskset en utilisant le facteur d'interférence (`interference_factor`) et la probabilité d'interférence (`probability_factor`). Si une interference a lieu (`probability_factor`), elle est calculée en fonction de `interference_factor` et du `wcet`.
- **`TasksetSetGenerator`**:  Calcule l'hyperpériode, le nombre d'activations (`N`), les `activations` et les `deadlines absolues` de chaque tâche. (ces données sont utilisées par RHMA).

### 2. Génération d'Assignments

Le processus d'assignation de tasksets vise à répartir les tâches entre différents coeurs selon certains critères.

#### 2.1. Paramètres d'assignation

Les paramètres de l'algorithme d'assignation sont définis dans le fichier `experience.json`. 

- **`assignment_method`**:  Nom de l'algorithme d'assignation à utiliser. (voir 2.2)
- **`sorting_criterion`**:  Critère de tri des tâches avant l'assignation.
    - `wcet_ascending`:  Tri des tâches par WCET croissant.
    - `wcet_descending`: Tri des tâches par WCET décroissant.
    - `period_ascending`:  Tri des tâches par période croissante.
    - `period_descending`:  Tri des tâches par période décroissante.
    - `utilization_ascending`:  Tri des tâches par utilisation croissante.
    - `utilization_descending`:  Tri des tâches par utilisation décroissante.
    - `execution_slack_ascending`:  Tri des tâches par marge d'exécution croissante (période - WCET).
    - `execution_slack_descending`:  Tri des tâches par marge d'exécution décroissante (période - WCET).
    - `random_order`:  Tri aléatoire des tâches.
- **`number_of_cores`**:  Nombre de processeurs disponibles pour l'assignation des tâches. (choix entre: 2, 4 ou 8). 
- **`assignment_options`**: Options spécifiques à l'algorithme d'assignation si nécessaire.
    - `solving_time_limit_MILP`:  Limite de temps imposée au solveur MILP avant d'abandonner la recherche. (choix à définir.) 


#### 2.2. Algorithmes d'assignation
Le code propose plusieurs algorithmes d'assignation qui peuvent être sélectionnés dans le fichier `experience.json`.

La classe `AssignmentGenerator` est responsable de la génération des assignations en fonction de l'algorithme spécifié (`assignment_method`) et des paramètres associés. Les algorithmes d'assignation suivants sont disponibles :

- **`CITTA`**:  Algorithme de partitionnement de tâches qui tient compte des interférences de cache lors de l'assignation des tâches aux cœurs. Utilise un modèle MILP pour calculer la borne supérieure de l'interférence de cache et recherche une partition qui garantit l'ordonnançabilité sous cette contrainte.

- **`WorstFitAssigner`**: Algorithme de partitionnement de tâches qui assigne chaque tâche au processeur ayant l'utilisation la plus faible parmi ceux pouvant encore l'accueillir. Les tâches sont préalablement triées selon le critère défini par `sorting_criterion`.  La validité de l'assignation est vérifiée en s'assurant que l'utilisation du processeur après l'ajout de la tâche ne dépasse pas 1.

- **`FirstFitAssigner`**: Algorithme de partitionnement de tâches qui assigne chaque tâche au premier processeur rencontré pouvant encore l'acceuillir.  Les tâches sont préalablement triées selon le critère défini par `sorting_criterion`.  La validité de l'assignation est vérifiée en s'assurant que l'utilisation du processeur après l'ajout de la tâche ne dépasse pas 1.

- **`BestFitAssigner`**: Algorithme de partitionnement de tâches qui assigne chaque tâche au processeur ayant l'utilisation la plus élevée parmi ceux pouvant encore l'accueillir. Les tâches sont préalablement triées selon le critère défini par `sorting_criterion`.  La validité de l'assignation est vérifiée en s'assurant que l'utilisation du processeur après l'ajout de la tâche ne dépasse pas 1. 

- **`Wmin`**: Algorithme d'allocation de tâches qui vise à minimiser l'interférence maximale potentielle entre les tâches. Il utilise une formulation MILP pour modéliser le problème et trouver une solution optimale en termes de minimisation de l'interférence. Wmin utilise le facteur d'interférence de chaque tâche pour estimer l'interférence potentielle et l'objectif est de minimiser la somme des interférences maximales possibles pour chaque cœur. 

### 3. Génération d'Ordonnancements

L'ordonnancement des tâches sur les processeurs est la dernière étape du processus de simulation.

#### 3.1. Paramètres d'ordonnancement

Les paramètres de l'algorithme d'ordonnancement sont définis dans le fichier `experience.json`. 

- **`scheduling_algorithm`**:  Nom de l'algorithme d'ordonnancement à utiliser. (voir 3.2)
- **`scheduling_options`**: Options spécifiques à l'algorithme d'ordonnancement si nécessaire. 
    - `non_preemption_time_variant_2`: Option disponible pour déterminer le facteur de non-preemption pour les variants 2 de EDF et DM. (choix entre: number_of_tasks, wcet_of_tasks ou system_utilization) définie selon [3] (Aceituno et al., 2022).
    - `solving_time_limit_MILP`:  Limite de temps imposée au solveur MILP avant d'abandonner la recherche. (choix à définir.) 

#### 3.2. Algorithmes d'ordonnancement

Le code propose plusieurs algorithmes d'ordonnancement qui peuvent être sélectionnés dans le fichier `experience.json`.

La classe `SchedulingGenerator` est responsable de la génération des ordonnancements en fonction de l'algorithme spécifié (`scheduling_algorithm`) et des paramètres associés. Les algorithmes d'ordonnancement suivants sont disponibles : 

- **`EarliestDeadlineFirst`**:  Algorithme "Earliest Deadline First" qui donne la priorité aux tâches ayant les deadlines relatives les plus proches.
- **`EarliestDeadlineFirstVariant1`**: Variante d'Earliest Deadline First qui gère l'inversion de priorité en favorisant la tâche en cours d'exécution si son temps d'exécution restant est inférieur à celui de la tâche de plus haute priorité qui veut la preempter.
- **`EarliestDeadlineFirstVariant2`**: Variante d'Earliest Deadline First qui introduit un temps de non-préemption pour chaque tâche selon certains critères. (voir `non_preemption_time_variant_2`)
- **`DeadlineMonotonic`**: Algorithme "Deadline Monotonic" qui donne la priorité aux tâches ayant les deadlines absolues les plus courtes.
- **`DeadlineMonotonicVariant1`**: Variante de Deadline Monotonic qui gère l'inversion de priorité comme `EarliestDeadlineFirstVariant1`.
- **`DeadlineMonotonicVariant2`**: Variante de Deadline Monotonic qui introduit un temps de non-préemption comme `EarliestDeadlineFirstVariant2`.
- **`CombinedScheduler`**: Algorithme qui combine plusieurs algorithmes d'ordonnancement simples pour trouver le meilleur ordonnancement possible pour chaque période occupée. Algorithme qui crée des busy periods (voir 3.3), des periodes divisées par des temps idle pour tous les coeurs.
- **`Rhma`**: Algorithme qui utilise un modèle MILP pour trouver un ordonnancement qui minimise à la fois les temps de réponse et les interférences.


#### 3.3. Busy period

Les algorithmes `CombinedScheduler` et `Rhma` utilisent le concept de busy period pour découper l'hyperpériode en intervalles de temps plus petits et indépendants.  La classe `BusyPeriodGenerator` est responsable de la génération des busy period.  

- **`generate_monocore_busy_periods_timeslice()`**:  Trouve les busy period sur un seul processeur (MBP).
- **`generate_busy_periods_timeslice()`**:  Fusionne les périodes occupées de tous les processeurs pour obtenir les périodes occupées globales.
- **`generate_busy_periods_from_schedule()`**:  Crée un objet `BusyPeriod` à partir d'un objet `Scheduling` en utilisant les périodes occupées globales.
- **`generate_busy_periods()`**:  Combine les fonctions précédentes pour générer un objet `BusyPeriod` à partir d'un objet `Scheduling`.
- **`generate_scheduling_length()`**:  Calcule la durée totale des périodes occupées d'un ordonnancement. Cela permet de comparer les Busy Period et choisir l'algorithme qui permet d'obtenir la plus courte BP.

## Références

- [1] Emberson, P., Stafford, R., & Davis, R. I. (2010). Techniques for the synthesis of multiprocessor tasksets. 

- [2] Goossens, J., & Macq, C. (2001). Limitation of the hyper-period in real-time periodic task set generation. In Proceedings of the 9th International Conference on Real-Time Systems (pp. 133–148). Teknea.

- [3] Aceituno, J. M., Guasque Ortega, A., Balbastre Betoret, P., Simó Ten, J., & Crespo Lorente, A. (2022). Planificador combinado: una estrategia para mejorar el rendimiento de los sistemas de tiempo real crítico. In XLIII Jornadas de Automática: libro de actas: 7, 8 y 9 de septiembre de 2022, Logroño (La Rioja) (pp. 870–876). Servizo de Publicacións da UDC. doi:10.17979/spudc.9788497498418.0870

