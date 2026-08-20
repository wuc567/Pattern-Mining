## WOPP-Miner: Window-based order-preserving pattern mining
***

Yajie Zhang, Youxi Wu, Cong Liu, Jinyan Li, Yan Li. WOPP-Miner: Window-based order-preserving pattern mining

#### Abstract:

Order-preserving pattern (OPP) mining is a sequential pattern mining method designed to discover frequent trends in time series. In many applications, continuously arriving time series need to be analyzed over windows. Traditional OPP mining methods mostly involve inefficient candidate generation and support calculation, which incur high cost for multiple windows. To effectively mine frequent patterns with windows, this paper presents an algorithm called WOPP-Miner, which consists of two main parts, candidate pattern generation and support calculation, using block windows strategy. In candidate pattern generation, we propose a dictionary-based strategy, which eliminates a large number of redundant prefix and suffix calculations, and brute-force enumeration operations for pattern matching. In support calculation, we represent occurrences as binary vectors and perform bitwise operations to accelerate the mining process. We select 12 datasets and eight competitive algorithms for experiments, and show that WOPP-Miner is about 4.24 to 52.75 times faster than the state-of-the-art algorithms. More importantly, we use OPPs in each window for concept drift detection tasks, and extract uptrend and downtrend OPPs for interpretability, demonstrating WOPP-Miner is well suited for drift detection and interpretation. 
