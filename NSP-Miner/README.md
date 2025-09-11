## NSP-Miner: Mining nonoverlapping skyline frequent-utility patterns in sequential database
***
 
Meng Geng, Youxi Wu, Yan Li, Jing Liu, Cong Liu, Jinyan Li, Xindong Wu.

#### Abstract:

 In the area of sequential pattern mining, consideration of the frequency or utility alone is insufficient for decision-making, since the frequent patterns discovered in this way may have low utilities, while the high-utility patterns may have low supports. Although skyline frequent-utility pattern mining can mine patterns with both high support and high utility, this method mines patterns only from simple itemset databases. To address this issue, we focus on the problem of mining nonoverlapping skyline frequent-utility patterns (NSPs) in sequential databases, and propose an algorithm called NSP-Miner. To reduce the need for repeated scanning of the database, we utilize a binary dictionary to store the positions of items, and adopt iterative binary operations to efficiently calculate the support. In addition, we propose a 0-Simplify strategy and a 1-Termination strategy to determine whether the iteration can be simplified and terminated early, respectively. At the candidate pattern generation stage, we adopt a dictionary structure to record the maximum utility for each support, and use a pattern join strategy to reduce the number of candidate patterns. Compared with alternative algorithms, the experimental results on eight databases show that NSP-Miner gives superior results. We also employ the information gain as the utility for each item, and find that use of NSPs as features can improve the clustering performance. All of the algorithms and databases considered here are available from https://github.com/wuc567/Pattern-Mining/tree/master/NSP-Miner.
---

#### Algorithms:

[NSP-Miner and all competitive algorithm](https://github.com/wuc567/Pattern-Mining/tree/master/NSP-Miner/code)

#### Datasets:
[Datasets](https://github.com/wuc567/Pattern-Mining/tree/master/NSP-Miner/dataset)  
