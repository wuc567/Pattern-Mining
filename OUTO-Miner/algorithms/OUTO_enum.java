package algorithms;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.*;

import static java.lang.Math.abs;
//2024.7.1在ENUM文件上，进行代码修改，老显示grow_Base问题，修改看

public class OUTO_enum {
    double xishu=10;
    double DTW;//DTW相似度阈值
    double fitt=5;//拟合差阈值
    int minsup=500;//最小支持度阈值
    //1:40, 2:205, 3:380, 4:340, 5:320, 6:500, 7:1030, 8:1220

    public int frequent_num = 0;  //总的频繁保序模式数量
    public int freCount;
    public int OUTOCount=0;

    //候选模式总数
    public int candCount;
    public int fre_num=0;//频繁模式数量
    public int cd_num=2;//候选模式数量
    public int OUTO_num=0; // 异常出现数量




    public static void main(String[] args) {
        //1
        //String fileName = "src/main/java/dataset/Crude Oil.txt";
        //2
        //String fileName = "src/main/java/dataset/1WTl.txt";
        //3
        //String fileName = "src/main/java/dataset/英国布伦特.txt";
        //4
        //String fileName = "src/main/java/dataset/KURIAS-ECG_HeartRate.txt";
        //5
        String fileName = "src/main/java/dataset/顺义PM2.5.txt";
        //6
        //String fileName = "src/main/java/dataset/ChengduPM2.5.txt"; //两个空格
        //7
        //String fileName = "src/main/java/dataset/DOW.txt";
        //8
        //String fileName = "src/main/java/dataset/NYSE.txt";



         // 1改编文件 原始序列长度=2496  fit=2， minsup=500，xishu=2.5
        //String fileName ="src/main/java/dataset/scalability/1k.txt";

        //2文件 原始序列长度= fit=2， minsup=，xishu=
        //String fileName ="src/main/java/dataset/scalability/5k.txt";

        //3文件  原始序列长度= fit=2， minsup=，xishu=
        //String fileName ="src/main/java/dataset/scalability/9k.txt";

        //4文件  原始序列长度= fit=2， minsup=，xishu=
        //String fileName ="src/main/java/dataset/scalability/13k.txt";

        //5文件 原始序列长度= fit=2， minsup=，xishu=
        //String fileName ="src/main/java/dataset/scalability/17k.txt";

        //6文件 原始序列长度= fit=2， minsup=，xishu=
        //String fileName = "src/main/java/dataset/scalability/21k.txt";

        //7文件  原始序列长度= fit=2， minsup=，xishu=
        //String fileName = "src/main/java/dataset/scalability/25k.txt";

        //8文件  Stock原始序列长度= fit=2， minsup=，xishu= 代码read中for(i<valuestring.length-1)
        //String fileName ="src/main/java/dataset/scalability/29k.txt";

        System.out.println("*********算法 OUTO_enum 开始**************");
        OUTO_enum eop_Miner = new OUTO_enum();
        eop_Miner.readDataPointsFromFile(fileName);
    }

        private void readDataPointsFromFile(String fileName) {
            long begintime = System.currentTimeMillis();
            File file = new File(fileName);
            L = new ArrayList<>();//存放每次生成的频繁模式
            Lc=new ArrayList<>();
            Z = new ArrayList<>(); //存放本次生成的末位数组
            Cd = new ArrayList<>(); //存放本次生成的模式
            Cd2 = new ArrayList<>(); //存放本次生成的模式
            S = new ArrayList<>();
            frequent_num = 0;  //总的频繁模式数量
            fre_num = 0;
            cd_num = 2;//候选模式数量

            try (BufferedReader br = new BufferedReader(new FileReader(file))) {
                String line;
                while ((line = br.readLine()) != null) {
                    if (line.isEmpty() == true
                            || line.charAt(0) == '#' || line.charAt(0) == '%'
                            || line.charAt(0) == '@') {
                        continue;
                    }
//              String[] valueStr = line.trim().split(",");
//				String[] valueStr = line.trim().split("	");
                    String[] valueStrings = line.split(" ");
                    double[] inS = new double[valueStrings.length];

                    //初始数据列表
                    List<Double> rawdataTemp = new ArrayList<>();


                    //提取极值点的列表
                    List<Double> extremepointsTemp = new ArrayList<>();
                    List<Integer> extremepointsTempIndex = new ArrayList<>();

                    //最终关键点集合
                    List<Double> finalextremepointsTemp = new ArrayList<>();
                    List<Integer> finalextremepointsTempIndex = new ArrayList<>();


                    //rawdataTemp存储的是一行数据
                    //valueStrings.length是每行数据个数
                    //使用逗号,分割该行数据到valueStrings数组中。
                    //将每个字符串转换为Double类型，并添加到rawdataTemp列表中。
                    for (int i = 0; i < valueStrings.length; i++) {
                        String value = valueStrings[i].trim(); // 去除字符串两端的空白字符
                        if (!value.isEmpty()) {
                            inS[i] = Double.parseDouble(value);
                            rawdataTemp.add(Double.parseDouble(valueStrings[i]));
                        }
                    }


                    extremepointsTempIndex = extractExtremePoints(inS);

                    boolean hasnewExtremePoints = true;
                    int i = 0;
                    List<Double> newExtremePoint = null;
                    List<Integer> newExtremePointIndex = null;

                    for (Integer extremepointindex : extremepointsTempIndex) {
                        finalextremepointsTempIndex.add(extremepointindex);
                    }
                    //此处只输出了一条序列的极值点
                    while (hasnewExtremePoints && i < extremepointsTempIndex.size() - 1) {
                        //  System.out.println("main中极值点个数"+extremepointsTempIndex.size());
//                    hasnewExtremePoints = false;

                        int startIndex = extremepointsTempIndex.get(i);
                        int endIndex = extremepointsTempIndex.get(i + 1);

                        double startValue = rawdataTemp.get(startIndex);
                        double endValue = rawdataTemp.get(endIndex);

                        //执行递归和拟合
                        newExtremePointIndex = recursiveFit(rawdataTemp, extremepointsTempIndex, startIndex, endIndex, startValue, endValue);

                        if (!newExtremePointIndex.isEmpty()) {
                            // 如果有新的极值点添加到列表中，更新标志位
                            hasnewExtremePoints = true;

                        }
                        for (Integer index : newExtremePointIndex) {
                            finalextremepointsTemp.add(rawdataTemp.get(index));
                            finalextremepointsTempIndex.add(index);
                        }
                        i++;
                    }
                    //对每行关键点的位置索引从小到大排序
                    List<Integer> B = new ArrayList<>();
                    for (Integer data : finalextremepointsTempIndex) {
                        B.add(data);
                        Collections.sort(B);
                    }

                    List<Double> A = new ArrayList<>();
                    for (Integer b : B) {
                        S.add(rawdataTemp.get(b));
                        A.add(rawdataTemp.get(b));
                    }
                    //   System.out.println("A: " + A);//A是单条序列

                    S=A;
                    //3.线性拟合递归提取

                    //4. 最大拟合差
                    System.out.println("S个数: "+S.size()+"  :"+S.get(0));
                    double ddtw=calculateVariance(S);
                    DTW=xishu*ddtw;

                    System.out.println("DTW: "+DTW);
                    //System.out.println("S: "+S);

                    runAlgorithm(S);

                    //fre_lop_num = 0; // 总的频繁异常保序模式数量
                    Cd = new ArrayList<>(); //存放本次生成的模式
                    freCount += frequent_num;
                    candCount += cd_num;
                    OUTOCount += OUTO_num;

                }
                //fre_lop_num = 0; // 总的频繁异常保序模式数量
                System.out.println("频繁模式的个数是: " + frequent_num);
                System.out.println("候选模式的个数是: " + cd_num);
                System.out.println("异常出现的个数是: " + OUTO_num);


                long endtime = System.currentTimeMillis();
                MemoryLogger.getInstance().checkMemory();
                /** memory of last execution */
                double maxMemory = MemoryLogger.getInstance().getMaxMemory();
                MemoryLogger.getInstance().reset();
                System.out.println("Maximum memory usage : " + maxMemory + " mb.");
                System.out.println("The time-consuming: " + (endtime - begintime) + "ms.");
            } catch (IOException e) {
                System.err.println("无法读取文件: " + fileName);
                e.printStackTrace();
            }
        }


        private  List<Integer> extractExtremePoints(double[] in) {
            List<Double> list1 = new ArrayList<>();

            //存储每条序列的极值点在原数据中的位置索引
            List<Integer> list1index = new ArrayList<>();

            list1.add(in[0]);
            list1index.add(0);
            for (int i = 1; i < in.length - 1; i++){
                //极值点在rawdataTemp的位置索引是i
                if ((in[i] >= in[i - 1] && in[i] > in[i + 1]) || (in[i] > in[i - 1] && in[i] >= in[i + 1])){
                    list1.add(in[i]);
                    list1index.add(i);
                } else if ((in[i] <= in[i - 1] && in[i] < in[i + 1]) || (in[i] < in[i - 1] && in[i] <= in[i + 1])){
                    list1.add(in[i]);
                    list1index.add(i);
                }
            }
            if (!list1.contains(in[in.length - 1])) {
                list1.add(in[in.length - 1]);
                list1index.add(in.length - 1);
            }
            //System.out.println("位置索引"+list1index);

            return list1index;
        }



        //单条序列中相邻两个极值点之间的，判断有无新的极值点,返回新的点的位置索引
        private  List<Integer> recursiveFit(List<Double> rawdataTemp,List<Integer> extremepointsTempIndex,int startIndex, int endIndex,double startValue,double endValue) {
            List<Double> newExtremePoint = new ArrayList<>();
            double data=-1;
            List<Integer> newExtremePointIndex = new ArrayList<>();
            int index=-1;

            double maxfitabsValue = 0.0;
            int maxFitIndex = -1;

            if (endIndex - startIndex <= 1) {
                // 停止拟合
                return newExtremePointIndex;
            }
//        System.out.println("区间[" + "s" + startIndex + "," + "s" + endIndex + "]拟合值:");


            for (int j = startIndex + 1; j < endIndex; j++) {
                double fitDataValue = linearInterpolation(j, startIndex, endIndex, startValue, endValue);
                double originalDataValue = rawdataTemp.get(j);


                double fitAbsValue = Math.abs(fitDataValue - originalDataValue);

                if (fitAbsValue >=fitt && fitAbsValue >= maxfitabsValue) {
                    // 如果拟合差大于阈值且大于当前最大拟合差，更新最大拟合差和索引
                    maxfitabsValue = fitAbsValue;
                    maxFitIndex = j;
                    data = originalDataValue;
                    index = maxFitIndex;
                }
//            System.out.print("[s" + j + "]:" + fitDataValue + "  ");
////            System.out.println("原始值："+ originalDataValue);
//            System.out.println("拟合差[s" + j + "]:" + fitAbsValue);
            }

            //System.out.println();

            if (maxFitIndex != -1) {
                // 找到大于阈值且最大拟合差的点，将其添加到新的极值点列表中
                newExtremePoint.add(rawdataTemp.get(index));
                newExtremePointIndex.add(index);
            }

            if (maxFitIndex == -1) {
                return newExtremePointIndex;
            }

            return newExtremePointIndex;
        }


        private static double linearInterpolation(int currentIndex, int startIndex, int endIndex, double startValue,
        double endValue) {
            double t = (double) (currentIndex - startIndex) / (endIndex - startIndex);
            return startValue + t * (endValue - startValue);
        }


    List<Integer> Z = new ArrayList<>();//存放本次生成的末尾数组
    List<Double> S = new ArrayList<>();
    List<List<Integer>> L = new ArrayList<>();//存放每次生成的频繁保序模式
    List<List<Integer>> L_index = new ArrayList<>(); // 频繁模式索引下标集合

    List<List<Integer>> Fre = new ArrayList<>();//存放每次生成的z最大频繁保序模式
    List<List<Integer>> Fre_index = new ArrayList<>(); // 最大频繁模式索引下标集合

    List<List<Integer>> Lc = new ArrayList<>(); // 长度为m的模式集合
    List<List<Integer>> Lc_index = new ArrayList<>(); // 长度为m的索引下标集合

    List<Integer> Cd = new ArrayList<>(); //存放本次生成的候选模式
    List<Integer> Cd2 = new ArrayList<>(); //存放本次生成的候选模式



        static class LNode {
            int data;
            LNode next = null;
            boolean flag = false;

        }


    /**
     * 从2-长度模式开始计算支持度
     * 找对频繁保序模式，进而找到异常保序模式出现
     */
    public void find(List<Double> s){
        boolean oop1=false;
        boolean oop2=false;
        int i = 0, j = 1;
        Cd.add(1);
        Cd.add(2);
        Cd2.add(2);
        Cd2.add(1);
        List<Integer> Z = new ArrayList<>();
        List<Integer> Z2 = new ArrayList<>();

        List<Integer> Cdtemp = new ArrayList<>();
        for (Integer integer : Cd) {
            Cdtemp.add(integer);
        }

        List<Integer> Cdtemp2 = new ArrayList<>();
        for (Integer integer : Cd2) {
            Cdtemp2.add(integer);
        }
        Lc.add(Cdtemp);
        Lc.add(Cdtemp2);

        //System.out.println("LC:  "+Lc);
        //S是一条序列
        while (j < s.size()) {
            if (s.get(j) > s.get(i))   //12模式
            {
                Z.add(j);
            } else if (s.get(j) < s.get(i))                //21模式
            {
                Z2.add(j);
            }
            i++;
            j++;
        }
        Lc_index.add(Z);
        Lc_index.add(Z2);
        //支持度是Z.size()和Z2.size()
       // System.out.println("find函数中Z个数:"+Z.size());
        //System.out.println("Lc_index:  "+Lc_index);

        oop1=judge_freoop(Z.size(),Cd,Z);
        Cd.clear();
        oop2=judge_freoop(Z2.size(),Cd2,Z2);
        Cd2.clear();
    }


    public int[] sort(List<Integer> src) {
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


    /**
     * 对应模式融合的一般情况，只生成一个候选模式
     * @param Ld 后缀模式集
     * @param L 前缀模式集
     * @return 当前模式是否加入了候选集
     */
    public boolean grow_BaseP1(List<Integer> Ld, List<LNode> L) {
        int size=Ld.size();
        int m=0;
        boolean oop1=false;
        //记录模式索引
        List<Integer> Z = new ArrayList<>();

        for (int i = 0; i < L.size(); i++) {
            LNode p = L.get(i);

            while(p.next != null && m < size){
                if (Ld.get(m) == p.next.data + 1) {
                    Z.add(Ld.get(m));
                    p.next = p.next.next;
                    m++;
                } else if(p.next.data < Ld.get(m)){
                    p = p.next;
                }else {
                    m++;
                }
            }
            L.get(i).data = L.get(i).data - Z.size();
        }
//        Lc.add(Cd);
        Lc_index.add(Z);

        oop1=judge_freoop(Z.size(), Cd, Z);
        return oop1;
    }

    public boolean grow_BaseP2(int slen, List<Integer> Ld, List<LNode> L, int flag, boolean opp) {
        //List<Integer> Ld =COPP_enum中的q
        List<Integer> Z = new ArrayList<>();//索引集合从0开始
        int m=0;
        int size=Ld.size();
        int lst, fri;
        for (int i = 0; i < L.size(); i++) {
            // p为前缀，q为后缀
            LNode p = L.get(i);
            while (p.next != null && m < size) {

                if (Ld.get(m) == p.next.data + 1) {

                    lst = Ld.get(m);
                    fri = lst - slen;

                    if (flag == 1) {
                        //有筛选
                        if (S.get(lst) > S.get(fri)){
                            Z.add(Ld.get(m));
                            p.next = p.next.next;
                        }
                    } else if (S.get(lst) < S.get(fri)) {
//                        System.out.println("S.get(lst):  "+S.get(lst)+"  S.get(fri): "+S.get(fri));
                        Z.add(Ld.get(m));
                        //System.out.println("Z: "+Z.get(0));
                        p.next = p.next.next;
                    }
                    m++;
                } else if (p.next.data < Ld.get(m)) {
                    p = p.next;
                } else {
                    m++;
                }
            }
            L.get(i).data = L.get(i).data - Z.size();
        }
//        Lc.add(Cd);
        Lc_index.add(Z);

        // System.out.println("grow_BaseP2():  "+Cd);
        opp=judge_freoop(Z.size(),Cd,Z);
      //  System.out.println("grow_BaseP2():  "+Z.size());

        return opp;
    }


    //枚举法生成候选模式
    private void patternEnum() {//P模式，pList位置索引
        int slen;
        List<Integer> Q = new ArrayList<>();
        List<Integer> R = new ArrayList<>();
        List<List<Integer>> Ld = new ArrayList<>();//频繁模式
        List<List<Integer>> Ld_index = new ArrayList<>();//频繁模式索引

        List<List<Integer>> Lcd = new ArrayList<>();//长度m模式
        List<List<Integer>> Lcd_index = new ArrayList<>();//长度m模式索引

        List<LNode> Lb = new ArrayList<>();

        int[] q = new int[256];
        int[] r = new int[256];

        int fre_number = 0;

        //模式
        for (List<Integer> Ltemp : L) {
            List<Integer> fretemp = new ArrayList<>();
            for (Integer integer : Ltemp) {
                fretemp.add(integer);
            }
            Ld.add(fretemp);
        }
        L.clear();
        //System.out.println("enum频繁:  "+Ld);

        //长度m模式
        for (List<Integer> Ltemp : Lc) {
            List<Integer> fretemp = new ArrayList<>();
            for (Integer integer : Ltemp) {
                fretemp.add(integer);
            }
            Lcd.add(fretemp);
        }
        Lc.clear();
        //System.out.println("enum长度m模式:  "+Lcd);

        //索引
        for (List<Integer> index : L_index) {
            Ld_index.add(index);
        }
        L_index.clear();
        //System.out.println("enum频繁索引:  "+Ld_index);

        //长度m索引
        for (List<Integer> index : Lc_index) {
            Lcd_index.add(index);
        }
        Lc_index.clear();
        //System.out.println("enum长度m索引:  "+Lcd_index);



        fre_number = fre_num;
        fre_num = 0;
        while (Lb.size() < fre_number) {
            Lb.add(new LNode());
        }


        int i = 0;
        int j = 0;
        int f = 0;
        int k = 0;
        int temp;
        int size = Lcd.size();
        slen = Ld.get(0).size();//模式长度

        while (Cd.size() < slen + 1) {
            Cd.add(0);
        }

        while (i < Ld.size()) {//遍历频繁模式集合

            List<Integer> index=Ld_index.get(i);//第i个索引集合；List<LNode>Lb

            //建立链表List<Integer>类型，对于List<Node>Lb进行添加
            for (int m = 0; m < index.size(); m++) {
                LNode pb;
                LNode qb = new LNode();
                LNode ptem = new LNode();
                ptem.data = index.size();//支持度
                Lb.add(m, ptem);
                qb = Lb.get(m);

                for (int d = 0; d < index.size(); d++) {
                    pb = new LNode();
                    pb.data = index.get(d);
                    qb.next = pb;
                    qb = pb;
                }
                qb.next = null;
            }

            for (temp = 1; temp <= slen + 1; temp++) {
                //生成超模式
                for (j = 0; j < slen; j++) {
                    if (Ld.get(i).get(j) < temp) {
                        Cd.set(j, Ld.get(i).get(j));
                    } else {
                        Cd.set(j, Ld.get(i).get(j) + 1);
                    }
                }
                Cd.set(slen, temp);
              // System.out.println("模式:  "+Cd);
                List<Integer> Cdtemp = new ArrayList<>();
                for (Integer integer : Cd) {
                    Cdtemp.add(integer);
                }
                Lc.add(Cdtemp);
               // System.out.println("Lc:  "+Cd.get(0)+" "+Cd.get(1)+" "+Cd.get(2));
                cd_num = cd_num + 1;

                // 求后缀
                Q = Cd.subList(1, Cd.size());
                q = sort(Q);
                for (k = 0; k < size; k++) {
                    r = sort(Lcd.get(k));
                    boolean oop = false;

                    //相对顺序相同
                    if (Arrays.equals(q, r)) {
                        // System.out.println("duid ");
                        // 一样
                        if (Ld.get(i).get(0) != Lcd.get(k).get(slen-1)) {
                            // System.out.println("A:  "+Ld.get(i).get(0)+"  B:  "+Lcd.get(k).get(slen - 1));
                            oop=grow_BaseP1(Lcd_index.get(k), Lb);
                            //System.out.println("enum:  "+Lcd_index.get(k));
                        } else {
                            if (Cd.get(0) < Cd.get(slen)) {
                                //  System.out.println("A1:  "+Ld.get(i).get(0)+"  B:  "+Lcd.get(k).get(slen - 1));
                                oop= grow_BaseP2(slen,Lcd_index.get(k),Lb,1,oop);
                            } else {
                                // System.out.println("2:  "+Ld.get(i).get(0)+"  B:  "+Lcd.get(k).get(slen - 1));
                                oop= grow_BaseP2(slen,Lcd_index.get(k),Lb,2,oop);
                                // System.out.println("GR完成");

                            }

                        }
                    }
                }
            }
            i++;
        }

    }

    //判断是否是频繁保序模式，模式支持度为sup_num,模式Cd,对应位置索引Z
    private boolean judge_freoop(int sup_num, List<Integer> Cd, List<Integer> Z) {
        // TODO Auto-generated method stub
        boolean oop_fre = false;

        //System.out.println("sup_num: "+ Z.size());
        if(sup_num>=minsup){
            List<Integer> Ztemp = new ArrayList<>();
            for (Integer integer : Z) {
                Ztemp.add(integer);
            }
            L_index.add(Ztemp);
            Fre_index.add(Ztemp);

            List<Integer> Cdtemp = new ArrayList<>();
            for (Integer integer : Cd) {
                Cdtemp.add(integer);
            }
            L.add(Cdtemp);
            Fre.add(Cdtemp);
            //System.out.println("fre中Cd："+Fre);

            //System.out.print("频繁模式：");
            for (Integer Cdint : Cd) {
                //System.out.print(Cdint + " ");
            }
            // System.out.print("      支持度为：" + sup_num);
            //System.out.println();
//            System.out.print("在字符串中出现的位置：");
//            for (Integer Zint : Z) {
//                System.out.print(Zint + "  ");
//            }
            //System.out.println(Z.size());
            // 此时才可以作为频繁候选模式，保留下来
            oop_fre=true;
            frequent_num++;
            // System.out.println("frequent_num: "+frequent_num++);
            //  System.out.println("频繁模式: "+L);
            fre_num++;
        }

        return oop_fre;
    }

    //判断是否是最大频繁保序模式，模式支持度为sup_num,模式Cd,对应位置索引Z
    private List<List<Integer>> judge_maxfreoop(List<List<Integer>>Fre,List<List<Integer>>Fre_index) {
        List<Integer> Q = new ArrayList<>();
        List<Integer> R = new ArrayList<>();
        int[] q = new int[256];
        int[] r = new int[256];

        for (int l =0;l<Fre.size(); l++) {
            // 求后缀
            Q = Fre.get(l).subList(1, Fre.get(l).size());
            q = sort(Q);
            List<Integer> qList = new ArrayList<>();
            for (int i : q) {
                qList.add(i); // 自动装箱
            }
            //System.out.println("集合中模式后缀: "+qList);

            List<Integer> rList = new ArrayList<>();
            // 求前缀
            R = Fre.get(l).subList(0, Fre.get(l).size() - 1);
            r = sort(R);
            for (int i : r) {
                rList.add(i); // 自动装箱
            }

            Iterator<List<Integer>> iterator = Fre.iterator();
            Iterator<List<Integer>> iterator_index = Fre_index.iterator();
            while (iterator.hasNext()) {
                List<Integer> pattern = iterator.next();
                List<Integer> pattern_index = iterator_index.next();
                if (qList.equals(pattern) || rList.equals(pattern)) {
                    iterator.remove();
                    iterator_index.remove();
                }
            }

        }

        return Fre;
    }




    //@param Cd 本轮生成的候选模式，且频繁
    //*@param Z 索引集合
    //outlying pattern,判断每个频繁保序模式，其是否存在异常出现出现
    private void judge_OUTO(List<Integer> Cd, List<Integer> Z) {
        int number = 0;

        List<Double> subSequence = new ArrayList<>();//存储单个子序列
        List<List<Double>> SequenceList = new ArrayList<>();//存储所有子序列
        List<Double> means = new ArrayList<>();//存储所有均值
        List<Double> meanss = new ArrayList<>();//存储所有均值
        List<Double> de = new ArrayList<>();//存储所有标准差
        List<Double> des = new ArrayList<>();//存储所有标准差

        // Step 1: 提取所有子序列均值
        for (Integer endIndex : Z) {
            for (int k = 1; k <= Cd.size(); k++) {
                //index 是第一个子序列在S中的初始位置（首位）索引
                int index = endIndex - Cd.size() + k;
                double a = S.get(index);
                subSequence.add(a);
            }
            double mean =calculateMean(subSequence);
            double devation=calculateVariance(subSequence);
            means.add(mean);
            meanss.add(mean);
            de.add(devation);
            des.add(devation);
            SequenceList.add(new ArrayList<>(subSequence));
            subSequence.clear();
        }

        //System.out.println("子序列集合： "+SequenceList);

        // Step 2: 计算均值四分位数和四分位距
        double mQ1 = calculatePercentile(means, 25);
        double mQ3 = calculatePercentile(means, 75);
        double mIQR = 1.5*(mQ3 - mQ1);

        //计算标准差四分位数和四分位距
        double dQ1 = calculatePercentile(de, 25);
        double dQ3 = calculatePercentile(de, 75);
        double dIQR = 1.5*(dQ3 - dQ1);


        // Step 4: 判断每个子序列均值是否在区间内，如果不在区间内，则与其他子序列进行DTW计算
        for (int i = 0; i < SequenceList.size(); i++) {

            double mean = meanss.get(i);
            double devation =des.get(i);
            //System.out.println("均值： "+mean);

            //均值判断是否可能为OUTO
            if (!isWithinBounds(mean, mQ1 - mIQR, mQ3 + mIQR)||
                    (isWithinBounds(mean, mQ1 - mIQR, mQ3 + mIQR)&&!isWithinBounds(devation, dQ1 -dIQR, dQ3 + dIQR))) {

                int num =0;
                List<Double> A = SequenceList.get(i);
                // System.out.println("异常子序列： "+A);
                num++;

                for (int j = 0; j < SequenceList.size(); j++) {
                    if (i != j) {
                        List<Double> B = SequenceList.get(j);
                        double dtw = calculateDTWDistance(A, B);
                        // System.out.println("DTW(" + A + ", " + B + ") = " + dtw);

                        if (dtw >= DTW) {
                            // System.out.println("A:   "+A+"B:   "+B+"dtw:   "+dtw);
                            number++;
                            // System.out.println("number:   " + number);
                        }
//                        B.clear();
                    }
                }
                if (number >= Math.ceil(Z.size() * 0.8)) {
                    // System.out.println("Z.size: "+Z.size()+"    "+Math.ceil((Z.size()+1) / 2));
                    // 序列被认为是异常模式序列
                    //      System.out.println("是异常保序模式");
                    List<List<Double>> lop = new ArrayList<>();
                    OUTO_num++;
                    List<Integer> lop_num = new ArrayList<>();
                    // System.out.println("异常出现数量：" + OUTO_num);

                } else {
                    //System.out.println("不是异常保序模式");
                }
                number = 0;

            }
        }

    }

    public boolean isWithinBounds(double value, double lowerBound, double upperBound) {
        return value >= lowerBound && value <= upperBound;
    }



    // 计算均值
    public double calculateMean(List<Double> list) {
        double sum = 0;
        for (double num : list) {
            sum += num;
        }
        return sum / list.size();
    }

    // 计算百分位数
    public double calculatePercentile(List<Double> sortedList, double percentile) {
        Collections.sort(sortedList);
        int index = (int) Math.ceil(percentile / 100.0 * sortedList.size()) - 1;
        return sortedList.get(index);
    }

    //计算相同保序模式下两个出现的DTW距离--首先要数据归一化
    public double calculateDTWDistance(List<Double> A, List<Double> B) {
        int i, j;
        double max = 999.0;
        Double a[] = A.toArray(new Double[0]);
        Double b[] = B.toArray(new Double[0]);
        int NUM1 = a.length + 1;// 加1是因为计算是有a[i-1]
        int NUM2 = b.length + 1;// 加1是因为计算是有b[j-1]

        double[][] distance = new double[NUM1][NUM2];
        double[][] output = new double[NUM1][NUM2];

        for (i = 0; i < NUM1; i++) {
            for (j = 0; j < NUM2; j++) {
                distance[i][j] = max;
                output[i][j] = max;
            }
        }
        distance[0][0] = 0;
        output[0][0] = 0;

        for (i = 1; i < NUM1; i++) {
            for (j = 1; j < NUM2; j++) {
                distance[i][j] = Math.abs(b[j - 1] - a[i - 1]); // 计算点与点之间的欧式距离
            }
        }
        // 输出整个欧式距离的矩阵
        for (i = 1; i < NUM1; i++) {
            for (j = 1; j < NUM2; j++) {
                // System.out.print(distance[i][j] + " ");
            }
            //System.out.println();
        }
        //System.out.println("=================================");

        // DP过程，计算DTW距离
        for (i = 1; i < NUM1; i++) {
            for (j = 1; j < NUM2; j++) {
                output[i][j] = Math.min(Math.min(output[i - 1][j - 1], output[i][j - 1]), output[i - 1][j])
                        + distance[i][j];
            }
        }

        // 输出最后的DTW距离矩阵，其中output[NUM1][NUM2]为最终的DTW距离和
        for (i = 1; i < NUM1; i++) {
            for (j = 1; j < NUM2; j++) {
//                System.out.print(output[i][j] + " ");
//            System.out.println();
            }
        }
        return output[NUM1-1][NUM2-1];
    }

    public static double calculateAverage(List<Double> timeSeries) {
        // 计算样本平均值
        double sum = 0;
        for (double value : timeSeries) {
            sum += value;
        }
        double mean = sum / timeSeries.size();
        System.out.println("均值: " + mean);
        return mean;
    }

    public static double calculateVariance(List<Double> timeSeries) {

        double sum = 0;
        for (double value : timeSeries) {
            sum += value;
        }
        double mean = sum / timeSeries.size();

        // 计算每个样本点与平均值的差的平方
        double squaredDiffSum = 0;
        for (double value : timeSeries) {
            squaredDiffSum += Math.pow(value - mean, 2);
        }

        // 计算总体方差
        double variance =squaredDiffSum / (timeSeries.size());

        //标准差
        double svariance=Math.sqrt(variance);
        // System.out.println("标准差: " + svariance);


        return svariance;
    }


    public void runAlgorithm(List<Double> seq) {

        boolean oop_fre = false;
        // 从2长度模式开始计算
        find(seq);
       // System.out.println("find完成");
        while (fre_num > 0) {
            //System.out.println("fre_num:  "+fre_num);
            patternEnum(); // 模式融合策略
            judge_maxfreoop(Fre,Fre_index);
//            System.out.println("模式:  "+Lc);
//            System.out.println("频繁模式:  "+L);
            // System.gc();
        }


//        judge_maxfreoop(Fre);
        for (int i = 0; i < Fre.size(); i++) {
            List<Integer> pattern = Fre.get(i);
            List<Integer> pattern_index = Fre_index.get(i);
            // System.out.println("pattern:  "+pattern+"   "+pattern_index);
            judge_OUTO(pattern,pattern_index);
        }

        System.out.println("Fre:  "+Fre.size());
//        System.out.println("Fre:  "+Fre+"   "+Fre_index);

    }
}

