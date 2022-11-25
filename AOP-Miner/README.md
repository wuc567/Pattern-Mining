##  AOP-Miner：Approximate Order-Preserving Pattern Mining for Time-Series

Yan Li, Jin Liu,  Yingchun Guo, Jing Liu, Youxi Wu 

####  Abstract：
In an order-preserving pattern, the rank of each value in the time series is used to represent the pattern. Order-preserving pattern mining aims to mine frequent subsequences with the same trend from a time series, since the same order-preserving patterns have the same trends. However, in the case where data noise is present, the trends of many meaningful patterns are usually similar rather than the same. To mine the similar trends in time-series, this paper addresses an approximate order-preserving pattern (AOP) mining method based on (δ-γ) distance, and proposes an algorithm called AOP-Miner to mine AOPs according to global and local approximation parameters. AOP-Miner has two key steps, candidate pattern generation and pattern support calculation. To generate the candidate patterns, the AOP-Miner algorithm adopts a pattern fusion strategy based on prefix and suffix splicing, which reduces the number of meaningless candidate patterns. To calculate the pattern support, the AOP-Miner algorithm employs the
screening strategy to find the candidate occurrences of a super pattern based on the occurrences of sub patterns and uses the pruning strategy to further prune the number of candidate patterns. Therefore, the screening and pruning strategies can significantly improve mining performance. Experimental results validate that AOP-Miner outperforms other competitive methods and can find more similar trends in time series.

---

#### Algorithms:
[AOP-Miner and all competitive algorithm](https://github.com/wuc567/Pattern-Mining/tree/master/AOP-Miner/algorithms)

#### Datasets:
[Datasets](https://github.com/wuc567/Pattern-Mining/tree/master/AOP-Miner/datasets)
