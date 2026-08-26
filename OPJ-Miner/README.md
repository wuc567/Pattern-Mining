## OPJ-Miner: 

Youxi Wu, Sen Guo, Yan Li, Cong Liu, Jinyan Li, and Xindong Wu

***

#### Abstract:
Order-preserving pattern (OPP) mining is a sequential pattern mining method for discovering frequent trends in time series, where an OPP represents the relative order of a sub-time series. However, existing OPP mining algorithms overlook the intensity of the fluctuations between adjacent points, thereby limiting the representational ability of OPPs. To address this problem, this paper explores OPP mining with joint trend-intensity representation (OPJ), in which an OPP is augmented with an intensity-level pattern that encodes local fluctuation intensities. We also propose an algorithm called OPJ-Miner to mine all frequent OPJs. To reduce redundant candidate patterns, besides a joint pattern fusion strategy, we explore two key optimizations: (i) an OPJIndex hash table that groups ILPs sharing the same OPP, and (ii) an enumeration-and-checking strategy that identifies fusible OPP pairs in linear time per key to avoid quadratic pairwise comparisons. For support calculation, we explore hash-set operations with a pruning strategy, which replaces the traditional two‑pointer traversal with set intersection, and further prunes infrequent candidates to improve the mining efficiency of OPJ-Miner. To validate the performance of OPJ-Miner, nine datasets and 13 competitive algorithms are considered. The experimental results show that OPJ-Miner achieves speedups exceeding 2 times over OPP mining algorithms adapted for OPJ mining. More importantly, OPJs achieve better clustering performance than raw series and OPPs by jointly representing trends and fluctuation intensities.

---

#### Datasets:
[Dataset](https://github.com/wuc567/Pattern-Mining/blob/master/OPJ-Miner/datasets)

#### Algorithms:

[OPM-Miner and all competitive algorithms](https://github.com/wuc567/Pattern-Mining/blob/master/OPJ-Miner/algorithms)
 