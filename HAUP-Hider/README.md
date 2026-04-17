## HAUP-Hider: Privacy-Preserving High Average Utility Pattern Mining
***

Youxi Wu, Qi Zhou, Yan Li, Cong Liu, Jianguo Wei, and Xindong Wu

#### Abstract:

The aim of privacy-preserving utility mining is to safeguard sensitive information when carrying out utility pattern mining; however, traditional methods mainly focus on transactional databases and apply uniform sanitization strategies to all sensitive information, resulting in limited applicability to sequential patterns and excessive database distortion. To address these issues, we focus on privacy-preserving high average utility pattern mining, and propose an algorithm called HAUP-Hider. To overcome the limitations of uniform sanitization, we prove that the optimal approach is to categorize sensitive patterns into three sensitivity zones, and design targeted victim item selection strategies for patterns in different zones. To maximize the privacy-preserving effect and minimize side effects, we propose a dual-objective optimization-based selection strategy for victim sequences. We explore different selection strategies for the victim items in each of the three zones. To enable effective application of this approach to sequential databases, a head-deletion strategy is introduced to determine the deletion positions of victim items. Experimental comparisons with 12 competitive algorithms on 14 databases demonstrate that HAUP-Hider achieves a 49.83\% reduction in MC and a 12.27\% improvement in DUS over classical algorithms such as HHUIF. More importantly, when applied to a real-world database, HAUP-Hider successfully hides all sensitive patterns while preserving non-sensitive patterns to the greatest possible extent.
---

#### Algorithms:

[HAUP-Hider and all competitive algorithm](https://github.com/wuc567/Pattern-Mining/tree/master/HAUP-Hider/Algorithms)

#### Databases:
[Databases](https://github.com/wuc567/Pattern-Mining/tree/master/HAUP-Hider/Databases)  
