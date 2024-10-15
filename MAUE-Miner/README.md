## Mining one-off high average utility episodes for process event logs

Zhihong Dong, Jing Liu, and Youxi Wu

***

#### Abstract:
High utility episode (HUE) mining is an emerging and highly popular research field within data mining, where the aim is to mine all episodes with utility no less than a user-specified threshold. It has been successfully applied in various domains. However, existing research on HUE does not consider the length of episodes, and it must be guaranteed that the utility of each event remains unchanged, which prevents the compatibility of HUE with real-life applications. To tackle this problem, we argue that there is a need to mine one-off high average utility episodes (MAUE). An approach called MAUE-Miner is presented, which has three main modules: database reconstruction, candidate episode generation, and average utility calculation. For the reconstructed database, we present a sequence extraction (SeqExtraction) strategy, which can improve the efficiency of searching for occurrences of episodes. Since MAUE mining does not satisfy the anti-monotonicity property, we introduce a pruning strategy based on the upper bound utility of an episode, which can prune unpromising candidate episodes in advance. To calculate the average utility, depth-first search and backtracking strategies for the event index are adopted, a method that can efficiently find occurrences by avoiding a linear search. Experimental results indicate that MAUE-Miner achieves better performance than alternative methods. More importantly, a case study shows that MAUE-Miner can be applied to a real industrial log to identify paths with high numbers of rejected parts, to discover optimal production processes, and to provide recommendations for further improvement. The code can be downloaded from https://github.com/wuc567/Pattern-Mining/tree/master/MAUE-Miner.

---

#### Datasets:
[Dataset](https://github.com/wuc567/Pattern-Mining/blob/master/MAUE-Miner/DataSets)

#### Algorithms:

[MAUE-Miner and all competitive algorithms](https://github.com/wuc567/Pattern-Mining/blob/master/MAUE-Miner/Algorithms)
 

