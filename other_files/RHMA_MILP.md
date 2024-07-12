### Decision Variables
- $$ x_{iajt} $$: $$1$$ if task $$i$$ in activation $$a$$ is allocated to core $$j$$ and executed at time $$t$$ and $$0$$ otherwise.

- $$m_{iakb}$$: Interference matrix. $$1$$ if execution of $$\tau_i$$ in activation $$a$$ coincides with the execution of $$\tau_k$$ in activation $$b$$ and $$0$$ otherwise.

- $$w_{ia}$$: Response time matrix. Response time of $$\tau_i$$ in activation $$a$$.

### Objective Function
To minimize interference and the response time of the tasks across all system executions:

$$  \min \text{Obj} = \frac{1}{\text{maxI}} \left( \sum_{\substack{\forall i, k \in \tau \\ \forall a \in S_{ih} \\ \forall b \in S_{kh}}} m_{iakb} \right) + \sum_{\forall i, a \in R_{iah}} \frac{w_{ia}}{D_i} $$

### Constraints
1. $$ x_{iajt} = o_{ij} \quad \forall i, a, j, t|i, a \in R_{iah}, t \in T_{h}, \quad \text{if } o_{ij}=0 $$

2. $$ m_{iakb} = 0 \quad \forall i, a \in R_{iah}, \forall k, b \in R_{kbh} \quad \text{if } k > i \quad \text{and if } R_{iah} \cap R_{kbh} = \emptyset  $$

3. $$ \sum_{\substack{a \in S_{ih} \\ t \in R_{iah}}} x_{iajt} = \text{len}(S_{ih}) \cdot C_i \cdot o_{ij} + \sum_{\substack{k \neq i \\ a \in S_{ih} \\ b \in S_{kh}}} m_{iakb} \cdot I_k \cdot o_{ij} \quad \forall i, j \quad \text{if } o_{ij} \neq o_{kj}$$

   $$ \text{ and if } I_i, I_k \neq 0 \quad \text{ and if len}(S_{ih}), \text{len}(S_{jh}) > 0 $$


4. $$ \sum_{\substack{t \in R_{iah}}} x_{iajt} =  C_i \cdot o_{ij} + \sum_{\substack{k \neq i  \\ b \in S_{kh}}} m_{iakb} \cdot I_k \cdot o_{ij} \quad \forall i, j, a | a \in S_{ih} \quad \text{if } o_{ij} \neq o_{kj}$$

   $$ \text{ and if } I_i, I_k \neq 0 \quad \text{ and if len}(S_{ih}), \text{len}(S_{jh}) > 0 $$


5. $$ t \sum_{j \in J} x_{iajt} \leq d_{ia} - 1 \quad \forall i, a, t | a \in S_{ih}, t \in T_h $$

6. $$ \sum_{\substack{\forall i \\ a \in S_{ih}}} x_{iajt} \leq 1 \quad \forall j, t | t \in T_h $$

7. $$ m_{iakb} \geq x_{iajt} + x_{kblt} - 1 \quad \forall i, a, k, b, j, l, t | a \in S_{ih}, b \in S_{kh}, t \in T_h  $$
  
$$\text{and if } i \neq k \text{ and if } j \neq l $$

8. $$ m_{iakb} = m_{kbia} \quad \forall i, a, k, b|a \in S_{ih}, b \in S_{kh}, \text{if } k \neq i $$

9. $$ w_{ia} \geq t \cdot x_{iajt} - aT_i + 1 \quad \forall t, i, a, j | a \in S_{ih}, t \in T_h $$

10. **Variable Domains**:
   - $$ x_{iajt}, m_{iakb} \in \{0, 1\} $$

   - $$ w_{ia} \geq 0 $$

### Parameters
- $$ C_i $$ : Worst case computation time of $$\tau_i$$.

- $$ D_i $$ : Relative deadline of $$\tau_i$$.

- $$d_{ia}$$ : Absolute deadline of $$\tau_i$$ in activation $$a$$.

- $$ T_i $$ : Period of $$\tau_i$$.

- $$ I_i $$ : Interference factor of $$\tau_i$$ over other tasks.

- $$N_i$$ : Number of activations of $$\tau_i$$.

- $$o_{ij}$$ : $$1$$ if $$\tau_i$$ is allocated to core $$M_j$$ and $$0$$ otherwise.

- $$S_{ih}$$ : Activations of task $$\tau_i$$ executed in the busy period $$\text{BP}_h$$.

- $$R_{iah}$$ : Possible execution time interval for task $$\tau_i$$ in its activation $$a$$ in the busy period $$\text{BP}_h$$.

- $$T_h$$ : Execution times for the busy period $$\text{BP}_h$$.

- $$lcm$$ : Hyperperiod of the task set.

- $$maxI$$ : Maximum possible received interferences.  