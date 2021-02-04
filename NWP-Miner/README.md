## NWP-Miner: Nonoverlapping weak-gap sequential pattern mining
***

Youxi Wu, Zhu Yuan, Yan Li, Lei Guo, Philippe Fournier-Viger, Xindong Wu. NWP-Miner: Nonoverlapping weak-gap sequential pattern mining

#### Abstract:

Nonoverlapping sequential pattern mining (SPM) is a type of repetitive SPM with gap constraints that can effectively mine valuable information. One of the disadvantages of nonoverlapping SPM is that any characters can be matched by the gap constraints, which may cause a large deviation (the occurrence is significantly different from its pattern). To tackle this issue, we propose nonoverlapping weak-gap sequential pattern (NWP) mining, which divides all characters into strong and weak types. This method can mine frequent patterns more accurately and efficiently by limiting the gap constraints to match only weak characters. To discover NWPs, an effective algorithm called NMP-Miner is proposed, which involves two key steps: support calculation and candidate pattern generation. To calculate the support (number of occurrences), depth-first search and backtracking strategies based on a simplified Nettree structure are adopted, which effectively reduce the time and space complexities of the algorithm. A pattern growth method is then applied to effectively reduce the number of candidate patterns. Our experiments show that NWP-Miner is not only more efficient than other competitive algorithms but can also discover more meaningful patterns. More importantly, experiments on data from the Dow Jones stock index show that NMP-Miner can help users analyze the range of fluctuation in the stock market by mining NWPs. The algorithms and data can be downloaded from https://wuc567.github.io/Wu-Youxi/index.

---

#### Datasets:
[Dataset](https://github.com/wuc567/Pattern-Mining/blob/master/NWP-Miner/DataSet.rar)  (All sequences)


#### Algorithms:

[NWP-Miner and all competitive algorithms](https://github.com/wuc567/Pattern-Mining/blob/master/NWP-Miner/NWP-Miner_code.rar)
 

