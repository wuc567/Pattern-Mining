## OUTO-Miner: Detecting outlying occurrences in maximal frequent
order-preserving patterns in time series

Youxi Wu, Siqi Lou, Yan Li, Lei Guo, Philippe Fournier-Viger, Xindong Wu

***

#### Abstract:
Order-preserving pattern (OPP) mining primarily focuses on the frequent trends of time series, and frequent OPPs have potential crucial value. However, the results of OPP mining ignore the significance of numerical values, especially in the field of outlier detection. In addition, OPP mining often generates redundant patterns, leading to high mem ory consumption or low operational efficiency in outlier detection. To address these problems, this paper focuses on detecting outlying occurrences (OUTO) in maximal frequent order-preserving patterns, which employs the dynamic time warping method to calculate the distance of two sub-time series, and proposes OUTO-Miner to detect outlying occurrences in frequent patterns. In the data preprocessing stage, a linear fitting method is employed, compressing the data and preserving the main features. To mitigate the generation of redundant patterns, OUTO-Miner utilizes maximal frequent OPPs for outlier detection. To avoid excessive computations, OUTO-Miner uses the interquartile range method to identify the sub-time series with a high probability of being an OUTO. To validate the performance of OUTO-Miner, 13 competitive algorithms, nine real-life datasets, and eight synthetic datasets are considered. The results conclusively demonstrate that OUTO-Miner outperforms all benchmark algorithms in terms of memory con sumption and running-time efficiency. All algorithms can be downloaded from https://github.com/wuc567/Pattern Mining/tree/master/OUTO-Miner.

---

#### Datasets:
[Dataset]( https://github.com/wuc567/Pattern-Mining/tree/master/OUTO-Miner/datasets)

#### Algorithms:

[OUTO-Miner and all competitive algorithms]( https://github.com/wuc567/Pattern-Mining/tree/master/OUTO-Miner/algorithms)
