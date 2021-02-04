## SNP-Miner: Self-Adaptive Nonoverlapping Sequential Pattern Mining 
***

Yuehua Wang, Youxi Wu, et al. SNP-Miner: Self-adaptive sequential pattern mining

#### Abstract:

As a kind of repetitive SPM with gap constraints, nonoverlapping sequential pattern mining (SPM) not only can avoid mining too many meaningless patterns but also flexibly satisfies the users’ needs. However, it is difficult for the existing algorithms to give a suitable gap without prior knowledge. More importantly, the existing algorithms are inefficient since they have to constantly determine whether the gap meets the requirements or not. To tackle these issues, this paper adopts self-adaptive mining strategy which generates gap according to the sequence and proposes a complete algorithm, named SNP-Miner. SNP-Miner is equipped with two key phases: candidate generation and support calculation. To effectively reduce the candidate patterns, SNP-Miner employs the pattern growth strategy. This paper also proposes incomplete Nettree structure stored in an array to efficiently calculate the support in one-way scanning, which avoids redundant calculation and reduces the time complexity. Experimental results show that SNP-Miner is not only more efficient, but can also discovers more valuable patterns without gap constraints.



---

#### Datasets:
[Dataset](https://github.com/wuc567/Pattern-Mining/blob/master/SNP-Miner/DataSet.zip)  (All sequences)


#### Algorithms:

[SNP-Miner and all competitive algorithms](https://github.com/wuc567/Pattern-Mining/blob/master/SNP-Miner/SNP-Miner_code.zip)
 

