package OPF;


import newalgorithm.MemoryLogger;

import java.io.*;
import java.util.*;

public class OPP_Miner {
    public static double minsup;
    static List<Double> S = new ArrayList<>(); // sequence
    public static int len;//DB长
    public static int fre_num = 0;//频繁模式数量
    public static int fre_number = 0;//每轮融合后新生成的频繁模式的数量
    private static int candNum = 2;//候选模式
    public static int element_num = 0;//元素总比较次数
    public static int contrast_num = 0;//模式融合时前缀后缀对比次数
    static List<List<Integer>> Candmap = new ArrayList<>();
    static List<List<Integer>> F = new ArrayList<>();
    static Map<String, Integer> allfrepattern = new LinkedHashMap<>();//所有频繁模式+支持度
    public static void main(String[] args) throws Exception {
        long startTime = System.currentTimeMillis();
        //对400只股票进行挖掘
        minsup = 50.0;
        String[] ts_code = {"1", "2", "4", "5", "6", "7", "8", "9", "10", "11", "12", "14", "16", "17", "19", "20", "21", "23", "25", "26", "27", "28", "29", "30", "31", "32", "34", "35", "36", "37", "39", "40", "42", "45", "46", "48", "49", "50", "55", "56", "58", "59", "60", "61", "62", "63", "65", "66", "68", "69", "70", "78", "88", "89", "90", "96", "99", "100", "150", "151", "153", "155", "156", "157", "158", "159", "301", "338", "400", "401", "402", "404", "407", "408", "409", "410", "411", "413", "415", "416", "417", "419", "420", "421", "422", "423", "425", "426", "428", "429", "430", "488", "498", "501", "503", "504", "505", "506", "507", "509", "510", "513", "514", "516", "517", "518", "519", "520", "521", "523", "524", "525", "526", "528", "529", "530", "531", "532", "533", "534", "536", "537", "538", "539", "540", "541", "543", "544", "545", "546", "547", "548", "550", "551", "552", "553", "554", "555", "558", "559", "560", "561", "563", "564", "565", "566", "567", "568", "570", "571", "572", "573", "576", "581", "582", "584", "586", "589", "590", "591", "592", "593", "595", "596", "597", "598", "599", "600", "601", "603", "605", "606", "607", "608", "609", "610", "612", "615", "616", "617", "619", "620", "622", "623", "625", "626", "627", "628", "629", "630", "631", "632", "633", "635", "636", "637", "638", "639", "650", "651", "652", "655", "656", "657", "659", "661", "663", "665", "666", "667", "668", "669", "671","676", "677", "678", "679", "680", "681", "682", "683", "685", "686", "688", "692", "695", "697", "698", "700", "701", "702", "703", "705", "707", "708", "709", "710", "711", "712", "713", "715", "716", "717", "718", "719", "720", "721", "722", "723", "725", "726", "727", "728", "729", "731", "732", "733", "735", "736", "737", "738", "739", "750", "751", "752", "753", "755", "756", "757", "758", "759", "761", "762", "766", "767", "768", "776", "777", "778", "779", "782", "783", "785", "786", "788", "789", "790", "791", "792", "793", "795", "796", "797", "798", "799", "800", "801", "802", "803", "806", "807", "809", "810", "811", "812", "813", "815", "816", "818", "819", "820", "821", "822", "823", "825", "826", "828", "829", "830", "831", "833", "836", "837", "838", "839", "848", "850", "851", "852", "856", "858", "859", "860", "861", "862", "863", "868", "869", "875", "876", "877", "878", "880", "881", "882", "883", "885", "886", "887", "888", "889", "890", "892", "893", "895", "897", "898", "899", "900", "901", "902", "903", "905", "906", "908", "909", "910", "911", "912", "913", "915", "917", "918", "919", "920", "921", "922", "923", "925", "926", "927", "928", "929", "930", "931", "932", "933", "935", "936", "937", "938", "948", "949","950", "951", "952","953","955","957","958"};
        List<File> files = getFiles("D:\\IDEA\\IdeaProjects\\code\\实验数据\\A-shares");
        int i = 0;
        for (File f : files) {
            allfrepattern=new LinkedHashMap<>();
            readFile1(String.valueOf(f));
            write("D:\\IDEA\\IdeaProjects\\code\\实验数据\\OPP挖掘结果（2180）\\" + "fre" + ts_code[i] + ".csv",allfrepattern);
           printCostTime(startTime);
           //System.out.println("UB长=" + S.size());
            i++;
        }
       //System.out.println(i);


        //readFile();
      //printCostTime(startTime);

    }
    private static void readFile1(String filepath) throws IOException {
        BufferedReader br = new BufferedReader(new FileReader(filepath));
        String s;
        S = new ArrayList<>();
          fre_num=0;
          contrast_num=0;
        //使用readLine方法，一次读一行
        while ((s = br.readLine()) != null) {
            s = s.trim();
            String[] str = s.split(" ");
            str = s.split(",");
            for (String s1 : str) {
                if (!" ".equals(s1) && !s1.isEmpty()) {
                    S.add(Double.parseDouble(s1));//DB
                }
            }
            List<Double> t = new ArrayList<>();
            t.addAll(S.subList(0, 2180)) ;
            S.clear();
            S.addAll(t);
            len = S.size();//DB长度
            int[] inBinaryArr = getBinary(S);
            find(inBinaryArr);
            getPatternMatching(inBinaryArr);
        }
    }
    public static void write(String filepath1, Map<String, Integer> map) {
        try {
            BufferedWriter writer1 = new BufferedWriter(new FileWriter(filepath1));
            String pattern = "";
            List<Integer> location = new ArrayList<>();
            Iterator<Map.Entry<String, Integer>> it = map.entrySet().iterator();
            while (it.hasNext()) {
                Map.Entry<String, Integer> entry = it.next();
                pattern = entry.getKey().toString();
                pattern = pattern.replace(",", ".");
                //  System.out.println(pattern);
                double occur = entry.getValue();
                writer1.write(pattern);
                writer1.write(",");
                writer1.write((String.valueOf(occur)));
                //   System.out.println(occur);
                writer1.newLine();
            }
            writer1.close();

        } catch (FileNotFoundException ex) {
            System.out.println("没找到文件！");
        } catch (IOException ex) {
            System.out.println("读写文件出错！");
        }
    }

    public static List<File> getFiles(String path) {
        File root = new File(path);
        List<File> files = new ArrayList<File>();
        if (!root.isDirectory()) {
            files.add(root);
        } else {
            File[] subFiles = root.listFiles();
            for (File f : subFiles) {
                files.addAll(getFiles(f.getAbsolutePath()));
            }
        }
        return files;
    }

    private static void printCostTime(long startTime) {
        System.out.println(System.currentTimeMillis() - startTime);
        System.out.println(candNum);
        System.out.println(fre_num);
        System.out.println(element_num);
        System.out.println(contrast_num);//模式融合前缀后缀比较次数
        MemoryLogger.getInstance().checkMemory();
        double maxMemory = MemoryLogger.getInstance().getMaxMemory();
        System.out.println(maxMemory);
    }

    private static void readFile() throws IOException {
        minsup = 4.0;

        File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\亚马逊.txt");// 5842  db1
        // File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\股票Russell2000（1987.9.10~2019.12.27）.txt");//  8141  db2
        //  File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\Nasdaq.txt");//1 2279  db3
        // File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\S&P500.txt");// 2 3046  db4
        // File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\NYSE.txt");//6W  db5
        //File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\cl.us.txt");//  1 0305  db6
        //  File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\hpq.us.txt");//1 2075  db7
        //  File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\ge.us.txt");// 1 4058  db8


        BufferedReader br = new BufferedReader(new FileReader(file));
        String s;
        //  S = new ArrayList<>();
        //  fre_num=0;
        //  contrast_num=0;
        //使用readLine方法，一次读一行
        while ((s = br.readLine()) != null) {
            s = s.trim();
            String[] str = s.split(" ");
            for (String s1 : str) {
                if (!" ".equals(s1) && !s1.isEmpty()) {
                    S.add(Double.parseDouble(s1));//DB
                }
            }
            len = S.size();//DB长度
            int[] inBinaryArr = getBinary(S);
            find(inBinaryArr);
            getPatternMatching(inBinaryArr);
        }
    }

    private static void find(int[] inBinaryArr) {
        candNum = 2;
        Integer[][] C2 = {{1, 2}, {2, 1}};
        for (int i = 0; i < 2; i++) {
            int[] pBinaryArr = getBinaryp(C2[i]);
            Integer[] subsetNumArr = bndm(inBinaryArr, pBinaryArr);
            Integer[] subsetNumArrNew = verificationStrategy(S, C2[i], subsetNumArr, C2[i].length);
            judge_fre(C2[i], subsetNumArrNew);
        }
    }

    private static void getPatternMatching(int[] inBinaryArr) {
        while (fre_number > 0) {
            fre_num += fre_number;
            fre_number = 0;
            List<List<Integer>> f = new ArrayList<>();
            f.addAll(F);
            F.clear();
            for (int a = 0; a < f.size(); a++) {
                List<Integer> P = f.get(a);
                Integer[] p = P.toArray(new Integer[0]);
                for (int b = 0; b < f.size(); b++) {
                    List<Integer> Q = f.get(b);
                    Integer[] q = Q.toArray(new Integer[0]);
                    //先求出suffixorder(p)与prefixorder(q)
                    Integer[] suffixp = new Integer[p.length - 1];
                    Integer[] prefixq = new Integer[q.length - 1];
                    int m = q.length;
                    //得出suffix(p)与prefix(q)
                    System.arraycopy(p, 1, suffixp, 0, p.length - 1);
                    System.arraycopy(q, 0, prefixq, 0, q.length - 1);
                    Integer[] suffixorder = new Integer[p.length - 1];
                    Integer[] prefixorder = new Integer[q.length - 1];
                    if (suffixp.length == 1) {
                        suffixorder[0] = 1;
                        prefixorder[0] = 1;
                    } else {
                        suffixorder = getOrder(suffixp);
                        prefixorder = getOrder(prefixq);
                    }
                    contrast_num++;
                    if (Arrays.equals(suffixorder, prefixorder)) {//后缀=前缀，可以融合
                        if (!Arrays.equals(suffixp, prefixq)) {//前缀的第一个不等于后缀的最后一个数字，生成1个超模式
                            Integer[] t = new Integer[p.length + 1];
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
                          //  Candmap.add(List.of(t));
                            candNum += 1;//候选模式++
                            matching(t, inBinaryArr);
                        }
                        if (Arrays.equals(suffixp, prefixq)) {//生成2个超模式
                            Integer[] t = new Integer[p.length + 1];
                            Integer[] k = new Integer[p.length + 1];
                            t[0] = p[0] + 1;
                            t[m] = p[0];
                            for (int i = 1; i < t.length - 1; i++) {
                                if (p[i] > p[0]) {
                                    t[i] = p[i] + 1;
                                } else {
                                    t[i] = p[i];
                                }
                            }
                        //    Candmap.add(List.of(t));
                            matching(t, inBinaryArr);
                            k[0] = p[0];
                            k[m] = p[0] + 1;
                            for (int i = 1; i < k.length - 1; i++) {
                                if (p[i] > p[0]) {
                                    k[i] = p[i] + 1;
                                } else {
                                    k[i] = p[i];
                                }
                            }
                         //   Candmap.add(List.of(k));
                            candNum += 2;//候选模式++
                            matching(k, inBinaryArr);
                        }
                    }
                }
            }
        }
    }

    public static void matching(Integer[] Cd, int[] inBinaryArr) {
        int[] pBinaryArr = getBinaryp(Cd);
        int[] sortedP = new int[pBinaryArr.length];
        System.arraycopy(pBinaryArr, 0, sortedP, 0, sortedP.length);
        Arrays.sort(sortedP);
        int[] aux = new int[pBinaryArr.length];
        genAux(aux, sortedP, pBinaryArr);
        Integer[] subsetNumArr = sbndm(inBinaryArr, pBinaryArr, aux, S);
        Integer[] subsetNumArrNew = verificationStrategy(S, Cd, subsetNumArr, Cd.length);
        judge_fre(Cd, subsetNumArrNew);
    }

    public static void judge_fre(Integer[] Cd, Integer[] Z) {   //判断是否频繁
        if (Z.length >= minsup) {
            fre_number++;
            F.add(List.of(Cd));
            allfrepattern.put(Arrays.toString(Cd), Z.length);
        }
    }


    private static Integer[] sbndm(int[] txt, int[] pat, int[] aux, List<Double> s) {
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
                        if (s.get(cand - 1 + aux[k]) >= s.get(cand - 1 + aux[k + 1])) {
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

    private static Integer[] verificationStrategy(List<Double> in, Integer[] candidateArr, Integer[] subsetNumArr, int plength) {
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
                if (in.get(value - 1 + indexArr[i]) >= in.get(value - 1 + indexArr[i + 1])) {
                    flag = true;
                    break;
                }
            }
            if (!flag) {
                subsetListNew.add(value + plength);
            }
        }
        Integer[] subsetNumArrNew = new Integer[subsetListNew.size()];
        subsetListNew.toArray(subsetNumArrNew);
        return subsetNumArrNew;
    }


    private static int[] getBinary(List<Double> arr) {
        int[] binary = new int[arr.size() - 1];
        for (int i = 0; i < arr.size() - 1; i++) {
            if (arr.get(i) > arr.get(i + 1)) {
                binary[i] = 0;
            } else if (arr.get(i) < arr.get(i + 1)) {
                binary[i] = 1;
            }
        }
        return binary;
    }

    private static int[] getBinaryp(Integer[] arr) {
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

    private static Integer[] getOrder(Integer[] seq) {
        Integer[] arr = new Integer[seq.length];
        System.arraycopy(seq, 0, arr, 0, seq.length);
        Integer[] order = new Integer[arr.length];
        Integer[] temp = new Integer[arr.length];
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
}
