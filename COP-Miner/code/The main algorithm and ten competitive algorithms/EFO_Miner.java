package COP_Mining;

import algorithm.RLF_Miner;
import newalgorithm.MemoryLogger;
import java.io.*;
import java.net.URL;
import java.util.*;
import java.util.stream.Collectors;

public class EFO_Miner {

    public static int minsup = 6000;
    public static int frequent_num = 0;  //总的频繁模式数量
    public static int fre_num = 0;
    public static int cd_num = 2;//候选模式数量
    public static int scan_num = 1;//扫描序列次数
    public static int read_num = 0;//访问序列次数
    public static int element_num = 0;

//    public static double[] p = new double[]{1,2};
//public static double[] p = new double[]{3,4,1,2};
//public static double[] p = new double[]{1,3,2,5,4,7,6,9};
//public static double[] p = new double[]{1,6,3,5,2,4,2.5,10};
//public static double[] p = new double[]{4,5,2,3,1,6};
//public static double[] p = new double[]{1,4,2,3};
//public static double[] p = new double[]{1,3,2,5,4,7,6,9};

//public static double[] p = new double[]{4,5,2,3,1,9,7,8};
//public static double[] p = new double[]{2,3,1,8,6,7,4,5};
//    public static double[] p = new double[]{1,3,2,5};
//public static double[] p = new double[]{5,6,3,4,1,2};
//public static double[] p = new double[]{2,3,1,6,4,5};
//public static double[] p = new double[]{2,1,4,3,6,5};
//public static double[] p = new double[]{1,4,2,5,3,6};

//public static double[] p = new double[]{2,4,1,5,3};
//public static double[] p = new double[]{5,6,3,4,1,2};
//public static double[] p = new double[]{1,3,2,5,4,7,6};
//public static double[] p = new double[]{1,3,2,5,4,7,6,8};
//public static double[] p = new double[]{1,3,2,5,4,7,6,9,8};


//public static double[] p = new double[]{3,6,4,5,1,2};
//public static double[] p = new double[]{1,3,2,5,4,6};
//    private static double[] p = new double[]{1.0, 4.0, 3.0,6.0,5.0, 2.0};
//private static double[] p = new double[]{4.0, 3.0, 6.0, 2.0, 5.0, 1.0};

private static double[] p = new double[]{1.0, 3.0, 2.0, 5.0, 4.0, 6.0};
//    private static double[] p = new double[]{1.0, 3.0, 2.0, 6.0, 4.0, 5.0};

//public static double[] p = new double[]{4,5,2,3,1,6};

    //!!!!!!!!!!!
//private static double[] p = new double[]{1.0, 5.0, 2.0, 6.0, 3.0, 4.0};
//private static double[] p = new double[]{1.0, 5.0, 3.0, 4.0, 2.0, 6.0};


//public static double[] p = new double[]{3.0, 4.0, 1.0, 7.0, 5.0, 6.0, 2.0};
//private static double[] p = new double[]{3.0, 4.0, 1.0, 7.0, 5.0, 6.0, 2.0,8.0};

//    private static double[] p = new double[]{7.0, 8.0, 5.0, 6.0, 3.0, 4.0, 1.0,2.0};
//    private static double[] p = new double[]{6.0, 7.0, 4.0, 5.0, 2.0, 3.0};
//private static double[] p = new double[]{8,7,3,2,4,1,5,6};

//    public static double[] p = new double[]{1,3,2,4};
//    public static double[] p = new double[]{1, 2};
//public static double[] p = new double[]{2.0,1.0,4.0,3.0};
//    public static double[] p = new double[]{2.0,1.0,4.0,3.0,6.0,5.0};
//    public static double[] p = new double[]{2.0,1.0,4.0,3.0,6.0,5.0,8.0,7.0};


    public static double[] pattern = getPatternExtreme(p);
    public static List<Candidate> candidateList = new ArrayList<>();
    private static Boolean flag;
    private static Map<Integer, Integer> map = new HashMap<>();
    private static List<Double> preList = new ArrayList<>();
    private static List<Double> sufList = new ArrayList<>();
    private static Set<String> set = new HashSet<>();
    private static int freCount = 0;
    private static int candCount = 0;
    private static int coFreCount = 0;
    private static int coFreSeqCount = 0;
    private static int coSimSeqCount = 0;


    static List<List<Integer>> P = new ArrayList<>(); //存放末位的数组
    static List<List<Integer>> L = new ArrayList<>();//存放每次生成的频繁模式
//    static List<List<Integer>> Pre = new ArrayList<>();//存放前缀模式
//    static List<List<Integer>> Suf = new ArrayList<>();//存放后缀模式

    static List<Integer> Z = new ArrayList<>(); //存放本次生成的末位数组
    static List<Integer> Z2 = new ArrayList<>();

    static List<Integer> Cd = new ArrayList<>(); //存放本次生成的模式
    static List<Integer> Cd2 = new ArrayList<>();

    static List<Double> Seq = new ArrayList<>(); // sequence
    static List<Double> S = new ArrayList<>(); // sequence

    public static void main(String[] args) throws IOException {
        System.gc();
        readFile();
//        System.out.println("The number of scan sequence: " + scan_num);
//        System.out.println("The number of read sequence: " + read_num);
        System.gc();
    }

    private static void runSingleSeq() {

        getExtremePoint();
        readLine();
//        System.out.println("The number of frequent patterns: " + frequent_num);
//        System.out.println("The number of candidate patterns: " + cd_num);

    }

    private static void readFile() throws IOException {
        long begintime = System.currentTimeMillis();
//        File file = new File("E:/Dataset/NYSE Price.txt");
//        File file = new File("E:/Dataset/NYSE1.txt");
//        File file = new File("E:/Dataset/NYSE2.txt");
//        File file = new File("E:/Dataset/NYSE3.txt");
//        File file = new File("E:/Dataset/NYSE4.txt");
//        File file = new File("E:/Dataset/NYSE5.txt");
//        File file = new File("E:/Dataset/NYSE6.txt");
//        File file = new File("E:/Dataset/NYSE7.txt");
        File file = new File("D:/Dataset/NYSE440_440.txt");
//        SDB1
//        File file = new File("E:/Dataset/Crude Oil.txt");

//        SDB2
//        File file = new File("E:/Dataset/CinCECGTorso.txt");

//        SDB3
//        File file = new File("E:/Dataset/FiveCitiesTempData.txt");

//        SDB4
//        File file = new File("E:/Dataset/S&P 500.txt");
//        File file = new File("E:/Dataset/STOCK-prediction.txt");
//        File file = new File("E:/Dataset/Online-Retail.txt");
//        File file = new File("E:/Dataset/Alabama_Confirmed.txt");

//        SDB5
//        File file = new File("E:/Dataset/NonInvasiveFetalECGThorax1.txt");
//        File file = new File("E:/Dataset/FiveCitiesTempData.txt");

//        SDB6
//        File file = new File("E:/Dataset/ChengduPM2.5.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5.txt");
//        File file = new File("E:/Dataset/PRSA_Data.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_HeartRate.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_PRInterval.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_PAxis.txt");

//        File file = new File("E:/Dataset/ToeSegmentation1_TRAIN.txt");
//        File file = new File("E:/Dataset/1WTl-2.txt");
//        File file = new File("E:/Dataset/Crude Oil.txt");
//        File file = new File("E:/Dataset/PRSA_Data_Nongzhanguan.txt");
//        File file = new File("E:/Dataset/Italian-temperature.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_database.txt");
//        File file = new File("E:/Dataset/ChengduPM2.5.txt");

//        File file = new File("E:/Dataset/Meat_TEST.txt");

//        SDB7
//        File file = new File("E:/Dataset/BeijingPM2.5.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5_2.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5_3.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5_4.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5_5.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5_6.txt");

//        SDB8
//        File file = new File("E:/Dataset/PRSA_Data.txt");

//        COVID-19
//        File file = new File("E:/Dataset/分类/CSSE COVID-19 Dataset.txt");

//        File file = new File("E:/Dataset/分类/Beef_TEST.txt");
//        File file = new File("E:/Dataset/分类/Car_TEST.txt");
//        File file = new File("E:/Dataset/分类/ShapeletSim_TEST.txt");

//        File file = new File("E:/Dataset/分类/CSSE COVID-19 - 副本.txt");
//        File file = new File("E:/Dataset/分类/BTC.txt");
//        File file = new File("E:/Dataset/分类/Beef_TEST.txt");
//        File file = new File("E:/Dataset/Meat_TEST.txt");
//        File file = new File("E:/Dataset/1WTl-2.txt");

//        File file = new File("E:/Dataset/分类/CSSE COVID-19.txt");

        BufferedReader br = new BufferedReader(new FileReader(file));
        String s;
        //使用readLine方法，一次读一行
        while ((s = br.readLine()) != null) {
            Seq = new ArrayList<>();
            S = new ArrayList<>();
            candidateList = new ArrayList<>();
            P = new ArrayList<>(); //存放末位的数组
            L = new ArrayList<>();//存放每次生成的频繁模式
            Z = new ArrayList<>(); //存放本次生成的末位数组
            Z2 = new ArrayList<>();
            Cd = new ArrayList<>(); //存放本次生成的模式
            Cd2 = new ArrayList<>();
            frequent_num = 0;  //总的频繁模式数量
            fre_num = 0;
            cd_num = 2;//候选模式数量
            scan_num = 1;//扫描序列次数
//            read_num = 0;//访问序列次数

            s = s.trim();
            String[] str = s.split(" ");
            String[] strArr = new String[str.length - 1];
            System.arraycopy(str, 1, strArr, 0, strArr.length);
            for (String s1 : strArr) {
                if (!" ".equals(s1) && !s1.isEmpty()) {
                    Seq.add(Double.parseDouble(s1));
                }
            }
            runSingleSeq();
//            System.gc();
        }
        br.close();
        System.out.println("候选模式的总数是:" + candCount);
        System.out.println("共生频繁模式的总数为:" + coFreCount);
        System.out.println("元素比较总次数为: "+element_num);
        System.out.println("---------------------------------------------------");
        System.out.println("花费总时间为:" + (System.currentTimeMillis() - begintime) + "ms");
        printCostMemory(begintime);

//        System.out.println("频繁模式的总数是:" + freCount);

//        System.out.println("共生频繁子序列的总数为:" + coFreSeqCount);
//        System.out.println("满足支持度及相似度阈值的共生子序列总为:" + coSimSeqCount);
//        System.out.println("---------------------------------------------------");
//        System.out.println("---------------------------------------------------");
//        System.out.println("The number of read sequence: "+read_num);


//        System.out.println("组合对的个数为：" + Pre.size() + ", " + Suf.size());
        /*System.out.println("花费总时间为:" + (System.currentTimeMillis() - begintime) + "ms");
        printCostMemory(begintime);*/
    }

    private static void readLine() {
        flag = null;
        preList = new ArrayList<>();
        sufList = new ArrayList<>();
        double similarityTv = 0.5;
        find();
        while (fre_num > 0) {
            generate_fre();
            System.gc();
        }

//        System.out.println("频繁模式的个数是: " + frequent_num);
//        System.out.println("候选模式的个数是: " + cd_num);

        freCount += frequent_num;
        candCount += cd_num;

        List<CoOccurrence> coOccurrences;
        coOccurrences = getIndex();
        printCoOccurrence(coOccurrences);
        //共生模式相似度阈值过滤并排序
//        List<Approximate> approximates = getSimilarity(coOccurrences, p, similarityTv);
//        printApproximate(approximates);
    }

    private static void printCostMemory(long startTime) {
        MemoryLogger.getInstance().checkMemory();
        double maxMemory = MemoryLogger.getInstance().getMaxMemory();
        System.out.println("最大内存占用: " + maxMemory + " Mb");
    }

    private static void printApproximate(List<Approximate> approximates) {
        if (approximates == null || approximates.size() == 0) {
//            System.out.println("无满足支持度及相似度阈值的子(共生)序列:");
//            System.out.println("---------------------------------------------------");
            return;
        }
        System.out.println("满足支持度及相似度阈值的共生子序列：");
        for (Approximate approximate : approximates) {
            System.out.print(approximate.getSimilarity() + ", ");
            printArray(approximate.getProximity());
        }
        System.out.println("满足支持度及相似度阈值的共生子序列个数为:" + approximates.size());
        coSimSeqCount += approximates.size();
        System.out.println("---------------------------------------------------");
    }


    private static List<Approximate> getSimilarity(List<CoOccurrence> coOccurrences, double[] pattern, double similarityTv) {
        if (coOccurrences == null) {
            return null;
        }
        List<double[]> subList = new ArrayList<>();
        coOccurrences.stream().peek(x -> subList.addAll(x.subModes)).collect(Collectors.toList());
        List<Approximate> approximates = getApproximateSimilarityList(subList, pattern, similarityTv);
        approximates.sort(Comparator.comparingDouble(Approximate::getSimilarity));
        return approximates;
    }

    private static List<Approximate> getApproximateSimilarityList(List<double[]> subList, double[] pattern, double similarityTv) {
        List<Approximate> approximates = new ArrayList<>();
        double[] paStatute = getStatute(pattern, false);
        for (double[] arr : subList) {
            double[] arrStatute = getStatute(arr, false);
            //double similarity = getProximity(paStatute, arrStatute);
            double similarity = getProximityByDtw(paStatute, arrStatute);
            if (similarity <= similarityTv) {
                Approximate approximate = new Approximate(similarity, arr);
                approximates.add(approximate);
            }
        }
        return approximates;
    }

    private static double getProximityByDtw(double[] x, double[] y) {
        double[][] dis = new double[y.length][x.length];
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

    private static double getDistance(double x, double y) {
        if (x >= y) {
            return x - y;
        } else {
            return y - x;
        }
    }

    private static double[] getStatute(double[] arr, boolean symbiosis) {
        if (symbiosis) {
            double[] arrNew = new double[arr.length - 1];
            System.arraycopy(arr, 0, arrNew, 0, arr.length - 1);
            double[] temp = new double[arr.length - 1];
            System.arraycopy(arr, 0, temp, 0, arr.length - 1);
            Arrays.sort(temp);
            double min = temp[0];
            double max = temp[temp.length - 1];
            for (int i = 0; i < arr.length - 1; i++) {
                arrNew[i] = (arrNew[i] - min) / (max - min);
            }
            double[] arrNewS = new double[arr.length];
            System.arraycopy(arrNew, 0, arrNewS, 0, arrNew.length);
            arrNewS[arrNewS.length - 1] = arr[arr.length - 1];
            return arrNewS;
        } else {
            double[] arrNew = new double[arr.length];
            System.arraycopy(arr, 0, arrNew, 0, arr.length);
            double[] temp = new double[arr.length];
            System.arraycopy(arr, 0, temp, 0, arr.length);
            Arrays.sort(temp);
            double min = temp[0];
            double max = temp[temp.length - 1];
            for (int i = 0; i < arr.length; i++) {
                arrNew[i] = (arrNew[i] - min) / (max - min);
            }
            return arrNew;
        }
    }


    private static void printCoOccurrence(List<CoOccurrence> coOccurrences) {

        if (coOccurrences == null || coOccurrences.size() == 0) {
//            System.out.println("无满足支持度的共生模式！！！");
            return;
        }
        /*System.out.println("满足支持度的共生模式：");
        for (CoOccurrence coOccurrence : coOccurrences) {
            printArray(coOccurrence.model);
        }*/
//        System.out.println("共生频繁模式的个数为:" + coOccurrences.size());
        coFreCount += coOccurrences.size();
//        System.out.println("---------------------------------------------------");
        int total = 0;
//        System.out.println("满足支持度的共生频繁子序列为:");
        for (CoOccurrence coOccurrence : coOccurrences) {
            for (double[] arr : coOccurrence.appearList) {
//                printArray(arr);
                total++;
            }
        }
//        System.out.println("共生频繁子序列的个数为:" + total);
        coFreSeqCount += total;
//         System.out.println("---------------------------------------------------");
    }

    private static void printArray(double[] arr) {
        for (double i : arr) {
            System.out.print(i + " ");
        }
        System.out.println();
    }

    public static List<CoOccurrence> getIndex() {
        if (candidateList.size() == 0) {
            return null;
        }
//        candCount +=candidateList.size();
        double[] input = new double[Seq.size()];
        for (int i = 0; i < input.length; i++) {
            input[i] = Seq.get(i);
        }
        List<CoOccurrence> coOccurrenceList = new ArrayList<>();
        for (Candidate candidate : candidateList) {
            double[] itemset = getItemset(candidate.itemset, pattern);
            if (Arrays.equals(getOrder(itemset), getOrder(pattern))) {
                List<double[]> appearList = new ArrayList<>();
                List<double[]> subModes = new ArrayList<>();
                if (!flag){
                    continue;
                }
                for (int index : candidate.support) {
                    int start = map.get(index - candidate.itemset.length);
                    int end = map.get(index - 1);
                    double[] appear = new double[end - start + 1];
                    System.arraycopy(input, start, appear, 0, appear.length);
                    appearList.add(appear);

                    int len;
                    if (flag) {
                        end = map.get(index - 2);
                        len = end - start + 1;
                    } else {
                        start = map.get(index - candidate.itemset.length + 1);
                        len = end - start + 1;
                    }
                    double[] subMode = new double[len];
                    System.arraycopy(input, start, subMode, 0, subMode.length);
                    subModes.add(subMode);
                }
                coOccurrenceList.add(new CoOccurrence(candidate.itemset, appearList, subModes));
            }
        }
        return coOccurrenceList;
    }

    private static double[] getItemset(double[] item, double[] pattern) {
        double[] itemset = new double[pattern.length];
        System.arraycopy(item, 0, itemset, 0, itemset.length);
        if (Arrays.equals(getOrder(itemset), getOrder(pattern))) {
            flag = true;
            return itemset;
        }
        System.arraycopy(item, 1, itemset, 0, itemset.length);
        flag = false;
        return itemset;
    }

    public static String fileToPath(String filename) throws UnsupportedEncodingException {
        URL url = RLF_Miner.class.getResource(filename);
        return java.net.URLDecoder.decode(url.getPath(), "UTF-8");
    }

    public static void read_file(String filePath) {

        BufferedReader br = null;
        BufferedReader br2 = null;
        try {
            br = new BufferedReader(new FileReader(filePath));
            String contentLine;
            List<String> arr1 = new ArrayList<>();

            while ((contentLine = br.readLine()) != null) {
                arr1.add(contentLine);
            }
            for (int k = 0; k < arr1.size(); k++) {
                Seq.add(Double.parseDouble(arr1.get(k)));
            }
        } catch (IOException e) {
            System.out.println("Error in closing the BufferedReader");
        }
    }

    public static void find() {
        int i = 0, j = 1;
        Cd.add(1);
        Cd.add(2);
        Cd2.add(2);
        Cd2.add(1);
        while (j < S.size()) {
            if (S.get(j) > S.get(i))   //12模式
            {
                Z.add(j + 1);
            } else if (S.get(j) < S.get(i))                //21模式
            {
                Z2.add(j + 1);
            }
            i++;
            j++;
        }
        judge_fre(Z.size(), Cd, Z);
        Cd.clear();
        judge_fre(Z2.size(), Cd2, Z2);
        Cd2.clear();

    }

    public static int generate_fre() {
        int slen = 0;

        List<Integer> Q = new ArrayList<>();
        List<Integer> R = new ArrayList<>();
        List<List<Integer>> pos = new ArrayList<>();
        List<List<Integer>> fre = new ArrayList<>();
        List<LNode> Lb = new ArrayList<>();

        int[] q = new int[256];
        int[] r = new int[256];

        int j = 0;
        int fre_number = 0;
        int t = 0;
        int k = 0;

        slen = L.get(0).size();//模式长度

        for (List<Integer> Ltemp : L) {
            List<Integer> fretemp = new ArrayList<>();
            for (Integer integer : Ltemp) {
                fretemp.add(integer);
            }
            fre.add(fretemp);
        }

//		fre = L;
        L.clear();

        fre_number = fre_num;
        fre_num = 0;

        for (List<Integer> Ptemp : P) {
            List<Integer> postemp = new ArrayList<>();
            for (Integer integer : Ptemp) {
                postemp.add(integer);
            }
            pos.add(postemp);
        }

//		pos = P;
        P.clear();

        while (Lb.size() < fre_number) {
            Lb.add(new LNode());
        }

        while (Cd.size() < slen + 1) {
            Cd.add(0);
        }

        while (Cd2.size() < slen + 1) {
            Cd2.add(0);
        }

        //建立链表
        for (int s = 0; s < fre_number; s++) {
            LNode pb;
            LNode qb = new LNode();
            LNode temp = new LNode();
            temp.data = pos.get(s).size();
            Lb.set(s, temp);
            qb = Lb.get(s);
            for (int d = 0; d < pos.get(s).size(); d++) {
                pb = new LNode();
                pb.data = pos.get(s).get(d);
                qb.next = pb;
                qb = pb;
            }
            qb.next = null;
        }

        for (int i = 0; i < fre_number; i++) {

            // 求后缀
            Q = fre.get(i).subList(1, fre.get(i).size());
            q = sort(Q);

            // 创建链表
            LNode L = new LNode();
            LNode p = new LNode();
            LNode s = new LNode();
            int size = pos.get(i).size();
            L.data = size;
            s = L;
            for (k = 0; k < size; k++) {
                p = new LNode();
                p.data = pos.get(i).get(k);
                s.next = p;
                s = p;
            }
            s.next = null;

            for (j = 0; j < fre_number; j++) {
                //有剪枝
                if (L.data >= minsup && Lb.get(j).data >= minsup) {

                    // 求前缀
                    R = fre.get(j).subList(0, fre.get(j).size() - 1);
                    r = sort(R);
                    //前后缀相对顺序相同
                    if (Arrays.equals(q, r)) {

                        //最前最后位置相等，拼接成两个模式
                        if (fre.get(i).get(0) == fre.get(j).get(slen - 1)) {
                            Cd.set(0, fre.get(i).get(0));
                            Cd2.set(0, fre.get(i).get(0) + 1);
                            Cd.set(slen, fre.get(i).get(0) + 1);
                            Cd2.set(slen, fre.get(i).get(0));
                            for (t = 1; t < slen; t++) {
                                if (fre.get(i).get(t) > fre.get(j).get(slen - 1)) {
                                    //中间位置增长
                                    Cd.set(t, fre.get(i).get(t) + 1);
                                    Cd2.set(t, fre.get(i).get(t) + 1);
                                } else {
                                    Cd.set(t, fre.get(i).get(t));
                                    Cd2.set(t, fre.get(i).get(t));
                                }
                            }
//                            Pre.add(fre.get(i));
//                            Suf.add(fre.get(j));
                            cd_num = cd_num + 2;
                            grow_BaseP2(Cd.size() - 1, Lb.get(j), L);

                        } else if (fre.get(i).get(0) < fre.get(j).get(slen - 1)) {
                            Cd.set(0, fre.get(i).get(0));//小的不变
                            Cd.set(slen, fre.get(j).get(slen - 1) + 1);//大的加一
                            for (t = 1; t < slen; t++) {
                                if (fre.get(i).get(t) > fre.get(j).get(slen - 1)) {
                                    //中间位置增长
                                    //小的一行的中间位置和大的一行的最后一个数比较，大于+1，小于等于不变
                                    Cd.set(t, fre.get(i).get(t) + 1);

                                } else {
                                    Cd.set(t, fre.get(i).get(t));

                                }
                            }
//                            Pre.add(fre.get(i));
//                            Suf.add(fre.get(j));
                            cd_num = cd_num + 1;
                            grow_BaseP1(Lb.get(j), L);
                        } else {
                            Cd.set(0, fre.get(i).get(0) + 1); // 大的加一
                            Cd.set(slen, fre.get(j).get(slen - 1)); // 小的不变
                            for (t = 0; t < slen - 1; t++) {
                                if (fre.get(j).get(t) > fre.get(i).get(0)) {
                                    // 中间位置增长
                                    Cd.set(t + 1, fre.get(j).get(t) + 1);
                                } else {
                                    Cd.set(t + 1, fre.get(j).get(t));
                                }
                            }
//                            Pre.add(fre.get(i));
//                            Suf.add(fre.get(j));
                            cd_num = cd_num + 1;
                            grow_BaseP1(Lb.get(j), L);
                        }
                    }
                }
            }

        }
//    	Lb.clear();
//    	pos.clear();
//    	fre.clear();
        return 0;

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

    static int[] sort(List<Integer> src) {
        int k, slen = 0, y = 0;
        int level = 1;

        slen = src.size();
        int[] sort_array = new int[slen];
        for (int i = 0; i < slen; i++) {
            k = src.get(i);
            for (int x = 0; x < slen; x++) {
                if (k > src.get(x)) {
                    level++;
                }
            }
            sort_array[i] = level;
            level = 1;
        }
        return sort_array;
    }

    public static void judge_fre(int sup_num, List<Integer> Cd, List<Integer> Z) {
        // TODO Auto-generated method stub
        if (sup_num >= minsup) {

            List<Integer> Ztemp = new ArrayList<>();
            for (Integer integer : Z) {
                Ztemp.add(integer);
            }
            P.add(Ztemp);

            List<Integer> Cdtemp = new ArrayList<>();
            for (Integer integer : Cd) {
                Cdtemp.add(integer);
            }
            L.add(Cdtemp);

        /*    System.out.print("频繁模式：");
            for (Integer Cdint : Cd) {
                System.out.print(Cdint + "  ");
            }
            System.out.print("  支持度为：" + sup_num);
			System.out.println();
            System.out.print("在字符串中出现的位置：");
            for (Integer Zint : Z) {
                System.out.print(Zint + "  ");
            }
            System.out.println(Z.size());
            System.out.println();*/


            if (Cd.size() > pattern.length) {

                int i = 0;
                double[] Cdarr = new double[Cd.size()];
                for (double item : Cd) {
                    Cdarr[i++] = item;
                }
                int j = 0;
                Integer[] Zarr = new Integer[Z.size()];
                for (Integer item : Z) {
                    Zarr[j++] = item;
                }

                Candidate candidateTo = new Candidate(Cdarr, Zarr);
                candidateList.add(candidateTo);
            }
            frequent_num++;
            fre_num++;
        }
    }

    static void grow_BaseP1(LNode Ld, LNode L) {

        LNode p = L;
        LNode q = Ld;
        Z.clear();

        while (p.next != null && q.next != null) {

            if (q.next.data == p.next.data + 1) {
                //有筛选
                Z.add(q.next.data);
                p.next = p.next.next;
                q.next = q.next.next;
            } else if (p.next.data < q.next.data) {
                p = p.next;
            } else {
                q = q.next;
            }
            element_num+=1;
        }

        L.data = L.data - Z.size();
        Ld.data = Ld.data - Z.size();
        judge_fre(Z.size(), Cd, Z);


    }

    static void grow_BaseP2(int slen, LNode Ld, LNode L) {
        int lst, fri;
        LNode p = L;
        LNode q = Ld;
        Z.clear();
        Z2.clear();
        while (p.next != null && q.next != null) {
            if (q.next.data == p.next.data + 1) {
                read_num = read_num + 1; // 比较次数
                lst = q.next.data;
                fri = lst - slen;
                //有筛选
                if (S.get(lst - 1) > S.get(fri - 1)) {
                    Z.add(q.next.data);
                } else if (S.get(lst - 1) < S.get(fri - 1)) {
                    Z2.add(q.next.data);
                }
                p.next = p.next.next;
                q.next = q.next.next;

            } else if (p.next.data < q.next.data) {
                p = p.next;
            } else {
                q = q.next;
            }
            element_num+=1;
        }

        L.data = L.data - Z.size() - Z2.size();
        Ld.data = Ld.data - Z.size() - Z2.size();
        judge_fre(Z.size(), Cd, Z);
        judge_fre(Z2.size(), Cd2, Z2);

    }

    private static double[] getPatternExtreme(double[] p) {
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
        double[] arr = new double[list.size()];
        for (double item : list) {
            arr[i++] = item;
        }
        return arr;
    }

    private static void getExtremePoint() {
        S.add(Seq.get(0));
        map.put(0, 0);
        int k = 1;
        for (int i = 1; i < Seq.size() - 1; i++) {

            if ((Seq.get(i) >= Seq.get(i - 1) && Seq.get(i) > Seq.get(i + 1)) || (Seq.get(i) > Seq.get(i - 1) && Seq.get(i) >= Seq.get(i + 1))) {
                S.add(Seq.get(i));
                map.put(k++, i);
            } else if ((Seq.get(i) <= Seq.get(i - 1) && Seq.get(i) < Seq.get(i + 1)) || (Seq.get(i) < Seq.get(i - 1) && Seq.get(i) <= Seq.get(i + 1))) {
                S.add(Seq.get(i));
                map.put(k++, i);
            } else {
                map.put(-1, i);
            }
        }
        S.add(Seq.get(Seq.size() - 1));
        map.put(k, Seq.size() - 1);
    }

    static class Approximate {
        private double similarity;
        private double[] proximity;

        public Approximate(double similarity, double[] proximity) {
            this.similarity = similarity;
            this.proximity = proximity;
        }

        public double getSimilarity() {
            return similarity;
        }

        public void setSimilarity(double similarity) {
            this.similarity = similarity;
        }

        public double[] getProximity() {
            return proximity;
        }

        public void setProximity(double[] proximity) {
            this.proximity = proximity;
        }
    }

    static class LNode {
        int data;
        LNode next = null;

    }

    static class CoOccurrence {
        private double[] model;
        private List<double[]> appearList;
        private List<double[]> subModes;
        private boolean flag;

        public CoOccurrence(double[] model, List<double[]> appearList, List<double[]> subModes) {
            this.model = model;
            this.appearList = appearList;
            this.subModes = subModes;
        }

        public double[] getModel() {
            return model;
        }

        public void setModel(double[] model) {
            this.model = model;
        }

        public List<double[]> getAppearList() {
            return appearList;
        }

        public void setAppearList(List<double[]> appearList) {
            this.appearList = appearList;
        }

        public List<double[]> getSubModes() {
            return subModes;
        }

        public void setSubModes(List<double[]> subModes) {
            this.subModes = subModes;
        }

        public boolean isFlag() {
            return flag;
        }

        public void setFlag(boolean flag) {
            this.flag = flag;
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
}




