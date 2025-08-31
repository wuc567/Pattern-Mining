##  HACE-Miner: Mining high average utility co-occurrence intermittent overlapping episodes

Yan Li, Zhenyu Rong, Jing Liu, Philippe Fournier-Viger, Youxi Wu

####  Abstract：
Episode mining can discover potentially useful information from a given sequence of events. High utility episode mining methods can mine episodes with low frequency but high utility. However, long episode can lead to high utility. More importantly, users are sometimes only interested in episodes with the same preffx, that is, co-occurrence episodes. To overcome these shortages, this paper develops a method of high average utility co-occurrence overlapping episode (HACE) mining, and presents an algorithm called HACE-Miner. To improve the efffciency of support calculation, HACE-Miner establishes an episode position index in combination with depth-ffrst search and index backtracking strategies to avoid redundant searches. To reduce the number of sequences in the database, HACEMiner adopts a pre-screening strategy to prune redundant sequences without preffx episodes. To reduce the number of candidate episodes, HACE-Miner employs a single episode pruning strategy and a binomial high average utility upper bound episode pruning strategy. To verify the performance of HACE-Miner, experiments are conducted on eight datasets and eight competitive algorithms. The experimental results indicate that HACE-Miner outperforms other competitive algorithms and yields better recommendation performance. 

---

#### Algorithms:
[HACE-Miner and all competitive algorithm](https://github.com/wuc567/Pattern-Mining/tree/master/HACE-Miner/code)

#### Datasets:
[Datasets](https://github.com/wuc567/Pattern-Mining/tree/master/HACE-Miner/datasets)
