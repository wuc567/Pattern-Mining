package OPF;
//无分组，无排序√
//23.9.3  提前计算遗忘系数 √
//23.9.3 前缀后缀剪枝不相同 √
//oooo

import newalgorithm.MemoryLogger;

import java.io.*;
import java.util.*;

public class OPF_noGroup {
    public static double minsup;
    public static double k;  //遗忘因子
    public static double e = Math.E;//自然常数e的近似值
    static List<Double> S = new ArrayList<>(); // sequence
    public static int len;//DB长
    private static int candNum = 2;//候选模式
    public static int element_num = 0;//元素总比较次数
    public static int contrast_num = 0;//模式融合前缀后缀对比次数
    private static double sup_num;//支持度
    static List<List<Integer>> Candmap = new ArrayList<>();
    private static Map<String, List<Double>> Fmap = new LinkedHashMap<>();//所有频繁模式集合
    private static Map<String, List<Double>> mapV1; //放每次生成的频繁模式，里边模式的长度都相同
    private static Map<String, List<Double>> mapV2; //放已出现过的模式
    static List<Double> forget_mech= new ArrayList<>();//遗忘机制
    static List<Double> suffset=new ArrayList<>();
    static List<Double> newsuffset=new ArrayList<>();
    public static void main(String[] args) throws IOException {
        long startTime = System.nanoTime();
        readFile1();
        long endTime = System.nanoTime();
        long duration = endTime - startTime;
        double seconds = (double)duration / 1_000_000_000.0;
        printCostTime(seconds);
        result(seconds);
        //System.out.println("UB长=" + S.size());
    }

    private static void printCostTime(double Time) {
        System.out.println(Time);
        System.out.println(candNum);
        System.out.println(Fmap.size());
        System.out.println(element_num);
        System.out.println(contrast_num);//模式融合前缀后缀比较次数
        MemoryLogger.getInstance().checkMemory();
        double maxMemory = MemoryLogger.getInstance().getMaxMemory();
        System.out.println(maxMemory);
    }
    public static void result(double time)throws IOException{
        String filePath = "OPF_noGroup.txt"; // 文件路径
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(filePath, true))) {

            // 在已有文件的末尾续写数据
            writer.write(Double.toString(time));
            writer.newLine(); // 换行
            MemoryLogger.getInstance().checkMemory();
            double maxMemory = MemoryLogger.getInstance().getMaxMemory();
            writer.write(Double.toString(maxMemory));
            writer.newLine(); // 换行
            writer.write(Integer.toString(Fmap.size()));
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


    private static void readFile1() throws IOException {

        minsup=4.0;
        // minsup=6.0;
        //  minsup=8.0;
        //  minsup = 10.0;
        // minsup=12.0;



        File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\亚马逊.txt");// 5842  db1
        // File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\股票Russell2000（1987.9.10~2019.12.27）.txt");//  8141  db2
        // File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\Nasdaq.txt");//1 2279  db3
        //  File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\S&P500.txt");// 2 3046  db4
        //  File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\NYSE.txt");//6W  db5
        //  File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\cl.us.txt");//  1 0305  db6  新
         //  File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\hpq.us.txt");//1 2075  db7  新
        // File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\ge.us.txt");// 1 4058  db8

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
            len = S.size();//DB长度
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
        double f1=0.0;
        double f2=0.0;
        while (j < len) {
            if (S.get(j) > S.get(i))   //12模式
            {
                Z.add(Double.valueOf(j + 1));
                f1+=forget_mech.get(j+1);
            } else if (S.get(j) < S.get(i))    //21模式
            {
                Z2.add(Double.valueOf(j + 1));
                f2+=forget_mech.get(j+1);
            }
            i++;
            j++;
        }
        judge_fre(Cd, Z, f1);
        judge_fre(Cd2, Z2,f2);
    }
    public static void judge_fre(Integer[] Cd, List<Double> Z,double sup_num) {   //判断是否频繁
        if (sup_num >= minsup) {
            mapV1.put(Arrays.toString(Cd), Z);
            suffset.add(sup_num);
            //   System.out.println(Arrays.toString(Cd) + "→" + sup_num);
        }
/*
        if (Z.size() >= minsup) {
            mapV1.put(Arrays.toString(Cd), Z);
             System.out.println(Arrays.toString(Cd)+":"+Z.size());
        }*/
    }

    private static void calculate() {
        Fmap.putAll(mapV1);//mapV1是上轮新生成的频繁模式
        while (mapV1.size() > 0) {
            newsuffset.addAll(suffset);
            suffset.clear();
            mapV2 = new LinkedHashMap<>();
            mapV2.putAll(mapV1);
            mapV1.clear();
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
                    double suff=newsuffset.get(i);
                    if (PNode.data >= minsup && suff>= minsup) {
                        String key2 = entry2.getKey(); //获取频繁模式
                        Integer[] Q = stringToArray(key2);
                        Integer[] QPre = new Integer[Q.length - 1];  //获取前缀
                        System.arraycopy(Q, 0, QPre, 0, QPre.length);
                        contrast_num++;
                        if (Arrays.equals(getOrder(PSuf), getOrder(QPre))) {
                            LNode QNode = Lb.get(i);//  QNode Q位置链表
                            patternFusion(P, PNode, Q, QNode,i);//模式融合
                        }
                    }
                    i++;
                }
            }
            Fmap.putAll(mapV1);
            newsuffset.clear();
        }
    }


    private static void patternFusion(Integer[] P, LNode PNode, Integer[] Q, LNode QNode,int index) {
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
            Candmap.add(List.of(Cd));
            Candmap.add(List.of(Cd2));
            candNum += 2;//候选模式++
            grow_BaseP2(P.length, QNode, PNode, Cd, Cd2,index);
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
            Candmap.add(List.of(Cd));
            candNum++;
            grow_BaseP1(QNode, PNode, Cd,index);
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
            Candmap.add(List.of(Cd));
            grow_BaseP1(QNode, PNode, Cd,index);
        }

    }

    private static void grow_BaseP2(int slen, LNode qNode,LNode pNode, Integer[] Cd, Integer[] Cd2,int index) {
        List<Double> Z = new ArrayList<>();
        List<Double> Z2 = new ArrayList<>();
        int lst;
        LNode p = pNode;
        LNode q = qNode;
        double f1=0.0;//减去的就是超模式的支持度
        double f2=0.0;//减去的就是超模式的支持度
        while (p.next != null && q.next != null) {
            if (q.next.data == p.next.data + 1) {
                lst = q.next.data.intValue();
                //有筛选
                int fri = lst - slen;
                //有筛选
                if (S.get(lst - 1) > S.get(fri - 1)) {
                    Z.add(q.next.data);
                    f1+= forget_mech.get(q.next.data.intValue());//每找到一次出现就减去一次
                } else if (S.get(lst - 1) < S.get(fri - 1)) {
                    Z2.add(q.next.data);
                    f2+= forget_mech.get(q.next.data.intValue());//每找到一次出现就减去一次
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
        newsuffset.set(index,newsuffset.get(index)-f1-f2);//更新后缀支持度
        judge_fre(Cd, Z,f1);
        judge_fre(Cd2, Z2,f2);
    }

    private static void grow_BaseP1(LNode qNode, LNode pNode, Integer[] Cd,int index) {
        List<Double> Z = new ArrayList<>();
       LNode p = pNode;
        LNode q = qNode;
        double f=0.0;//减去的就是超模式的支持度
        while (p.next != null && q.next != null) {
            if (q.next.data == p.next.data + 1) {
                //有筛选
                Z.add(q.next.data);
                f+= forget_mech.get(q.next.data.intValue());//每找到一次出现就减去一次
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
        newsuffset.set(index,newsuffset.get(index)-f);//更新后缀支持度
        judge_fre(Cd, Z, f);
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
