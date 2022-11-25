## NTP-Miner: Nonoverlapping three-way sequential pattern mining
***

Youxi Wu, Lanfang  Luo, Yan Li, Lei Guo, Philippe Fournier-Viger, Xingquan Zhu, Xindong Wu. NTP-Miner: Nonoverlapping three-way sequential pattern mining

#### Abstract:

Nonoverlapping sequential pattern mining is an important type of sequential pattern mining with gap constraints, which not only can reveal interesting patterns to users but also can effectively reduce the search space using the Apriori (anti-monotonicity) property. However, existing algorithms do not focus on attributes of interest to users, meaning that existing methods may discover many frequent patterns that are redundant. To solve this problem, this paper proposes a task called nonoverlapping three-way sequential pattern (NTP) mining, where attributes are categorized according to three levels of interest: strong, medium and weak interest. NTP mining can effectively avoid mining redundant patterns since the NTPs are composed of strong and medium interest items. Moreover, NTPs can avoid serious deviations (the occurrence is significantly different from its pattern) since gap constraints cannot match with strong interest patterns. To effectively mine NTPs, an effective algorithm is put forward, called NTP-Miner, which applies two main steps: support (frequency occurrence) calculation and candidate pattern generation. To calculate the support of a NTP, depth-first and backtracking strategies are adopted, which do not require creating a whole Nettree structure, meaning that many redundant nodes and parent-child relationships do not need to be created. Hence, time and space efficiency is improved. To generate candidate patterns while reducing their number, NTP-Miner employs a pattern growth strategy and only mines patterns of strong and medium interest. Experimental results show that NTP-Miner is not only more efficient than compared approaches but can also help users in finding more valuable patterns. Algorithms and data are available at: https://github.com/wuc567/Pattern-Mining/blob/master/NTP-Miner.

---

#### Algorithms:
[C++](https://github.com/wuc567/Pattern-Mining/blob/master/NTP-Miner/C++)

[Python](https://github.com/wuc567/Pattern-Mining/blob/master/NTP-Miner/Python)
 
#### Datasets:
[Dataset](https://github.com/wuc567/Pattern-Mining/blob/master/NTP-Miner/Dataset)

#### Paper:
[NTP-Miner](https://github.com/wuc567/Pattern-Mining/blob/master/NTP-Miner/2022tkdd.pdf)