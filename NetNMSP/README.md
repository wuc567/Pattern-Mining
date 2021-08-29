NetNMSP: Nonoverlapping maximal sequential pattern mining
Yan Li, Shuai Zhang, Lei Guo, Jing Liu, Youxi Wu*, Xindong Wu

Abstract: Nonoverlapping sequential pattern mining, as a kind of repetitive sequential pattern mining with gap constraints, can find more valuable patterns. Traditional algorithms focused on finding all frequent patterns and found lots of redundant short patterns. However, it not only reduces the mining efficiency, but also increases the difficulty in obtaining the demand information. To reduce the frequent patterns and retain its expression ability, this paper focuses on the Nonoverlapping Maximal Sequential Pattern (NMSP) mining which refers to finding frequent patterns whose super-patterns are infrequent. In this paper, we propose an effective mining algorithm, Nettree for NMSP mining (NetNMSP), which has three key steps: calculating the support, generating the candidate patterns, and determining NMSPs. To efficient calculate the support, NetNMSP employs the backtracking strategy to get a nonoverlapping occurrence from the leftmost leaf to its root with the leftmost parent node method in a Nettree. To reduce candidate patterns, NetNMSP generates candidate patterns by the pattern join strategy. Furthermore, to determine NMSPs, NetNMSP adopts the screening method. Experiments on biological sequence datasets verify that not only does NetNMSP outperform the state-of-the-arts algorithms, but also NMSP mining has better compression performance than closed pattern mining. 


---

#### Datasets:
[Dataset](https://github.com/wuc567/Pattern-Mining/blob/master/NetNMSP/DataSet.rar)  (All sequences)

#### Algorithms:

[NetNMSP and all competitive algorithms](https://github.com/wuc567/Pattern-Mining/blob/master/NetNMSP/NetNMSP_codes.rar)
