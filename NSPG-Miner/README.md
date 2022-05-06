## NSPG-Miner: Negative sequential pattern mining with gap constraints
***
 
Youxi Wu, Zhulin Wang, Yan Li, Jing Liu, Lei Guo, Philippe Fournier-Viger, Xindong Wu.

#### Abstract:

 Sequential pattern mining (SPM) with gap constraints can reveal the common sub-sequences at a certain interval by setting a gap. However, classical SPM with gap constraints focuses on mining frequent behaviors in a series of events and cannot find the missing behaviors. To tackle this issue, this paper explores the negative sequential pattern with gap constraints (NSPG), which can reflect missing behaviors more flexibly. In this paper, we propose an efficient NSPG-Miner algorithm that can mine both frequent positive sequential patterns with gap constraints and NSPGs at the same time. NSPG-Miner adopts a pattern join strategy to effectively reduce candidate patterns. Moreover, NSPG-Miner employs a key-value pair array structure to calculate the support (frequency of occurrence) of a pattern in each sequence. Experimental results not only validate the effectiveness of the strategies adopted by NSPG-Miner, but also verify that NSPG-Miner can find more meaningful patterns than other state-of-the-art algorithms.
This study expands the semantics and application fields of SPM. The algorithms and data can be downloaded https://github.com/wuc567.
 
---

#### Algorithms:

[NSPG-Miner and all competitive algorithm](https://github.com/wuc567/Pattern-Mining/tree/master/NSPG-Miner/algorithms)

#### Datasets:
[Datasets](https://github.com/wuc567/Pattern-Mining/tree/master/NSPG-Miner/datasets)  