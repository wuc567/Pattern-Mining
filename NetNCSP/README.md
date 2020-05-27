## NetNCSP: Nonoverlapping closed sequential pattern mining
***

Youxi Wu, Changrui Zhu, Yan Li, Lei Guo, Xindong Wu. NetNCSP: Nonoverlapping closed sequential pattern mining. Knowledge-Based Systems. 2020:105812. DOI: 10.1016/j.knosys.2020.105812.

#### Abstract:

Nonoverlapping sequential pattern mining means that any two occurrences cannot use the same sequence letter in the same position of the occurrences. This method can be used to find subsequences with a certain gap, and solve the key problem to make a balance between efficiency and completeness which cannot be handled by other methods. The frequent pattern set discovered by existing methods normally contains redundant patterns, which are too many to be analyzed. In order to reduce redundant patterns to obtain the lossless compression of frequent patterns, this paper adopts the closed pattern mining strategy and proposes a complete algorithm NetNCSP (Nettree for Nonoverlapping Closed Sequential Pattern) based on Nettree structure. NetNCSP is equipped with two key steps: support calculation and closeness determination. This paper employs backtracking strategy to calculate the nonoverlapping support of a pattern on the corresponding Nettree, which reduces the time complexity. This paper also proposes three kinds of pruning strategies: inheriting, predicting, and determining. These pruning strategies are able to find the redundant patterns effectively, since the strategies can predict the frequency and closeness of the patterns before the generation of the candidate patterns. We show that NetNCSP is a complete algorithm which satisfies the Apriori property. A large number of comparative experiments show that NetNCSP is not only more efficient, but also can discover more closed patterns with good compressibility.

---

#### Datasets:

[Datasets](https://github.com/wuc567/Pattern-Mining/blob/master/NetNCSP/DataSet.rar)  (All sequences)

#### Algorithms:

[NetNCP and all competitive algorithms](https://github.com/wuc567/Pattern-Mining/blob/master/NetNCSP/NetNCSP_code.rar)
