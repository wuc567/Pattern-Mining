## OPF-Miner: Order-preserving pattern mining with forgetting mechanism for time-series

Yan Li, Chenyu Ma, Rong Gao, Youxi Wu, Jinyan Li, Wenjian Wang, and Xindong Wu

***

#### Abstract:
Order-preserving pattern (OPP) mining is a type of sequential pattern mining method in which a group of ranks of time series is used to represent an OPP. This approach can discover frequent trends in time series. Existing OPP mining algorithms consider data points at different time to be equally important; however, newer data usually have a more significant impact, while older data have a weaker impact. We therefore introduce the forgetting mechanism into OPP mining to reduce the importance of older data. This paper explores the mining of OPPs with a forgetting mechanism (OPF) and proposes an algorithm called OPF-Miner that can discover frequent OPFs. OPF-Miner performs two tasks, candidate pattern generation and support calculation. At the candidate pattern generation stage, OPF-Miner employs a maximal support priority strategy and a group pattern fusion strategy to avoid redundant pattern fusions. For the support calculation stage, we propose an algorithm called support calculation with forgetting mechanism, which uses prefix and suffix pattern pruning strategies to avoid redundant support calculations. The completeness of these pruning strategies is proved, and experiments are conducted on nine datasets and 12 alternative algorithms. The results verify that OPF-Miner is superior to other competitive algorithms. More importantly, OPF-Miner yields good clustering performance for time series data, since the forgetting machanism is employed.

---

#### Datasets:
[Dataset](https://github.com/wuc567/Pattern-Mining/blob/master/OPF-Miner/DataSets)

#### Algorithms:

[MCoR-Miner and all competitive algorithms](https://github.com/wuc567/Pattern-Mining/blob/master/OPF-Miner/Algorithms)
 

