package algorithms;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.*;
import java.util.stream.Collectors;
//2024.7.11 基于OPP-Miner挖掘出OUTO
public class OUTO_opp {
    private static Map<Integer, Integer> map = new HashMap<>();
    private static double[] input;//预处理后的序列
    private static double[] seq;//原始的序列
    private static boolean flag;
    private static int allFreCount = 0;
    private static int candCount = 0;
    private static int coFreSeqCount = 0;
    private static int coSimSeqCount = 0;
    private static int OUTO_num=0;
    private static  List<Double> A=new ArrayList<>();
    //    private static Set<String> freSet = new HashSet<>();
    private static List<FreItemset> freItemsetList;
    private static List<double[]> Fre=new ArrayList<>();
    private static List<Integer[]> Fre_index=new ArrayList<>();
    private static List<List<Integer>> fre=new ArrayList<>();//是Fre的List<Integer>类型，将模式double[]转换成List<Integer>

    private static List<List<Integer>> fre_index=new ArrayList<>();//是Fre_index的List<Integer>类型，将模式double[]转换成List<Integer>
    private static int candidateCount;

    private static double fitt=5;
    private static double DTW;
    private static double xishu=2.5;
    private static int supportTv =200;
    //1:40, 2:205, 3:380, 4:340, 5:320, 6:500, 7:1030, 8:1220

    private static void getInArr() throws Exception {
        //1
        //File file=new File( "src/main/java/dataset/Crude Oil.txt");
        //2
        // File file=new File( "src/main/java/dataset/1WTl.txt");
        //3
        //File file=new File( "src/main/java/dataset/英国布伦特.txt");
        //4
        //File file=new File( "src/main/java/dataset/KURIAS-ECG_HeartRate.txt");
        //5
        File file=new File( "src/main/java/dataset/顺义PM2.5.txt");
        //6
        //File file=new File( "src/main/java/dataset/ChengduPM2.5.txt"); //两个空格
        //7
        //File file=new File("src/main/java/dataset/DOW.txt");
        //8
        //File file=new File( "src/main/java/dataset/NYSE.txt");

        //File file=new File( "src/main/java/dataset/electricity.txt");
        //File file=new File(= "src/main/java/algorithms/recursive");
        //File file=new File( "src/main/java/algorithms/text.txt");

        //File file = new File("src/main/java/dataset/scalability/1k.txt");
        //File file = new File("src/main/java/dataset/scalability/5k.txt");
        //File file = new File("src/main/java/dataset/scalability/9k.txt");
        //File file = new File("src/main/java/dataset/scalability/13k.txt");
        //File file = new File("src/main/java/dataset/scalability/17k.txt");
        //File file = new File("src/main/java/dataset/scalability/21k.txt");
        //File file = new File("src/main/java/dataset/scalability/25k.txt");
        //File file = new File("src/main/java/dataset/scalability/29k.txt");



        BufferedReader br = new BufferedReader(new FileReader(file));
        String s;

        //初始数据列表
        List<Double> rawdataTemp = new ArrayList<>();
        List<ExtremePoint> extremePoints=new ArrayList<>();
        //使用readLine方法，一次读一行
        while ((s = br.readLine()) != null) {
            freItemsetList = new ArrayList<>();
            List<Double> inList = new ArrayList<>();
            s = s.trim();
            String[] str = s.split(" ");
            String[] strArr = new String[str.length];
//            System.arraycopy(str, 1, strArr, 0, strArr.length);
            for (int i = 0; i < str.length; i++) {
                String value = str[i].trim(); // 去除字符串两端的空白字符
                if (!value.isEmpty()) {
                    inList.add(Double.parseDouble(str[i]));
                }
            }

            double[] in = new double[inList.size()];
            int m = 0;
            for (double inLine : inList) {
                in[m++] = inLine;
            }
            System.out.println("原始序列个数："+in.length);
            seq=in;


            extremePoints=KeyPointsExtraction(in);
            System.out.println("极值点个数："+extremePoints.size());


            input=findMaxFitDifference(in,extremePoints);
            for(int l=0;l<input.length;l++){
                A.add(input[l]);
            }

//            input = in;
//            input=getExtremePoint(in);
            double ddtw=calculateVariance(A);
            System.out.println("预处理后的序列个数："+A.size());
            //System.out.println("aaa："+A.size());
            //A也是预处理后的序列
            System.out.println("方差："+ddtw);
            DTW=xishu*ddtw;
            System.out.println("DTW: "+DTW);
            readLine();
//            System.gc();
        }
        br.close();
    }


    public static void main(String[] args) throws Exception {
        long startTime = System.currentTimeMillis();
        getInArr();
       // System.out.println("候选模式的总数是:" + candCount);
        System.out.println("---------------------------------------------------");
        printCostTime(startTime);
        //System.out.println("频繁模式的总数是:" + allFreCount);

    }



    private static Integer[] sbndm(int[] txt, int[] pat, int[] aux, double[] s) {
        List<Integer> subsetNumList = new ArrayList<>();
        int txt_length = txt.length;
        int pat_length = pat.length;
        int pos, D, j, q;
        int pattern_num = 0;
        int flag = 0, f = 0;
        int B[] = new int[pat_length + 1];
        for (j = 0; j < pat_length; j++) {
            B[pat[j]] = B[pat[j]] | (1 << (pat_length - j - 1));
        }
        pos = pat_length - 1;
        while (pos <= txt_length - 1) {
            D = (B[txt[pos - 1]]) & (B[txt[pos]] << 1);
            if (D != 0) {
                j = pos - pat_length + 1;
                do {
                    pos = pos - 1;
                    if (pos == 0) {
                        D = 0;
                    } else {
                        D = (D << 1) & B[txt[pos - 1]];
                    }
                }
                while (D != 0);
                if (j == pos) {
                    int len_cand = j + pat_length;
                    int x = 0;
                    int k = 0;
                    int cand = j;
                    for (x = j; x < len_cand; x++) {
                        if (s[cand - 1 + aux[k]] >= s[cand - 1 + aux[k + 1]]) {
                            f = 0;
                            subsetNumList.add(pos);
                            break;
                        } else {
                            f = 1;
                        }
                        k++;
                    }
                    if (f > 0) {
                        flag = 1;
                        pattern_num++;
                        subsetNumList.add(pos);
                    }
                    pos = pos + 1;
                }
            }
            pos = pos + pat_length - 1;
        }
        Integer[] subsetNumArr = new Integer[subsetNumList.size()];
        subsetNumList.toArray(subsetNumArr);
        return subsetNumArr;
    }

    private static void genAux(int[] aux, int[] sortedP, int[] p) {
        for (int i = 0; i < p.length; i++) {
            for (int j = 0; j < p.length; j++) {
                if (sortedP[i] == p[j]) {
                    aux[i] = j + 1;
                }
            }
        }
    }

    private static Integer[] bndm(int[] inBinaryArr, int[] pBinaryArr) {
        List<Integer> subsetNumList = new ArrayList<>();
        if (inBinaryArr.length <= pBinaryArr.length) {
            return new Integer[0];
        } else {
            int[] B = new int[pBinaryArr.length + 1];
            int pos = 0;

            for (int i = 0; i < pBinaryArr.length; i++) {
                B[pBinaryArr[i]] = B[pBinaryArr[i]] | 1 << (pBinaryArr.length - i - 1);
            }

            while (pos < inBinaryArr.length - pBinaryArr.length + 1) {
                int D = (-1);
                int j = pBinaryArr.length - 1;
                while (D != 0) {
                    D = B[inBinaryArr[pos + j]] & D;
                    j--;
                    D = D << 1;
                    if (j < 0 && D != 0) {
                        subsetNumList.add(pos);
                        break;
                    }
                }
                pos++;
            }

            Integer[] subsetNumArr = new Integer[subsetNumList.size()];
            subsetNumList.toArray(subsetNumArr);
            return subsetNumArr;
        }
    }

    //@param Cd 本轮生成的候选模式，且频繁
    //*@param Z 索引集合
    //outlying pattern,判断每个频繁保序模式，其是否存在异常出现出现
    private static void judge_OUTO(List<Integer> Cd, List<Integer> Z) {
        int number = 0;

        List<Double> subSequence = new ArrayList<>();//存储单个子序列
        List<List<Double>> SequenceList = new ArrayList<>();//存储所有子序列
        List<Double> means = new ArrayList<>();//存储所有均值
        List<Double> meanss = new ArrayList<>();//存储所有均值
        List<Double> de = new ArrayList<>();//存储所有标准差
        List<Double> des = new ArrayList<>();//存储所有标准差

        // Step 1: 提取所有子序列均值
        for (Integer endIndex : Z) {
            for (int k = 0; k < Cd.size(); k++) {
                //index 是第一个子序列在S中的初始位置（首位）索引
                int index = endIndex + k;
                //System.out.println("Z: "+endIndex+"    "+index);
                double a = seq[index];
                subSequence.add(a);
            }
            double mean =calculateMean(subSequence);
            double devation=calculateVariance(subSequence);
            means.add(mean);
            meanss.add(mean);
            de.add(devation);
            des.add(devation);
            SequenceList.add(new ArrayList<>(subSequence));
            subSequence.clear();
        }

        //System.out.println("子序列集合： "+SequenceList);

        // Step 2: 计算均值四分位数和四分位距
        double mQ1 = calculatePercentile(means, 25);
        double mQ3 = calculatePercentile(means, 75);
        double mIQR = 1.5*(mQ3 - mQ1);

        //计算标准差四分位数和四分位距
        double dQ1 = calculatePercentile(de, 25);
        double dQ3 = calculatePercentile(de, 75);
        double dIQR = 1.5*(dQ3 - dQ1);


        // Step 4: 判断每个子序列均值是否在区间内，如果不在区间内，则与其他子序列进行DTW计算
        for (int i = 0; i < SequenceList.size(); i++) {

            double mean = meanss.get(i);
            double devation =des.get(i);
            //System.out.println("均值： "+mean);

            //均值判断是否可能为OUTO
            if (!isWithinBounds(mean, mQ1 - mIQR, mQ3 + mIQR)||
                    (isWithinBounds(mean, mQ1 - mIQR, mQ3 + mIQR)&&!isWithinBounds(devation, dQ1 -dIQR, dQ3 + dIQR))) {

                int num =0;
                List<Double> A = SequenceList.get(i);
                // System.out.println("异常子序列： "+A);
                num++;

                for (int j = 0; j < SequenceList.size(); j++) {
                    if (i != j) {
                        List<Double> B = SequenceList.get(j);
                        double dtw = calculateDTWDistance(A, B);
                        // System.out.println("DTW(" + A + ", " + B + ") = " + dtw);

                        if (dtw >= DTW) {
                            // System.out.println("A:   "+A+"B:   "+B+"dtw:   "+dtw);
                            number++;
                            // System.out.println("number:   " + number);
                        }
//                        B.clear();
                    }
                }
                if (number >= Math.ceil(Z.size() * 0.8)) {
                    // System.out.println("Z.size: "+Z.size()+"    "+Math.ceil((Z.size()+1) / 2));
                    // 序列被认为是异常模式序列
                    //      System.out.println("是异常保序模式");
                    List<List<Double>> lop = new ArrayList<>();
                    OUTO_num++;

                    List<Integer> lop_num = new ArrayList<>();
                     //System.out.println("异常出现数量：" + OUTO_num);

                } else {
                    //System.out.println("不是异常保序模式");
                }
                number = 0;

            }
        }

    }

    public static boolean isWithinBounds(double value, double lowerBound, double upperBound) {
        return value >= lowerBound && value <= upperBound;
    }



    // 计算均值
    public static double calculateMean(List<Double> list) {
        double sum = 0;
        for (double num : list) {
            sum += num;
        }
        return sum / list.size();
    }

    // 计算百分位数
    public static double calculatePercentile(List<Double> sortedList, double percentile) {
        Collections.sort(sortedList);
        int index = (int) Math.ceil(percentile / 100.0 * sortedList.size()) - 1;
        return sortedList.get(index);
    }


    // 22.
    //计算相同保序模式下两个出现的余弦距离
    public static double calculateCosineDistance(List<Double> A, List<Double> B) {

        // 将 List 转换为数组
        Double[] ss1 = A.toArray(new Double[0]);
        // 将 List 转换为数组

        Double[] ss2 = B.toArray(new Double[0]);

        // 打印数组元素
        double sum = 0;
        double magnitude1 = 0.0;
        double magnitude2 = 0.0;
        double cos = 0.0;

        for (int i = 0; i < ss1.length; i++) {
            sum += ss1[i] * ss2[i];
            magnitude1 += Math.pow(ss1[i], 2);
            magnitude2 += Math.pow(ss2[i], 2);
        }
        magnitude1 = Math.sqrt(magnitude1);
        magnitude2 = Math.sqrt(magnitude2);
        cos = sum / (magnitude1 * magnitude2);


        if (magnitude1 == 0 || magnitude2 == 0) {
            return 0;
        }
        return cos;
    }

    //计算相同保序模式下两个出现的DTW距离--首先要数据归一化
    public static double calculateDTWDistance(List<Double> A, List<Double> B) {
        int i, j;
        double max = 999.0;
        Double a[] = A.toArray(new Double[0]);
        Double b[] = B.toArray(new Double[0]);
        int NUM1 = a.length + 1;// 加1是因为计算是有a[i-1]
        int NUM2 = b.length + 1;// 加1是因为计算是有b[j-1]

        double[][] distance = new double[NUM1][NUM2];
        double[][] output = new double[NUM1][NUM2];

        for (i = 0; i < NUM1; i++) {
            for (j = 0; j < NUM2; j++) {
                distance[i][j] = max;
                output[i][j] = max;
            }
        }
        distance[0][0] = 0;
        output[0][0] = 0;

        for (i = 1; i < NUM1; i++) {
            for (j = 1; j < NUM2; j++) {
                distance[i][j] = Math.abs(b[j - 1] - a[i - 1]); // 计算点与点之间的欧式距离
            }
        }
        // 输出整个欧式距离的矩阵
        for (i = 1; i < NUM1; i++) {
            for (j = 1; j < NUM2; j++) {
                // System.out.print(distance[i][j] + " ");
            }
            //System.out.println();
        }
        //System.out.println("=================================");

        // DP过程，计算DTW距离
        for (i = 1; i < NUM1; i++) {
            for (j = 1; j < NUM2; j++) {
                output[i][j] = Math.min(Math.min(output[i - 1][j - 1], output[i][j - 1]), output[i - 1][j])
                        + distance[i][j];
            }
        }

        // 输出最后的DTW距离矩阵，其中output[NUM1][NUM2]为最终的DTW距离和
        for (i = 1; i < NUM1; i++) {
            for (j = 1; j < NUM2; j++) {
//                System.out.print(output[i][j] + " ");
//            System.out.println();
            }
        }
        return output[NUM1-1][NUM2-1];
    }

    public static double calculateAverage(List<Double> timeSeries) {
        // 计算样本平均值
        double sum = 0;
        for (double value : timeSeries) {
            sum += value;
        }
        double mean = sum / timeSeries.size();
        System.out.println("均值: " + mean);
        return mean;
    }

    public static double calculateVariance(List<Double> timeSeries) {

        double sum = 0;
        for (double value : timeSeries) {
            sum += value;
        }
        double mean = sum / timeSeries.size();

        // 计算每个样本点与平均值的差的平方
        double squaredDiffSum = 0;
        for (double value : timeSeries) {
            squaredDiffSum += Math.pow(value - mean, 2);
        }

        // 计算总体方差
        double variance =squaredDiffSum / (timeSeries.size());

        //标准差
        double svariance=Math.sqrt(variance);
        // System.out.println("标准差: " + svariance);


        return svariance;
    }







    private static void printCostTime(long startTime) {
        MemoryLogger.getInstance().checkMemory();
        System.out.println("花费总时间为:" + (System.currentTimeMillis() - startTime) + "ms");
//        System.out.println("---------------------------------------------------");

        double maxMemory = MemoryLogger.getInstance().getMaxMemory();
        System.out.println("最大内存占用: " + maxMemory + " Mb");
    }

    private static void printCoOccurrence() {

        if (freItemsetList == null || freItemsetList.size() == 0) {
//            System.out.println("无频繁模式！！！");
        }
//        System.out.println("频繁模式：");
        int freCount = 0;
        for (FreItemset freItemset : freItemsetList) {
//            System.out.println(Arrays.toString(freItemset.itemset) + " sup: " + freItemset.support);
            freCount++;
        }
        for (int i = 0; i < fre.size(); i++) {
            List<Integer> pattern = fre.get(i);
            List<Integer> pattern_index = fre_index.get(i);
           // System.out.println("pattern:  "+pattern+"   "+pattern_index);
            judge_OUTO(pattern,pattern_index);
        }
        System.out.println("频繁模式的个数是:" + freCount);
        System.out.println("候选模式的个数是:" + candidateCount);
        System.out.println("最大频繁模式的个数是:" + fre.size());
        System.out.println("OUTO的个数是:" + OUTO_num);

        allFreCount += freCount;
        candCount += candidateCount;

        int total = 0;

    }

    private static List<Candidate> getPatternMatching(double[] in,  int supportTv) throws Exception {
        List<double[]> resList = new ArrayList<double[]>() {{
            add(new double[]{1, 2});
            add(new double[]{2, 1});
        }};
        List<Candidate> candidateList = new ArrayList<>();
        List<Candidate> candidateListNew = new ArrayList<>();
        //List<Candidate> candidates;
        while (resList.size() > 0) {
//            candidateList = new ArrayList<>();
            candidateListNew = new ArrayList<>();
            for (double[] candidateArr : resList) {
                int[] inBinaryArr = getBinary(in);
                int[] pBinaryArr = getBinary(candidateArr);
                //Integer[] subsetNumArr = getSubset(inBinaryArr, pBinaryArr);
                Integer[] subsetNumArr;
                if (candidateArr.length == 2) {
                    subsetNumArr = bndm(inBinaryArr, pBinaryArr);
                } else {
                    int[] sortedP = new int[pBinaryArr.length];
                    System.arraycopy(pBinaryArr, 0, sortedP, 0, sortedP.length);
                    Arrays.sort(sortedP);
                    int[] aux = new int[pBinaryArr.length];
                    genAux(aux, sortedP, pBinaryArr);
                    subsetNumArr = sbndm(inBinaryArr, pBinaryArr, aux, in);
                }
                Integer[] subsetNumArrNew = verificationStrategy(in, candidateArr, subsetNumArr);
                if (subsetNumArrNew.length >= supportTv) {
                    candidateListNew.add(new Candidate(candidateArr, subsetNumArrNew));
                    //System.out.println("模式"+candidateArr);
                    freItemsetList.add(new FreItemset(candidateArr, subsetNumArrNew.length));
                    Fre_index.add(subsetNumArrNew);
                    Fre.add(candidateArr);
                   // System.out.println("1"+freItemsetList.size());
                }
            }
            resList = candidateListNew.stream().map(Candidate::getItemset).collect(Collectors.toList());
            if (resList.size() > 0) {
                resList = patternFusion(resList);
                candidateCount += resList.size();
            } else {
                break;
            }
        }
        judge_maxfreoop(Fre,Fre_index);
        //System.out.println("cwec:"+Fre.size());

        if (candidateList == null || candidateList.size() == 0) {
            return null;
        }

//        candCount +=candidateList.size();
//        if (candidateList.get(0).itemset.length != pattern.length + 1) {
//            return null;
//        }


        return candidateList;
    }


    /**
     * 计算模式的相对顺序
     * @param src
     * @return
     */
    public static int[] sort(List<Integer> src){
        int k, slen = 0;
        int level = 1;

        slen = src.size();
        int[] sort_array = new int[slen];
        for(int i = 0 ; i < slen ; i++)
        {
            k = src.get(i);
            for(int x = 0;x < slen;x++)
            {
                if(k > src.get(x))
                {
                    level++;
                }
            }
            sort_array[i] = level;
            level = 1;
        }
        return sort_array;
    }

    // 将List<Integer[]>转换为List<List<Integer>>的方法
    public static List<List<Integer>> convertToListOfLists(List<Integer[]> list) {
        List<List<Integer>> result = new ArrayList<>();
        for (Integer[] array : list) {
            // 创建一个新的List<Integer>来存储当前数组的元素
            List<Integer> tempList = new ArrayList<>();
            // 将数组的元素添加到tempList中
            for (Integer value : array) {
                tempList.add(value);
            }
            // 将tempList添加到结果列表中
            result.add(tempList);
        }
        return result;
    }



    // 将List<double[]>转换为List<List<Integer>>的方法
    public static List<List<Integer>> convertToDoubleListList(List<double[]> list) {
        List<List<Integer>> result = new ArrayList<>();
        for (double[] array : list) {
            // 将double[]转换为List<Integer>
            List<Integer> tempList = new ArrayList<>();
            for (double value : array) {
                // 假设我们使用Math.round()进行四舍五入，并强制转换为int
                tempList.add((int) Math.round(value));
                // 如果你想要向下取整，可以直接使用 (int)value
            }
            // 将转换后的List<Integer>添加到结果List中
            result.add(tempList);
        }
        return result;
    }

    //判断是否是最大频繁保序模式，模式支持度为sup_num,模式Cd,对应位置索引Z
    private static List<List<Integer>> judge_maxfreoop(List<double[]>Fre,List<Integer[]>Fre_index) {


        // 将List<double[]>转换为List<List<Integer>>
         fre= convertToDoubleListList(Fre);
        // 将List<Integer[]>转换为List<List<Integer>>的方法
         fre_index=convertToListOfLists(Fre_index);


        List<Integer> Q = new ArrayList<>();
        List<Integer> R = new ArrayList<>();
        int[] q = new int[256];
        int[] r = new int[256];

        for (int l =0;l<fre.size(); l++) {
            // 求后缀
            Q = fre.get(l).subList(1, fre.get(l).size());
            q = sort(Q);
            List<Integer> qList = new ArrayList<>();
            for (int i : q) {
                qList.add(i); // 自动装箱
            }
            //System.out.println("集合中模式后缀: "+qList);

            List<Integer> rList = new ArrayList<>();
            // 求前缀
            R = fre.get(l).subList(0, fre.get(l).size() - 1);
            r = sort(R);
            for (int i : r) {
                rList.add(i); // 自动装箱
            }

            //  System.out.println("集合: "+Fre+"   后缀： "+qList+"   前缀：  "+rList);
//                for(List<Integer> pattern:Fre){
//                    System.out.println("pattern: "+pattern);
//                    if(qList.equals(pattern) || rList.equals(pattern)){
//                        Fre.remove(pattern);
//                    }
//                }

            Iterator<List<Integer>> iterator = fre.iterator();
            Iterator<List<Integer>> iterator_index = fre_index.iterator();
            while (iterator.hasNext()) {
                List<Integer> pattern = iterator.next();
                List<Integer> pattern_index = iterator_index.next();
                if (qList.equals(pattern) || rList.equals(pattern)) {
                    iterator.remove();
                    iterator_index.remove();
                }
            }
            //System.out.println("集合: "+Fre);
        }
        //System.out.println("集合结果: "+Fre+"   "+Fre_index);
        return fre;
    }

    private static List<double[]> patternFusion(List<double[]> list) {

        List<double[]> resList = new ArrayList<>();

        for (double[] p : list) {
            for (double[] q : list) {
                int m = q.length;
                //先求出suffixorder(p)与prefixorder(q)
                double[] suffixp = new double[p.length - 1];
                double[] prefixq = new double[q.length - 1];

                //得出suffix(p)与prefix(q)
                System.arraycopy(p, 1, suffixp, 0, p.length - 1);
                System.arraycopy(q, 0, prefixq, 0, q.length - 1);

                double[] suffixorder = new double[p.length - 1];
                double[] prefixorder = new double[q.length - 1];

                if (suffixp.length == 1) {
                    suffixorder[0] = 1;
                    prefixorder[0] = 1;
                } else {
                    suffixorder = getOrder(suffixp);
                    prefixorder = getOrder(prefixq);
                }

                if (Arrays.equals(suffixorder, prefixorder) && !Arrays.equals(suffixp, prefixq)) {
                    double[] t = new double[p.length + 1];
                    if (p[0] < q[m - 1]) {
                        t[0] = p[0];
                        t[m] = q[m - 1] + 1;
                        for (int i = 1; i < t.length - 1; i++) {
                            if (p[i] > q[m - 1]) {
                                t[i] = p[i] + 1;
                            } else {
                                t[i] = p[i];
                            }
                        }
                    } else {
                        t[0] = p[0] + 1;
                        t[m] = q[m - 1];
                        for (int i = 0; i < t.length - 1; i++) {
                            if (q[i] > p[0]) {
                                t[i + 1] = q[i] + 1;
                            } else {
                                t[i + 1] = q[i];
                            }
                        }
                    }
                    resList.add(t);
                }

                if (Arrays.equals(suffixorder, prefixorder) && Arrays.equals(suffixp, prefixq)) {
                    double[] t = new double[p.length + 1];
                    double[] k = new double[p.length + 1];

                    t[0] = p[0] + 1;
                    t[m] = p[0];
                    for (int i = 1; i < t.length - 1; i++) {
                        if (p[i] > p[0]) {
                            t[i] = p[i] + 1;
                        } else {
                            t[i] = p[i];
                        }
                    }
                    resList.add(t);

                    k[0] = p[0];
                    k[m] = p[0] + 1;
                    for (int i = 1; i < k.length - 1; i++) {
                        if (p[i] > p[0]) {
                            k[i] = p[i] + 1;
                        } else {
                            k[i] = p[i];
                        }
                    }
                    resList.add(k);
                }
            }
        }
        return resList;
    }


    private static double[] getOrder(double[] seq) {
        double[] arr = new double[seq.length];
        System.arraycopy(seq, 0, arr, 0, seq.length);
        double[] order = new double[arr.length];
        double[] temp = new double[arr.length];
        System.arraycopy(arr, 0, temp, 0, arr.length);
        Arrays.sort(temp);

        for (int j = 0; j < arr.length; j++) {
            double min = temp[temp.length - 1] + 1;
            int index = 0;
            for (int i = 0; i < arr.length; i++) {
                if (arr[i] < min && arr[i] != -1) {
                    min = arr[i];
                    index = i;
                }
            }
            arr[index] = -1;
            order[index] = j + 1;
        }
        return order;
    }

    private static Integer[] verificationStrategy(double[] in, double[] candidateArr, Integer[] subsetNumArr) {
        List<Integer> subsetListNew = new ArrayList<>();
        List<SupportOrder> supportOrderList = new ArrayList<>();
        int index = 1;
        for (double order : candidateArr) {
            SupportOrder supportOrder = new SupportOrder(order, index++);
            supportOrderList.add(supportOrder);
        }
        supportOrderList.sort(Comparator.comparingDouble(SupportOrder::getOrder));
        int[] indexArr = new int[supportOrderList.size()];
        int sub = 0;
        for (SupportOrder supportOrder : supportOrderList) {
            indexArr[sub++] = supportOrder.index;
        }
        for (Integer value : subsetNumArr) {
            boolean flag = false;
            for (int i = 0; i < indexArr.length - 1; i++) {
                if (in[value - 1 + indexArr[i]] >= in[value - 1 + indexArr[i + 1]]) {
                    flag = true;
                    break;
                }
            }
            if (!flag) {
                subsetListNew.add(value);
            }
        }
        Integer[] subsetNumArrNew = new Integer[subsetListNew.size()];
        subsetListNew.toArray(subsetNumArrNew);
        return subsetNumArrNew;
    }


    private static int[] getBinary(double[] arr) {
        int[] binary = new int[arr.length - 1];
        for (int i = 0; i < arr.length - 1; i++) {
            if (arr[i] > arr[i + 1]) {
                binary[i] = 0;
            } else if (arr[i] < arr[i + 1]) {
                binary[i] = 1;
            }
        }
        return binary;
    }


    // 辅助类，用于存储极值点及其索引
    static class ExtremePoint {
        double value;
        int index;

        ExtremePoint(double value, int index) {
            this.value = value;
            this.index = index;
        }
    }

    private static List<ExtremePoint>  KeyPointsExtraction(double[] input) {
        List<ExtremePoint> extremePoints = new ArrayList<>();

        extremePoints.add(new ExtremePoint(input[0],0));
        for (int i = 1; i < input.length - 1; i++) {
            if ((input[i] >= input[i - 1] && input[i] > input[i + 1]) || (input[i] > input[i - 1] && input[i] >= input[i + 1])){
                extremePoints.add(new ExtremePoint(input[i], i));
            } else if ((input[i] <= input[i - 1] && input[i] < input[i + 1]) || (input[i] < input[i - 1] && input[i] <= input[i + 1])){
                extremePoints.add(new ExtremePoint(input[i], i));
            }
        }
//        if (!extremePoints.contains(input[input.length - 1])) {
//            extremePoints.add(new ExtremePoint(input[input.length-1],input.length-1));
//        }

        return extremePoints;
    }


        // 找到最大拟合差的点
        private static double[] findMaxFitDifference(double[] input, List<ExtremePoint> extremePoints) {
           List<Integer> index=new ArrayList<>();
           for(ExtremePoint p:extremePoints){
               index.add(p.index);
           }
          // System.out.println("index: "+index.size());



            for (int i = 0; i < extremePoints.size() - 1; i++) {


                ExtremePoint p1 = extremePoints.get(i);
                ExtremePoint p2 = extremePoints.get(i + 1);
                if(p2.index - p1.index <=1){
                    continue;
                }

                if (p2.index - p1.index > 1){

                    double maxDeviation = -1;
                    int maxDeviationIndex = -1;
                    int Index=-1;

                    //System.out.println("[" + p1.index + "," + p2.index + "]");
                    for (int j = p1.index + 1; j < p2.index; j++) {
                        double t = (double) (j - p1.index) / (p2.index - p1.index);
                        double fittedValue = p1.value + t * (p2.value - p1.value);
                        ;//拟合值
                        double deviation = Math.abs(seq[j] - fittedValue);//拟合差
                       // System.out.println("[" + p1.index + "," + p2.index + "]:  " + j+"值：  " + fittedValue + "  " + deviation);
                        if (deviation >= fitt && deviation >= maxDeviation) {
                            maxDeviation = deviation;
                            //System.out.println("拟合差" + maxDeviation );
                            maxDeviationIndex = j;
                            Index=maxDeviationIndex;
                            //System.out.println(" " + maxDeviationIndex);
                        }
                    }
                    if(maxDeviationIndex !=-1) {
                        index.add(Index);
                       // System.out.println("  " + Index + "     " + index.size());
                    }
                    Index=0;
                    if(maxDeviationIndex ==-1) {
                       continue;
                    }
                }

            }
                    Collections.sort(index);

            //System.out.println("d "+index.size());


            // 如果需要，可以在这里添加处理 maxDeviationIndex 的逻辑
            // 例如，可以返回包含 maxDeviationIndex 值的数组

                // 返回极值点数组
                double[] keyextremeValues = new double[index.size()];
                int m=0;
                for(Integer i:index){
                    keyextremeValues[m]=input[i];
                    m++;
                }
            return keyextremeValues;

    }



    private static double[] getExtremePoint(double[] input) {
        List<Double> list = new ArrayList<>();
        list.add(input[0]);
        map.put(0, 0);
        int k = 1;
        for (int i = 1; i < input.length - 1; i++) {
            if ((input[i] >= input[i - 1] && input[i] > input[i + 1]) || (input[i] > input[i - 1] && input[i] >= input[i + 1])) {
                list.add(input[i]);
                map.put(k++, i);
            } else if ((input[i] <= input[i - 1] && input[i] < input[i + 1]) || (input[i] < input[i - 1] && input[i] <= input[i + 1])) {
                list.add(input[i]);
                map.put(k++, i);
            } else {
                map.put(-1, i);
            }
        }
        list.add(input[input.length - 1]);
        map.put(k, input.length - 1);
        int i = 0;
        double[] arr = new double[list.size()];
        for (double item : list) {
            arr[i++] = item;
        }
        return arr;
    }



    private static void readLine() throws Exception {
        map = new HashMap<>();
        candidateCount = 2;

        OUTO_num=0;

        List<Candidate> coOccurrences;

        coOccurrences = getPatternMatching(input,  supportTv);
        printCoOccurrence();

    }

    // 将List<Double>转换为double[]的方法
    public static double[] listToDoubleArray(List<Double> list) {
        // 如果List为空，则返回一个空的double数组
        if (list == null || list.isEmpty()) {
            return new double[0];
        }

        // 初始化数组大小与List相同
        double[] array = new double[list.size()];

        // 遍历List，将Double转换为double并存储在数组中
        for (int i = 0; i < list.size(); i++) {
            array[i] = list.get(i); // Double类型自动拆箱为double
        }

        return array;
    }

    private static List<Integer> extractExtremePoints(double[] in) {
        List<Double> list1 = new ArrayList<>();

        //存储每条序列的极值点在原数据中的位置索引
        List<Integer> list1index = new ArrayList<>();

        list1.add(in[0]);
        list1index.add(0);
        map.put(0,0);
        int k=1;
        for (int i = 1; i < in.length - 1; i++){
            //极值点在rawdataTemp的位置索引是i
            if ((in[i] >= in[i - 1] && in[i] > in[i + 1]) || (in[i] > in[i - 1] && in[i] >= in[i + 1])){
                list1.add(in[i]);
                list1index.add(i);
                map.put(k++,i);
            } else if ((in[i] <= in[i - 1] && in[i] < in[i + 1]) || (in[i] < in[i - 1] && in[i] <= in[i + 1])){
                list1.add(in[i]);
                list1index.add(i);
                map.put(-1,i);
            }
        }
        if (!list1.contains(in[in.length - 1])) {
            list1.add(in[in.length - 1]);
            list1index.add(in.length - 1);
            map.put(k,in.length-1);
        }
        //System.out.println("位置索引"+list1index);

        return list1index;
    }

    //单条序列中相邻两个极值点之间的，判断有无新的极值点,返回新的点的位置索引
    private static List<Integer> recursiveFit(List<Double> rawdataTemp,List<Integer> extremepointsTempIndex,int startIndex, int endIndex,double startValue,double endValue) {
        List<Double> newExtremePoint = new ArrayList<>();
        double data=-1;
        List<Integer> newExtremePointIndex = new ArrayList<>();
        int index=-1;

        double maxfitabsValue = 0.0;
        int maxFitIndex = -1;

        if (endIndex - startIndex <= 1) {
            // 停止拟合
            return newExtremePointIndex;
        }
//        System.out.println("区间[" + "s" + startIndex + "," + "s" + endIndex + "]拟合值:");


        for (int j = startIndex + 1; j < endIndex; j++) {
            double fitDataValue = linearInterpolation(j, startIndex, endIndex, startValue, endValue);
            double originalDataValue = rawdataTemp.get(j);


            double fitAbsValue = Math.abs(fitDataValue - originalDataValue);

            if (fitAbsValue >=fitt && fitAbsValue >= maxfitabsValue) {
                // 如果拟合差大于阈值且大于当前最大拟合差，更新最大拟合差和索引
                maxfitabsValue = fitAbsValue;
                maxFitIndex = j;
                data = originalDataValue;
                index = maxFitIndex;
            }
//            System.out.print("[s" + j + "]:" + fitDataValue + "  ");
////            System.out.println("原始值："+ originalDataValue);
//            System.out.println("拟合差[s" + j + "]:" + fitAbsValue);
        }

        //System.out.println();

        if (maxFitIndex != -1) {
            // 找到大于阈值且最大拟合差的点，将其添加到新的极值点列表中
            newExtremePoint.add(rawdataTemp.get(index));
            newExtremePointIndex.add(index);
        }

        if (maxFitIndex == -1) {
            return newExtremePointIndex;
        }

        return newExtremePointIndex;
    }


    private static double linearInterpolation(int currentIndex, int startIndex, int endIndex, double startValue,
                                              double endValue) {
        double t = (double) (currentIndex - startIndex) / (endIndex - startIndex);
        return startValue + t * (endValue - startValue);
    }


    static class SupportOrder {
        private double order;
        private Integer index;

        public SupportOrder(double order, Integer index) {
            this.order = order;
            this.index = index;
        }

        public double getOrder() {
            return order;
        }

        public void setOrder(Integer order) {
            this.order = order;
        }

        public Integer getIndex() {
            return index;
        }

        public void setIndex(Integer index) {
            this.index = index;
        }
    }

    static class Candidate {
        private double[] itemset;
        private Integer[] support;
        private Integer[] supportPre;
        private Integer[] supportSuf;

        public Candidate(double[] itemset, Integer[] support) {
            this.itemset = itemset;
            this.support = support;
        }

        public double[] getItemset() {
            return itemset;
        }

        public void setItemset(double[] itemset) {
            this.itemset = itemset;
        }

        public Integer[] getSupport() {
            return support;
        }

        public void setSupport(Integer[] support) {
            this.support = support;
        }

        public Integer[] getSupportPre() {
            return supportPre;
        }

        public void setSupportPre(Integer[] supportPre) {
            this.supportPre = supportPre;
        }

        public Integer[] getSupportSuf() {
            return supportSuf;
        }

        public void setSupportSuf(Integer[] supportSuf) {
            this.supportSuf = supportSuf;
        }
    }



    static class FreItemset {
        private double[] itemset;
        private Integer support;

        public FreItemset(double[] itemset, Integer support) {
            this.itemset = itemset;
            this.support = support;
        }

        public double[] getItemset() {
            return itemset;
        }

        public void setItemset(double[] itemset) {
            this.itemset = itemset;
        }

        public Integer getSupport() {
            return support;
        }

        public void setSupport(Integer support) {
            this.support = support;
        }
    }


}