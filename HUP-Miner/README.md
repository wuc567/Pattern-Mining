## HUP-Miner: Mining high average utility nonoverlapping patterns from sequential database

Meng Geng, Youxi Wu, Yan Li, Jing Liu, Lei Guo, Xingquan Zhu,and Xindong Wu

***

#### Abstract:
As a crucial aspect of data mining, high average utility sequential pattern mining (SPM) aims to discover low frequency and high average utility patterns (subsequences) in sequence data. Most existing high average utility SPM meth-ods overlook the repetitive occurrences of patterns in each sequence, resulting in some important patterns being ignored. To address this issue, we focus on the problem of mining high average utility nonoverlapping patterns (HUPs) from sequential database, and propose an HUP-Miner algorithm. To reduce the need for repeated scanning of the original database, we use a positional dictionary to record the occurrence information of each item. To reduce the number of candidate patterns generated, we adopt a pattern join strategy and explore four pruning strategies. To efficiently calculate the average utility of a pattern, we propose an SPC algorithm to obtain the occurrence of super-patterns by utilizing the occurrence posi-tions of sub-patterns. When compared with eight competitive algorithms, the experimental results on 14 databases show that HUP-Miner gives superior results. Furthermore, we use information gain as the utility for each item, and find that the HUPs discovered in this way can generate better performance via a clustering analysis. All of the algorithms and databases used here are available from https://github.com/wuc567/Pattern-Mining/tree/master/HUP-Miner.

---

#### Datasets:
[Dataset](https://github.com/wuc567/Pattern-Mining/blob/master/HUP-Miner/Databases)

#### Algorithms:

[HUP-Miner and all competitive algorithms](https://github.com/wuc567/Pattern-Mining/blob/master/HUP-Miner/Algorithm)
 

