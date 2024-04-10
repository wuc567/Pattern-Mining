package OPF;
//不采用 maximal support priority strategy

import newalgorithm.MemoryLogger;

import java.io.*;
import java.util.*;

public class OPF_noPriority {

    public static double minsup;
    public static double k;  //遗忘因子
    public static double e = Math.E;//自然常数e的近似值
    static List<Double> S = new ArrayList<>(); // sequence
    public static int len;//DB长
    public static int fre_num = 0;//频繁模式数量
    public static int fre_number;//每轮融合后新生成的频繁模式的数量
    private static int candNum = 2;//候选模式
    public static int element_num = 0;//元素总比较次数
    public static int contrast_num = 0;//模式融合前缀后缀对比次数
      static List<List<Integer>> Candmap = new ArrayList<>();
    static Map<String, List<Integer>> map = new HashMap<>();//
    static Map<String, Double> Fmap = new LinkedHashMap<>();

    private static List<Map<String, List<Integer>>> fre_group = new ArrayList<>();//
    private static Map<String, List<Integer>> map0 = new LinkedHashMap<>();//
    private static Map<String, List<Integer>> mapV1 = new LinkedHashMap<>(); //放每次生成的频繁模式，里边模式的长度都相同
    private static Map<String, List<Integer>> mapV2 = new LinkedHashMap<>(); //放已出现过的模式
    private static Map<String, List<Integer>> mapV3 = new LinkedHashMap<>(); //放已出现过的模式
    private static Map<String, List<Integer>> mapV4 = new LinkedHashMap<>(); //放已出现过的模式
    static List<Double> forget_mech= new ArrayList<>();//遗忘机制
    public static void main(String[] args) throws IOException {
        long startTime = System.nanoTime();
        readFile();
        long endTime = System.nanoTime();
        long duration = endTime - startTime;
        double seconds = (double)duration / 1_000_000_000.0;
        printCostTime(seconds);
        System.out.println("UB长=" + S.size());
    }

    private static void printCostTime(double Time) {
        System.out.println(Time);
        System.out.println(candNum);//候选
        System.out.println(fre_num);//频繁
        System.out.println(element_num);
        System.out.println(contrast_num);//模式融合前缀后缀比较次数
        MemoryLogger.getInstance().checkMemory();
        double maxMemory = MemoryLogger.getInstance().getMaxMemory();
        System.out.println(maxMemory);
    }

    private static void readFile() throws IOException {

         minsup=4.0;
        //  minsup=6.0;
        //   minsup=8.0;
        // minsup = 10.0;
        //minsup=12.0;


         File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\亚马逊.txt");// 5842  db1
        //  File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\股票Russell2000（1987.9.10~2019.12.27）.txt");//  8141  db2
        // File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\Nasdaq.txt");//1 2279  db3
        //File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\S&P500.txt");// 2 3046  db4
        //    File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\NYSE.txt");//6W  db5
        // File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\cl.us.txt");//  1 0305  db6
        // File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\hpq.us.txt");//1 2075  db7
        //  File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\ge.us.txt");// 1 4058  db8

        BufferedReader br = new BufferedReader(new FileReader(file));
        String s;

        //使用readLine方法，一次读一行
        while ((s = br.readLine()) != null) {
            s = s.trim();
            String[] str = s.split(" ");
            //   str = s.split(",");
            for (String s1 : str) {
                if (!" ".equals(s1) && !s1.isEmpty()) {
                    S.add(Double.parseDouble(s1));//DB
                }
            }
            len = S.size();//DB长度
            k=1.0/len; // k=1/len
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
        mapV1 = new LinkedHashMap<>();
        List<Integer> Z = new ArrayList<>();
        List<Integer> Z2 = new ArrayList<>();
        int i = 0, j = 1;
        Integer[] Cd = new Integer[2];
        Integer[] Cd2 = new Integer[2];
        Cd[0] = 1;
        Cd[1] = 2;
        Cd2[0] = 2;
        Cd2[1] = 1;
        double f1=0.0;
        double f2=0.0;
        while (j < S.size()) {
            if (S.get(j) > S.get(i))   //12模式
            {
                Z.add(j + 1);
                f1+=forget_mech.get(j+1);
            } else if (S.get(j) < S.get(i))    //21模式
            {
                Z2.add(j + 1);
                f2+=forget_mech.get(j+1);
            }
            i++;
            j++;
        }
        fre_group.add(map);
        judge_fre(Cd, Z, f1,1);//频繁的放入了mapV1
        fre_group.add(map);
        map0 = new LinkedHashMap<>();
        judge_fre(Cd2, Z2,f2, 2);
    }

    public static void judge_fre(Integer[] Cd, List<Integer> Z,double sup_num, int group) {   //判断是否频繁
        if (sup_num >= minsup) {
            Map<String, List<Integer>> fmap = new HashMap<>();
            fre_number++;//此轮生成的频繁模式数量
            fmap.put(Arrays.toString(Cd), Z);//此次生成的频繁模式和位置，里面只有一个模式
            map0.putAll(fmap);
            fre_group.set(group - 1, map0);
           //  System.out.println(Arrays.toString(Cd)+": "+" "+sup_num);
            //  System.out.println(Arrays.toString(Cd)+sup_num);
            Fmap.put(Arrays.toString(Cd), sup_num);
            //allfrepattern.put(Arrays.toString(Cd),sup_num);
        }
    }

    private static void generate_fre(Map<String, List<Integer>> map1, List<LNode> Lb1,
                                     Map<String, List<Integer>> map2, List<LNode> Lb2,int group) {

        map0 = new LinkedHashMap<>();
        fre_group.add(map);
        for (Iterator<Map.Entry<String, List<Integer>>> iterator1 = map1.entrySet().iterator(); iterator1.hasNext(); ) {
            Map.Entry<String, List<Integer>> entry1 = iterator1.next();
            LNode PNode = Lb1.get(0); //  PNode P位置链表
            String key1 = entry1.getKey(); //获取频繁模式
            Integer[] P = stringToArray(key1);
            for (Iterator<Map.Entry<String, List<Integer>>> iterator2 = map2.entrySet().iterator(); iterator2.hasNext(); ) {
                Map.Entry<String, List<Integer>> entry2 = iterator2.next();
                LNode QNode = Lb2.get(0);//  QNode Q位置链表
                String key2 = entry2.getKey(); //获取频繁模式
                double suff=Fmap.get(key2) ;
                if (PNode.data >= minsup && suff >= minsup) {//
                    Integer[] Q = stringToArray(key2);
                    patternFusion(P, PNode, Q, QNode, key2,group);//模式融合
                }
            }
        }
    }

    private static void calculate() {
        if (fre_number > 0) {
            fre_num += fre_number;
            fre_number = 0;
            mapV1 = new LinkedHashMap<>();
            mapV2 = new LinkedHashMap<>();
            mapV1.putAll(fre_group.get(0));//组1
            mapV2.putAll(fre_group.get(1));//组2
            fre_group.clear();
            List<LNode> Lb1 = new ArrayList<>();
            List<LNode> Lb2 = new ArrayList<>();
            List<LNode> Lb3 = new ArrayList<>();
            List<LNode> Lb4 = new ArrayList<>();
            for (Iterator<Map.Entry<String, List<Integer>>> iterator1 = mapV1.entrySet().iterator(); iterator1.hasNext(); ) {
                Map.Entry<String, List<Integer>> entry1 = iterator1.next();
                List<Integer> PLocation = entry1.getValue();
                Lb1.add(getLNode(PLocation));
                Lb3.add(getLNode(PLocation));
            }

            for (Iterator<Map.Entry<String, List<Integer>>> iterator1 = mapV2.entrySet().iterator(); iterator1.hasNext(); ) {
                Map.Entry<String, List<Integer>> entry1 = iterator1.next();
                List<Integer> PLocation = entry1.getValue();
                Lb2.add(getLNode(PLocation));
                Lb4.add(getLNode(PLocation));
            }
            //g1+g1
            generate_fre(mapV1, Lb1, mapV1, Lb3,1);
            //g1+g2
            generate_fre(mapV1, Lb1, mapV2, Lb4,2);
            //g2+g1
            generate_fre(mapV2, Lb2, mapV1, Lb3,3);
            //g2+g2
            generate_fre(mapV2, Lb2, mapV2, Lb4,4);

        }
        while (fre_number > 0) {

            fre_num += fre_number;
            fre_number = 0;
            mapV1 = new LinkedHashMap<>();
            mapV2 = new LinkedHashMap<>();
            mapV3 = new LinkedHashMap<>();
            mapV4 = new LinkedHashMap<>();
            mapV1.putAll(fre_group.get(0)); // 12 21
            mapV2.putAll(fre_group.get(1)); //21  12
            mapV3.putAll(fre_group.get(2)); //12 12
            mapV4.putAll(fre_group.get(3));//21 21
            fre_group.clear();
            Map<String, List<Integer>> map = new HashMap<>();
            List<LNode> Lb1 = new ArrayList<>();
            List<LNode> Lb2 = new ArrayList<>();
            List<LNode> Lb3 = new ArrayList<>();
            List<LNode> Lb4 = new ArrayList<>();
            List<LNode> Lb5 = new ArrayList<>();
            List<LNode> Lb6 = new ArrayList<>();
            List<LNode> Lb7 = new ArrayList<>();
            List<LNode> Lb8 = new ArrayList<>();
            for (Iterator<Map.Entry<String, List<Integer>>> iterator1 = mapV1.entrySet().iterator(); iterator1.hasNext(); ) {
                Map.Entry<String, List<Integer>> entry1 = iterator1.next();
                List<Integer> PLocation = entry1.getValue();
                Lb1.add(getLNode(PLocation)); // 前缀
                Lb5.add(getLNode(PLocation)); //后缀
            }
            for (Iterator<Map.Entry<String, List<Integer>>> iterator1 = mapV2.entrySet().iterator(); iterator1.hasNext(); ) {
                Map.Entry<String, List<Integer>> entry1 = iterator1.next();
                List<Integer> PLocation = entry1.getValue();
                Lb2.add(getLNode(PLocation));  //后缀
                Lb6.add(getLNode(PLocation));  //前缀
            }
            for (Iterator<Map.Entry<String, List<Integer>>> iterator1 = mapV3.entrySet().iterator(); iterator1.hasNext(); ) {
                Map.Entry<String, List<Integer>> entry1 = iterator1.next();
                List<Integer> PLocation = entry1.getValue();
                Lb3.add(getLNode(PLocation));  //前缀
                Lb7.add(getLNode(PLocation));   //后缀
            }
            for (Iterator<Map.Entry<String, List<Integer>>> iterator1 = mapV4.entrySet().iterator(); iterator1.hasNext(); ) {
                Map.Entry<String, List<Integer>> entry1 = iterator1.next();
                List<Integer> PLocation = entry1.getValue();
                Lb4.add(getLNode(PLocation));  //前缀
                Lb8.add(getLNode(PLocation));  //后缀
            }
            fre_group.add(map);
            fre_group.add(map);
            fre_group.add(map);
            fre_group.add(map);

            if (Lb1.size() != 0 && (Lb5.size() != 0 | Lb6.size() != 0)) {
                generate_fre2(mapV1, Lb1, mapV1, Lb5, mapV2, Lb6, 1);//组1  组1   +组2 放在组1里
            }
            if (Lb2.size() != 0 && (Lb7.size() != 0 | Lb8.size() != 0)) {
                generate_fre2(mapV2, Lb2, mapV3, Lb7, mapV4, Lb8, 2);//组2 组3   +组4 放在组2里
            }
            if (Lb3.size() != 0 && (Lb5.size() != 0 | Lb6.size() != 0)) {
                generate_fre2(mapV3, Lb3, mapV1, Lb5, mapV2, Lb6, 3);//组3 组1   +组2 放在组3里
            }
            if (Lb4.size() != 0 && (Lb7.size() != 0 | Lb8.size() != 0)) {
                generate_fre2(mapV4, Lb4, mapV3, Lb7, mapV4, Lb8,  4);//组4  组3 +组4 放在组4里
            }
        }
    }

    private static void generate_fre2(Map<String, List<Integer>> map1, List<LNode> Lb1,
                                      Map<String, List<Integer>> map2, List<LNode> Lb2,
                                      Map<String, List<Integer>> map3, List<LNode> Lb3, int group) {
        map0 = new LinkedHashMap<>();
        int j, i = 0;
        for (Iterator<Map.Entry<String, List<Integer>>> iterator1 = map1.entrySet().iterator(); iterator1.hasNext(); ) {
            Map.Entry<String, List<Integer>> entry1 = iterator1.next();
            LNode PNode = Lb1.get(i); //  PNode P位置链表
            String key1 = entry1.getKey(); //获取频繁模式
            Integer[] P = stringToArray(key1);
            Integer[] PSuf = new Integer[P.length - 1];
            System.arraycopy(P, 1, PSuf, 0, PSuf.length); //获取后缀
            j = 0;
            for (Iterator<Map.Entry<String, List<Integer>>> iterator2 = map2.entrySet().iterator(); iterator2.hasNext(); ) {
                Map.Entry<String, List<Integer>> entry2 = iterator2.next();
                LNode QNode = Lb2.get(j);//  QNode Q位置链表
                String key2 = entry2.getKey(); //获取频繁模式q
                double suff=Fmap.get(key2) ;
                if (PNode.data >= minsup && suff >= minsup) {
                    Integer[] Q = stringToArray(key2);
                    Integer[] QPre = new Integer[Q.length - 1];  //获取前缀
                    System.arraycopy(Q, 0, QPre, 0, QPre.length);
                    contrast_num++;//前缀后缀比较次数
                    if (Arrays.equals(getOrder(PSuf), getOrder(QPre))) {
                        patternFusion(P, PNode, Q, QNode,key2,  group);//模式融合       组1和组2 的结果
                    }
                }
                j++;
            }
            j = 0;
            //  if (PNode.data >= minsup) {
            for (Iterator<Map.Entry<String, List<Integer>>> iterator2 = map3.entrySet().iterator(); iterator2.hasNext(); ) {
                Map.Entry<String, List<Integer>> entry2 = iterator2.next();
                LNode QNode = Lb3.get(j);//  QNode Q位置链表
                String key2 = entry2.getKey(); //获取频繁模式
                double suff=Fmap.get(key2) ;
                if (PNode.data >= minsup && suff >= minsup) {
                    Integer[] Q = stringToArray(key2);
                    Integer[] QPre = new Integer[Q.length - 1];  //获取前缀
                    System.arraycopy(Q, 0, QPre, 0, QPre.length);
                    contrast_num++;//前缀后缀比较次数
                    if (Arrays.equals(getOrder(PSuf), getOrder(QPre))) {
                        patternFusion(P, PNode, Q, QNode,key2, group);//模式融合
                    }
                }
                j++;
            }
            // }
            i++;
        }
    }

    private static void patternFusion(Integer[] P, LNode PNode, Integer[] Q, LNode QNode, String key2,int group) {
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
            grow_BaseP2(P.length, QNode, PNode, Cd, Cd2, key2,group);
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
             // Candmap.add(List.of(Cd));
            candNum++;
            grow_BaseP1(QNode, PNode, Cd, key2,group);
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
           //  Candmap.add(List.of(Cd));
            grow_BaseP1(QNode, PNode, Cd, key2,group);
            //}
        }
        // }
    }

    private static void grow_BaseP2(int slen, LNode qNode, LNode pNode, Integer[] Cd, Integer[] Cd2, String key2,int group) {
        List<Integer> Z = new ArrayList<>();
        List<Integer> Z2 = new ArrayList<>();
        int lst;
        LNode p = pNode;
        LNode q = qNode;
        double f1=0.0;//减去的就是超模式的支持度
        double f2=0.0;//减去的就是超模式的支持度
        while (p.next != null && q.next != null) {
            if (q.next.data == p.next.data + 1) {
                lst = q.next.data;
                //有筛选
                int fri = lst - slen;
                //有筛选
                if (S.get(lst - 1) > S.get(fri - 1)) {
                    Z.add(q.next.data);
                    f1+= forget_mech.get(q.next.data);//每找到一次出现就减去一次
                } else if (S.get(lst - 1) < S.get(fri - 1)) {
                    Z2.add(q.next.data);
                    f2+= forget_mech.get(q.next.data);//每找到一次出现就减去一次
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
        Fmap.put(key2,Fmap.get(key2)-f1-f2);
        judge_fre(Cd, Z,f1, group);
        judge_fre(Cd2, Z2, f2,group);
    }

    private static void grow_BaseP1(LNode qNode, LNode pNode, Integer[] Cd, String key2,int group) {
        List<Integer> Z = new ArrayList<>();
        LNode p = pNode;
        LNode q = qNode;
        double f=0.0;//减去的就是超模式的支持度
        while (p.next != null && q.next != null) {
            if (q.next.data == p.next.data + 1) {
                //有筛选
                Z.add(q.next.data);
                f+= forget_mech.get(q.next.data);//每找到一次出现就减去一次
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
        Fmap.put(key2,Fmap.get(key2)-f);
        judge_fre(Cd, Z,f, group);
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

    private static LNode getLNode(List<Integer> List) {
        LNode PNode = new LNode();
        PNode.data = List.size();
        LNode p = new LNode();//p是节点
        LNode s = new LNode();//s是节点
        s = PNode;
        for (Integer val : List) {
            p = new LNode();
            p.data = val;
            s.next = p;
            s = p;
        }
        s.next = null;
        return PNode;
    }

    static class LNode {
        int data;
        LNode next = null;
    }


}
