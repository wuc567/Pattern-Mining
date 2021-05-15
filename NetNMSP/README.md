NetNMSP: Nonoverlapping maximal sequential pattern mining
Youxi Wu, Shuai Zhang, Yan Li, Lei Guo, Xindong Wu

Abstract: Sequential pattern mining with gap constraints is an extension of repetitive sequential pattern mining, which has become a hot research field in data 

mining and has flexible expression and good performance. Compared with other similar methods, nonoverlapping pattern mining, as a kind of sequential pattern mining 

with gap constraints, can find more valuable patterns. Traditional algorithms focused on finding all frequent patterns and found lots of redundant short patterns. 

However, it not only reduces the mining efficiency, but also increases the difficulty in obtaining the demand information. To reduce the number of frequent 

patterns and retain its expression ability, this paper focuses on the Nonoverlapping Maximal Sequential Pattern (NMSP) mining which refers to finding frequent 

patterns whose super-patterns are infrequent. Meanwhile, it provides boundary information for frequent patterns and infrequent patterns. In this paper, we propose 

an effective mining algorithm, Nettree for NMSP mining (NetNMSP), which has three key steps calculating the support, generating the candidate patterns, and 

determining NMSPs. To calculate the support, NetNMSP employs the backtracking strategy to get a nonoverlapping occurrence from the leftmost leaf to its root with 

the leftmost parent node method in a Nettree. Therefore, NetNMSP does not need to find and prune invalid nodes. Due to nonoverlapping pattern mining satisfying the 

Apriori property, we generate candidate patterns by the pattern join strategy, which reduces the number of candidate patterns. Furthermore, we propose the 

screening method to find NMSPs. Experiments on biological sequence datasets verify that not only does NetNMSP outperform the state-of-the-arts algorithms, but also 

NMSP mining has better compression performance than closed pattern mining.  NetNMSP is also applied in NMSP mining in SARS and SARS-CoV-2. The results show that 

the two viruses are similar in the short patterns and  different in the long patterns. More importantly, NMSP mining is easier to find the difference between the 

two viruses. 

Source codes:
Datasets:
