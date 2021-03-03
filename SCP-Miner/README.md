## SCP-Miner: Top-k Self-adaptive Contrast Sequential Pattern Mining
***

Youxi Wu, Yuehua Wang, Yan Li*, Xingquan Zhu, Xindong Wu. SNP-Miner: Self-Adaptive Nonoverlapping Sequential Pattern Mining

#### Abstract:

For sequence classification, an important issue is to find discriminative features, where sequential pattern mining (SPM) is often used to find frequent patterns from sequences as features. To improve classification accuracy and pattern interpretability, contrast pattern mining emerges to discover patterns with high contrast rates between different categories. To date, existing contrast SPM methods face many challenges, including excessive parameter selections and inefficient occurrences counting. To tackle these issues, this paper proposes a top-k self-adaptive contrast SPM, which adaptively adjusts the gap constraints to find top-k self-adaptive contrast patterns (SCPs) from positive and negative sequences. One of the key tasks of the mining problem is to calculate the support (the number of occurrences) of a pattern in each sequence. To support efficient counting, we store all occurrences of a pattern in a special array in a Nettree, an extended tree structure with multiple roots and multiple parents. We employ the array to calculate the occurrences of all its super-patterns with one-way scanning to avoid redundant calculation. Meanwhile, because the contrast SPM problem does not satisfy the Apriori property, we propose Zero and Less strategies to prune candidate patterns and a Contrast-first mining strategy to select patterns with the highest contrast rate as the prefix sub-pattern and calculate the contrast rate of all its super-patterns. Experiments validate the efficiency of the proposed algorithm, and show that contrast patterns significantly outperform frequent patterns for sequence classification. Algorithms and data can be downloaded from https://github.com/wuc567/Pattern-Mining/tree/master/SCP-Miner.

---

#### Datasets:
[Dataset](https://github.com/wuc567/Pattern-Mining/blob/master/SCP-Miner/DataSet.zip)  (All sequences)


#### Algorithms:

[SCP-Miner and all competitive algorithms](https://github.com/wuc567/Pattern-Mining/blob/master/SCP-Miner/SCP-Miner_code.zip)
 

