## RNP-Miner: Repetitive nonoverlapping sequential pattern mining
***

Meng Geng, Youxi Wu, Yan Li, Jing Liu, Philippe Fournier-Viger, Xingquan Zhu, and Xindong Wu

#### Abstract:

  Sequential pattern mining (SPM) is an important branch of knowledge discovery that aims to mine frequent sub-sequences (patterns) in a sequential database. Various SPM methods have been investigated, and most of them are classical SPM methods, since these methods only consider whether or not a given pattern occurs within a sequence. Classical SPM can only find the common features of sequences, but it ignores the number of occurrences of the pattern in each sequence, i.e., the degree of interest of specific users. To solve this problem, this paper addresses the issue of repetitive nonoverlapping sequential pattern (RNP) mining and proposes the RNP-Miner algorithm. To reduce the number of candidate patterns, RNP-Miner adopts an itemset pattern join strategy. To improve the efficiency of support calculation, RNP-Miner utilizes the candidate support calculation algorithm based on the position dictionary. To validate the performance of RNP-Miner, 10 competitive algorithms and 20 sequence databases were selected. The experimental results verify that RNP-Miner outperforms the other algorithms, and using RNPs can achieve a better clustering performance than raw data and classical frequent patterns. 
---

#### Algorithms:

[RNP-Miner and all competitive algorithm](https://github.com/wuc567/Pattern-Mining/tree/master/RNP-Miner/algorithms)

#### Datasets:
[Datasets](https://github.com/wuc567/Pattern-Mining/tree/master/RNP-Miner/datasets)  
