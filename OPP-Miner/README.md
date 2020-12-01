## OPP-Miner: Order-preserving sequential pattern mining
***

Youxi Wu, Qian Hu, Yan Li, Lei Guo, Xingquan Zhu, Xindong Wu. OPP-Miner: Order-preserving sequential pattern mining

#### Abstract:

A time series is a collection of measurements in chronological order. Discovering patterns from time series is useful in many domains, such as stock analysis, disease detection, and weather forecast. To discover patterns, existing methods often convert times series data into another form, such as nominal/symbolic format, to reduce dimensionality, which inevitably deviate the data values. Moreover, existing methods mainly focus on finding specific patterns and neglect the order relationships between time series values. To tackle these issues, this paper proposes an Order-Preserving sequential Pattern (OPP) mining method, which represents patterns based on the order relationships of the time series data. An inherent advantage of such representation is that the trend of a time series can be represented by the relative order of the values underneath the time series data. To obtain frequent trends in time series, we propose the OPP-Miner algorithm to mine patterns with the same trend (subsequences with the same relative order). OPP-Miner employs the filtration and verification strategies to calculate the support and uses pattern fusion strategy to generate candidate patterns. To compress the result set, we also study finding the maximal OPPs and develop an MOPP-Miner algorithm. Experiments validate that OPP-Miner is not only efficient and scalable but can also discover similar sub-sequences in time series. In addition, case studies show that our algorithms have high utility in analyzing the COVID-19 epidemic by identifying critical trends and improve the clustering performance.
---

#### Datasets:
[Dataset](https://github.com/wuc567/Pattern-Mining/blob/master/OPP-Miner/DataSet.rar)  (All sequences)

#### Algorithms:

[OPP-Miner and all competitive algorithms](https://github.com/wuc567/Pattern-Mining/blob/master/OPP-Miner/OPP-Miner_code.rar)
 

