##  Co-occurrence order-preserving pattern mining with keypoint alignment for time series

Youxi Wu, Zhen Wang, Yan Li, Yingchun Guo, Xingquan Zhu, Xindong Wu 

####  Abstract：
Recently, order-preserving pattern (OPP) mining has been proposed to find trend changes in time series. Although existing OPP mining algorithms have achieved satisfactory performance, they discover all frequent patterns. However, in some cases, users focus on a particular trend and its associated trends, rather than all patterns. To efficiently discover trend information related to a specific prefix pattern, this paper addresses the issue of co-occurrence OPP mining (COP) and proposes the COP-Miner algorithm to discover COPs from historical time series. COP-Miner consists of three parts: extracting keypoints, preparation stage, and iteratively calculating supports and mining frequent COPs. Extracting keypoints is used to obtain local extreme points of patterns and time series. The preparation stage is designed to prepare for the first round of mining, which contains four steps: obtaining the suffix OPP of the keypoint sub-time series, calculating the occurrences of the suffix OPP, verifying the occurrences of the keypoint sub-time series, and calculating the occurrences of all fusion patterns of the keypoint sub-time series. To further improve the efficiency of support calculation, we propose a method of calculating support with an ending strategy. Experimental results indicate that COP-Miner outperforms the other competing algorithms in running time and scalability. Moreover, COPs with keypoint alignment yield better prediction performance.

---

#### Algorithms:
[COP-Miner and all competitive algorithm](https://github.com/wuc567/Pattern-Mining/tree/master/COP-Miner/code)

#### Datasets:
[Datasets](https://github.com/wuc567/Pattern-Mining/tree/master/COP-Miner/datasets)