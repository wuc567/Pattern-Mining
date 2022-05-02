## OPR-Miner: Order-preserving rule mining for time series
***

Youxi Wu, Xiaoqian Zhao, Yan Li, Lei Guo, Xingquan Zhu, Philippe Fournier-Viger, Xindong Wu. 

#### Abstract:

  Discovering frequent trends in time series is a critical task in data mining.Recently, order-preserving matchingwas proposed to find all occurrences of a pattern in a time series, where the pattern is a relative order (regarded as a trend) and an occurrence is a sub-time series whose relative order coincides with the pattern. Inspired by the order-preserving matching, the existing order-preserving pattern (OPP) mining algorithm employs order-preserving matching to calculate the support, which leads to low efficiency. To address this deficiency, this paper proposes an algorithm called efficient frequent OPP miner (EFO-Miner) to find all frequent OPPs. EFO-Miner is composed of four parts: a pattern fusion strategy to generate candidate patterns, a matching process for the results of subpatterns to calculate the support of super-patterns, a screening strategy to dynamically reduce the size of prefix and suffix arrays, and a pruning strategy to further dynamically prune candidate patterns. Moreover, this paper explores the orderpreserving rule (OPR) mining and proposes an algorithm called OPR-Miner to discover strong rules from all frequent OPPs using EFO-Miner. Experimental results verify that OPR-Miner gives better performance than other competitive algorithms. More importantly, clustering and classification experiments further validate that OPR-Miner achieves good performance.The algorithms and data can be downloaded https://github.com/wuc567.
 
---

#### Algorithms:

[OPR-Miner and all competitive algorithm](https://github.com/wuc567/Pattern-Mining/tree/master/OPR-Miner/algorithms)

#### Datasets:
[Datasets](https://github.com/wuc567/Pattern-Mining/tree/master/OPR-Miner/datasets)  