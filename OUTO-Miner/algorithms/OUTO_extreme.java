package algorithms;

        import java.io.BufferedReader;
        import java.io.File;
        import java.io.FileReader;
        import java.io.IOException;
        import java.util.*;

        import static java.lang.Math.abs;

//2024.06.15 基于IQR文件，提取极值点 有IQR方法 找出最大长度频繁保序模式

public class OUTO_extreme {

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

    List<List<Integer>> Fre = new ArrayList<>();//存放生成的频繁模式集合
    List<List<Integer>> Fre_index = new ArrayList<>();//存放生成的频繁模式集合位置索引

    List<Integer> Z = new ArrayList<>();//存放本次生成的末尾数组
    List<Integer> Z2 = new ArrayList<>();

    // 模式融合可能会生成两个超模式
    List<Integer> Cd = new ArrayList<>(); //存放本次生成的候选模式
    List<Integer> Cd2 = new ArrayList<>();

    List<Double> Seq = new ArrayList<>();//序列
    List<Double> S = new ArrayList<>();

    double COS = 0.9;  // 余弦距离阈值

    double xishu=5;
    double DTW;//DTW相似度阈值

    double fitt=5;//拟合差阈值
    int minsup=200;//最小支持度阈值
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
        //String fileName = "src/main/java/dataset/顺义PM2.5.txt";
        //6
        //String fileName = "src/main/java/dataset/ChengduPM2.5.txt"; //两个空格
        //7
        //String fileName = "src/main/java/dataset/DOW.txt";
        //8
        String fileName = "src/main/java/dataset/NYSE.txt";

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

        //8文件  Stock原始序列长度= fit=2， minsup=，xishu=
        //代码read中for(i<valuestring.length-1)
        //String fileName ="src/main/java/dataset/scalability/29k.txt";

        System.out.println("*********算法 EOPP_Miner 开始**************");
        OUTO_extreme eop_Miner = new OUTO_extreme();
        eop_Miner.readDataPointsFromFile(fileName);
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

                extremepointsTemp = extractExtremePoints(inS);

                S=extremepointsTemp;

                System.out.println("S个数: "+S.size());
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


    class LNode{
        int data;
        LNode next = null;
    }

    private  List<Double> extractExtremePoints(double[] in) {
        List<Double> list1 = new ArrayList<>();


        list1.add(in[0]);
        for (int i = 1; i < in.length - 1; i++){
            //极值点在rawdataTemp的位置索引是i
            if ((in[i] >= in[i - 1] && in[i] > in[i + 1]) || (in[i] > in[i - 1] && in[i] >= in[i + 1])){
                list1.add(in[i]);
            } else if ((in[i] <= in[i - 1] && in[i] < in[i + 1]) || (in[i] < in[i - 1] && in[i] <= in[i + 1])){
                list1.add(in[i]);
            }
        }
        if (!list1.contains(in[in.length - 1])) {
            list1.add(in[in.length - 1]);

        }
        //System.out.println("位置索引"+list1index);

        return list1;
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

    //判断是否是最大频繁保序模式
    private boolean judge_maximaioop(int sup_num, List<Integer> Cd, List<Integer> Z) {
        boolean max_oop=false;
        List<Integer> rec=new ArrayList<>();
        int rectemp;
        int reclen = 0;
        int flag1,flag2=0;



        return max_oop;
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
            for (int k = 0; k < Cd.size(); k++) {
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

            if (!isWithinBounds(mean, mQ1 - mIQR, mQ3 + mIQR)||
                    (isWithinBounds(mean, mQ1 - mIQR, mQ3 + mIQR)&&!isWithinBounds(devation, dQ1 - dIQR, dQ3 + dIQR))) {

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
        // System.out.println("标准差: " + svariance);


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
            //System.out.println("频繁模式:  "+L);
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

    }
}
