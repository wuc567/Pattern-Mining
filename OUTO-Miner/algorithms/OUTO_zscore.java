
package algorithms;

        import java.io.*;
        import java.util.*;

        import static java.lang.Math.abs;

//2025.04.13 OUTO-Miner

public class OUTO_zscore {

    public int frequent_num = 0;  //总的频繁保序模式数量
    public int freCount;
    public int OUTOCount=0;

    //候选模式总数
    public int candCount;
    public int fre_num=0;//频繁模式数量
    public int cd_num=2;//候选模式数量
    public int OUTO_num=0; // 异常出现数量

    private static double[] input;//预处理后的序列
    private static double[] seq;//原始的序列

    List<List<Integer>> L = new ArrayList<>();//存放每次生成的频繁模式
    List<List<Integer>> P = new ArrayList<>();//存放所有频繁模式的末位索引

    List<List<Integer>> Fre = new ArrayList<>();//存放生成的频繁模式集合
    List<List<Integer>> Fre_index = new ArrayList<>();//存放生成的频繁模式集合位置索引
    List<List<Double>> Fre_seq = new ArrayList<>();//存放生成的频繁模式子序列集合

    List<Integer> Z = new ArrayList<>();//存放本次生成的末尾数组
    List<Integer> Z2 = new ArrayList<>();

    // 模式融合可能会生成两个超模式
    List<Integer> Cd = new ArrayList<>(); //存放本次生成的候选模式
    List<Integer> Cd2 = new ArrayList<>();

    List<Double> Seq = new ArrayList<>();//序列
    List<Double> S = new ArrayList<>();
    double[] s;//预处理后的序列

    double COS = 0.9;  // 余弦距离阈值


    double DTW;//DTW相似度阈值
    double Z_SCORE_THRESHOLD=3;
    //文件 1-3
    double fitt=2;//拟合差阈值
    double xishu=5;
    int minsup=100;//最小支持度阈值

//    //文件 4
//    double fitt=2;//拟合差阈值
//    double xishu=5;
//    int minsup=500;//最小支持度阈值

//    //文件 5
//    double fitt=20;//拟合差阈值
//    double xishu=2.5;
//    int minsup=500;//最小支持度阈值

//    //文件 6
//    double fitt=5;//拟合差阈值
//    double xishu=5;
//    int minsup=1000;//最小支持度阈值

//    //文件 7
//    double fitt=20;//拟合差阈值
//    double xishu=10;
//    int minsup=2000;//最小支持度阈值

//    //文件 8
//    double fitt=2;//拟合差阈值
//    double xishu=5;
//    int minsup=2000;//最小支持度阈值

    //D(Q)个数>0.8sup()

    public static void main(String[] args){

        //1 2 500
        //String fileName = "src/main/java/dataset/Crude Oil.txt";
        //2  2  500
        // String fileName = "src/main/java/dataset/1WTl.txt";
        //3  2  500
        //String fileName = "src/main/java/dataset/英国布伦特.txt";
        //4  2  500
        //String fileName = "src/main/java/dataset/KURIAS-ECG_HeartRate.txt";
        //5  20  500
        //String fileName = "src/main/java/dataset/顺义PM2.5.txt";
        //6  5  5 1000
        //String fileName = "src/main/java/dataset/ChengduPM2.5.txt"; //两个空格
        //7  20 10 2000
        //String fileName = "src/main/java/dataset/DOW.txt";
        //8  2 5 2000
        //String fileName = "src/main/java/dataset/NYSE.txt";

        //String fileName = "src/main/java/dataset/electricity.txt";
        //String fileName = "src/main/java/algorithms/recursive";
        //String fileName = "src/main/java/algorithms/text.txt";
       // String fileName = "src/main/java/dataset/study2.txt";
        String fileName ="src/main/java/dataset/ProcessedTravelTime.txt";


        // 1文件 原始序列长度=2496  fit=2， minsup=40，xishu=2.5
        //String fileName ="src/main/java/dataset/scalability/1k.txt";

        //2文件 原始序列长度= fit=2， minsup=205，xishu=
        //String fileName ="src/main/java/dataset/scalability/5k.txt";

        //3文件  原始序列长度= fit=2， minsup=380，xishu=
        //String fileName ="src/main/java/dataset/scalability/9k.txt";

        //4文件  原始序列长度= fit=2， minsup=340，xishu=
        //String fileName ="src/main/java/dataset/scalability/13k.txt";

        //5文件 原始序列长度= fit=2， minsup=320，xishu=
        //String fileName ="src/main/java/dataset/scalability/17k.txt";

        //6文件 原始序列长度= fit=2， minsup=500，xishu=
        //String fileName = "src/main/java/dataset/scalability/21k.txt";

        //7文件  原始序列长度= fit=2， minsup=1030，xishu=
       // String fileName = "src/main/java/dataset/scalability/25k.txt";

        //8文件  Stock原始序列长度= fit=2， minsup=1220，xishu=
        //代码read中for(i<valuestring.length-1)
        //String fileName ="src/main/java/dataset/scalability/29k.txt";



        System.out.println("*********算法 EOPP_Miner 开始**************");
        OUTO_zscore outo_Miner = new OUTO_zscore();
        outo_Miner.readDataPointsFromFile(fileName);
    }


    //1. 读取文件
    private void readDataPointsFromFile(String fileName) {
        String timeOutputFilePath = "src/main/java/dataset/OUTO_z2_running_times.txt";
        String memoryOutputFilePath = "src/main/java/dataset/OUTO_z2_memory_usages.txt";    //!!1

        for (int run = 1; run <= 1; run++) { // 运行35次

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

        try (BufferedReader br = new BufferedReader(new FileReader(file));
            BufferedWriter timeWriter = new BufferedWriter(new FileWriter(timeOutputFilePath, true));
            BufferedWriter memoryWriter = new BufferedWriter(new FileWriter(memoryOutputFilePath, true))) {
                //!!2
            String s;
            List<ExtremePoint> extremePoints=new ArrayList<>();
            //使用readLine方法，一次读一行
            while ((s = br.readLine()) != null) {
                List<Double> inList = new ArrayList<>();
                s = s.trim();
                String[] str = s.split(" ");
                String[] strArr = new String[str.length];
//            System.arraycopy(str, 1, strArr, 0, strArr.length);
                for (int i = 0; i < str.length; i++) {
                    String value = str[i].trim(); // 去除字符串两端的空白字符
                    if (!value.isEmpty()) {
                        inList.add(Double.parseDouble(str[i]));
                    }
                }
                double[] in = new double[inList.size()];
                int m = 0;
                for (double inLine : inList) {
                    in[m++] = inLine;
                }
                System.out.println("原始序列个数："+in.length);
                seq=in;


                extremePoints=KeyPointsExtraction(in);
                System.out.println("极值点个数："+extremePoints.size());


                input=findMaxFitDifference(in,extremePoints);
                for(int l=0;l<input.length;l++){
                    S.add(input[l]);
                }

                //4. 最大拟合差
                System.out.println("S个数: "+S.size());
                double ddtw=calculateStandardDeviation(S);
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
//            System.out.println("频繁模式的个数是: " + frequent_num);
//            System.out.println("候选模式的个数是: " + cd_num);
//            System.out.println("异常出现的个数是: " + OUTO_num);


                long endtime = System.currentTimeMillis();
                MemoryLogger.getInstance().checkMemory();
                double runningTime = (endtime - begintime) / 1000.0; // 转换为秒

                // 写入运行时间
                timeWriter.write( runningTime + "\n");

                // 写入内存消耗
                double maxMemory = MemoryLogger.getInstance().getMaxMemory();
                memoryWriter.write( maxMemory + "\n");

                MemoryLogger.getInstance().reset();                //!!3

        } catch (IOException e) {
            System.err.println("无法读取文件: " + fileName);
            e.printStackTrace();
        }
    }
            System.out.println("所有运行完成，结果已写入文件");
        }

    private List<ExtremePoint>  KeyPointsExtraction(double[] input) {
        List<ExtremePoint> extremePoints = new ArrayList<>();

        extremePoints.add(new ExtremePoint(input[0],0));
        for (int i = 1; i < input.length - 1; i++) {
            if ((input[i] >= input[i - 1] && input[i] > input[i + 1]) || (input[i] > input[i - 1] && input[i] >= input[i + 1])){
                extremePoints.add(new ExtremePoint(input[i], i));
            } else if ((input[i] <= input[i - 1] && input[i] < input[i + 1]) || (input[i] < input[i - 1] && input[i] <= input[i + 1])){
                extremePoints.add(new ExtremePoint(input[i], i));
            }
        }
//        if (!extremePoints.contains(input[input.length - 1])) {
//            extremePoints.add(new ExtremePoint(input[input.length-1],input.length-1));
//        }

        return extremePoints;
    }


    // 找到最大拟合差的点
    private double[] findMaxFitDifference(double[] input, List<ExtremePoint> extremePoints) {
        List<Integer> index=new ArrayList<>();
        for(ExtremePoint p:extremePoints){
            index.add(p.index);
        }
        // System.out.println("index: "+index.size());



        for (int i = 0; i < extremePoints.size() - 1; i++) {


            ExtremePoint p1 = extremePoints.get(i);
            ExtremePoint p2 = extremePoints.get(i + 1);
            if(p2.index - p1.index <=1){
                continue;
            }

            if (p2.index - p1.index > 1){

                double maxDeviation = -1;
                int maxDeviationIndex = -1;
                int Index=-1;

                //System.out.println("[" + p1.index + "," + p2.index + "]");
                for (int j = p1.index + 1; j < p2.index; j++) {
                    double t = (double) (j - p1.index) / (p2.index - p1.index);
                    double fittedValue = p1.value + t * (p2.value - p1.value);
                    ;//拟合值
                    double deviation = Math.abs(seq[j] - fittedValue);//拟合差
                    // System.out.println("[" + p1.index + "," + p2.index + "]:  " + j+"值：  " + fittedValue + "  " + deviation);
                    if (deviation >= fitt && deviation >= maxDeviation) {
                        maxDeviation = deviation;
                        //System.out.println("拟合差" + maxDeviation );
                        maxDeviationIndex = j;
                        Index=maxDeviationIndex;
                        //System.out.println(" " + maxDeviationIndex);
                    }
                }
                if(maxDeviationIndex !=-1) {
                    index.add(Index);
                    // System.out.println("  " + Index + "     " + index.size());
                }
                Index=0;
                if(maxDeviationIndex ==-1) {
                    continue;
                }
            }

        }
        Collections.sort(index);

        //System.out.println("d "+index.size());


        // 如果需要，可以在这里添加处理 maxDeviationIndex 的逻辑
        // 例如，可以返回包含 maxDeviationIndex 值的数组

        // 返回极值点数组
        double[] keyextremeValues = new double[index.size()];
        int m=0;
        for(Integer i:index){
            keyextremeValues[m]=input[i];
            m++;
        }
        return keyextremeValues;

    }



    class LNode{
        int data;
        LNode next = null;
    }



    // 辅助类，用于存储极值点及其索引
    static class ExtremePoint {
        double value;
        int index;

        ExtremePoint(double value, int index) {
            this.value = value;
            this.index = index;
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
//        if(oop1){
//            //System.out.println("模式P1: "+Cd+"  Fre:  "+Fre);
//            judge_maxfreoop(Fre);
//            for(List<Integer> max_pattern:Fre){
//                judge_OUTO(Cd,Z);
//            }

        //}
//            judge_OUTO(Cd,Z);
        // }
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

//        // 判断模式Cd是否加入候选集
        oop1=judge_freoop(Z.size(),Cd,Z);
//        if(oop1){
//            judge_maxfreoop(Fre,Fre_index);

//            for(List<Integer> max_pattern:Fre){
//                judge_OUTO(Cd,Z);
//            }

        //     System.out.println("模式P2--: "+Cd+"  Fre:  "+Fre);
//            judge_OUTO(Cd,Z);
        //}
        oop2=judge_freoop(Z2.size(),Cd2,Z2);
//        if(oop2){
//            judge_maxfreoop(Fre,Fre_index);
        //  System.out.println("模式P2---2: "+Cd2+"  Fre:  "+Fre);
//            judge_OUTO(Cd2,Z2);

//            for(List<Integer> max_pattern:Fre){
//                judge_OUTO(Cd,Z);
//            }
//        }
        // System.out.println("grow_BaseP2算法： "+Cd);//第四处
    }

    /**
     * 模式融合策略
     * @return
     */
    public int generate_fre() {
//        boolean oop1=false;
//        boolean oop2=false;
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
//            Fre.add(fretemp);
        }
//System.out.println("S:  "+fre);
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
//            Fre_index.add(postemp);
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

            int count=0;//判断fre.get(i)是否为最大频繁保序模式
            for (j = 0; j < fre_number; j++) {
                //有剪枝
                if (L.data >= minsup && Lb.get(j).data >= minsup) {

                    // 求前缀
                    R = fre.get(j).subList(0, fre.get(j).size() - 1);
                    r = sort(R);



//大循环从i开始，对于模式fre.get(i),其要遍历fre中其他频繁模式fre.get(j)，
// 当生成超模式Cd，Cd2不频繁时候，记数count+1;当i=0j遍历完后，若count=0，说明模式fre.get(i)没有生成任何频繁模式，此时就是最大频繁保序模式

                    //前后缀相对顺序相同
                    if (Arrays.equals(q, r)) {
                        //最前最后位置相等，拼接成两个模式 模式p和q p1=qm
                        if (fre.get(i).get(0) == fre.get(j).get(slen - 1)) {
                            Cd.set(0, fre.get(i).get(0));
                            Cd2.set(0, fre.get(i).get(0) + 1);
                            Cd.set(slen, fre.get(i).get(0) + 1);
                            Cd2.set(slen, fre.get(i).get(0));
                            //模式Cd 长度m+1，第一个位置相对顺序(0处，m+1处)
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
//                            oop1=judge_freoop(Z.size(), Cd, Z);
//                            System.out.println("特殊情况: ");
//                            System.out.println("子模式1: "+fre.get(i));
//                            System.out.println("子模式2: "+fre.get(j));
//                            System.out.println("Cd1: "+Cd);

//                            oop2=judge_freoop(Z2.size(), Cd2, Z2);

//                            if(oop1==true){
//                                //System.out.println("初始: "+Fre);
//                                Fre.add(Cd);
//                                System.out.println("特殊情况Cd: "+Fre);
////                                Fre.remove(fre.get(i));
//                             //System.out.println("删除前缀: "+fre_list);
//                            }
//                            if(oop2==true){
//                               // System.out.println("添加Cd2: "+fre_list);
//                                Fre.add(Cd2);
//                                System.out.println("特殊情况Cd2: "+Fre);
////                                Fre.remove(fre.get(j));
//                                //System.out.println("删除Cd2: "+fre_list);
//                            }
//                            System.out.println("fre_list: "+Fre);
//                            if(oop1==false&&oop2==false){
//                                count=0;
//                            }else{ count=count+1;}
//                            System.out.println("支持度: "+Z.size()+"  "+Z2.size());
//                            System.out.println("count: "+count);

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
                            // oop1=judge_freoop(Z.size(), Cd, Z);
//                            if(oop1==true){//超模不频繁
//                                Fre.add(Cd);
//                                System.out.println("一般情况Cd: "+Fre);
//                            }

//                            if(oop1==false){
//                                count=0;
//                            }else{count=count+1;
//                            }

//                            System.out.println("一般情况1: ");
//                            System.out.println("子模式1: "+fre.get(i));
//                            System.out.println("子模式2: "+fre.get(j));
//                            System.out.println("Cd1: "+Cd);
//                            System.out.println("支持度: "+Z.size());
//                            System.out.println("count: "+count);

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
                            //     oop1=judge_freoop(Z.size(), Cd, Z);
//                            if(oop1==true){//超模式频繁
//                                Fre.add(Cd);
//                                System.out.println("一般情况2Cd: "+Fre);
//                            }

//                            if(oop1==false){//超模式不频繁
//                                count=0;
//                        }else{ count=count+1;}
//                            System.out.println("一般情况2: ");
//                            System.out.println("子模式1: "+fre.get(i));
//                            System.out.println("子模式2: "+fre.get(j));
//                            System.out.println("Cd1: "+Cd);
//                            System.out.println("支持度: "+Z.size());
//                            System.out.println("count: "+count);
                        }
                    }
                }
            }

//            if(count==0){
//                judge_OUTO(fre.get(i),pos.get(i));//说明当前模式是最大频繁保序模式
//              //  System.out.println("最大频繁保序模式："+fre.get(i));
//            }
        }
        return 0;
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

            //  System.out.println("集合: "+Fre+"   后缀： "+qList+"   前缀：  "+rList);
//                for(List<Integer> pattern:Fre){
//                    System.out.println("pattern: "+pattern);
//                    if(qList.equals(pattern) || rList.equals(pattern)){
//                        Fre.remove(pattern);
//                    }
//                }

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
            //System.out.println("集合: "+Fre);
        }
        //System.out.println("集合结果: "+Fre+"   "+Fre_index);
        return Fre;
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
            //System.out.println("frequent_num: "+frequent_num++);
            //  System.out.println("频繁模式: "+L);
            fre_num++;
        }

        return oop_fre;
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

        // Step 1: 提取所有子序列均值和标准差
        for (Integer endIndex : Z) {
            for (int k = 0; k < Cd.size(); k++) {
                //index 是第一个子序列在S中的初始位置（首位）索引
                int index = endIndex - Cd.size() + k;
                double a = S.get(index);
                subSequence.add(a);
            }
            double mean =calculateMean(subSequence);
            double devation=calculateStandardDeviation(subSequence);
            means.add(mean);
            meanss.add(mean);
            de.add(devation);
            des.add(devation);
            SequenceList.add(new ArrayList<>(subSequence));
            subSequence.clear();
        }

//        System.out.println("子序列集合： "+SequenceList.size());
//        System.out.println("子序列： "+SequenceList);

        // Step 2: 计算所有子序列均值的整体均值和标准差
        double overallMeanOfMeans = calculateMean(means);
        double overallStdDevOfMeans = calculateStandardDeviation(means);
// Step 3: 判断每个子序列均值是否为异常
        for (int i = 0; i < SequenceList.size(); i++) {
            double mean = means.get(i);
            double deviation = de.get(i);

            // 使用 Z-Score 判断均值是否异常
            double zScoreMean = (mean - overallMeanOfMeans) / overallStdDevOfMeans;
            double zScoreDeviation = (deviation - calculateMean(de)) / calculateStandardDeviation(de); // 如果需要，也可对标准差做 Z-Score

            // 判断规则：如果均值或标准差的 Z-Score 超过阈值（例如 3 或 -3），认为是异常
            if (Math.abs(zScoreMean) > Z_SCORE_THRESHOLD || Math.abs(zScoreDeviation) > Z_SCORE_THRESHOLD) {
                int num = 0;
                List<Double> A = SequenceList.get(i);

                for (int j = 0; j < SequenceList.size(); j++) {
                    if (i != j) {
                        List<Double> B = SequenceList.get(j);
                        double dtw = calculateDTWDistance(A, B);

                        if (dtw >= DTW) {
                            number++;
                        }
                    }
                }

                if (number >= Math.ceil(Z.size() * 0.8)) {
                    // 序列被认为是异常模式序列
                    Fre_seq.add(A);
                    OUTO_num++;
                } else {
                    // 不是异常保序模式
                }

                number = 0;
            }
        }
    }


    // 计算均值
    public double calculateMean(List<Double> list) {
        double sum = 0;
        for (double num : list) {
            sum += num;
        }
        return sum / list.size();
    }

    //计算相同保序模式下两个出现的DTW距离--首先要数据归一化
    public double calculateDTWDistance(List<Double> A, List<Double> B) {
        double sum = 0.0;
        for (int i = 0; i < A.size(); i++) {
            double diff = A.get(i) - B.get(i);
            sum += Math.abs(diff); // 累加绝对值差
        }
        return sum;
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

    // 计算标准差
    public double calculateStandardDeviation(List<Double> list) {
        double mean = calculateMean(list);
        double sumOfSquaredDifferences = 0;
        for (double num : list) {
            sumOfSquaredDifferences += Math.pow(num - mean, 2);
        }
        return Math.sqrt(sumOfSquaredDifferences / list.size());
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
            System.out.println("频繁模式:  "+L);
            // System.gc();
            judge_maxfreoop(Fre,Fre_index);
        }

//        judge_maxfreoop(Fre);
        for (int i = 0; i < Fre.size(); i++) {
            List<Integer> pattern = Fre.get(i);
            List<Integer> pattern_index = Fre_index.get(i);
            // System.out.println("pattern:  "+pattern+"   "+pattern_index);
            judge_OUTO(pattern,pattern_index);
        }

        System.out.println("Fre:  "+Fre.size());
        System.out.println("最大频繁模式:  "+Fre);
//        System.out.println("  ");
//        System.out.println("  ");
//        System.out.println("  ");
//        System.out.println("  ");
//        System.out.println("OUTO:  "+Fre_seq);

    }
}
