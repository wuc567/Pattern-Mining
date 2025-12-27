##  FGE-Miner: Federated one-off general episodes mining for process event logs

Zhihong Dong, Jing Liu, Youxi Wu

####  Abstract：
Frequent episode mining is a significant component within the field of sequence mining research, aiming to capture temporal dependencies in data. Most existing studies on frequent episode mining can only handle simple event sequences and struggle with complex event sequences, which are more common in real-world scenarios. Furthermore, traditional federated mining algorithms suffer from the problem of incomplete mining results. To address these, we focus on mining federated one-off general episodes (FGE). A method called FGE-Miner is proposed, which primarily consists of two modules: client mining and server aggregation. In client mining, we propose extension pruning and suffix pruning strategies to reduce candidate episodes. Additionally, we utilize depth-first search and backtracking strategies based on independent episode index to discover the one-off occurrences of episodes. In server aggregation, we propose aggregation pruning, rescanning, and upper bound strategies, which selectively query specific clients to guarantee the completeness of the final mining results. Experimental results show that FGE-Miner is over 10 times faster than the baseline algorithms. More importantly, a case study demonstrates the application of FGE-Miner on employee activity logs, which successfully mined behavioral episodes from unstructured logs across multiple clients, thereby providing insights for identifying non-compliant operations. All algorithms can be downloaded from https://github.com/wuc567/Pattern-Mining/tree/master/FGE-Miner.

---

#### Algorithms:
[FGE-Miner and all competitive algorithm](https://github.com/wuc567/Pattern-Mining/tree/master/FGE-Miner/code)

#### Datasets:
[Datasets](https://github.com/wuc567/Pattern-Mining/tree/master/FGE-Miner/dataset)
