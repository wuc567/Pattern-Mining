package OPF;

import newalgorithm.MemoryLogger;

import java.io.*;
import java.util.*;
import java.util.stream.Collectors;

public class Mat_OPF {
    public static double minsup;
    public static int[] inBinaryArr;
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
    static List<List<Integer>> Candmap = new ArrayList<>();
    static List<Double> forget_mech= new ArrayList<>();//遗忘机制
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
        // minsup=6.0;
        //  minsup=8.0;
        //minsup = 10.0;
        //   minsup=12.0;


     File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\亚马逊.txt");// 5842  db1
        //  File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\股票Russell2000（1987.9.10~2019.12.27）.txt");//  8141  db2
        //  File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\Nasdaq.txt");//1 2279  db3
        // File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\S&P500.txt");// 2 3046  db4
        //  File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\NYSE.txt");//6W  db5
        //  File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\cl.us.txt");//  1 0305  db6
        //   File file = new File("D:\\IDEA\\IdeaProjects\\code\\实验数据\\hpq.us.txt");//1 2075  db7
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
            k=1.0/len;
            forgetting_mechanism();
            inBinaryArr = getBinary(S);
            find();//找2长度频繁模式
            caculate();   //模式融合、计算支持度、判断是否频繁、若频繁继续模式融合
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
        while (j < len) {
            if (S.get(j) > S.get(i))   //12模式
            {
                Z.add(Double.valueOf(j + 1));
            } else if (S.get(j) < S.get(i))    //21模式
            {
                Z2.add(Double.valueOf(j + 1));
            }
            i++;
            j++;
        }
        judge_fre(Cd, Z, 1);
        judge_fre(Cd2, Z2, 3);
    }

    public static void judge_fre(Integer[] Cd, List<Double> Z, int group) {   //判断是否频繁
        double sup_num = 0;
        for (int i = 0; i < Z.size(); i++) {
            sup_num += forget_mech.get(Z.get(i).intValue());
        }
        if (sup_num >= minsup) {
            List<List<Double>>content =  new ArrayList<>();
            fre_number++;
            content.add(Z);
            content.add(List.of(sup_num));
            content.add(List.of((double)group));
            Fmap.put(Arrays.toString(Cd), content);
           //   System.out.println(Arrays.toString(Cd)+ "→" + Z + "→" + sup_num+ "→" +group);
        } else {
           //  System.out.println(Arrays.toString(Cd) + "→"+Z + "→" +sup_num);
        }
    }

    private static void caculate() {
        if (fre_number > 0) {
            fre_num += fre_number;
            fre_number = 0;
            boolean flag = true;
            //1.降序排序
            Comparator<Map.Entry<String, List<List<Double>>>> comparator = (entry1, entry2) -> {
                double value1 = entry1.getValue().get(1).get(0);
                double value2 = entry2.getValue().get(1).get(0);
                return Double.compare(value2, value1);
            };
            List<Map.Entry<String, List<List<Double>>>> sortedData = new ArrayList<>(Fmap.entrySet());
            Collections.sort(sortedData, comparator);
            if (Fmap.get("[1, 2]").get(1).get(0) < Fmap.get("[2, 1]").get(1).get(0)) {
                flag = false;
            }
            Fmap = new LinkedHashMap<>();
            List<Mat_OPF.LNode> Lb1 = new ArrayList<>();
            for (Map.Entry<String, List<List<Double>>> entry1 : sortedData) {
                List<Double> Location = entry1.getValue().get(0);
                Lb1.add(getLNode(Location));
            }
            //2.融合
            if (flag) {
                for (Map.Entry<String, List<List<Double>>> entry1 : sortedData) {
                    Integer[] P = stringToArray(entry1.getKey()); //P
                    List<List<Double>> value1 = entry1.getValue();
                    List<Double> PLocation = value1.get(0);
                    Mat_OPF.LNode PNode = getLNode(PLocation);//p位置
                    int group = value1.get(2).get(0).intValue();
                    int i = 0;
                    for (Map.Entry<String, List<List<Double>>> entry2 : sortedData) {
                        Mat_OPF.LNode QNode = Lb1.get(i);
                        if (PNode.data >= minsup &&QNode.data >= minsup) {
                            Integer[] Q = stringToArray(entry2.getKey());   //Q
                            patternFusion(P, PNode, Q, QNode, group);//模式融合
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
                    Mat_OPF.LNode PNode = getLNode(PLocation);//p位置
                    int group = value1.get(2).get(0).intValue() + 1;
                    int i = 0;
                    for (Map.Entry<String, List<List<Double>>> entry2 : sortedData) {
                        Mat_OPF.LNode QNode = Lb1.get(i);
                        if (PNode.data >= minsup &&QNode.data >= minsup) {//剪枝
                            Integer[] Q = stringToArray(entry2.getKey());   //Q
                            patternFusion(P, PNode, Q, QNode, group);//模式融合
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
            List<Mat_OPF.LNode> Lb1 = new ArrayList<>();
            List<Mat_OPF.LNode> Lb2 = new ArrayList<>();
            for (Map.Entry<String, List<List<Double>>> set : G1) {
                List<Double> PLocation = set.getValue().get(0);
                Lb1.add(getLNode(PLocation));
            }
            for (Map.Entry<String, List<List<Double>>> set : G2) {
                List<Double> PLocation = set.getValue().get(0);
                Lb2.add(getLNode(PLocation));
            }
            //3.融合
            for (Map.Entry<String, List<List<Double>>> entry1 : sortedData) {
                Integer[] P = stringToArray(entry1.getKey()); //P
                Integer[] PSuf = new Integer[P.length - 1];
                System.arraycopy(P, 1, PSuf, 0, PSuf.length); //获取P后缀
                List<List<Double>> value1 = entry1.getValue();
                List<Double> PLocation = value1.get(0);
                Mat_OPF.LNode PNode = getLNode(PLocation);//p位置
                int group = value1.get(2).get(0).intValue();
                int i = 0;
                if ((group == 1) || (group == 3)) {
                    if (G1 != null)
                        for (Map.Entry<String, List<List<Double>>> entry2 : G1) {  //G1是组1和组2
                            Mat_OPF.LNode QNode = Lb1.get(i);  //Q位置
                            if ( PNode.data >= minsup &&QNode.data >= minsup) {
                                Integer[] Q = stringToArray(entry2.getKey());   //Q
                                Integer[] QPre = new Integer[Q.length - 1];  //获取Q前缀
                                System.arraycopy(Q, 0, QPre, 0, QPre.length);
                                contrast_num++;//前缀后缀比较次数
                                if (Arrays.equals(getOrder(PSuf), getOrder(QPre))) {
                                    patternFusion(P, PNode, Q, QNode, group);//模式融合       组1和组2 的结果
                                }
                            }
                            i++;
                        }
                } else {
                    for (Map.Entry<String, List<List<Double>>> entry2 : G2) {
                        Mat_OPF.LNode QNode = Lb2.get(i);  //Q位置
                        if (PNode.data >= minsup &&QNode.data >= minsup) {
                            Integer[] Q = stringToArray(entry2.getKey());   //Q
                            Integer[] QPre = new Integer[Q.length - 1];  //获取Q前缀
                            System.arraycopy(Q, 0, QPre, 0, QPre.length);
                            contrast_num++;//前缀后缀比较次数
                            if (Arrays.equals(getOrder(PSuf), getOrder(QPre))) {
                                patternFusion(P, PNode, Q, QNode, group);//模式融合
                            }
                        }
                        i++;
                    }
                }
            }
        }
    }

    private static void patternFusion(Integer[] P, Mat_OPF.LNode PNode, Integer[] Q, Mat_OPF.LNode QNode, int group) {
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
          //  Candmap.add(List.of(Cd));
         //   Candmap.add(List.of(Cd2));
            //  System.out.println(Arrays.toString(Cd));
            // System.out.println(Arrays.toString(Cd2));
            candNum += 2;//候选模式++
          //  grow_BaseP2(P.length, QNode, PNode, Cd, Cd2, group);
            matching(Cd,group);
            matching(Cd2,group);
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
            // System.out.println(Arrays.toString(Cd));
            candNum++;
          //  grow_BaseP1(QNode, PNode, Cd, group);
            matching(Cd,group);
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
            //  System.out.println(Arrays.toString(Cd));
          //  grow_BaseP1(QNode, PNode, Cd, group);
            matching(Cd,group);

        }

    }
    public static void matching(Integer[] Cd,  int group) {
        int[] pBinaryArr = getBinaryp(Cd);
        int[] sortedP = new int[pBinaryArr.length];
        System.arraycopy(pBinaryArr, 0, sortedP, 0, sortedP.length);
        Arrays.sort(sortedP);
        int[] aux = new int[pBinaryArr.length];
        genAux(aux, sortedP, pBinaryArr);
        Integer[] subsetNumArr = sbndm(inBinaryArr, pBinaryArr, aux, S);
        List<Double> subsetNumArrNew = verificationStrategy(S, Cd, subsetNumArr, Cd.length);
        judge_fre(Cd, subsetNumArrNew, group);
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

    private static Integer[] stringToArray(String key) {
        key = key.substring(1, key.length() - 1);
        String[] str = key.split(",");
        Integer[] arr = new Integer[str.length];
        for (int i = 0; i < str.length; i++) {
            arr[i] = Integer.valueOf((str[i].trim()));
        }
        return arr;
    }

    private static Mat_OPF.LNode getLNode(List<Double> List) {
        Mat_OPF.LNode PNode = new Mat_OPF.LNode();
        PNode.data = Double.valueOf(List.size());
        Mat_OPF.LNode p = new Mat_OPF.LNode();//p是节点
        Mat_OPF.LNode s = new Mat_OPF.LNode();//s是节点
        s = PNode;
        for (Double val : List) {
            p = new Mat_OPF.LNode();
            p.data = val;
            s.next = p;
            s = p;
        }
        s.next = null;
        return PNode;
    }

    static class LNode {
        Double data;
        Mat_OPF.LNode next = null;
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

    private static List<Double> verificationStrategy(List<Double> in, Integer[] candidateArr, Integer[] subsetNumArr, int plength) {
        List<Double> subsetListNew = new ArrayList<>();
        List<OPP_Miner.SupportOrder> supportOrderList = new ArrayList<>();
        int index = 1;
        for (double order : candidateArr) {
            OPP_Miner.SupportOrder supportOrder = new OPP_Miner.SupportOrder(order, index++);
            supportOrderList.add(supportOrder);
        }
        supportOrderList.sort(Comparator.comparingDouble(OPP_Miner.SupportOrder::getOrder));
        int[] indexArr = new int[supportOrderList.size()];
        int sub = 0;
        for (OPP_Miner.SupportOrder supportOrder : supportOrderList) {
            indexArr[sub++] = supportOrder.getIndex();
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
                subsetListNew.add(Double.valueOf(value + plength));
            }
        }
        Double[] subsetNumArrNew = new Double[subsetListNew.size()];
        subsetListNew.toArray(subsetNumArrNew);

        List<Double> subsetNumList = Arrays.stream(subsetNumArrNew)
                .map(Double::doubleValue)
                .collect(Collectors.toList());

        return subsetNumList;
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

}