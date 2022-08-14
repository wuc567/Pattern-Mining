## MCoR-Miner: Maximal co-occurrence nonoverlapping sequential rule mining
***

#### Abstract:
The aim of sequential pattern mining (SPM) is to discover potentially useful information from a given sequence. Although various SPM methods have been investigated, most of these focus on mining all of the patterns that satisfy the predefined constraints. However, users sometimes have certain prior knowledge, and want to mine patterns with the same specific prefix pattern, rather than all patterns. Since sequential rule mining can make better use of the results of SPM, avoid mining excessive patterns or rules and obtain better recommendation performance, this paper addresses the issue of maximal co-occurrence nonoverlapping sequential rule (MCoR) mining and proposes the MCoR-Miner algorithm. In addition to the support calculation, MCoR-Miner consists of three parts: a filtering strategy, candidate pattern generation, and a screening strategy. To improve the efficiency of support calculation, we propose an algorithm that employs a depth-first search and backtracking   with an indexing mechanism to avoid the use of sequential searching. To obviate useless support calculations for some sequences, we explore the use of a filtering strategy to prune the sequences without the prefix pattern (or rule-antecedent). To reduce the number of candidate patterns, we apply the frequent item and binomial enumeration tree strategies. To avoid searching the maximal rules through brute force, we explore the use of a screening strategy. Experiments were conducted on eight sequences, and nine competitive algorithms were considered. Our experimental results showed that MCoR-Miner yielded better running performance and scalability than other competitive algorithms,  and better recommendation performance than frequent co-occurrence pattern mining.

---

#### Datasets:
[Dataset](https://github.com/wuc567/Pattern-Mining/blob/master/MCoR-Miner/DataSets)

#### Algorithms:

[MCoR-Miner and all competitive algorithms](https://github.com/wuc567/Pattern-Mining/blob/master/MCoR-Miner/Algorithms)
 

