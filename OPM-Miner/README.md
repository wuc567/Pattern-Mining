## OPM-Miner: One-off Pattern Mining for Multivariate Time Series

Youxi Wu, Yaqi Liu, Yan Li, Jing Liu, Cong Shen, Yazhou Zhang, and Xindong Wu

***

#### Abstract:
A time series is a common form of data that contains a wealth of valuable information. Sequential pattern mining (SPM) methods can be used to analyze this type of series; however, traditional SPM methods mainly focus on analyzing one-dimensional time series, and it is difficult to analyze multivariate time series. More importantly, multivariate time series may interact with each other. With the aim of discovering frequent sequence patterns in multivariate time series and the correlations between variables, this paper addresses the problem of one-off SPM for multivariate time series (OPM) and presents the OPM-Miner algorithm. At the data preprocessing stage, the original multivariate time series is converted into binary inverted dictionaries to avoid the need to scan the original database. To reduce the number of candidate patterns, OPM-Miner employs an itemset pattern join strategy. At the support calculation stage, we introduce strategies for pruning infrequent items and bit index sliding, and develop strategies called Over and Under to further improve the efficiency of support calculation. This paper selected 10 competitive algorithms and 16 real-life multivariate databases to verify the performance of OPM-Miner. The experimental results presented here show that OPM-Miner outperforms other competitive algorithms. More importantly, OPM-Miner can be used in the field of air pollution detection, as it reveals the interactive relationships between various air pollutants, and can be used to predict future trends in air pollutants. 

---

#### Datasets:
[Dataset](https://github.com/wuc567/Pattern-Mining/blob/master/OPM-Miner/DataSets)

#### Algorithms:

[MCoR-Miner and all competitive algorithms](https://github.com/wuc567/Pattern-Mining/blob/master/OPM-Miner/Algorithms)
 

