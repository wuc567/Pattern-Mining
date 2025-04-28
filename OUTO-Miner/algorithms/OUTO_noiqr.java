package algorithms;
//2024.4.2  不分组模式融合成功找出异常发现!!! 坚决不能动
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.*;
import static java.lang.Math.abs;

//2024.5.16 线性拟合+无最大频繁模式+无箱线图+OUTO检测

public class OUTO_noiqr {

    public int frequent_num = 0;  //总的频繁保序模式数量
    public int freCount;
    public int OUTOCount=0;

    //候选模式总数
    public int candCount;
    public int fre_num=0;//频繁模式数量
    public int cd_num=2;//候选模式数量
    public int OUTO_num=0; // 异常出现数量


    List<List<Integer>> L = new ArrayList<>();//存放每次生成的频繁模式
    List<List<Integer>> P = new ArrayList<>();//存放所有频繁模式的末位索引

    List<Integer> Z = new ArrayList<>();//存放本次生成的末尾数组
    List<Integer> Z2 = new ArrayList<>();

    // 模式融合可能会生成两个超模式
    List<Integer> Cd = new ArrayList<>(); //存放本次生成的候选模式
    List<Integer> Cd2 = new ArrayList<>();

    List<Double> Seq = new ArrayList<>();//序列
    List<Double> S = new ArrayList<>();

    double COS = 0.9;  // 余弦距离阈值
    double xishu=2.5;

    double DTW;//DTW相似度阈值

   double fitt=5;//拟合差阈值
    int minsup=500;//最小支持度阈值
    //1:40, 2:205, 3:380, 4:340, 5:320, 6:500, 7:1030, 8:1220

    //D(Q)个数>0.8sup()

    public static void main(String[] args){
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



        // 1文件 原始序列长度=2496  fit=2， minsup=500，xishu=2.5
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

        //8文件  Stock原始序列长度= fit=2， minsup=，xishu=
        //String fileName ="src/main/java/dataset/scalability/29k.txt";

        System.out.println("*********算法 EOPP_Miner 开始**************");
        OUTO_noiqr eop_Miner = new OUTO_noiqr();
        eop_Miner.readDataPointsFromFile(fileName);
    }

    class LNode{
        int data;
        LNode next = null;
    }


    //1. 读取文件
    private void readDataPointsFromFile(String fileName) {
        long begintime = System.currentTimeMillis();
        File file = new File(fileName);
        P = new ArrayList<>(); //存放末位的数组
        L = new ArrayList<>();//存放每次生成的频繁模式
        Z = new ArrayList<>(); //存放本次生成的末位数组
        Z2 = new ArrayList<>();
        Cd = new ArrayList<>(); //存放本次生成的模式
        Cd2 = new ArrayList<>();
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
                // System.out.println(valueStrings.length);

//                System.out.println(rawdataTemp);
//                rawdataTemp.size()是每行包含的数据个数
//                System.out.println(rawdataTemp.size());

                extremepointsTempIndex = extractExtremePoints(inS);

                boolean hasnewExtremePoints = true;
                int i = 0;
                List<Double> newExtremePoint = null;
                List<Integer> newExtremePointIndex = null;

                for (Integer extremepointindex : extremepointsTempIndex) {
                    finalextremepointsTempIndex.add(extremepointindex);
                    finalextremepointsTemp.add(rawdataTemp.get(extremepointindex));
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
                //对单条序列进行频繁保序模式判断

                double ddtw=calculateVariance(S);
                DTW=xishu*ddtw;
                System.out.println("DTW: "+DTW);
                runAlgorithm(S);


                //fre_lop_num = 0; // 总的频繁异常保序模式数量
                Cd = new ArrayList<>(); //存放本次生成的模式
                Cd2 = new ArrayList<>();
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
//            System.out.println("拟合位置索引"+j);
//            System.out.println("拟合值"+fitDataValue);
//            System.out.println("原始数值"+originalDataValue);
//            System.out.println();

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
//            System.out.println("最大拟合差位置：[s" + maxFitIndex+"]");

//            System.out.print("新的极值点[s" + rawData.get(maxFitIndex - 1).getPositionIndex() + "]:" + rawData.get(maxFitIndex - 1).getValue());

//            Double maxFitDataPoint = rawdataTemp.get(maxFitIndex);
//            newExtremePoint.add(new Double(maxFitDataPoint));

            // 递归处理左子区间
//            System.out.println("左区间:");
            newExtremePointIndex.addAll(recursiveFit(rawdataTemp, extremepointsTempIndex, startIndex, maxFitIndex, startValue, rawdataTemp.get(maxFitIndex)));
//                    System.out.println("新的极值点[s" + maxFitIndex + "]:" + rawData.get(maxFitIndex - 1).getValue());

            // 递归处理右子区间
//            System.out.println("右区间：");
            newExtremePointIndex.addAll(recursiveFit(rawdataTemp, extremepointsTempIndex, maxFitIndex, endIndex, rawdataTemp.get(maxFitIndex), endValue));
//                    System.out.println("新的极值点[s" + rawData.get(maxFitIndex - 1) + "]:" + rawData.get(maxFitIndex - 1).getValue());

        }

        if (maxFitIndex == -1) {
            return newExtremePointIndex;
        }
        //System.out.println("新的极值点[s" + maxFitIndex + "]:" + rawdataTemp.get(maxFitIndex - 1));
        //System.out.println("1新的极值点位置索引:" +newExtremePointIndex);
        //System.out.println("recursive函数中新的极值点:" +newExtremePoint);
        //System.out.println();
        return newExtremePointIndex;
    }


    private static double linearInterpolation(int currentIndex, int startIndex, int endIndex, double startValue,
                                              double endValue) {
        double t = (double) (currentIndex - startIndex) / (endIndex - startIndex);
        return startValue + t * (endValue - startValue);
    }

    /**
     * 计算模式的相对顺序
     * @param src
     * @return
     */
    public int[] sort(List<Integer> src){
        int k, slen = 0;
        int level = 1;

        slen = src.size();
        int[] sort_array = new int[slen];
        for(int i = 0 ; i < slen ; i++)
        {
            k = src.get(i);
            for(int x = 0;x < slen;x++)
            {
                if(k > src.get(x))
                {
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
     * @return 当前模式是否加入了候选集，如果加入了才计算负类
     */
    public void grow_BaseP1(LNode Ld, LNode L) {
        boolean oop1=false;
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
        }

        L.data = L.data - Z.size();
        Ld.data = Ld.data - Z.size();
        oop1=judge_freoop(Z.size(), Cd, Z);
        if(oop1){
            judge_OUTO(Cd,Z);
        }
        //System.out.println("grow_BaseP1算法： "+Cd);
    }

    /**
     * 对应模式融合的特殊情况，生成两个超模式
     * @param slen 上一个模式长度，为了计算first last
     * @param Ld 后缀模式集
     * @param L 前缀模式集
     * @return
     */
    public void grow_BaseP2(int slen, LNode Ld,LNode L){
        boolean oop1=false;
        boolean oop2=false;
        int lst, fri;
        LNode p = L;
        LNode q = Ld;
        Z.clear();
        Z2.clear();
        while (p.next != null && q.next != null) {
            if (q.next.data == p.next.data + 1) {
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
        }

        L.data = L.data - Z.size() - Z2.size();
        Ld.data = Ld.data - Z.size() - Z2.size();

        // 判断模式Cd是否加入候选集
        oop1=judge_freoop(Z.size(),Cd,Z);
        if(oop1){
            judge_OUTO(Cd,Z);
        }
        oop2=judge_freoop(Z2.size(),Cd2,Z2);
        if(oop2){
            judge_OUTO(Cd2,Z2);
        }
        // System.out.println("grow_BaseP2算法： "+Cd);//第四处
    }

    /**
     * 模式融合策略
     * @return
     */
    public int generate_fre() {
        boolean oop1=false;
        boolean oop2=false;
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

                    boolean oop_fre=false;

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
                            cd_num = cd_num + 1;
                            grow_BaseP1(Lb.get(j), L);
                        }
                    }
                }
            }

        }
        //System.out.println("generate_fre算法完成");
        return 0;
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
            P.add(Ztemp);

            List<Integer> Cdtemp = new ArrayList<>();
            for (Integer integer : Cd) {
                Cdtemp.add(integer);
            }
            L.add(Cdtemp);

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
            //System.out.println("frequent_num: "+frequent_num++);
            fre_num++;
        }
        return oop_fre;
    }

    //@param Cd 本轮生成的候选模式，且频繁
    //*@param Z 索引集合
    //outlying pattern,判断每个频繁保序模式，其是否存在异常出现出现
    private void judge_OUTO(List<Integer> Cd, List<Integer> Z) {
        int number = 0;
        //double Cos = 0.9;  // 余弦距离阈值

        // 模式的支持度 Z.size   模式长度 Cd.size()
        //< Z.size(),子序列两两比较； 从第一个出现开始比较
        //模式从长度3的模式开始寻找异常出现

        //i 循环，遍历所有出现子序列，两两比较
        for (int i = 0; i < Z.size(); i++) {
            // System.out.println("模式：" + Cd);

            //app1就是单条序列中第一次出现,末位位置索引   Z中索引从0开始计算
            Integer app1 = Z.get(i);
            double app1value=S.get(app1-1);

            //calculateCosineDistance()函数就是计算两个出现的余弦距离
            //需要创建两个比较之处的列表，索引从0开始
            //在序列S中，索引从0开始；
            List<Double> A = new ArrayList<>();
            List<Double> B = new ArrayList<>();

            //List<Integer> ZZ 就是单条序列中A不包含当前索引的其他索引集合
            List<Integer> ZZ = new ArrayList<>();
            for (Integer a : Z) {
                if (a != app1) {
                    ZZ.add(a);
                }
            }

            //子序列A要比较ZZ.size()次
            for (int j = 0; j < ZZ.size(); j++) {

                //模式长度为zc.len,出现的数值集合(长度zc.len)
                for (int k = 0; k < Cd.size(); k++) {
                    //index 是第一个子序列在S中的初始位置（首位）索引
                    int index = app1 - Cd.size() + k;
                    double a = S.get(index);
                    A.add(a);

                    //System.out.println("a: "+a);
                    //ZZ.get(k-1)是第二个子序列的末位位置索引
                    // System.out.println("ZZ.get(j): " + S.get(ZZ.get(j)));
                    //index2 是第二个子序列在S中的初始位置索引
                    int index2 = ZZ.get(j) - Cd.size() + k;
                    //System.out.println("index2: " + index2);
                    double b = S.get(index2);
                    // System.out.println("b: " + b);
                    B.add(b);
                }
                //  System.out.println("A:" + A);
                // System.out.println("B:" + B);

                double cos = calculateCosineDistance(A, B);
                double dtw = calculateDTWDistance(A, B);
                // System.out.println("DTW["+A+","+B+"]: "+dtw);
                //System.out.println("cos(" + A + "," + B +"):"+ cos);
//                        if (cos <= COS) {
//                            number++;
//                        }
                if (dtw >= DTW) {
                   // System.out.println("A:   "+A+"B:   "+B+"dtw:   "+dtw);
                    number++;
                    //System.out.println("number:   "+number);
                }

                A.clear();
                B.clear();
            }
            //单个出现x与序列中其他出现的cos值，满足<阈值的个数
            //System.out.println("cos数量：" + number);

            // System.out.println("支持度：" + seq.len / 2);
            //到此为止，是一条序列中，一个固定出现和剩余其他出现的余弦距离遍历完毕
            if (number >= Math.ceil(Z.size() *0.8)) {
                //  System.out.println("Z.size: "+Z.size()+"    "+Math.ceil((Z.size()+1) / 2));
                // 序列被认为是异常模式序列
                //      System.out.println("是异常保序模式");
                List<List<Double>> lop = new ArrayList<>();
                OUTO_num++;
                List<Integer> lop_num = new ArrayList<>();
                // System.out.println("异常出现数量：" + OUTO_num);

            } else {
                //System.out.println("不是异常保序模式");
            }
            number=0;
        }
    }

    // 22.
    //计算相同保序模式下两个出现的余弦距离
    public double calculateCosineDistance(List<Double> A, List<Double> B) {

        // 将 List 转换为数组
        Double[] ss1 = A.toArray(new Double[0]);
        // 将 List 转换为数组

        Double[] ss2 = B.toArray(new Double[0]);

        // 打印数组元素
        double sum = 0;
        double magnitude1 = 0.0;
        double magnitude2 = 0.0;
        double cos = 0.0;

        for (int i = 0; i < ss1.length; i++) {
            sum += ss1[i] * ss2[i];
            magnitude1 += Math.pow(ss1[i], 2);
            magnitude2 += Math.pow(ss2[i], 2);
        }
        magnitude1 = Math.sqrt(magnitude1);
        magnitude2 = Math.sqrt(magnitude2);
        cos = sum / (magnitude1 * magnitude2);


        if (magnitude1 == 0 || magnitude2 == 0) {
            return 0;
        }
        return cos;
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
        System.out.println("标准差: " + svariance);


        return svariance;
    }


    //归一化函数—1  ———线性归一化（max-min归一化）  x'= (x-min)/(max-min)
    private static List<Double> normalize1(List<Double> data) {
        List<Double> normalizedData = new ArrayList<>();
        if(!data.isEmpty()) {
            //找每行的最小值和最大值
            Double min = Collections.min(data);
            Double max = Collections.max(data);

            //归一化数据
            for(int i=0;i<data.size();i++){
                Double Data=(data.get(i) - min)/(max - min);
                normalizedData.add(Data);
            }
        }else{
            System.out.println("该序列为空");
        }
        return normalizedData;
    }

    //归一化函数—2 ——— x'=|x-min|+1
    private static List<Double> normalize2(List<Double> data) {
        List<Double> normalizedData = new ArrayList<>();
        if(!data.isEmpty()) {
            //找每行的最小值和最大值
            Double min = Collections.min(data);
            Double max = Collections.max(data);

            //归一化数据
            for(int i=0;i<data.size();i++){
                Double Data=abs(data.get(i)-min)+1;
                normalizedData.add(Data);
            }
        }else{
            System.out.println("该序列为空");
        }
        return normalizedData;
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
        //S是一条序列
        while (j < s.size()) {
            if (s.get(j) > s.get(i))   //12模式
            {
                Z.add(j + 1);
                //System.out.println("find函数中Z个数:"+Z.size());
            } else if (s.get(j) < s.get(i))                //21模式
            {
                Z2.add(j + 1);
            }
            i++;
            j++;
        }
        //支持度是Z.size()和Z2.size()
        judge_freoop(Z.size(),Cd,Z);
        Cd.clear();
        judge_freoop(Z2.size(),Cd2,Z2);
        Cd2.clear();

    }


    public void runAlgorithm(List<Double> seq) {

        boolean oop_fre = false;
        // 从2长度模式开始计算
        find(seq);
        while (fre_num > 0) {
            generate_fre(); // 模式融合策略

            // System.gc();
        }
    }
}
