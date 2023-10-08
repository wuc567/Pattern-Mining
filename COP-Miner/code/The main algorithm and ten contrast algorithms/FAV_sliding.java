package COP_Mining;


import newalgorithm.MemoryLogger;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.text.DecimalFormat;
import java.util.*;
import java.util.stream.Collectors;


public class FAV_sliding {


    static int id;
    public static String lab;
    static boolean sign = false;
    static List<String> pat = new ArrayList<>();

    private static Map<Integer, Integer> map = new HashMap<>();
    private static Double[] input;
    private static Double[] in;
//            private static Double[] p = new Double[]{1.0, 5.0, 2.0};
//    private static Double[] p = new Double[]{1.0, 5.0, 2.0, 6.0};
//    private static Double[] p = new Double[]{1.0, 5.0, 2.0, 6.0, 3.0};
//    private static Double[] p = new Double[]{1.0, 5.0, 2.0, 6.0, 3.0, 4.0};
//    private static Double[] p = new Double[]{1.0, 6.0, 3.0, 7.0, 4.0, 5.0, 2.0};
//    private static Double[] p = new Double[]{1.0, 3.0, 2.0,5.0,4.0,6.0};
//private static Double[] p = new Double[]{1.0,4.0,2.0};
//private static Double[] p = new Double[]{3.0, 1.0, 2.0, 4.0, 5.0};

//        private static Double[] p = new Double[]{1.0, 3.0, 2.0};
//    private static Double[] p = new Double[]{1.0, 3.0, 2.0, 4.0};
//    private static Double[] p = new Double[]{1.0, 3.0, 2.0, 5.0, 4.0};
    private static Double[] p = new Double[]{1.0, 3.0, 2.0, 5.0, 4.0, 6.0};
//    private static Double[] p = new Double[]{1.0, 4.0, 2.0, 6.0, 5.0, 7.0, 3.0};

    private static Double[] pattern = getPatternExtreme(p);
    //无提取
//private static Double[] pattern = p;


    private static int minsup = 16;
    private static Map<String, Integer> supMap = new HashMap<>();
    private static int canNum; //候选
    private static int freNum; //频繁
    private static int canNumCount; //候选总数
    private static int freNumCount; //频繁总数
    private static int compareNum; //比较次数
    private static Double[] oneTwo = new Double[]{1D, 2D};
    private static Double[] twoOne = new Double[]{2D, 1D};
    private static Double[] pOrder = getOrder(pattern);

    public static void main(String[] args) throws Exception {
        long startTime = System.currentTimeMillis();
        //读文件
        getInArr();
        printCostTime(startTime);
    }

    private static void getInArr() throws Exception {
        File file = new File("D:/Dataset/NYSE1.txt");

//        File file = new File("E:/Dataset/BeijingPM2.5.txt");
//        File file = new File("E:/Dataset/PRSA_Data.txt");
//        File file = new File("E:/Dataset/Data-Stock.txt");
//        File file = new File("E:/Dataset/Increase rate.txt");
//        File file = new File("E:/Dataset/Online-Retail.txt");
//        File file = new File("E:/Dataset/USincrease.txt");
//        File file = new File("E:/Dataset/Alabama_Confirmed.txt");

//        File file = new File("E:/Dataset/KURIAS-ECG_HeartRate.txt");

//        File file = new File("E:/Dataset/KURIAS_HeartRate训练集.txt");
//        File file = new File("E:/Dataset/KURIAS_HeartRate测试集.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_PAxis训练集.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_PAxis测试集.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_PRInterval训练集.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_PRInterval测试集.txt");
//                File file = new File("E:/Dataset/S&P 500训练集.txt");
//        File file = new File("E:/Dataset/S&P 500测试集.txt");
//                File file = new File("E:/Dataset/ChengduPM2.5训练集.txt");
//        File file = new File("E:/Dataset/ChengduPM2.5测试集.txt");
//        File file = new File("E:/Dataset/GuangZhouTemp训练集.txt");
//        File file = new File("E:/Dataset/GuangZhouTemp测试集.txt");
//        File file = new File("E:/Dataset/Alabama_Confirmed训练集.txt");
//        File file = new File("E:/Dataset/Alabama_Confirmed测试集.txt");
//        File file = new File("E:/Dataset/Online-Retail训练集.txt");
//        File file = new File("E:/Dataset/Online-Retail测试集.txt");
//        File file = new File("E:/Dataset/Brent.txt");
//        File file = new File("E:/Dataset/NYSE训练集.txt");
//                File file = new File("E:/Dataset/NYSE测试集.txt");


//        File file = new File("E:/Dataset/GuangZhou_Temp.txt");
//        File file = new File("E:/Dataset/NYSE1.txt");
//        File file = new File("E:/Dataset/NYSE2.txt");
//        File file = new File("E:/Dataset/NYSE3.txt");
//        File file = new File("E:/Dataset/NYSE4.txt");
//        File file = new File("E:/Dataset/NYSE5.txt");
//        File file = new File("E:/Dataset/NYSE6.txt");
//        File file = new File("E:/Dataset/NYSE7.txt");
//        File file = new File("E:/Dataset/NYSE8.txt");
        BufferedReader br = new BufferedReader(new FileReader(file));
        String s;
        //使用readLine方法，一次读一行
        while ((s = br.readLine()) != null) {
            List<Double> outList = new ArrayList<>();
            List<Double> inList = new ArrayList<>();
            s = s.trim();
            String[] str = s.split(" ");
            lab = str[0];
            String[] strArr = new String[str.length - 1];
            System.arraycopy(str, 1, strArr, 0, strArr.length);
            for (String s1 : strArr) {
                if (!" ".equals(s1) && !s1.isEmpty()) {
                    inList.add(Double.parseDouble(s1));
                    outList.add(Double.parseDouble(s1));
                }
            }
            Double[] inArr = new Double[inList.size()];
            int i = 0;
            for (double inLine : inList) {
                inArr[i++] = inLine;
            }
            input = inArr;
            in = getExtremePoint(input);
            //无提取
//            in = input;

            sign = false;
            readLine();
            i++;
//            System.gc();
//            System.out.println(Arrays.toString(in));
//            System.out.println(Arrays.toString(pattern));
        }
        br.close();
    }

    private static void readLine() {
        //初始化数据
        canNum = 0;
        freNum = 0;
        //找出现
        List<FindOcc> findOccList = findOcc(in, pattern);
        //找共生
        List<CoOccurrence> occurrenceList = findCoOc(findOccList);
//        打印共生模式

//        printCoOccurrence(occurrenceList);
    }

    private static void printCoOccurrence(List<CoOccurrence> occurrenceList) {
        for (CoOccurrence coOccurrence : occurrenceList) {
            System.out.println("共生模式为：" + coOccurrence.model);
            System.out.println("支持度为：" + coOccurrence.sup);
            System.out.println("-------------------------------");
        }
//        System.out.println("候选总个数为：" + canNum);
//        System.out.println("频繁总个数为：" + freNum);
//        System.out.println("-------------------------------------------");
    }

    private static void printCostTime(long startTime) {
        System.out.println("候选模式的总数是：" + canNumCount);
        System.out.println("共生频繁模式的总数为：" + freNumCount);
        System.out.println("元素比较总次数为：" + compareNum);
        System.out.println("-------------------------------------------");
        System.out.println("花费总时间为:" + (System.currentTimeMillis() - startTime) + "ms");
//        System.out.println("---------------------------------------------------");
        MemoryLogger.getInstance().checkMemory();
        double maxMemory = MemoryLogger.getInstance().getMaxMemory();
        System.out.println("最大内存占用: " + maxMemory + " Mb");
    }

    private static List<CoOccurrence> findCoOc(List<FindOcc> findOccList) {
        List<CoOccurrence> occurrenceList = new ArrayList<>();
        while (findOccList != null && findOccList.size() > 0) {
            supMap = new HashMap<>();
            if (findOccList.get(0).order.length == 2) {
                for (FindOcc findOcc : findOccList) {
                    if (findOcc.index >= in.length - 1) {
                        //共生超出长度，设-1，淘汰
                        findOcc.index = -1;
                    } else {
                        findOcc.index++;
                        if (Arrays.asList(findOcc.sub).contains(in[findOcc.index])) {
                            //序列出现重复数据，设-1，淘汰
                            findOcc.index = -1;
                            continue;
                        }
                        Double[] sub = Arrays.copyOf(findOcc.sub, findOcc.sub.length + 1);
                        sub[sub.length - 1] = in[findOcc.index];
                        findOcc.sub = sub;
                        compareNum++;
                        if (Arrays.equals(pOrder, oneTwo)) {
                            if (sub[sub.length - 1] > sub[0]) {
                                findOcc.order = new Double[]{1D, 3D, 2D};
                            } else {
                                findOcc.order = new Double[]{2D, 3D, 1D};
                            }
                        } else {
                            if (sub[sub.length - 1] > sub[0]) {
                                findOcc.order = new Double[]{2D, 1D, 3D};
                            } else {
                                findOcc.order = new Double[]{3D, 1D, 2D};
                            }
                        }
                        supMap.merge(Arrays.toString(findOcc.order), 1, Integer::sum);
                    }
                }
            } else {
                for (FindOcc findOcc : findOccList) {
                    if (findOcc.index >= in.length - 1) {
                        //共生超出长度，设-1，淘汰
                        findOcc.index = -1;
                    } else {
                        findOcc.index++;
                        if (Arrays.asList(findOcc.sub).contains(in[findOcc.index])) {
                            //序列出现重复数据，设-1，淘汰
                            findOcc.index = -1;
                            continue;
                        }
                        Double[] sub = Arrays.copyOf(findOcc.sub, findOcc.sub.length + 1);
                        sub[sub.length - 1] = in[findOcc.index];
                        findOcc.sub = sub;
                        findOcc.order = getCompareOrder(findOcc.sub, findOcc.order);
                        supMap.merge(Arrays.toString(findOcc.order), 1, Integer::sum);
                    }
                }
            }
            canNum += supMap.size();
            findOccList = findOccList.stream().filter(x -> x.index != -1).collect(Collectors.toList());
//            Map<String, Integer> lowMap =supMap.entrySet().stream().filter(x -> x.getValue() < minsup).collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
            supMap = supMap.entrySet().stream().filter(x -> x.getValue() >= minsup).collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
            freNum += supMap.size();
            if (supMap.size() == 0) {
                findOccList = new ArrayList<>();
            }
            findOccList = findOccList.stream().filter(x -> supMap.containsKey(Arrays.toString(x.order))).collect(Collectors.toList());
            DecimalFormat decimalFormat = new DecimalFormat("0.00");
            for (Map.Entry<String, Integer> entry : supMap.entrySet()) {
                occurrenceList.add(new CoOccurrence(entry.getKey(), entry.getValue()));
            }
            canNumCount += canNum;
            freNumCount += freNum;
            canNum = 0;
            freNum = 0;
        }

        return occurrenceList;
    }

    private static List<FindOcc> findOcc(Double[] in, Double[] pattern) {
//        int[] inBinaryArr = getBinary(in);
//        int[] pBinaryArr = getBinary(pattern);
        Integer[] subsetNumArr;
        if (pattern.length == 2) {
            //subsetNumArr = bndm(inBinaryArr, pBinaryArr);
            subsetNumArr = getSubset(in, pattern);
        } else {
            int[] inBinaryArr = getBinary(in);
            int[] pBinaryArr = getBinary(pattern);
            int[] sortedP = new int[pBinaryArr.length];
            System.arraycopy(pBinaryArr, 0, sortedP, 0, sortedP.length);
            Arrays.sort(sortedP);
            int[] aux = new int[pBinaryArr.length];
            genAux(aux, sortedP, pBinaryArr);
            subsetNumArr = sbndm(inBinaryArr, pBinaryArr, aux, in);
        }
        Integer[] subsetNumArrNew;
        if (pattern.length == 2) {
            subsetNumArrNew = subsetNumArr;
        } else {
            subsetNumArrNew = verificationStrategy(in, pattern, subsetNumArr);
        }
        if (subsetNumArrNew.length < minsup) {
            //不满足支持度
            return null;
        }
        List<FindOcc> findOccList = new ArrayList<>();
        for (int index : subsetNumArrNew) {
            Double[] sub = new Double[pattern.length];
            System.arraycopy(in, index, sub, 0, sub.length);
            findOccList.add(new FindOcc(index + pattern.length - 1, sub, getOrder(sub)));
        }
        return findOccList;
    }

    private static Integer[] getSubset(Double[] in, Double[] pattern) {
        List<Integer> subsetNumList = new ArrayList<>();
        if (Arrays.equals(pOrder, oneTwo)) {
            for (int i = 0; i < in.length - 1; i++) {
                if (in[i + 1] > in[i]) {
                    subsetNumList.add(i);
                }
            }
        } else {
            for (int i = 0; i < in.length - 1; i++) {
                if (in[i + 1] < in[i]) {
                    subsetNumList.add(i);
                }
            }
        }
        Integer[] subsetNumArr = new Integer[subsetNumList.size()];
        subsetNumList.toArray(subsetNumArr);
        return subsetNumArr;
    }

    private static Double[] getExtremePoint(Double[] input) {
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
        Double[] arr = new Double[list.size()];
        for (double item : list) {
            arr[i++] = item;
        }
        return arr;
    }

    private static Double[] getPatternExtreme(Double[] p) {
        List<Double> list = new ArrayList<>();
        list.add(p[0]);
        for (int i = 1; i < p.length - 1; i++) {
            if ((p[i] >= p[i - 1] && p[i] > p[i + 1]) || (p[i] > p[i - 1] && p[i] >= p[i + 1])) {
                list.add(p[i]);
            } else if ((p[i] <= p[i - 1] && p[i] < p[i + 1]) || (p[i] < p[i - 1] && p[i] <= p[i + 1])) {
                list.add(p[i]);
            }
        }
        list.add(p[p.length - 1]);
        int i = 0;
        Double[] arr = new Double[list.size()];
        for (double item : list) {
            arr[i++] = item;
        }
        return arr;
    }

    private static int[] getBinary(Double[] arr) {
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

    private static void genAux(int[] aux, int[] sortedP, int[] p) {
        for (int i = 0; i < p.length; i++) {
            for (int j = 0; j < p.length; j++) {
                if (sortedP[i] == p[j]) {
                    aux[i] = j + 1;
                }
            }
        }
    }

    private static Integer[] sbndm(int[] txt, int[] pat, int[] aux, Double[] s) {
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

    private static Integer[] verificationStrategy(Double[] in, Double[] pattern, Integer[] subsetNumArr) {
        List<Integer> subsetListNew = new ArrayList<>();
        List<SupportOrder> supportOrderList = new ArrayList<>();
        int index = 1;
        for (double order : pattern) {
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

    private static Double[] getOrder(Double[] seq) {
        Double[] arr = new Double[seq.length];
        System.arraycopy(seq, 0, arr, 0, seq.length);
        Double[] order = new Double[arr.length];
        Double[] temp = new Double[arr.length];
        System.arraycopy(arr, 0, temp, 0, arr.length);
        Arrays.sort(temp);

        for (int j = 0; j < arr.length; j++) {
            double min = temp[temp.length - 1] + 1;
            int index = 0;
            for (int i = 0; i < arr.length; i++) {
                if (arr[i] < min && arr[i] != (double) Integer.MIN_VALUE) {
                    min = arr[i];
                    index = i;
                }
            }
            arr[index] = (double) Integer.MIN_VALUE;
            order[index] = j + 1D;
        }
        return order;
    }

    private static Double[] getCompareOrder(Double[] sub, Double[] order) {
        compareNum += order.length;
        double end = sub[sub.length - 1];
        double rank = 1;
        for (int i = 0; i < order.length; i++) {
            if (sub[i] > end) {
                order[i]++;
            } else {
                rank++;
            }
        }
        Double[] orderNew = Arrays.copyOf(order, order.length + 1);
        orderNew[orderNew.length - 1] = rank;
        return orderNew;
    }

    static class FindOcc {
        private int index; //出现位置
        private Double[] sub; //子序列
        private Double[] order; //次序

        public FindOcc(int index, Double[] sub, Double[] order) {
            this.index = index;
            this.sub = sub;
            this.order = order;
        }
    }

    static class SupportOrder {
        private double order;
        private Integer index;

        SupportOrder(double order, Integer index) {
            this.order = order;
            this.index = index;
        }

        public double getOrder() {
            return order;
        }

        public void setOrder(double order) {
            this.order = order;
        }

        public Integer getIndex() {
            return index;
        }

        public void setIndex(Integer index) {
            this.index = index;
        }
    }

    static class CoOccurrence {
        private String model; //模式
        private int sup; //支持度
        private List<double[]> appearList; //原序列出现

        public CoOccurrence(String model, int sup) {
            this.model = model;
            this.sup = sup;
        }
    }
}

