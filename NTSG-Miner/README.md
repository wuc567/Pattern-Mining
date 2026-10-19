**Nonoverlapping Three-Way Sequential Pattern Mining with Self-Adaptive
Gap Constraints**


Sana Ejaz Hashmi, Youxi Wu, 

#### Abstract:
Abstract 
Nonoverlapping sequential pattern mining (SPM) with gap constraints can effectively discover useful information from sequences. However, without prior knowledge, it is hard to set a suitable gap constraint. Therefore, users usually find appropriate constraints by trial and error, which is a time-consuming process. Although existing self-adaptive gap methods avoid this issue, they do not differentiate characters based on their level of interest to users, meaning many redundant patterns may be discovered. Three-way methods solve this redundancy with fixed gap constraints. To address these problems, this paper proposed nonoverlapping three-way sequential pattern mining with self-adaptive gap constraints, composed of strong, medium, and weak characters according to the level of interest. The proposed algorithm NTSG-Miner has three steps: data preprocessing, support calculation, and candidate pattern generation. At the preprocessing step, NTSG-Miner creates an inverted index, a prefix-Γ counter, and a binomial search list for each character pair to avoid brute-force matching. At the support calculation step, we employ a binomial search list to generate valid occurrence spans, achieving speedups ranging from 1.8× to 117.7× on the benchmark datasets. At the candidate generation step, prefix-suffix matching to reduce the number of candidate patterns and employ pruning strategies eliminate infrequent patterns. The experimental results demonstrate that NTSG-Miner outperforms the competitive methods.

