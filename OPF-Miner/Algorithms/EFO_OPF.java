package OPF;


import newalgorithm.MemoryLogger;

import java.io.*;
import java.util.*;


public class EFO_OPF {
    public static double minsup;
    public static double k;  //遗忘因子
    public static double e = Math.E;//自然常数e的近似值
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

    private static void printCostTime(double seconds) {
        System.out.println(seconds);//时间
        System.out.println(candNum);
        System.out.println(Fmap.size());//频繁模式数量
        System.out.println(element_num);
        System.out.println(contrast_num);//模式融合前缀后缀比较次数
        MemoryLogger.getInstance().checkMemory();
        double maxMemory = MemoryLogger.getInstance().getMaxMemory();
        System.out.println(maxMemory);
    }

    public static void judge_fre(Integer[] Cd, List<Double> Z) {   //判断是否频繁
        double sup_num = 0;
        for (int i = 0; i < Z.size(); i++) {
            sup_num += forget_mech.get(Z.get(i).intValue());
        }
        if (sup_num >= minsup) {
            mapV1.put(Arrays.toString(Cd), Z);
            //   System.out.println(Arrays.toString(Cd) + "→" + Z.size());
         // allfrepattern.put(Arrays.toString(Cd), Z.size());
        }
    }

    private static void readFile() throws IOException {

        minsup=4.0;
        //  minsup=6.0;
        //   minsup=8.0;
        //   minsup = 10.0;
        // minsup=12.0;

      File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\亚马逊.txt");// 5842  db1
        //  File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\股票Russell2000（1987.9.10~2019.12.27）.txt");//  8141  db2
        //File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\Nasdaq.txt");//1 2279  db3
        //  File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\S&P500.txt");// 2 3046  db4
        // File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\NYSE.txt");//6W  db5
        // File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\cl.us.txt");//  1 0305  db6
        // File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\hpq.us.txt");//1 2075  db7
        //   File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\ge.us.txt");// 1 4058  db8


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
            len=S.size();
            k=1.0/len;
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
            List<EFO_Miner.LNode> Lb = new ArrayList<>();
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
                EFO_Miner.LNode PNode = getLNode(PLocation); //  PNode P位置链表
                i = 0;
                for (Iterator<Map.Entry<String, List<Double>>> iterator2 = mapV2.entrySet().iterator(); iterator2.hasNext(); ) {
                    Map.Entry<String, List<Double>> entry2 = iterator2.next();
                    EFO_Miner.LNode QNode = Lb.get(i);//  QNode Q位置链表
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


    private static void patternFusion(Integer[] P, EFO_Miner.LNode PNode, Integer[] Q, EFO_Miner.LNode QNode) {
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
            //  Candmap.add(List.of(Cd));//###################
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

    private static void grow_BaseP2(int slen, EFO_Miner.LNode qNode, EFO_Miner.LNode pNode, Integer[] Cd, Integer[] Cd2) {
        List<Double> Z = new ArrayList<>();
        List<Double> Z2 = new ArrayList<>();
        int lst;
        EFO_Miner.LNode p = pNode;
        EFO_Miner.LNode q = qNode;
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

    private static void grow_BaseP1(EFO_Miner.LNode qNode, EFO_Miner.LNode pNode, Integer[] Cd) {
        List<Double> Z = new ArrayList<>();
        EFO_Miner.LNode p = pNode;
        EFO_Miner.LNode q = qNode;
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

    private static EFO_Miner.LNode getLNode(List<Double> List) {
        EFO_Miner.LNode PNode = new EFO_Miner.LNode();
        PNode.data = Double.valueOf(List.size());
        EFO_Miner.LNode p = new EFO_Miner.LNode();//p是节点
        EFO_Miner.LNode s = new EFO_Miner.LNode();//s是节点
        s = PNode;
        for (Double val : List) {
            p = new EFO_Miner.LNode();
            p.data = val;
            s.next = p;
            s = p;
        }
        s.next = null;
        return PNode;
    }

    static class LNode {
        Double data;
        EFO_Miner.LNode next = null;
    }

}
