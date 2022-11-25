## SNP-Miner: Self-Adaptive Nonoverlapping Sequential Pattern Mining 
***

Yuehua Wang, Youxi Wu*, Yan Li, Fang Yao, Philippe Fournier-Viger, Xindong Wu. SNP-Miner: Self-Adaptive Nonoverlapping Sequential Pattern Mining

#### Abstract:

As a type of repetitive SPM with gap constraints, nonoverlapping sequential pattern mining (SPM) can not only avoid mining too many meaningless patterns, but can also be used in a flexible way to meet the user’s needs. However, it is difficult for existing algorithms to identify a suitable gap without prior knowledge. More importantly, existing algorithms are inefficient, since they constantly need to determine whether or not the gap constraint meets the requirements. To tackle these issues, this paper presents a complete algorithm called SNP-Miner that has two key phases: generation of candidate patterns, and calculation of the supports (occurrence frequency) of these candidate patterns. To effectively reduce the number of candidate patterns, SNP-Miner employs a pattern growth strategy. We also propose the use of an incomplete Nettree structure that is stored in an array to efficiently calculate the support via one-way scanning, which avoids redundant calculations and reduces the time complexity. Experimental results show that SNP-Miner is not only more efficient than alternative approaches but can also discover more valuable patterns without gap constraints. Algorithms and data can be downloaded from https://github.com/wuc567/Pattern-Mining/tree/master/SNP-Miner.



---

#### Algorithms:
[C++](https://github.com/wuc567/Pattern-Mining/blob/master/SNP-Miner/C++)

[Python](https://github.com/wuc567/Pattern-Mining/blob/master/SNP-Miner/Python)
 
#### Datasets:
[Dataset](https://github.com/wuc567/Pattern-Mining/blob/master/SNP-Miner/Dataset)

#### Paper:
[SNP-Miner](https://github.com/wuc567/Pattern-Mining/blob/master/SNP-Miner/Self-adaptiveNonoverlappingSeq.pdf)