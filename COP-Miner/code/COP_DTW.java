package COP_Mining;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.*;
import java.util.stream.Collectors;

public class COP_DTW {

    private static Map<Integer, Integer> map = new HashMap<>();
    private static Double[] input;
    private static Double[] in;

        private static Double[] p = new Double[]{2.0, 5.0, 3.0, 7.0, 6.0, 9.0, 1.0, 8.0};

//    private static Double[] p = new Double[]{1.0, 3.0, 2.0, 4.0};
//    private static Double[] p = new Double[]{1.0, 4.0, 2.0, 3.0};
//private static Double[] p = new Double[]{3.0, 2.0, 4.0, 1.0};
//private static Double[] p = new Double[]{3.0, 1.0, 5.0, 2.0,4.0};

//        private static Double[] p = new Double[]{3.0, 1.0, 2.0, 4.0,5.0};
//        private static Double[] p = new Double[]{1.0, 4.0, 2.0, 3.0};
//    private static Double[] p = new Double[]{1.0, 3.0, 2.0};
//        private static Double[] p = new Double[]{3.0, 2.0, 5.0, 1.0,4.0};
    private static Double[] pattern = getPatternExtreme(p);
    private static Double[] oneTwo = new Double[]{1D, 2D};
    private static Double[] pOrder = getOrder(pattern);
    private static int minsup = 8000;
    private static int k = 500; //相似度排序前几

    public static void main(String[] args) throws Exception {
        getInArr();
    }

    private static void readLine() {
        //找出现
        List<FindAppear> findOccList = findAppear(in, pattern);
        //输出相似度、共生
        printSimilarity(findOccList);
    }

    private static void printSimilarity(List<FindAppear> findOccList) {
        findOccList = findOccList.stream().sorted(Comparator.comparingDouble(FindAppear::getSimilar)).limit(k).collect(Collectors.toList());
        System.out.println("符合相似条件的模式为: ");
        for (FindAppear findAppear : findOccList){
            //求共生
            Double[] subOcc = new Double[pattern.length + 1];
            System.arraycopy(in, findAppear.index - pattern.length, subOcc, 0, subOcc.length);
            //打印输出
            System.out.println("出现的位置为：" + findAppear.index + ", " + "子序列为：" + Arrays.toString(findAppear.sub)
                    + ", " + "极值前子序列为：" + Arrays.toString(findAppear.subFor)
                    + ", " + "相似度为：" + findAppear.similar
                    + ", " + "其共生模式为：" + Arrays.toString(getOrder(subOcc)));
        }
    }

    private static List<FindAppear> findAppear(Double[] in, Double[] pattern) {
        Integer[] subsetNumArr;
        if (pattern.length == 2) {
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
            System.out.println("无满足支持度的模式！！！");
            return null;
        }
        List<FindAppear> findAppears = new ArrayList<>();
        for (int val : subsetNumArrNew){
            Double[] sub = new Double[pattern.length];
            System.arraycopy(in, val, sub, 0, sub.length);
            int len = map.get(val + pattern.length - 1) - map.get(val) + 1;
            Double[] subFor = new Double[len];
            System.arraycopy(input, map.get(val), subFor, 0, len);
            double similarity = getProximityByDtw(p, subFor);
            findAppears.add(new FindAppear(val + pattern.length, sub, subFor, similarity));
        }
        return findAppears;
    }

    private static void getInArr() throws Exception {


//        File file = new File("E:/Dataset/KURIAS_HeartRate训练集.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_PAxis训练集.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_PRInterval训练集.txt");
//        File file = new File("E:/Dataset/S&P 500训练集.txt");
//                File file = new File("E:/Dataset/ChengduPM2.5训练集.txt");
//                File file = new File("E:/Dataset/GuangZhouTemp训练集.txt");
//                File file = new File("E:/Dataset/Alabama_Confirmed训练集.txt");
//                File file = new File("E:/Dataset/NYSE训练集.txt");
                        File file = new File("D:/Dataset/NYSE352_352.txt");


        BufferedReader br = new BufferedReader(new FileReader(file));
        String s;
        //使用readLine方法，一次读一行
        while ((s = br.readLine()) != null) {
            List<Double> inList = new ArrayList<>();
            s = s.trim();
            String[] str = s.split(" ");
            String[] strArr = new String[str.length - 1];
            System.arraycopy(str, 1, strArr, 0, strArr.length);
            for (String s1 : strArr) {
                if (!" ".equals(s1) && !s1.isEmpty()) {
                    inList.add(Double.parseDouble(s1));
                }
            }
            Double[] inArr = new Double[inList.size()];
            int i = 0;
            for (double inLine : inList) {
                inArr[i++] = inLine;
            }
            input = inArr;
            in = getExtremePoint(input);
            readLine();
        }
        br.close();
    }

    private static double getProximityByDtw(Double[] x, Double[] y) {
        Double[][] dis = new Double[y.length][x.length];
        for (int i = 0; i < x.length; i++) {
            if (i == 0) {
                dis[0][i] = getDistance(x[i], y[0]);
            } else {
                dis[0][i] = getDistance(x[i], y[0]) + dis[0][i - 1];
            }
        }

        for (int i = 0; i < y.length; i++) {
            if (i == 0) {
                dis[i][0] = getDistance(x[0], y[i]);
            } else {
                dis[i][0] = getDistance(x[0], y[i]) + dis[i - 1][0];
            }
        }

        for (int i = 1; i < y.length; i++) {
            for (int j = 1; j < x.length; j++) {
                dis[i][j] = getDistance(x[j], y[i]) + Math.min(dis[i - 1][j], Math.min(dis[i][j - 1], dis[i - 1][j - 1]));
            }
        }
        return dis[y.length - 1][x.length - 1];
    }

    private static Double getDistance(Double x, Double y) {
        if (x >= y) {
            return x - y;
        } else {
            return y - x;
        }
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

    private static Double[] getOrder(Double[] seq) {
        Set<Double> set = new TreeSet<>();
        Collections.addAll(set, seq);
        if (seq.length != set.size()){
            return null;
        }
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

    static class FindAppear{
        private int index; //出现位置
        private Double[] sub; //子序列
        private Double[] subFor; //极值前子序列
        private Double similar; //相似度

        public FindAppear(int index, Double[] sub, Double[] subFor, Double similar) {
            this.index = index;
            this.sub = sub;
            this.subFor = subFor;
            this.similar = similar;
        }

        public Double getSimilar() {
            return similar;
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
}
