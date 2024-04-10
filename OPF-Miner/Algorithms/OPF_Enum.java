package OPF;


import newalgorithm.MemoryLogger;

import java.io.*;
import java.util.*;

public class OPF_Enum {
    public static double minsup;
    private static Map<String, List<Double>> Fmap = new LinkedHashMap<>();

    public static double k;  //遗忘因子
    public static double e = Math.E;//自然常数e的近似值
    static List<Double> S = new ArrayList<>(); // sequence
    public static int len;//DB长
    public static int fre_num = 0;//频繁模式数量
    public static int fre_number = 0;//每轮融合后新生成的频繁模式的数量
    private static int candNum = 2;//候选模式
    public static int element_num = 0;//元素总比较次数
    //   private static int comparison_num = 0;//融合生成两个模式情况下计算支持度时元素比较次数
    public static int contrast_num = 0;//模式融合时前缀后缀对比次数
    private static Map<String, List<Double>> Candmap = new LinkedHashMap<>();
    static List<Double> forget_mech = new ArrayList<>();//遗忘机制

    public static void main(String[] args) throws IOException {
        long startTime = System.nanoTime();
        readFile1();
        long endTime = System.nanoTime();
        long duration = endTime - startTime;
        double seconds = (double)duration / 1_000_000_000.0;
        printCostTime(seconds);
        System.out.println("UB长=" + S.size());
    }

    private static void printCostTime(double Time) {
        System.out.println(Time);
        System.out.println(candNum);
        System.out.println(fre_num);
        System.out.println(element_num);
        System.out.println(contrast_num);//模式融合前缀后缀比较次数
        MemoryLogger.getInstance().checkMemory();
        double maxMemory = MemoryLogger.getInstance().getMaxMemory();
        System.out.println(maxMemory);
        //  System.out.println(Candmap);
        /*System.out.println("候选模式为：");
        for (int g = 0; g < Candmap.size(); g++) {
            System.out.println(Candmap.get(g));
        }*/
    }


    private static void readFile1() throws IOException {

          minsup=4.0;
        //   minsup=6.0;
        //  minsup=8.0;
    //   minsup = 10.0;
        //  minsup=12.0;

        File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\亚马逊.txt");// 5842  db1
        // File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\股票Russell2000（1987.9.10~2019.12.27）.txt");//  8141  db2
        //   File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\Nasdaq.txt");//1 2279  db3
        // File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\S&P500.txt");// 2 3046  db4
        //File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\NYSE.txt");//6W  db5
        // File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\cl.us.txt");//  1 0305  db6
        //  File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\hpq.us.txt");//1 2075  db7
        // File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\ge.us.txt");// 1 4058  db8

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
            k =1.0 /len;
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
        judge_fre(Cd, Z,f1);
        judge_fre(Cd2, Z2,f2);
        Candmap.put(Arrays.toString(Cd), Z);
        Candmap.put(Arrays.toString(Cd2), Z2);
    }

    public static void judge_fre(Integer[] Cd, List<Double> Z,double sup_num) {   //判断是否频繁
        if (sup_num >= minsup) {
            fre_number++;
            Fmap.put(Arrays.toString(Cd), Z);
            //  System.out.println(Arrays.toString(Cd) + "→" + Z + "→" + sup_num);
        }
    }

    private static void calculate() {
        while (fre_number > 0) {
            fre_num += fre_number;
            fre_number = 0;
            Map<String, List<Double>> Fremap = new LinkedHashMap<>();
            Fremap.putAll(Fmap);
            Fmap.clear();
            Map<String, List<Double>> Candidatemap = new LinkedHashMap<>();
            Candidatemap.putAll(Candmap);
            Candmap.clear();
            for (Map.Entry<String, List<Double>> entry : Fremap.entrySet()) {
                String key = entry.getKey();
                Integer[] P = stringToArray(key);
                List<Double> PLocation = entry.getValue();
                OPF_Same.LNode PNode = getLNode(PLocation);//p位置
                patternEnum(P, PNode, Candidatemap);
            }
        }
    }


    private static void patternEnum(Integer[] P, OPF_Same.LNode PNode, Map<String, List<Double>> Candidatemap) {
        int slen = P.length;
        for (int temp = 1; temp <= slen + 1; temp++) {
            //1.生成超模式Cd
            Integer[] Cd = new Integer[P.length + 1];
            for (int j = 0; j < slen; j++) {
                if (P[j] < temp) {
                    Cd[j] = P[j];
                } else {
                    Cd[j] = P[j] + 1;
                }
            }
            Cd[slen] = temp;//得到Cd
            candNum++;
            if (PNode.data >= minsup) {//剪枝
                //2.求超模式后缀，再在候选模式中找后缀的位置集合
                Integer[] Q = new Integer[Cd.length - 1];
                System.arraycopy(Cd, 1, Q, 0, Q.length);
                Integer[] q = getOrder(Q);
                for (Map.Entry<String, List<Double>> entry : Candidatemap.entrySet()) {
                    String key = entry.getKey();
                    Integer[] r = stringToArray(key);
                    //相对顺序相同
                    if (Arrays.equals(q, r)) {
                        double A = P[0];
                        double B = q[q.length - 1];
                        List<Double> postion = entry.getValue();
                        if (A != B) {
                            grow_BaseP1(postion, PNode, Cd);
                        } else {
                            // p[0] == q[max]
                            if (Cd[0] < Cd[slen]) {
                                grow_BaseP2(slen, postion, PNode, 1, Cd);
                            } else {
                                grow_BaseP2(slen, postion, PNode, 2, Cd);
                            }

                        }
                        break;
                    }
                }
        }
        }

    }

    static void grow_BaseP1(List<Double> postion, OPF_Same.LNode pNode, Integer[] Cd) {

        int m = 0;
        int size = postion.size();
        OPF_Same.LNode p = pNode;
        List<Double> Z = new ArrayList<>();
        double f=0.0;//减去的就是超模式的支持度
        while (p.next != null && m < size) {
            if (postion.get(m) == p.next.data + 1) {
                Z.add(postion.get(m));
                f+= forget_mech.get(postion.get(m).intValue());//每找到一次出现就减去一次
                m++;
                p.next = p.next.next;
            } else if (p.next.data < postion.get(m)) {
                p = p.next;
            } else {
                m++;
            }
            element_num++;
        }
        Candmap.put(Arrays.toString(Cd), Z);
        pNode.data = pNode.data - Z.size();
        judge_fre(Cd, Z, f);

    }

    static void grow_BaseP2(int slen, List<Double> postion, OPF_Same.LNode L, int flag, Integer[] Cd) {

        int m = 0;
        int lst, fri;
        int size = postion.size();
        OPF_Same.LNode p = L;
        List<Double> Z = new ArrayList<>();
        double f=0.0;//减去的就是超模式的支持度
        while (p.next != null && m < size) {
            if (postion.get(m) == p.next.data + 1) {
                lst = postion.get(m).intValue();
                fri = lst - slen;
                if (flag == 1) {
                    if (S.get(lst - 1) > S.get(fri - 1)) {
                        Z.add(postion.get(m));
                        f+= forget_mech.get(postion.get(m).intValue());//每找到一次出现就减去一次
                        p.next = p.next.next;
                    }
                } else if (S.get(lst - 1) < S.get(fri - 1)) {
                    Z.add(postion.get(m));
                    f+= forget_mech.get(postion.get(m).intValue());//每找到一次出现就减去一次
                    p.next = p.next.next;
                }
                m++;

            } else if (p.next.data < postion.get(m)) {
                p = p.next;
            } else {
                m++;
            }
            element_num++;
        }
        Candmap.put(Arrays.toString(Cd), Z);
        L.data = L.data - Z.size();
        judge_fre(Cd, Z,f);
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

    private static OPF_Same.LNode getLNode(List<Double> List) {
        OPF_Same.LNode PNode = new OPF_Same.LNode();
        PNode.data = Double.valueOf(List.size());
        OPF_Same.LNode p = new OPF_Same.LNode();//p是节点
        OPF_Same.LNode s = new OPF_Same.LNode();//s是节点
        s = PNode;
        for (Double val : List) {
            p = new OPF_Same.LNode();
            p.data = val;
            s.next = p;
            s = p;
        }
        s.next = null;
        return PNode;
    }

    static class LNode {
        Double data;
        OPF_Same.LNode next = null;
    }


}
