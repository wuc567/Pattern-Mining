package OPF;


import newalgorithm.MemoryLogger;

import java.io.*;
import java.util.*;

public class EFO_Miner {
    public static double minsup;
    static List<Double> S = new ArrayList<>(); // sequence
    public static int len;//DB长
    private static int candNum = 2;//候选模式
    public static int element_num = 0;//元素总比较次数
    public static int contrast_num = 0;//模式融合前缀后缀对比次数
    static List<List<Integer>> Candmap = new ArrayList<>();
    private static Map<String, List<Double>> Fmap = new LinkedHashMap<>();//所有频繁模式集合
    private static Map<String, List<Double>> mapV1; //放每次生成的频繁模式，里边模式的长度都相同
    private static Map<String, List<Double>> mapV2; //放已出现过的模式
    static Map<String, Integer> allfrepattern = new LinkedHashMap<>();//所有频繁模式+支持度

    public static void main(String[] args) throws IOException {
        long startTime = System.currentTimeMillis();
        //对400只股票进行挖掘
        minsup = 50.0;
        String[] ts_code = {"1", "2", "4", "5", "6", "7", "8", "9", "10", "11", "12", "14", "16", "17", "19", "20", "21", "23", "25", "26", "27", "28", "29", "30", "31", "32", "34", "35", "36", "37", "39", "40", "42", "45", "46", "48", "49", "50", "55", "56", "58", "59", "60", "61", "62", "63", "65", "66", "68", "69", "70", "78", "88", "89", "90", "96", "99", "100", "150", "151", "153", "155", "156", "157", "158", "159", "301", "338", "400", "401", "402", "404", "407", "408", "409", "410", "411", "413", "415", "416", "417", "419", "420", "421", "422", "423", "425", "426", "428", "429", "430", "488", "498", "501", "503", "504", "505", "506", "507", "509", "510", "513", "514", "516", "517", "518", "519", "520", "521", "523", "524", "525", "526", "528", "529", "530", "531", "532", "533", "534", "536", "537", "538", "539", "540", "541", "543", "544", "545", "546", "547", "548", "550", "551", "552", "553", "554", "555", "558", "559", "560", "561", "563", "564", "565", "566", "567", "568", "570", "571", "572", "573", "576", "581", "582", "584", "586", "589", "590", "591", "592", "593", "595", "596", "597", "598", "599", "600", "601", "603", "605", "606", "607", "608", "609", "610", "612", "615", "616", "617", "619", "620", "622", "623", "625", "626", "627", "628", "629", "630", "631", "632", "633", "635", "636", "637", "638", "639", "650", "651", "652", "655", "656", "657", "659", "661", "663", "665", "666", "667", "668", "669", "671","676", "677", "678", "679", "680", "681", "682", "683", "685", "686", "688", "692", "695", "697", "698", "700", "701", "702", "703", "705", "707", "708", "709", "710", "711", "712", "713", "715", "716", "717", "718", "719", "720", "721", "722", "723", "725", "726", "727", "728", "729", "731", "732", "733", "735", "736", "737", "738", "739", "750", "751", "752", "753", "755", "756", "757", "758", "759", "761", "762", "766", "767", "768", "776", "777", "778", "779", "782", "783", "785", "786", "788", "789", "790", "791", "792", "793", "795", "796", "797", "798", "799", "800", "801", "802", "803", "806", "807", "809", "810", "811", "812", "813", "815", "816", "818", "819", "820", "821", "822", "823", "825", "826", "828", "829", "830", "831", "833", "836", "837", "838", "839", "848", "850", "851", "852", "856", "858", "859", "860", "861", "862", "863", "868", "869", "875", "876", "877", "878", "880", "881", "882", "883", "885", "886", "887", "888", "889", "890", "892", "893", "895", "897", "898", "899", "900", "901", "902", "903", "905", "906", "908", "909", "910", "911", "912", "913", "915", "917", "918", "919", "920", "921", "922", "923", "925", "926", "927", "928", "929", "930", "931", "932", "933", "935", "936", "937", "938", "948", "949","950", "951", "952","953","955","957","958"};
        List<File> files = getFiles("D:\\IDEA\\IdeaProjects\\code\\实验数据\\A-shares");
        int i = 0;
        for (File f : files) {
            allfrepattern = new LinkedHashMap<>();
            readFile1(String.valueOf(f));
            write("D:\\IDEA\\IdeaProjects\\code\\实验数据\\EFO挖掘结果（2180）\\" + "fre" + ts_code[i] + ".csv",allfrepattern);
            printCostTime(startTime);
            System.out.println(S.size());
            i++;
        }
        System.out.println(i);

        //  readFile();
        //  printCostTime(startTime);
        //System.out.println("UB长=" + S.size());
    }

    private static void readFile1(String filepath) throws IOException {
        BufferedReader br = new BufferedReader(new FileReader(filepath));
        String s;
        S = new ArrayList<>(); // sequence
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
            t.addAll(S.subList(0, 2180)) ;
            S.clear();
            S.addAll(t);
            len = S.size();//DB长度
            find();//找2长度频繁模式
            calculate();   //模式融合、计算支持度、判断是否频繁、若频繁继续模式融合
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
        System.out.println(Fmap.size());
        System.out.println(element_num);
        System.out.println(contrast_num);//模式融合前缀后缀比较次数
        MemoryLogger.getInstance().checkMemory();
        double maxMemory = MemoryLogger.getInstance().getMaxMemory();
        System.out.println(maxMemory);
    }

    public static void judge_fre(Integer[] Cd, List<Double> Z) {   //判断是否频繁

        if (Z.size() >= minsup) {
            mapV1.put(Arrays.toString(Cd), Z);
            //   System.out.println(Arrays.toString(Cd) + "→" + Z.size());
            allfrepattern.put(Arrays.toString(Cd), Z.size());
        }
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
        // S = new ArrayList<>();
        //   contrast_num=0;
        //   Fmap = new LinkedHashMap<>();
        //使用readLine方法，一次读一行
        while ((s = br.readLine()) != null) {
            s = s.trim();
            String[] str = s.split(" ");
            for (String s1 : str) {
                if (!" ".equals(s1) && !s1.isEmpty()) {
                    S.add(Double.parseDouble(s1));//DB
                }
            }
            find();//找2长度频繁模式
            calculate();   //模式融合、计算支持度、判断是否频繁、若频繁继续模式融合
        }
    }

    public static void find() {  //2长度模式
        candNum = 2;
        mapV1 = new LinkedHashMap<>();
        List<Double> Z = new ArrayList<>();
        List<Double> Z2 = new ArrayList<>();
        int i = 0, j = 1;
        Integer[] Cd = new Integer[2];
        Integer[] Cd2 = new Integer[2];
        Cd[0] = 1;
        Cd[1] = 2;
        Cd2[0] = 2;
        Cd2[1] = 1;
        while (j < S.size()) {
            if (S.get(j) > S.get(i))   //12模式
            {
                Z.add(Double.valueOf(j + 1));
            } else if (S.get(j) < S.get(i))    //21模式
            {
                Z2.add(Double.valueOf(j + 1));
            }
            i++;
            j++;
            // comparison_num++;
        }
        judge_fre(Cd, Z);//频繁的放入了mapV1
        judge_fre(Cd2, Z2);
    }

    private static void calculate() {
        Fmap.putAll(mapV1);//mapV1是上轮新生成的频繁模式
        while (mapV1.size() > 0) {
            mapV2 = new LinkedHashMap<>();
            mapV2.putAll(mapV1);
            mapV1.clear();
            //   int fre_num = mapV2.size();
            List<LNode> Lb = new ArrayList<>();
            for (Iterator<Map.Entry<String, List<Double>>> iterator1 = mapV2.entrySet().iterator(); iterator1.hasNext(); ) {
                Map.Entry<String, List<Double>> entry1 = iterator1.next();
                List<Double> PLocation = entry1.getValue();
                Lb.add(getLNode(PLocation));
            }
            int i;
            for (Iterator<Map.Entry<String, List<Double>>> iterator1 = mapV2.entrySet().iterator(); iterator1.hasNext(); ) {
                Map.Entry<String, List<Double>> entry1 = iterator1.next();
                String key1 = entry1.getKey(); //获取频繁模式
                Integer[] P = stringToArray(key1);
                Integer[] PSuf = new Integer[P.length - 1];
                System.arraycopy(P, 1, PSuf, 0, PSuf.length); //获取后缀
                List<Double> PLocation = entry1.getValue();
                LNode PNode = getLNode(PLocation); //  PNode P位置链表
                i = 0;
                for (Iterator<Map.Entry<String, List<Double>>> iterator2 = mapV2.entrySet().iterator(); iterator2.hasNext(); ) {
                    Map.Entry<String, List<Double>> entry2 = iterator2.next();
                    LNode QNode = Lb.get(i);//  QNode Q位置链表
                    if (PNode.data >= minsup && QNode.data >= minsup) {
                        String key2 = entry2.getKey(); //获取频繁模式
                        Integer[] Q = stringToArray(key2);
                        Integer[] QPre = new Integer[Q.length - 1];  //获取前缀
                        System.arraycopy(Q, 0, QPre, 0, QPre.length);
                        contrast_num++;
                        if (Arrays.equals(getOrder(PSuf), getOrder(QPre))) {
                            patternFusion(P, PNode, Q, QNode);//模式融合
                        }
                    }
                    i++;
                }
            }
            Fmap.putAll(mapV1);
        }
    }


    private static void patternFusion(Integer[] P, LNode PNode, Integer[] Q, LNode QNode) {
        int slen = P.length;

        if (P[0].doubleValue() == Q[Q.length - 1].doubleValue()) {
            Integer[] Cd = new Integer[P.length + 1];
            Integer[] Cd2 = new Integer[P.length + 1];
            Cd[0] = P[0].intValue();
            Cd2[0] = P[0].intValue() + 1;
            Cd[slen] = P[0].intValue() + 1;
            Cd2[slen] = P[0].intValue();
            for (int t = 1; t < slen; t++) {
                if (P[t] > Q[slen - 1]) {
                    //中间位置增长
                    //小的一行的中间位置和大的一行的最后一个数比较，大于+1，小于等于不变
                    Cd[t] = P[t].intValue() + 1;
                    Cd2[t] = P[t].intValue() + 1;
                } else {
                    Cd[t] = P[t].intValue();//Cd:(1,3,2)
                    Cd2[t] = P[t].intValue();//Cd2:(2,1,3)
                }
            }
            // Candmap.add(List.of(Cd));
            // Candmap.add(List.of(Cd2));
            candNum += 2;//候选模式++
            grow_BaseP2(P.length, QNode, PNode, Cd, Cd2);
        } else if (P[0].doubleValue() < Q[Q.length - 1].doubleValue()) {
            Integer[] Cd = new Integer[P.length + 1];
            Cd[0] = P[0].intValue();//小的不变  （1,0,0）
            Cd[slen] = Q[slen - 1].intValue() + 1;//大的加一 1,0,3）
            for (int t = 1; t < slen; t++) {
                if (P[t] > Q[slen - 1]) {
                    //中间位置增长
                    //小的一行的中间位置和大的一行的最后一个数比较，大于+1，小于等于不变
                    Cd[t] = P[t].intValue() + 1;

                } else {
                    Cd[t] = P[t].intValue();
                }
            }
            //  Candmap.add(List.of(Cd));
            candNum++;
            grow_BaseP1(QNode, PNode, Cd);
        } else {
            Integer[] Cd = new Integer[P.length + 1];
            Cd[0] = P[0].intValue() + 1; // 大的加一
            Cd[slen] = Q[slen - 1].intValue(); // 小的不变
            for (int t = 0; t < slen - 1; t++) {
                if (Q[t] > P[0]) {
                    // 中间位置增长
                    Cd[t + 1] = Q[t].intValue() + 1;
                } else {
                    Cd[t + 1] = Q[t].intValue();
                }
            }
            candNum++;
            //   Candmap.add(List.of(Cd));
            grow_BaseP1(QNode, PNode, Cd);
            //}
        }

    }

    private static void grow_BaseP2(int slen, LNode qNode, LNode pNode, Integer[] Cd, Integer[] Cd2) {
        List<Double> Z = new ArrayList<>();
        List<Double> Z2 = new ArrayList<>();
        int lst;
        LNode p = pNode;
        LNode q = qNode;
        while (p.next != null && q.next != null) {
            if (q.next.data == p.next.data + 1) {
                lst = q.next.data.intValue();
                //有筛选
                int fri = lst - slen;
                //有筛选
                if (S.get(lst - 1) > S.get(fri - 1)) {
                    Z.add(q.next.data);
                } else if (S.get(lst - 1) < S.get(fri - 1)) {
                    Z2.add(q.next.data);
                }
                //comparison_num++;
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
        qNode.data = qNode.data - Z.size() - Z2.size();
        judge_fre(Cd, Z);
        judge_fre(Cd2, Z2);
    }

    private static void grow_BaseP1(LNode qNode, LNode pNode, Integer[] Cd) {
        List<Double> Z = new ArrayList<>();
        LNode p = pNode;
        LNode q = qNode;
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
            element_num++;//元素总比较次数
        }
        pNode.data = pNode.data - Z.size();
        qNode.data = qNode.data - Z.size();
        judge_fre(Cd, Z);
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

    private static LNode getLNode(List<Double> List) {
        LNode PNode = new LNode();
        PNode.data = Double.valueOf(List.size());
        LNode p = new LNode();//p是节点
        LNode s = new LNode();//s是节点
        s = PNode;
        for (Double val : List) {
            p = new LNode();
            p.data = val;
            s.next = p;
            s = p;
        }
        s.next = null;
        return PNode;
    }

    static class LNode {
        Double data;
        LNode next = null;
    }


}
