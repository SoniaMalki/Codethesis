### Decision Variables
- $$O_{ik}$$: Allocation matrix. $$1$$ if $$\tau_i$$ is allocated in core $$k$$ and $$0$$ otherwise.

- $$U_{M_{k}}$$: Theoretical utilization of core $$k$$, calculated as $$U_{M_{k}} = \sum_{\tau_i \in M_k} U_i$$.

- $$maxW_k$$: Maximum value of the sum of all elements of $$W$$ for core $$k$$

- $$maxW$$: Maximum value of the sum of all elements of $$W$$ for all cores

### Objective Function
To minimize the total maximum interference across all cores:


$$ \text{Minimise } maxW = \sum_{\forall k} maxW_k $$

### Constraints
1. $$ \sum_{\forall k} O_{ik} = 1 \quad \forall i $$

2. $$ \sum_{i \in k} U_i \cdot O_{ik} = U_{M_{k}} \quad \forall k$$

3. $$ U_{M_{k}} \leq 1 \quad \forall k $$

4. $$ \sum_{\substack{\tau_i \in M_{k} \\ I_i \neq 0}} \sum_{\tau_j \notin M_k} I_j = maxW_k \quad \forall k $$

### Variable Domains
- $$ O_{ik} \in \{0, 1\} $$

- $$ U_{M_{k}} \geq 0 $$

- $$ maxW_k \geq 0 $$

### Parameters
- $$ C_i $$: Worst case execution time of $$\tau_i$$.

- $$ T_i $$: Period of $$\tau_i$$.

- $$ U_i $$: Theoretical utilization of $$\tau_i$$, defined as $$U_i = \frac{C_i}{T_i}$$.

- $$ I_i $$: Interference factor of $$\tau_i$$ over other tasks.

