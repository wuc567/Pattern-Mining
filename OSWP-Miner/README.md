## One-Off Sequential Pattern Mining Using a Sliding Window

Youxi Wu, Kaixuan Cao, Yan Li, Jing Liu, Lei Guo, Xingquan Zhu, and Xindong Wu 

***

#### Abstract:
In sequential pattern mining (SPM), when the data take the form of a continuous stream, it is not feasible to mine sequential patterns from the complete data stream due to time and memory constraints. A sliding window model was therefore proposed, in which mining operations could be performed with a focus on the recently accumulated parts of data streams. Moreover, when classical SPM methods are applied to a data stream, they only take into account whether a pattern occurs in a sequence, and ignore the frequency of its occurrences within the sequence. To address this problem, this paper presents a one-off sliding window sequential pattern (OSWP) mining scheme, and proposes the OSWP-Miner algorithm. At the data preprocessing stage, OSWP-Miner employs an inverted index structure to avoid the need for duplicate scanning of the original database. To efficiently calculate the support, our model employs the SCOD algorithm based on an ordered set dictionary. In order to reduce the quantity of candidate patterns, OSWP-Miner applies an itemset pattern joining strategy, and to improve the efficiency of frequent pattern updating, a window pruning strategy and incremental calculation strategy are employed. To verify the performance of OSWP-Miner, eight competitive algorithms and 13 databases were selected. Our experimental results show that OSWP-Miner outperforms other competitive algorithms; more importantly, it enables changes in the data stream to be captured effectively, and can handle the impact of concept drift.
---

#### Datasets:
[Dataset](https://github.com/wuc567/Pattern-Mining/blob/master/OSWP-Miner/DataSets)

#### Algorithms:

[OSWP-Miner and all competitive algorithms](https://github.com/wuc567/Pattern-Mining/blob/master/OSWP-Miner/Algorithms)
 

