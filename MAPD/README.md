## Mining sequential patterns with periodic wildcard gaps
***

Youxi Wu, Lingling Wang, Jiadong Ren, Wei Ding, Xindong Wu. Mining sequential patterns with periodic wildcard gaps. Applied Intelligence. Volume 41, Issue 1 (2014), Page 99-116.

#### Abstract:

Mining frequent patterns with periodic wildcard gaps is a critical data mining problem to deal with complex real-world problems. This problem can be described as follows: given a subject sequence, a pre-specified threshold, and a variable gap-length with wildcards between each two consecutive letters. The task is to gain all frequent patterns with periodic wildcard gaps. State-of-the-art mining algorithms which use matrix or other linear data structures to solve the problem not only consume a large amount of memory but also run slowly. In this study, we use an Incomplete Nettree structure (the last layer of a Nettree which is an extension of a tree) of a sub-pattern P to efficiently create Incomplete Nettrees of all its super-patterns with prefix pattern P and compute the numbers of their supports in a one-way scan. We propose two new algorithms, MAPB (Mining sequentiAl Pattern using incomplete Nettree with Breadth first search) and MAPD (Mining sequentiAl Pattern using incomplete Nettree with Depth first search), to solve the problem effectively with low memory requirements. Furthermore, we design a heuristic algorithm MAPBOK (MAPB for tOp-K) based on MAPB to deal with the Top-K frequent patterns for each length. Experimental results on real-world biological data demonstrate the superiority of the proposed algorithms in running time and space consumption and also show that the pattern matching approach can be employed to mine special frequent patterns effectively.
---

#### Algorithms:

[MAPD](https://github.com/wuc567/Pattern-Mining/tree/master/MAPD)
