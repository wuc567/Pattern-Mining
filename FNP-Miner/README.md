## FNP-Miner: Fuzzy three-way nonoverlapping sequential pattern Mining
***

Youxi Wu, Yunda Qiao, Jing Liu, Yan Li, Cong Liu, Jianguo Wei, and Wenjian Wang

#### Abstract:

In sequential pattern mining (SPM), three-way SPM aims to reduce redundant patterns by classifying items into weak, medium, and strong groups, mining only patterns of medium and strong items with no strong items in pattern gaps. However, this approach requires users to categorize the items manually, producing discrete results with undetermined boundaries, and its rigid gap constraint overfilters valid patterns. To address this problem, based on item frequency and user interest, we mine fuzzy three-way nonoverlapping sequential patterns (FNPs) with flexible quantitative gap constraints, and propose an algorithm called FNP-Miner. 
FNP mining does not satisfy the anti-monotonicity property, and we overcome this limitation by deriving a fuzzy support upper bound and designing a pruning strategy to effectively reduce the number of candidate patterns. Furthermore, to enhance the efficiency of fuzzy support computation, the support of a pattern is calculated using the occurrence information of its subpatterns based on an inverted index structure. To evaluate the performance of FNP-Miner, we compare it with 13 competitive algorithms on eight benchmark datasets, and propose two indicators to measure the interest degree of patterns and gaps. The experimental results show that FNP-Miner finds patterns that are more preferred by the user, and achieves better performance than the compared algorithms.
---

#### Algorithms:

[FNP-Miner and all competitive algorithms](https://github.com/wuc567/Pattern-Mining/tree/master/FNP-Miner/tree/main/Algorithms)

#### Databases:
[Databases](https://github.com/wuc567/Pattern-Mining/tree/master/FNP-Miner/Databases)
