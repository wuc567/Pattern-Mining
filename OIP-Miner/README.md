## OIP-Miner: One-off Incremental Sequential Pattern Mining with Forgetting Factor

Youxi Wu, Shuang Tian, Yan Li, Jing Liu, and Xindong Wu 

***

#### Abstract:
In sequential pattern mining (SPM), when a database is incremented, sequential patterns also need to be dy-namically maintained. An incremental SPM method has therefore been proposed which can avoid the need for brute-force mining of all sequences. Classical incremental SPM methods only consider whether or not a pattern occurs in a sequence, and ignore the number of occurrences in the sequence. Moreover, in some time-sensitive applications, more recent data are generally believed to be more valuable. Inspired by the forgetting mechanism, this paper focuses on one-off incremental sequential pattern (OIP) mining with forgetting factor, in which the supports of patterns in older data will gradually decline. To tackle the problem of OIP mining, we propose the OIP-Miner algorithm. To reduce the number of candidate patterns, OIP-Miner employs an ‘itemset pattern join plus’ strategy and four pruning strategies based on S-join and I-join. To efficiently calculate the supports, OIP-Miner constructs a monomial search dictionary based on an inverted dictionary. To improve the efficiency of incremental pattern mining, OIP-Miner mines only incremental data based on a global pattern dictionary. To verify the performance of OIP-Miner, nine competitive algorithms and 16 databases are selected. Experimental results on real databases show that OIP-Miner outperforms other competitive algorithms. More importantly, recommendations made with the forgetting factor have a higher recommendation confidence.

---

#### Datasets:
[Dataset](https://github.com/wuc567/Pattern-Mining/blob/master/OIP-Miner/DataSets)

#### Algorithms:

[OIP-Miner and all competitive algorithms](https://github.com/wuc567/Pattern-Mining/blob/master/OIP-Miner/Algorithms)
 

