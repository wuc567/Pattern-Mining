## Top-k contrast order-preserving pattern mining for time series classification
***

Youxi Wu, Yufei Meng, Yan Li, Lei Guo, Xingquan Zhu, Philippe Fournier-Viger, Xindong Wu. 

#### Abstract:

  Recently, order-preserving pattern (OPP) mining, a new sequential pattern mining method, has been proposed to mine frequent relative orders in a time series. Although frequent relative orders can be used as features to classify a time series, the mined patterns do not reflect the differences between two classes of time series well. To effectively discover the differences between time series, this paper addresses top-k contrast OPP mining (COPP) and proposes a COPP-Miner algorithm to discover the top-k contrast patterns as features for time series classification, avoiding the problem of improper parameter setting. COPP-Miner is composed of three parts: extreme point extraction to reduce the length of the original time series, forward mining and reverse mining to discover COPPs. Forward mining contains three steps: pattern fusion strategy to generate candidate patterns, the support rate calculation method to efficiently calculate the support of a pattern, and the pruning strategies to further prune candidate patterns. Reverse mining consists of applying the same process as forward mining but positive and negative sequences are swapped. Experimental results validate the efficiency of the proposed algorithm and show that top-k COPPs can be used as features and significantly outperform other time series classification methods.
---

#### Algorithms:

[COPP-Miner and all competitive algorithm](https://github.com/wuc567/Pattern-Mining/tree/master/COPP-Miner/algorithms)

#### Datasets:
[Datasets](https://github.com/wuc567/Pattern-Mining/tree/master/COPP-Miner/datasets)  
