## OSP-Miner: Mining one-off weak-gap strong sequential patterns

Yan Li, Hongxi Yang, Meng Geng, Yajing Zhou, Jie Li, Youxi Wu, and Xindong Wu 

***

#### Abstract:
One-off sequential pattern mining (SPM) (or SPM under the one-off condition) can effectively discover potentially useful information from sequences, since it calculates the number of occurrences of patterns in sequences. However, existing one-off SPM methods mainly discover patterns from simple sequences, rather than from general sequences composed of itemsets. To discover the patterns that users are more concerned with, we mine one-off weak-gap strong patterns (OSPs) composed of strong items. We propose an effective algorithm called OSP-Miner that has three parts: preparation stage, support calculation process, and candidate pattern generation. In the preparation stage, to avoid brute-force matching, OSP-Miner creates binomial search lists for patterns with length two, based on the inverted index for each item. To effectively calculate the support of a pattern with length m (m >2), OSP-Miner first creates m − 1 level nodes based on the binomial search lists, and then employs a depth-first search strategy to obtain an occurrence. OSP-Miner employs I-Join and S-Join to reduce the number of candidate patterns. Compared with eight competitive algorithms, the experimental results on eight datasets show that OSP-Miner outperforms the competitive algorithms and makes it easier to mine patterns in which the users will be interested. Furthermore, OSP-Miner yields better performance in the clustering analysis of the driving trajectory.

---

#### Datasets:
[Dataset](https://github.com/wuc567/Pattern-Mining/blob/master/OSP-Miner/DataSets)

#### Algorithms:

[MCoR-Miner and all competitive algorithms](https://github.com/wuc567/Pattern-Mining/blob/master/OSP-Miner/Algorithms)
 

