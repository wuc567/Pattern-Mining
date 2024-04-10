package OPF;

import newalgorithm.MemoryLogger;

import java.io.*;
import java.util.*;

public class OPF_Miner {
    public static double minsup;
    private static Map<String, List<List<Double>>> Fmap = new LinkedHashMap<>();
    public static double k;  //遗忘因子
    public static double e = Math.E;//自然常数e的近似值
    static List<Double> S = new ArrayList<>(); // sequence
    public static int len;//DB长
    public static int fre_num = 0;//频繁模式数量
    public static int fre_number = 0;//每轮融合后新生成的频繁模式的数量
    private static int candNum = 2;//候选模式
    public static int element_num = 0;//元素总比较次数
    public static int contrast_num = 0;//模式融合时前缀后缀对比次数
    // static List<List<Integer>> Candmap = new ArrayList<>();
    static List<Double> forget_mech = new ArrayList<>();//遗忘机制
    static Map<String, Double> allfrepattern = new LinkedHashMap<>();//所有频繁模式+支持度

    public static void main(String[] args) throws IOException {
        //算法性能验证实验：
        long startTime = System.nanoTime();
        readFile();
        long endTime = System.nanoTime();
        long duration = endTime - startTime;
        double seconds = (double)duration / 1_000_000_000.0;
        printCostTime(seconds);
        System.out.println("DB长=" + S.size());

      /*  //对400只股票进行挖掘:
        minsup = 50.0;
        long startTime = System.nanoTime();
        String[] ts_code = {"1", "2", "4", "5", "6", "7", "8", "9", "10", "11", "12", "14", "16", "17", "19", "20", "21", "23", "25", "26", "27", "28", "29", "30", "31", "32", "34", "35", "36", "37", "39", "40", "42", "45", "46", "48", "49", "50", "55", "56", "58", "59", "60", "61", "62", "63", "65", "66", "68", "69", "70", "78", "88", "89", "90", "96", "99", "100", "150", "151", "153", "155", "156", "157", "158", "159", "301", "338", "400", "401", "402", "404", "407", "408", "409", "410", "411", "413", "415", "416", "417", "419", "420", "421", "422", "423", "425", "426", "428", "429", "430", "488", "498", "501", "503", "504", "505", "506", "507", "509", "510", "513", "514", "516", "517", "518", "519", "520", "521", "523", "524", "525", "526", "528", "529", "530", "531", "532", "533", "534", "536", "537", "538", "539", "540", "541", "543", "544", "545", "546", "547", "548", "550", "551", "552", "553", "554", "555", "558", "559", "560", "561", "563", "564", "565", "566", "567", "568", "570", "571", "572", "573", "576", "581", "582", "584", "586", "589", "590", "591", "592", "593", "595", "596", "597", "598", "599", "600", "601", "603", "605", "606", "607", "608", "609", "610", "612", "615", "616", "617", "619", "620", "622", "623", "625", "626", "627", "628", "629", "630", "631", "632", "633", "635", "636", "637", "638", "639", "650", "651", "652", "655", "656", "657", "659", "661", "663", "665", "666", "667", "668", "669", "671","676", "677", "678", "679", "680", "681", "682", "683", "685", "686", "688", "692", "695", "697", "698", "700", "701", "702", "703", "705", "707", "708", "709", "710", "711", "712", "713", "715", "716", "717", "718", "719", "720", "721", "722", "723", "725", "726", "727", "728", "729", "731", "732", "733", "735", "736", "737", "738", "739", "750", "751", "752", "753", "755", "756", "757", "758", "759", "761", "762", "766", "767", "768", "776", "777", "778", "779", "782", "783", "785", "786", "788", "789", "790", "791", "792", "793", "795", "796", "797", "798", "799", "800", "801", "802", "803", "806", "807", "809", "810", "811", "812", "813", "815", "816", "818", "819", "820", "821", "822", "823", "825", "826", "828", "829", "830", "831", "833", "836", "837", "838", "839", "848", "850", "851", "852", "856", "858", "859", "860", "861", "862", "863", "868", "869", "875", "876", "877", "878", "880", "881", "882", "883", "885", "886", "887", "888", "889", "890", "892", "893", "895", "897", "898", "899", "900", "901", "902", "903", "905", "906", "908", "909", "910", "911", "912", "913", "915", "917", "918", "919", "920", "921", "922", "923", "925", "926", "927", "928", "929", "930", "931", "932", "933", "935", "936", "937", "938", "948", "949","950", "951", "952","953","955","957","958"};
        List<File> files = getFiles("D:\\IDEA\\IdeaProjects\\code\\实验数据\\A-shares");
        int i = 0;
        for (File f : files) {
            allfrepattern=new LinkedHashMap<>();
            readFile1(String.valueOf(f));
         //   System.out.println(f.getName());
            write("D:\\IDEA\\IdeaProjects\\code\\实验数据\\OPF挖掘结果（2180）\\" + "fre" + ts_code[i] + ".csv", allfrepattern);
       long endTime = System.nanoTime();
       long duration = endTime - startTime;
       double seconds = (double)duration / 1_000_000_000.0;
        printCostTime(seconds);
           // System.out.println("UB长=" + S.size());
          //  System.out.println(ts_code[i]);
            i++;
        }
        System.out.println(i);*/


    }

    private static void printCostTime(double seconds) {
        System.out.println(seconds);//运行时间
        System.out.println(candNum);//候选模式数量
        System.out.println(fre_num);//频繁模式数量
        System.out.println(element_num);//支持度计算元素比较次数
        System.out.println(contrast_num);//模式融合前缀后缀比较次数
        MemoryLogger.getInstance().checkMemory();
        double maxMemory = MemoryLogger.getInstance().getMaxMemory();
        System.out.println(maxMemory);
        //  System.out.println(Candmap);
    }


    private static void readFile() throws IOException {
        minsup=4.0;
        //minsup=6.0;
        //  minsup=8.0;
        //  minsup = 10.0;
        //  minsup=12.0;


         File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\亚马逊.txt");// 5842  db1
        //File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\股票Russell2000（1987.9.10~2019.12.27）.txt");//  8141  db2
        //   File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\Nasdaq.txt");//1 2279  db3
        // File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\S&P500.txt");// 2 3046  db4
        //File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\NYSE.txt");//6W  db5
        //File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\cl.us.txt");//  1 0305  db6
        //  File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\hpq.us.txt");//1 2075  db7
        //  File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\ge.us.txt");// 1 4058  db8

        BufferedReader br = new BufferedReader(new FileReader(file));
        String s;
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
            k =1.0/len;
            forgetting_mechanism();
            find();//找2长度频繁模式
            calculate();   //模式融合、计算支持度、判断是否频繁、若频繁继续模式融合
        }
    }

    public static void forgetting_mechanism() {
        forget_mech.add(0.0);
        for (int i = 1; i <= len; i++) {
            double f = Math.pow(e, -k * (len - i));
            forget_mech.add(f);
        }
    }

    public static void find() {  //2长度模式
        candNum = 2;
        List<Double> Z = new ArrayList<>();
        List<Double> Z2 = new ArrayList<>();
        int i = 0, j = 1;
        Integer[] Cd = new Integer[2];
        Integer[] Cd2 = new Integer[2];
        Cd[0] = 1;
        Cd[1] = 2;
        Cd2[0] = 2;
        Cd2[1] = 1;
        double f1 = 0.0;
        double f2 = 0.0;
        while (j < len) {
            if (S.get(j) > S.get(i))   //12模式
            {
                Z.add(Double.valueOf(j + 1));
                f1 += forget_mech.get(j + 1);
            } else if (S.get(j) < S.get(i))    //21模式
            {
                Z2.add(Double.valueOf(j + 1));
                f2 += forget_mech.get(j + 1);
            }
            i++;
            j++;
        }
        judge_fre(Cd, Z, f1, 1);
        judge_fre(Cd2, Z2, f2, 3);
    }

    public static void judge_fre(Integer[] Cd, List<Double> Z, double sup_num, int group) {   //判断是否频繁
        if (sup_num >= minsup) {
            List<List<Double>> content = new ArrayList<>();
            fre_number++;
            content.add(Z);
            content.add(List.of(sup_num));
            content.add(List.of((double) group));
            Fmap.put(Arrays.toString(Cd), content);
           allfrepattern.put(Arrays.toString(Cd),sup_num);
              //  System.out.println(Arrays.toString(Cd)+ "→" + Z + "→" + sup_num+ "→" +group);
        }
    }

    private static void calculate() {
        if (fre_number > 0) {
            fre_num += fre_number;
            fre_number = 0;
            //1.降序排序
            Comparator<Map.Entry<String, List<List<Double>>>> comparator = (entry1, entry2) -> {
                double value1 = entry1.getValue().get(1).get(0);
                double value2 = entry2.getValue().get(1).get(0);
                return Double.compare(value2, value1);
            };
            List<Map.Entry<String, List<List<Double>>>> sortedData = new ArrayList<>(Fmap.entrySet());
            Collections.sort(sortedData, comparator);

            boolean flag = Fmap.get("[1, 2]").get(1).get(0) > Fmap.get("[2, 1]").get(1).get(0);

            Fmap = new LinkedHashMap<>();
            List<OPF_Miner.LNode> Lb1 = new ArrayList<>();
            List<Double> suffset = new ArrayList<>();
            for (Map.Entry<String, List<List<Double>>> entry1 : sortedData) {
                List<Double> Location = entry1.getValue().get(0);
                Lb1.add(getLNode(Location));
                suffset.add(entry1.getValue().get(1).get(0));
            }
            //2.融合
            if (flag) {
                for (Map.Entry<String, List<List<Double>>> entry1 : sortedData) {
                    Integer[] P = stringToArray(entry1.getKey()); //P
                    OPF_Miner.LNode PNode = getLNode(entry1.getValue().get(0));//p位置
                    int group = entry1.getValue().get(2).get(0).intValue();
                    int i = 0;
                    for (Map.Entry<String, List<List<Double>>> entry2 : sortedData) {
                        if (PNode.data >= minsup && suffset.get(i) >= minsup) {
                            OPF_Miner.LNode QNode = Lb1.get(i);
                            Integer[] Q = stringToArray(entry2.getKey());   //Q
                            patternFusion(P, PNode, Q, QNode, group, suffset, i);//模式融合
                        }
                        group = group + 1;
                        i++;
                    }
                }
            } else {
                for (Map.Entry<String, List<List<Double>>> entry1 : sortedData) {
                    Integer[] P = stringToArray(entry1.getKey()); //P
                    List<List<Double>> value1 = entry1.getValue();
                    List<Double> PLocation = value1.get(0);
                    OPF_Miner.LNode PNode = getLNode(PLocation);//p位置
                    int group = value1.get(2).get(0).intValue() + 1;
                    int i = 0;
                    for (Map.Entry<String, List<List<Double>>> entry2 : sortedData) {
                        if (PNode.data >= minsup && suffset.get(i) >= minsup) {//剪枝
                            OPF_Miner.LNode QNode = Lb1.get(i);
                            Integer[] Q = stringToArray(entry2.getKey());   //Q
                            patternFusion(P, PNode, Q, QNode, group, suffset, i);//模式融合
                        }
                        group = group - 1;
                        i++;
                    }
                }
            }
        }
        while (fre_number > 0) {
            fre_num += fre_number;
            fre_number = 0;
            //1.排序
            Comparator<Map.Entry<String, List<List<Double>>>> comparator = (entry1, entry2) -> {
                double value1 = entry1.getValue().get(1).get(0);
                double value2 = entry2.getValue().get(1).get(0);
                return Double.compare(value2, value1);
            };
            List<Map.Entry<String, List<List<Double>>>> sortedData = new ArrayList<>(Fmap.entrySet());
            Collections.sort(sortedData, comparator);
            //2.分组
            List<Map.Entry<String, List<List<Double>>>> G1 = new LinkedList<>();
            List<Map.Entry<String, List<List<Double>>>> G2 = new LinkedList<>();
            for (Map.Entry<String, List<List<Double>>> entry : sortedData) {
                int groupnum = entry.getValue().get(2).get(0).intValue();
                if ((groupnum == 1) || (groupnum == 2)) {
                    G1.add(entry);
                } else {
                    G2.add(entry);
                }
            }
            Fmap = new LinkedHashMap<>();

            List<OPF_Miner.LNode> Lb1 = new ArrayList<>();
            List<OPF_Miner.LNode> Lb2 = new ArrayList<>();
            List<Double> suffset1 = new ArrayList<>();
            List<Double> suffset2 = new ArrayList<>();
            for (Map.Entry<String, List<List<Double>>> set : G1) {
                List<Double> PLocation = set.getValue().get(0);
                Lb1.add(getLNode(PLocation));
                suffset1.add(set.getValue().get(1).get(0));
            }
            for (Map.Entry<String, List<List<Double>>> set : G2) {
                List<Double> PLocation = set.getValue().get(0);
                Lb2.add(getLNode(PLocation));
                suffset2.add(set.getValue().get(1).get(0));
            }
            //3.融合
            for (Map.Entry<String, List<List<Double>>> entry1 : sortedData) {
                Integer[] P = stringToArray(entry1.getKey()); //P
                Integer[] PSuf = Arrays.copyOfRange(P, 1, P.length);//获取P后缀
                OPF_Miner.LNode PNode = getLNode(entry1.getValue().get(0));
                int group = entry1.getValue().get(2).get(0).intValue();
                int i = 0;
                if ((group == 1) || (group == 3)) {
                    // if (G1 != null)
                    for (Map.Entry<String, List<List<Double>>> entry2 : G1) {  //G1是组1和组2
                        if (PNode.data >= minsup && suffset1.get(i) >= minsup) {
                            Integer[] Q = stringToArray(entry2.getKey());   //Q
                            Integer[] QPre = Arrays.copyOfRange(Q, 0, Q.length - 1);     //获取Q前缀
                            contrast_num++;//前缀后缀比较次数
                            if (Arrays.equals(getOrder(PSuf), getOrder(QPre))) {
                                OPF_Miner.LNode QNode = Lb1.get(i);  //Q位置
                                patternFusion(P, PNode, Q, QNode, group, suffset1, i);//模式融合       组1和组2的结果
                            }
                        }
                        i++;
                    }
                } else {
                    for (Map.Entry<String, List<List<Double>>> entry2 : G2) {
                        if (PNode.data >= minsup && suffset2.get(i) >= minsup) {
                            Integer[] Q = stringToArray(entry2.getKey());   //Q
                            Integer[] QPre = Arrays.copyOfRange(Q, 0, Q.length - 1); //获取Q前缀
                            contrast_num++;//前缀后缀比较次数
                            if (Arrays.equals(getOrder(PSuf), getOrder(QPre))) {
                                OPF_Miner.LNode QNode = Lb2.get(i);  //Q位置
                                patternFusion(P, PNode, Q, QNode, group, suffset2, i);//模式融合
                            }
                        }
                        i++;
                    }
                }
            }
        }
    }

    private static void patternFusion(Integer[] P, OPF_Miner.LNode PNode, Integer[] Q, OPF_Miner.LNode QNode, int group, List<Double> suffset, int index) {
        int slen = P.length;
        if (P[0] == Q[Q.length - 1]) {
            Integer[] Cd = new Integer[P.length + 1];
            Integer[] Cd2 = new Integer[P.length + 1];
            Cd[0] = P[0];
            Cd2[0] = P[0] + 1;
            Cd[slen] = Cd2[0];
            Cd2[slen] = Cd[0];
            for (int t = 1; t < slen; t++) {
                if (P[t] > Q[slen - 1]) {
                    //中间位置增长
                    //小的一行的中间位置和大的一行的最后一个数比较，大于+1，小于等于不变
                    Cd[t] = P[t] + 1;
                    Cd2[t] = P[t] + 1;
                } else {
                    Cd[t] = P[t];//Cd:(1,3,2)
                    Cd2[t] = P[t];//Cd2:(2,1,3)
                }
            }
            //  Candmap.add(List.of(Cd));
            //  Candmap.add(List.of(Cd2));
            //  System.out.println(Arrays.toString(Cd));
            // System.out.println(Arrays.toString(Cd2));
            candNum += 2;//候选模式++
            grow_BaseP2(P.length, QNode, PNode, Cd, Cd2, group, suffset, index);
        } else if (P[0] < Q[Q.length - 1]) {
            Integer[] Cd = new Integer[P.length + 1];
            Cd[0] = P[0];//小的不变  （1,0,0）
            Cd[slen] = Q[slen - 1] + 1;//大的加一 1,0,3）
            for (int t = 1; t < slen; t++) {
                if (P[t] > Q[slen - 1]) {
                    //中间位置增长
                    //小的一行的中间位置和大的一行的最后一个数比较，大于+1，小于等于不变
                    Cd[t] = P[t] + 1;
                } else {
                    Cd[t] = P[t];
                }
            }
            //  Candmap.add(List.of(Cd));
            // System.out.println(Arrays.toString(Cd));
            candNum++;
            grow_BaseP1(QNode, PNode, Cd, group, suffset, index);
        } else {
            Integer[] Cd = new Integer[P.length + 1];
            Cd[0] = P[0] + 1; // 大的加一
            Cd[slen] = Q[slen - 1]; // 小的不变
            for (int t = 0; t < slen - 1; t++) {
                if (Q[t] > P[0]) {
                    // 中间位置增长
                    Cd[t + 1] = Q[t] + 1;
                } else {
                    Cd[t + 1] = Q[t];
                }
            }
            candNum++;
            //   Candmap.add(List.of(Cd));
            // System.out.println(Arrays.toString(Cd));
            grow_BaseP1(QNode, PNode, Cd, group, suffset, index);
        }
    }

    private static void grow_BaseP2(int slen, OPF_Miner.LNode qNode, OPF_Miner.LNode pNode, Integer[] Cd, Integer[] Cd2, int group, List<Double> suffset, int index) {
        List<Double> Z = new ArrayList<>();
        List<Double> Z2 = new ArrayList<>();
        int lst;
        OPF_Miner.LNode p = pNode;
        OPF_Miner.LNode q = qNode;
        double f1 = 0.0;//减去的就是超模式的支持度
        double f2 = 0.0;//减去的就是超模式的支持度
        while (p.next != null && q.next != null) {
            if (q.next.data == p.next.data + 1) {
                lst = q.next.data.intValue();
                //有筛选
                int fri = lst - slen;
                //有筛选
                if (S.get(lst - 1) > S.get(fri - 1)) {
                    Z.add(q.next.data);
                    f1 += forget_mech.get(q.next.data.intValue());//每找到一次出现就减去一次
                } else if (S.get(lst - 1) < S.get(fri - 1)) {
                    Z2.add(q.next.data);
                    f2 += forget_mech.get(q.next.data.intValue());//每找到一次出现就减去一次
                }
                p.next = p.next.next;
                q.next = q.next.next;
            } else if (p.next.data < q.next.data) {
                p = p.next;
            } else {
                q = q.next;
            }
            element_num++;
        }
        pNode.data = pNode.data - Z.size() - Z2.size();
        suffset.set(index, suffset.get(index) - f1 - f2);//更新后缀支持度
        judge_fre(Cd, Z, f1, group);
        judge_fre(Cd2, Z2, f2, group);
    }

    private static void grow_BaseP1(OPF_Miner.LNode qNode, OPF_Miner.LNode pNode, Integer[] Cd, int group, List<Double> suffset, int index) {
        List<Double> Z = new ArrayList<>();
        OPF_Miner.LNode p = pNode;
        OPF_Miner.LNode q = qNode;
        double f = 0.0;//减去的就是超模式的支持度
        while (p.next != null && q.next != null) {
            if (q.next.data == p.next.data + 1) {
                //有筛选
                Z.add(q.next.data);
                f += forget_mech.get(q.next.data.intValue());//每找到一次出现就减去一次
                p.next = p.next.next;
                q.next = q.next.next;
            } else if (p.next.data < q.next.data) {
                p = p.next;
            } else {
                q = q.next;
            }
            element_num++;//元素总比较次数
        }
        pNode.data = pNode.data - Z.size();
        suffset.set(index, suffset.get(index) - f);//更新后缀支持度
        judge_fre(Cd, Z, f, group);
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
                if (arr[i] < min && arr[i] != (double) Integer.MIN_VALUE) {
                    min = arr[i];
                    index = i;
                }
            }
            arr[index] = Integer.MIN_VALUE;
            Double lst = j + 1D;
            order[index] = lst.intValue();
        }
        return order;
    }

    private static Integer[] stringToArray(String key) {
        key = key.substring(1, key.length() - 1);
        String[] str = key.split(",");
        Integer[] arr = new Integer[str.length];
        for (int i = 0; i < str.length; i++) {
            arr[i] = Integer.valueOf((str[i].trim()));
        }
        return arr;
    }

    private static OPF_Miner.LNode getLNode(List<Double> List) {
        OPF_Miner.LNode PNode = new OPF_Miner.LNode();
        PNode.data = Double.valueOf(List.size());
        OPF_Miner.LNode p = new OPF_Miner.LNode();//p是节点
        OPF_Miner.LNode s = new OPF_Miner.LNode();//s是节点
        s = PNode;
        for (Double val : List) {
            p = new OPF_Miner.LNode();
            p.data = val;
            s.next = p;
            s = p;
        }
        s.next = null;
        return PNode;
    }

    static class LNode {
        Double data;
        OPF_Miner.LNode next = null;
    }
    public static void result(double time) throws IOException {
        String filePath = "OPF_Miner.txt"; // 文件路径
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(filePath, true))) {
            // 在已有文件的末尾续写数据
            writer.write(Double.toString(time));
            writer.newLine(); // 换行
            MemoryLogger.getInstance().checkMemory();
            double maxMemory = MemoryLogger.getInstance().getMaxMemory();
            writer.write(Double.toString(maxMemory));
            writer.newLine(); // 换行
            writer.write(Integer.toString(fre_num));
            writer.newLine(); // 换行
            writer.write(Integer.toString(candNum));
            writer.newLine(); // 换行
            writer.write(Integer.toString(element_num));
            writer.newLine(); // 换行
            writer.write(Integer.toString(contrast_num));
            writer.newLine(); // 换行
            writer.write("-----------------");
            writer.newLine(); // 换行
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    //用于聚类
    private static void readFile1(String filepath) throws IOException {
        BufferedReader br = new BufferedReader(new FileReader(filepath));
        String s;
        S = new ArrayList<>(); // sequence
        fre_num = 0;//频繁模式数量
        fre_number = 0;//每轮融合后新生成的频繁模式的数量
        Fmap = new LinkedHashMap<>();
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
            t.addAll(S.subList(0, 2180));
            S.clear();
            S.addAll(t);
            len = S.size();//DB长度
            //k = Math.log(len) / len;  // 1.  k=-ln((1/len)/1)/len
            k = 1.0 /len;   //  2.  k=1/len
            forgetting_mechanism();
            find();//找2长度频繁模式
            calculate();   //模式融合、计算支持度、判断是否频繁、若频繁继续模式融合
        }
    }
    public static void write(String filepath1, Map<String, Double> map) {
        try {
            BufferedWriter writer1 = new BufferedWriter(new FileWriter(filepath1));
            String pattern = "";
            List<Integer> location = new ArrayList<>();
            Iterator<Map.Entry<String, Double>> it = map.entrySet().iterator();
            while (it.hasNext()) {
                Map.Entry<String, Double> entry = it.next();
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
}
