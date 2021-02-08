## NWP-Miner: Nonoverlapping weak-gap sequential pattern mining
***

Youxi Wu, Zhu Yuan, Yan Li, Lei Guo, Philippe Fournier-Viger, Xindong Wu. NWP-Miner: Nonoverlapping weak-gap sequential pattern mining

#### Abstract:

Nonoverlapping sequential pattern mining (SPM) is a type of repetitive SPM with gap constraints that can effectively mine valuable information in sequences of characters. One of the disadvantages of nonoverlapping SPM is that any characters can match with gap constraints. Hence, there can be large deviation between a pattern and its occurrences. To tackle this issue, we propose nonoverlapping weak-gap sequential pattern (NWP) mining, where characters are divided into two types: weak and strong characters. This allows discovering frequent patterns more accurately by limiting the gap constraints to match only weak characters. To discover NWPs, an efficient algorithm called NMP-Miner is proposed, which involves two key steps: support calculation and candidate pattern generation. To calculate the support (number of occurrences) of candidate patterns, depth-first search and backtracking strategies based on a simplified Nettree structure are adopted, which effectively reduce the time and space complexities of the algorithm.  Moreover, a pattern growth approach is applied to effectively reduce the number of candidate patterns. The experiments show that NWP-Miner is not only more efficient than other competitive algorithms but can also discover more meaningful patterns. In addition, NWPs discovered in data from the Dow Jones stock index show that NMP-Miner can help users analyze the range of fluctuation in the stock market. Algorithms and data can be downloaded from https://github.com/wuc567/Pattern-Mining/tree/master/NWP-Miner.

---

#### Datasets:
[Dataset](https://github.com/wuc567/Pattern-Mining/blob/master/NWP-Miner/DataSet.rar)  (All sequences)


#### Algorithms:

[NWP-Miner and all competitive algorithms](https://github.com/wuc567/Pattern-Mining/blob/master/NWP-Miner/NWP-Miner_code.rar)
 

