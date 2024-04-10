## OER-Miner: One-off episode rule mining for process event logs

Youxi Wu, Zhihong Dong, Jing Liu, Yan Li, Cong Liu, Lijie Wen, and Xindong Wu

***

#### Abstract:
Episode mining is an active subfield of data mining in which the aim is to retrieve important knowledge from temporal data and can be used for fault reports and web navigation logs. However, existing methods generally do not consider time gap constraints, and overestimate the frequency of episodes, which may lead to mining a large number of episodes that users are not interested in. To tackle this problem, this paper investigates one-off episode rule (OER) mining with time gap constraints for process event logs and proposes a one-off episode rule mining algorithm called OER-Miner that can mine frequent one-off episodes and the implicit relationship among them. To generate fewer and prune unpromising candidate episodes, OER-Miner utilizes episode join and pruning strategies, respectively. To efficiently calculate the candidate episode support, position indexes, and depth-first search and backtracking strategies are applied to calculate the number of occurrences. Experimental results verify that OER-Miner yields a better performance than seven other competitive algorithms on nine publicly available event logs. More importantly, OER-Miner can be applied to a real-industrial log to identify rework phenomena in the production process by mining strong one-off episode rules, to discover the optimal processes and deficiencies of the system, and to provide recommendations for further improvement.

---

#### Datasets:
[Dataset](https://github.com/wuc567/Pattern-Mining/blob/master/OER-Miner/DataSets)

#### Algorithms:

[MCoR-Miner and all competitive algorithms](https://github.com/wuc567/Pattern-Mining/blob/master/OER-Miner/Algorithms)
 

