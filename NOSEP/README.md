## NOSEP: Non-Overlapping Sequence Pattern Mining with Gap Constraints</p>
***

Youxi Wu, Yao Tong, Xingquan Zhu, Xindong Wu. NOSEP: Nonoverlapping Sequence Pattern Mining with Gap Constraints. IEEE Transactions on Cybernetics.  DOI (identifier) 10.1109/TCYB.2017.2750691

#### Abstract:

Sequence pattern mining aims to discover frequent subsequences as patterns in a single sequence or a sequence database. By combining gap constraints (or flexible wildcards), users can specify special characteristics of the patterns and discover meaningful subsequences suitable for their own application domains, such as finding gene transcription sites from DNA sequences or discovering patterns for time series data classification.  However, due to the inherent complexity of sequence patterns, including the exponential candidate space with respect to pattern letters and gap constraints, to date, existing sequence pattern mining methods are either incomplete or do not support the Apriori property since the support or support ratio of a pattern may be greater than that of its sub-patterns. Most importantly, patterns discovered by these methods are either too restrictive or too general and cannot represent underlying meaningful knowledge in the sequences. In this paper, we focus on a non-overlapping sequence pattern mining task with gap constraints, where a non-overlapping sequence pattern allows sequence letters to be flexible, yet maximally, utilized for pattern discovery. A new non-overlapping sequence pattern mining algorithm (NOSEP), which is an Apriori-based and complete mining algorithm, is proposed by using Nettree, a specially designed data structure, to calculate the exact occurrence of a pattern in the sequence. Experimental results and comparisons with biology DNA sequences, time series data,  and  Gazelle Datasets demonstrate the efficiency of the proposed algorithm and the uniqueness of non-overlapping sequence patterns compared to other methods.

Datasets:[Dataset1](https://github.com/wuc567/Pattern-Mining/blob/master/NOSEP/DataSet.rar)  (DNA and Protein sequences)

 

Gazelle Datasets (From SPMF):

BMSWebView1 (Gazelle) ( KDD CUP 2000)

BMSWebView2 (Gazelle) ( KDD CUP 2000)

 

 

Algorithms:

NOSEP   for character version(small alphabet size)

NOSEPi   for integer version(large alphabet size)

 

NOSEP-B   (backtracking strategy) for character version(small alphabet size)

NOSEP-B-i  for integer version(large alphabet size)

 

NetM-B   (BFS strategy) for character version(small alphabet size)

NetM-B-i   for integer version(large alphabet size)

 

NetM-D  (DFS strategy) for character version(small alphabet size)

NetM-D-i   for integer version(large alphabet size)

 

 

GSgrow  for character version(small alphabet size)

GSgrow-i  for integer version(large alphabet size)

is proposed by Ding et al[1] .

 

[1] Ding B, Lo D, Han J, et al. Efficient mining of closed repetitive gapped subsequences from a sequence database. In: Proceedings of IEEE International Conference on Data Engineering, Shanghai, 2009. 1024-1035

**中文摘要**：序列模式挖掘是在单序列或序列数据库中发现频繁子序列。在结合间隙约束（或可变长度通配符）后形成具有间隙约束的序列模式挖掘，这种间隙约束可以用来指定模式的特点，以用于发现有意义的子序列，其已在诸多领域得到了广泛的应用，如DNA序列寻找基因转录位点或时间序列数据分类的模式发现。由于在序列字符和间隙的作用下，候选空间呈现指数形式，因此该挖掘具有一定的复杂性。迄今为止现有的挖掘方法要么是挖掘结果不具有完备性的算法，要么是不支持的Apriori性质的算法，因为模式的支持度或支持率可能大于其子模式的。更为重要的是这些方法发现的模式要么限制性太强，要么过于笼统，难以表示序列中隐含的有意义的知识。在本文中，我们研究了一种无重叠的序列模式挖掘，其是一种允许序列字符更加灵活并最大限度地用于模式发现。在此基础上，提出了一种新的基于Apriori性质的无重叠序列模式挖掘算法（NOSEP），该算法是一个具有完备性的模式挖掘算法，其采用模式匹配策略并运用一个称为网树的特殊数据结构来计算一个模式的支持度，并采用模式增长策略实现候选模式有效剪枝。在生物DNA序列、时间序列数据和一个公开的电子商务点击流数据集上与同类算法进行对比，实验结果不但验证了NOSEP算法的效率，并且表明在相同条件下其可以发现更多且更加有意义的频繁模式。

