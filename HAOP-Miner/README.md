## HAOP-Miner: Self-adaptive high-average utility one-off sequential pattern mining
***

Youxi Wu, Rong  Lei, Yan Li, Lei Guo, Xindong Wu. HAOP-Miner: Self-adaptive high-average utility one-off sequential pattern mining

#### Abstract:
One-off sequential pattern mining (SPM) (or SPM under the one-off condition) is a kind of repetitive SPM with gap constraints, and has been widely applied in many fields. However, current research on one-off SPM ignores the utility (can be price or profit) of items, resulting in some low-frequency but extremely important patterns being ignored. To solve this issue, this paper addresses self-adaptive High-Average utility One-off sequential Pattern (HAOP) mining which has following three characteristics. Any two occurrences cannot share any letter in the sequence. The support (number of occurrences), utility and length of the pattern are considered simultaneously. The HAOP mining discovers patterns with a self-adaptive gap which means that users do not need to set the gap constraints. We propose an effective algorithm called HAOP-Miner that involves two key steps: support calculation and candidate pattern generation. For the support calculation, we propose a heuristic algorithm named the Reverse filling (Rf) algorithm that can effectively calculate the support by avoiding creating redundant nodes and pruning the redundant and useless nodes after finding an occurrence. Since HAOP mining does not satisfy the Apriori property, a support lower bound method combined with the pattern growth strategy is adopted to generate the candidate patterns. The experimental results first validate the effectiveness of HAOP-Miner, and then demonstrate that HAOP-Miner has better performance than other state-of-the-art algorithms. More importantly, HAOP-Miner is easier to mine valuable patterns.

---

#### Algorithms:
[C++](https://github.com/wuc567/Pattern-Mining/blob/master/HAOP-Miner/C++)

[Python](https://github.com/wuc567/Pattern-Mining/blob/master/HAOP-Miner/Python)
 
#### Datasets:
[Dataset](https://github.com/wuc567/Pattern-Mining/blob/master/HAOP-Miner/Dataset)

#### Paper:
[HAOP-Miner](https://github.com/wuc567/Pattern-Mining/blob/master/HAOP-Miner/haop-miner.pdf)