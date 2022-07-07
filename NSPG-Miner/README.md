## NSPG-Miner: Negative sequential pattern mining with gap constraints
***
 
Youxi Wu, Zhulin Wang, Yan Li, Jing Liu, Lei Guo, Philippe Fournier-Viger, Xindong Wu.

#### Abstract:

 Sequential pattern mining (SPM) with gap constraints can find frequently repetitive subsequences satisfying gap constraints. However, classical SPM with gap constraints focuses on mining frequent events in a series of events and cannot find the missing events. To tackle this issue, this paper explores the negative sequential pattern with gap constraints (NSPG), which can reflect the missing events more flexibly. In this paper, we propose an efficient NSPG-Miner algorithm that can mine both frequent positive sequential patterns with gap constraints and NSPGs at the same time. NSPG-Miner adopts a pattern join strategy to effectively reduce candidate patterns. Moreover, NSPG-Miner employs a key-value pair array structure to calculate the support (frequency of occurrence) of a pattern in each sequence. Experimental results not only validate the effectiveness of the strategies adopted by NSPG-Miner, but also verify that NSPG-Miner can find more negative patterns than other state-of-the-art algorithms. 
 
---

#### Algorithms:

[NSPG-Miner and all competitive algorithm](https://github.com/wuc567/Pattern-Mining/tree/master/NSPG-Miner/algorithms)

#### Datasets:
[Datasets](https://github.com/wuc567/Pattern-Mining/tree/master/NSPG-Miner/datasets)  