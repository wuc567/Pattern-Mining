##  FLE-Miner: Federated one-off correlated low average cost episodes mining for process event logs

Zhihong Dong, Youxi Wu, and Jing Liu

####  Abstract：
Low average cost episode mining is an emerging research topic in data mining, which is introduced to evaluate episodes based on average costs. Unlike high utility episode mining, this task focuses on cost minimization. More importantly, current researches face the dilemma of data silos and fail to integrate multi-source data to generate comprehensive insights with preserving privacy. In light of these shortages, we focus on mining federated one-off correlated low average cost episodes (FLE). A method called FLE-Miner is proposed, which comprises two main modules: client mining and server aggregation. For client mining, we adopt the event splitting strategy to preprocess the client local logs and employ depth-first search and backtracking strategies based on event index to identify all occurrences of episodes. For server aggregation, we introduce a pruning strategy and an average cost lower bound to prune unpromising candidate episodes in advance. Additionally, we design the screening and episode merge strategies to generate merged episode sets for each client. Experimental results demonstrate that FLE-Miner outperforms baseline methods. More importantly, a case study shows the application of FLE-Miner to an industrial log, successfully discovering low average cost paths from multiple client logs without uploading raw data, thereby supporting client process optimization. All algorithms can be downloaded from https://github.com/wuc567/Pattern-Mining/tree/master/FLE-Miner.

---

#### Algorithms:
[FLE-Miner and all competitive algorithm](https://github.com/wuc567/Pattern-Mining/tree/master/FLE-Miner/code)

#### Datasets:
[Datasets](https://github.com/wuc567/Pattern-Mining/tree/master/FLE-Miner/dataset)
