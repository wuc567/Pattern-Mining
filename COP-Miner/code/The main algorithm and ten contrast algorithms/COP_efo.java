package COP_Mining;

import newalgorithm.MemoryLogger;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.*;
import java.util.stream.Collectors;

public class COP_efo {

    private static Double[] input;
    private static Double[] in;

//    private static Double[] p = new Double[]{2.0, 3.0, 1.0, 6.0, 4.0, 5.0};
//    private static Double[] p = new Double[]{3.0, 6.0, 4.0, 5.0, 1.0, 2.0};

    //    private static Double[] p = new Double[]{5D, 3D, 7D, 13D};
    //private static Double[] p = new Double[]{5.0,2.0,4.0};
//private static Double[] p = new Double[]{5.0,2.0,4.0,1.0};
//    private static Double[] p = new Double[]{3D, 6D, 4D, 5D,1D,2D};
//    private static Double[] p = new Double[]{1D,3D,2D,5D,4D,6D};
//    private static Double[] p = new Double[]{1.0, 4.0, 3.0,6.0,5.0, 2.0};
//    private static Double[] p = new Double[]{4.0, 3.0, 6.0, 2.0, 5.0, 1.0};

//    private static Double[] p = new Double[]{1.0, 5.0, 3.0, 4.0, 2.0, 6.0};

//    private static Double[] p = new Double[]{1.0, 5.0, 2.0};
//    private static Double[] p = new Double[]{1.0, 5.0, 2.0, 6.0};
//    private static Double[] p = new Double[]{1.0, 5.0, 2.0, 6.0, 3.0};
//    private static Double[] p = new Double[]{1.0, 5.0, 2.0, 6.0, 3.0, 4.0};
//    private static Double[] p = new Double[]{1.0, 6.0, 3.0, 7.0, 4.0, 5.0, 2.0};

    //SDB8
//    private static Double[] p = new Double[]{1.0, 3.0, 2.0};
//    private static Double[] p = new Double[]{1.0, 3.0, 2.0, 4.0};
//    private static Double[] p = new Double[]{1.0, 3.0, 2.0, 5.0, 4.0};
    private static Double[] p = new Double[]{1.0, 3.0, 2.0, 5.0, 4.0, 6.0};
//    private static Double[] p = new Double[]{1.0, 4.0, 2.0, 6.0, 5.0, 7.0, 3.0};


//    private static Double[] p = new Double[]{1D,3D,4D,2D,6D,7D,5D,8D};
//    private static Double[] p = new Double[]{2.0, 5.0, 1.0, 4.0, 3.0};
//    private static Double[] p = new Double[]{2D,3D,1D,6D,4D,5D};
//    private static Double[] p = new Double[]{5D,6D,3D,4D,1D,2D};
//    private static Double[] p = new Double[]{1D,3D,2D,5D,4D,6D};
//private static Double[] p = new Double[]{4D,5D,2D,3D,1D,6D};
//    private static Double[] p = new Double[]{1.0, 5.0, 2.0, 6.0, 3.0, 4.0};
//private static Double[] p = new Double[]{1.0, 5.0, 3.0, 4.0, 2.0, 6.0};

//    private static Double[] p = new Double[]{2D,1D,4D,3D,6D,5D};
//    private static Double[] p = new Double[]{1D,3D,2D,5D,4D,6D};
//    private static Double[] p = new Double[]{1.0, 4.0, 2.0, 5.0, 3.0, 7.0};

    //    private static Double[] p = new Double[]{2D,1D,4D,3D,6D,5D,8D,7D};
    private static Double[] pattern = getPatternExtreme(p);

    public static int pattern_length = 0;
    static List<List<Integer>> P = new ArrayList<>(); //存放末位的数组
    static List<List<Integer>> L = new ArrayList<>();//存放每次生成的频繁模式
//    static List<List<Integer>> Pre = new ArrayList<>();//存放前缀模式
//    static List<List<Integer>> Suf = new ArrayList<>();//存放后缀模式

    static List<List<Integer>> PCOP = new ArrayList<>();
    static List<List<Integer>> LCOP = new ArrayList<>();


    static List<Integer> Z = new ArrayList<>(); //存放本次生成的末位数组
    static List<Integer> Z2 = new ArrayList<>();

    static List<Integer> W = new ArrayList<>(); //存放本次生成的末位数组
    static List<Integer> W2 = new ArrayList<>();

    static List<Integer> Parr = new ArrayList<>();

    static List<Integer> Cd = new ArrayList<>(); //存放本次生成的模式
    static List<Integer> Cd2 = new ArrayList<>();

    private static int minsup = 6000;

    private static Double[] oneTwo = new Double[]{1D, 2D};
    private static Double[] pOrder = getOrder(pattern);
    private static Map<String, List<Integer>> map; //放P的后缀为前缀的模式
    private static Map<String, List<Integer>> mapV2; //放P长度+1共生模式
    private static Map<String, List<Integer>> mapV3; //放新生成后缀为前缀的模式
    private static Map<String, List<Integer>> mapV4; //放新生成长度+1共生模式
    private static Map<String, Map<String, List<Integer>>> occMap;
    private static int freNum = 0;
    private static int candNum = 0;
    public static int element_num = 0;

    public static void main(String[] args) throws Exception {
        long startTime = System.currentTimeMillis();
        getInArr();
//        input = new Double[]{16D, 8D, 11D, 10D, 12D, 16D, 17D, 13D, 20D, 18D, 21D, 22D, 18D, 14D, 21D, 24D, 23D, 25D};
//        in = getExtremePoint(input);
//        readLine();
        printCostTime(startTime);
    }

    private static void printCostTime(long startTime) {
        System.out.println("候选模式的总数是：" + candNum);
        System.out.println("共生频繁模式的总数为：" + freNum);
        System.out.println("元素比较总次数为: " + element_num);
        System.out.println("-------------------------------------------");
        System.out.println("花费总时间为:" + (System.currentTimeMillis() - startTime) + "ms");
        MemoryLogger.getInstance().checkMemory();
        double maxMemory = MemoryLogger.getInstance().getMaxMemory();
        System.out.println("最大内存占用: " + maxMemory + " Mb");
    }

    private static void getInArr() throws Exception {
//        File file = new File("E:/Dataset/FiveCitiesTempData.txt");
//        File file = new File("E:/Dataset/分类/CinCECGTorso_TRAIN.txt");
//        File file = new File("E:/Dataset/ChengduPM2.5.txt");
//        File file = new File("E:/Dataset/PRSA_Data.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_HeartRate.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_PRInterval.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_PAxis.txt");

//        File file = new File("E:/Dataset/分类/ShapeletSim_TEST.txt");
//        File file = new File("E:/Dataset/test.txt");

//        File file = new File("E:/Dataset/分类/CSSE COVID-19.txt");
//        File file = new File("E:/Dataset/分类/BTC.txt");
//        File file = new File("E:/Dataset/分类/Beef_TEST.txt");
//        File file = new File("E:/Dataset/分类/Car_TEST.txt");
//        File file = new File("E:/Dataset/FiveCitiesTempData.txt");
//                File file = new File("E:/Dataset/Data-Stock.txt");
//        File file = new File("E:/Dataset/STOCK-prediction.txt");
//        File file = new File("E:/Dataset/Online-Retail.txt");
//        File file = new File("E:/Dataset/Alabama_Confirmed.txt");
//        File file = new File("E:/Dataset/NYSE Price.txt");
        File file = new File("D:/Dataset/NYSE440_440.txt");
//        File file = new File("E:/Dataset/NYSE2.txt");
//        File file = new File("E:/Dataset/NYSE3.txt");
//        File file = new File("E:/Dataset/NYSE4.txt");
//        File file = new File("E:/Dataset/NYSE5.txt");
//        File file = new File("E:/Dataset/NYSE6.txt");
//        File file = new File("E:/Dataset/NYSE7.txt");
//        File file = new File("E:/Dataset/NYSE8.txt");

//        File file = new File("E:/Dataset/ChengduPM2.5.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5.txt");

//        File file = new File("E:/Dataset/分类/ShapeletSim_TEST.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5.txt");
//        File file = new File("E:/Dataset/PRSA_Data.txt");
//        File file = new File("E:/Dataset/ToeSegmentation1_TRAIN.txt");
//        File file = new File("E:/Dataset/Crude Oil.txt");
//        File file = new File("E:/Dataset/PRSA_Data_Nongzhanguan.txt");
//        File file = new File("E:/Dataset/Italian-temperature.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_database.txt");
//        File file = new File("E:/Dataset/ChengduPM2.5.txt");

//        File file = new File("E:/Dataset/1WTl-2.txt");
//        File file = new File("E:/Dataset/Meat_TEST.txt");

        BufferedReader br = new BufferedReader(new FileReader(file));
        String s;
        //使用readLine方法，一次读一行
        while ((s = br.readLine()) != null) {

            pattern_length = 0;
            P = new ArrayList<>(); //存放末位的数组
            L = new ArrayList<>();//存放每次生成的频繁模式

            PCOP = new ArrayList<>();
            LCOP = new ArrayList<>();

            Z = new ArrayList<>(); //存放本次生成的末位数组
            Z2 = new ArrayList<>();

            Parr = new ArrayList<>();
            W = new ArrayList<>();
            W2 = new ArrayList<>();

            Cd = new ArrayList<>(); //存放本次生成的模式
            Cd2 = new ArrayList<>();
            List<Double> outList = new ArrayList<>();

            List<Double> inList = new ArrayList<>();
            s = s.trim();
            String[] str = s.split(" ");
            String[] strArr = new String[str.length - 1];
            System.arraycopy(str, 1, strArr, 0, strArr.length);
            for (String s1 : strArr) {
                if (!" ".equals(s1) && !s1.isEmpty()) {
                    inList.add(Double.parseDouble(s1));
                    outList.add(Double.parseDouble(s1));

                }
            }
            Double[] inArr = new Double[inList.size()];
            int i = 0;
            for (double inLine : inList) {
                inArr[i++] = inLine;
            }
            input = inArr;
            in = getExtremePoint(input);
            readLine();
            i++;
//            System.gc();
        }
        br.close();
    }

    private static void readLine() {
        map = new HashMap<>();
        mapV2 = new HashMap<>();
        mapV3 = new HashMap<>();
        mapV4 = new HashMap<>();
        occMap = new HashMap<>();
        Double[] pSuf = new Double[pattern.length - 1];
        System.arraycopy(pattern, 1, pSuf, 0, pSuf.length);
        Integer[] subsetNumArr = getPSufLocation(pSuf);
        if (subsetNumArr.length < minsup) {
//            System.out.println("P后缀不满足支持度！！！");
            return;
        }
        List<Integer> pList = new ArrayList<>();
//        for (Integer val : subsetNumArr) {
//            Double[] sub = new Double[pSuf.length];
//            System.arraycopy(in, val - pSuf.length, sub, 0, sub.length);
//            //求P的出现
//            if (val > pSuf.length) {
//                Double[] patternOrder = getCompareOrder(sub, getOrder(pSuf), in[val - pSuf.length - 1], false);
//                if (patternOrder != null) {
//                    if (Arrays.equals(pOrder, patternOrder)) {
//                        pList.add(val);
//                    }
//                }
//            }
//
//            //求pSuf后缀出现
//            if (val < in.length) {
//                Double[] pSufSufOrder = getCompareOrder(sub, getOrder(pSuf), in[val], true);
//                if (pSufSufOrder != null) {
//                    List<Integer> list = map.get(Arrays.toString(pSufSufOrder));
//                    if (list != null) {
//                        list.add(val + 1);
//                        map.put(Arrays.toString(pSufSufOrder), list);
//                    } else {
//                        list = new ArrayList<>();
//                        list.add(val + 1);
//                        map.put(Arrays.toString(pSufSufOrder), list);
//                    }
//                }
//            }
//        }
        find();
        while (Cd.size() < pattern.length) {

            generate_fre();

        }

        Double[] patternSuf = new Double[pattern.length - 1];
        System.arraycopy(pattern, 1, patternSuf, 0, patternSuf.length);
        Double[] patternSufOrder = getOrder(patternSuf);
        for (int i = 0; i < L.size(); i++) {
            if (getOrderInt(pattern).toString().equals(L.get(i).toString())){
                pList = P.get(i);
            }
            Double[] l = new Double[L.get(i).size()];
            for (int j = 0; j < L.get(i).size(); j++){
                l[j] = L.get(i).get(j).doubleValue();
            }
            Double[] lPre = new Double[L.get(i).size() - 1];
            System.arraycopy(l, 0, lPre, 0, lPre.length);
            if (Arrays.equals(patternSufOrder, getOrder(lPre))){
                map.put(Arrays.toString(l), P.get(i));
            }
        }

        map = map.entrySet().stream().filter(x -> x.getValue().size() >= minsup).collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
        patternFusion(pOrder, pList);
        while (mapV2 != null && mapV2.size() > 0) {
            for (Map.Entry<String, List<Integer>> entry : mapV2.entrySet()) {
                String key = entry.getKey();
                Double[] P = stringToArray(key);
                List<Integer> PLocation = entry.getValue();
                Double[] PSuf = new Double[P.length - 1];
                System.arraycopy(P, 1, PSuf, 0, PSuf.length);
                Map<String, List<Integer>> mapInNew = occMap.get(Arrays.toString(getOrder(PSuf)));
                if (mapInNew != null) {
                    LNode PNode = getLNode(PLocation);
                    for (Map.Entry<String, List<Integer>> entryIn : mapInNew.entrySet()) {
                        patternFusionNew(P, PLocation, entryIn, PNode);
                    }
                    continue;
                }
                List<Integer> PSufLocation = map.get(Arrays.toString(getOrder(PSuf)));
                /*if (PSufLocation == null || PSufLocation.size() == 0) {
                    continue;
                }*/
                Map<String, List<Integer>> mapIn = new HashMap<>();
                for (Integer val : PSufLocation) {
                    Double[] sub = new Double[PSuf.length];
                    System.arraycopy(in, val - PSuf.length, sub, 0, sub.length);
                    //求PSuf后缀出现
                    if (val < in.length) {
                        Double[] PSufSufOrder = getCompareOrder(sub, getOrder(PSuf), in[val], true);
                        if (PSufSufOrder != null) {
                            List<Integer> list = mapIn.get(Arrays.toString(PSufSufOrder));
                            if (list != null) {
                                list.add(val + 1);
                                mapIn.put(Arrays.toString(PSufSufOrder), list);
                            } else {
                                list = new ArrayList<>();
                                list.add(val + 1);
                                mapIn.put(Arrays.toString(PSufSufOrder), list);
                            }
                        }
                    }
                }
                mapIn = mapIn.entrySet().stream().filter(x -> x.getValue().size() >= minsup).collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
                occMap.put(Arrays.toString(getOrder(PSuf)), mapIn);
                mapV3.putAll(mapIn);
                LNode PNode = getLNode(PLocation);
                for (Map.Entry<String, List<Integer>> entryIn : mapIn.entrySet()) {
                    patternFusionNew(P, PLocation, entryIn, PNode);
                }
            }
            mapV2 = mapV4;
            mapV4 = new HashMap<>();
            map = mapV3;
            mapV3 = new HashMap<>();
        }

//        int i = 0;
    }

    public static int generate_fre() {
        int slen = 0;

        List<Integer> Q = new ArrayList<>();
        List<Integer> R = new ArrayList<>();
        List<List<Integer>> pos = new ArrayList<>();
        List<List<Integer>> fre = new ArrayList<>();

        List<List<Integer>> pos_COP = new ArrayList<>();
        List<List<Integer>> fre_COP = new ArrayList<>();

        List<LNode> Lb = new ArrayList<>();

        List<LNode> Lb_cop = new ArrayList<>();
//        List<LNode> Pnode = new ArrayList<>();

        int[] q = new int[256];
        int[] r = new int[256];

//        int j = 0;
        int fre_number = 0;
        int COPfre_number = 0;
        int t = 0;
        int k = 0;

        slen = L.get(0).size();//L:(1,2)(2,1) 模式长度 2  slen=2

        for (List<Integer> Ltemp : L) {//L:(1,2),(2,1)
            List<Integer> fretemp = new ArrayList<>();
            for (Integer integer : Ltemp) {//Ltemp:(1,2)|(2,1)
                fretemp.add(integer);//fretemp:(1,2)|(2,1)
            }
            fre.add(fretemp);//fre:(1,2),(2,1)
        }

//		fre = L;
        L.clear();//清空L

        for (List<Integer> Ltemp : LCOP) {//L:(1,2),(2,1)
            List<Integer> fretemp2 = new ArrayList<>();
            for (Integer integer : Ltemp) {//Ltemp:(1,2)|(2,1)
                fretemp2.add(integer);//fretemp:(1,2)|(2,1)
            }
            fre_COP.add(fretemp2);//fre_COP:(1,2),(2,1)
        }

//		fre_COP = LCOP;
        LCOP.clear();

        for (List<Integer> Ptemp : P) {//P:{3,5,7,9,11,13}{2,4,6,8,10,12}
            List<Integer> postemp = new ArrayList<>();
            for (Integer integer : Ptemp) {//Ptemp:{3,5,7,9,11,13}|{2,4,6,8,10,12}
                postemp.add(integer);//postemp:{3,5,7,9,11,13}|{2,4,6,8,10,12}
            }
            pos.add(postemp);//pos:{3,5,7,9,11,13}{2,4,6,8,10,12}
        }

//		pos = P;
        P.clear();

        for (List<Integer> Ptemp : PCOP) {//P:{3,5,7,9,11,13}{2,4,6,8,10,12}
            List<Integer> postemp = new ArrayList<>();
            for (Integer integer : Ptemp) {//Ptemp:{3,5,7,9,11,13}|{2,4,6,8,10,12}
                postemp.add(integer);//postemp:{3,5,7,9,11,13}|{2,4,6,8,10,12}
            }
            pos_COP.add(postemp);//pos:{3,5,7,9,11,13}{2,4,6,8,10,12}
        }

//		pos_COP = PCOP;
        PCOP.clear();

        while (Lb.size() < fre.size()) {//Lb.size=0
            Lb.add(new LNode());//Lb 的节点个数就是此时二长度的频繁模式的个数：2
        }

        while (Cd.size() < slen + 1) {//Cd.size=0,slen=2
            Cd.add(0);//Cd本来为空，现在变成（0,0,0） 三长度
        }

        while (Cd2.size() < slen + 1) {//Cd2.size=0,slen=2
            Cd2.add(0);//Cd2本来为空，现在变成（0，0，0）三长度
        }

        //建立链表
        for (int s = 0; s < fre.size(); s++) {//fre_number=2
            LNode pb;//pb是节点
            LNode qb = new LNode();//qb是节点
            LNode temp = new LNode();//temp是节点
            temp.data = pos.get(s).size();//pos:{3,5,7,9,11,13}{2,4,6,8,10,12}  temp.data=6
            Lb.set(s, temp);//s:0,temp:6 第一个节点data值为6  List<LNode> Lb(此时长度为2，有2个二长度的频繁模式（1,2），（2,1）
            qb = Lb.get(s);//qb: data=6  next=null
            for (int d = 0; d < pos.get(s).size(); d++) {//pos.get(s).size()=6
                pb = new LNode();//pb:data=0,next=null
                pb.data = pos.get(s).get(d);//d=0,  pos.get(s).get(d)=3,  pb.data=3  pb.next=null
                qb.next = pb;//qb:data=6,next=3
                qb = pb;// pb.data=3  pb.next=null  所以qb.data=3  qb.next=null
            }//Lb.get(0)变成了 6->3->5->7->9->11->13->null  Lb.get(1)变成了 6->2->4->6->8->10->12->null
            qb.next = null;
        }


        //新写的
        for (int s = 0; s < COPfre_number; s++) {//fre_number=2
            LNode pb;//pb是节点
            LNode qb = new LNode();//qb是节点
            LNode temp = new LNode();//temp是节点
            temp.data = pos_COP.get(s).size();//pos:{3,5,7,9,11,13}{2,4,6,8,10,12}  temp.data=6
            Lb_cop.add(s, temp);//s:0,temp:6 第一个节点data值为6  List<LNode> Lb(此时长度为2，有2个二长度的频繁模式（1,2），（2,1）
            qb = Lb_cop.get(s);//qb: data=6  next=null
            for (int d = 0; d < pos_COP.get(s).size(); d++) {//pos.get(s).size()=6
                pb = new LNode();//pb:data=0,next=null
                pb.data = pos_COP.get(s).get(d);//d=0,  pos.get(s).get(d)=3,  pb.data=3  pb.next=null
                qb.next = pb;//qb:data=6,next=3
                qb = pb;// pb.data=3  pb.next=null  所以qb.data=3  qb.next=null
            }//Lb_cop.get(0)变成了 6->3->5->7->9->11->13->null  Lb_cop.get(1)变成了 6->2->4->6->8->10->12->null
            qb.next = null;
        }//Lb_cop存放位置链表  fre_COP:是频繁的共生

      /*  if(Parr.size()>0){
            LNode pb;
            LNode qb = new LNode();
            LNode temp = new LNode();
            temp.data = Parr.size();
            Pnode.set(0, temp);
            qb = Pnode.get(0);
            for (int d = 0; d < Parr.size(); d++) {
                pb = new LNode();
                pb.data = Parr.get(d);
                qb.next = pb;
                qb = pb;
            }
            qb.next = null;
        }*/


        for (int i = 0; i < fre.size(); i++) {//fre_number=2

            List<Integer> prefix = fre.get(i);

            int a = 0;
            Double[] Prefixarr = new Double[prefix.size()];
            for (double item : prefix) {
                Prefixarr[a++] = item;//Cdarr:(1,2)
            }


            // 求后缀
            Q = fre.get(i).subList(1, fre.get(i).size());//fre:(1,2),(2,1)
            q = sort(Q);

            // 创建链表
            LNode L = new LNode();//L是节点  data=0,next=null
            LNode p = new LNode();//p是节点
            LNode s = new LNode();//s是节点
            int size = pos.get(i).size();//pos.get(0).size()=6  pos:{3,5,7,9,11,13}{2,4,6,8,10,12}

            L.data = size;//L.data =size=6
            s = L;//s.data=6,next=null
            for (k = 0; k < size; k++) {//size=6
                p = new LNode();//p.data=0,p.next=null
                p.data = pos.get(i).get(k);//pos.get(0).get(0)=3  p.data=3  pos:{3,5,7,9,11,13}{2,4,6,8,10,12}
                s.next = p;
                s = p;//p.data=3,p.next=null
            }
            s.next = null;//s:6->3->5->7->9->11->13->null
            //L:6->3->5->7->9->11->13->null 作为前缀的支持度+索引位置

            LNode Pnode = new LNode();
            LNode u = new LNode();
            LNode v = new LNode();
            int size1 = Parr.size();
            Pnode.data = size1;
            v = Pnode;
            for (int m = 0; m < size1; m++) {
                u = new LNode();
                u.data = Parr.get(m);
                v.next = u;
                v = u;
            }
            v.next = null;


            for (int j = 0; j < fre.size(); j++) {//fre_number=2  二长度的频繁模式的个数
                //有剪枝
                if (L.data >= minsup && Lb.get(j).data >= minsup) {//L.data=6,L.next=null  Lb.get(0)变成了 6->3->5->7->9->11->13->null

                    // 求前缀
                    R = fre.get(j).subList(0, fre.get(j).size() - 1);
                    r = sort(R);//q为后缀，r为前缀
                    //前后缀相对顺序相同
                    if (Arrays.equals(q, r)) {

                        //最前最后位置相等，拼接成两个模式
                        if (fre.get(i).get(0) == fre.get(j).get(slen - 1)) {//slen=2 就是此时进行融合的模式的长度
                            Cd.set(0, fre.get(i).get(0));
                            Cd2.set(0, fre.get(i).get(0) + 1);
                            Cd.set(slen, fre.get(i).get(0) + 1);
                            Cd2.set(slen, fre.get(i).get(0));
                            for (t = 1; t < slen; t++) {
                                if (fre.get(i).get(t) > fre.get(j).get(slen - 1)) {
                                    //中间位置增长
                                    //小的一行的中间位置和大的一行的最后一个数比较，大于+1，小于等于不变
                                    Cd.set(t, fre.get(i).get(t) + 1);
                                    Cd2.set(t, fre.get(i).get(t) + 1);
                                } else {
                                    Cd.set(t, fre.get(i).get(t));//Cd:(1,3,2)
                                    Cd2.set(t, fre.get(i).get(t));//Cd2:(2,1,3)
                                }
                            }
//                            Pre.add(fre.get(i));
//                            Suf.add(fre.get(j));
//                            cd_num = cd_num + 2;//候选模式的个数+2
                            if (slen < pattern.length) {
                                grow_BaseP2(Cd.size() - 1, Lb.get(j), L);
                            } else if (slen == pattern.length) {
                                if (Arrays.equals(Prefixarr, pattern)) {
                                    grow_BaseP2NEW(Cd.size() - 1, Lb.get(j), L, Pnode);
                                } else {
                                    grow_BaseP2(Cd.size() - 1, Lb.get(j), L);
//                                    grow_BaseP22(Cd.size() - 1, Lb.get(j), L);
                                }
//                          if( slen==pattern.length&&Arrays.equals(Prefixarr, pattern)){

                            } else if (slen > pattern.length) {
                                boolean fl = false;
                                for (int m = 0; m < COPfre_number; m++) {
                                    //Lb_cop存放位置链表  fre_COP:是频繁的共生

                                    List<Integer> long_prefix = fre_COP.get(m);
                                    int b = 0;
                                    Double[] long_Prefixarr = new Double[long_prefix.size()];
                                    for (int c = 0; c < long_prefix.size(); c++) {
                                        long_Prefixarr[c] = Double.valueOf(long_prefix.get(c));
                                    }
                                   /* for (double item : prefix) {
                                        Prefixarr[b++] = item;
                                    }*/
                                   /* if (i == 1 && j == 9){
                                        int ac = 0;
                                    }*/
                                    LNode long_Pnode = Lb_cop.get(m);
                                    if (Arrays.equals(Prefixarr, long_Prefixarr)) {
                                        grow_BaseP2NEW(Cd.size() - 1, Lb.get(j), L, long_Pnode);
                                        fl = true;
                                        break;
                                    }
//                                    else {
//                                        if (i == 1 && j == 9){
//                                            LNode lNode = Lb.get(j);
//                                            int num = 0;
//                                            while (lNode != null){
//                                                System.out.print(lNode.data + "->");
//                                                lNode = lNode.next;
//                                                num++;
//                                            }
//                                            System.out.println(num);
//                                        }

//                                        if (i == 1 && j == 9){
//                                            LNode lNode = Lb.get(j);
//                                            int num = 0;
//                                            while (lNode != null){
//                                                System.out.print(lNode.data + "->");
//                                                lNode = lNode.next;
//                                                num++;
//                                            }
//                                            System.out.println(num);
//                                        }
//                                    }
                                }
                                if (!fl) {
                                    grow_BaseP2(Cd.size() - 1, Lb.get(j), L);

//                                    grow_BaseP22(Cd.size() - 1, Lb.get(j), L);
                                }
                            }
//                            else {
//                                grow_BaseP2(Cd.size() - 1, Lb.get(j), L);
//                            }


                            //Cd.size() - 1=2,Lb.get(j)是后缀的支持度和索引位置，L是前缀的支持度和索引位置

                        } else if (fre.get(i).get(0) < fre.get(j).get(slen - 1)) {
                            Cd.set(0, fre.get(i).get(0));//小的不变  （1,0,0）
                            Cd.set(slen, fre.get(j).get(slen - 1) + 1);//大的加一 1,0,3）
                            for (t = 1; t < slen; t++) {
                                if (fre.get(i).get(t) > fre.get(j).get(slen - 1)) {
                                    //中间位置增长
                                    //小的一行的中间位置和大的一行的最后一个数比较，大于+1，小于等于不变
                                    Cd.set(t, fre.get(i).get(t) + 1);

                                } else {
                                    Cd.set(t, fre.get(i).get(t));//Cd:(1,2,3)

                                }
                            }
//                            Pre.add(fre.get(i));
//                            Suf.add(fre.get(j));
//                            cd_num = cd_num + 1;//候选模式的个数加1

                            if (slen < pattern.length) {
                                grow_BaseP1(Lb.get(j), L);
                            } else if (slen == pattern.length) {
                                if (Arrays.equals(Prefixarr, pattern)) {
                                    grow_BaseP1NEW(Lb.get(j), L, Pnode);
                                } else {

                                    grow_BaseP1(Lb.get(j), L);

//                                    grow_BaseP11(Lb.get(j), L);
                                }
                            } else if (slen > pattern.length) {
                                boolean fl = false;
                                for (int m = 0; m < COPfre_number; m++) {
                                    //Lb_cop存放位置链表  fre_COP:是频繁的共生

                                    List<Integer> long_prefix = fre_COP.get(m);
                                    int b = 0;
                                    Double[] long_Prefixarr = new Double[long_prefix.size()];
                                    for (int c = 0; c < long_prefix.size(); c++) {
                                        long_Prefixarr[c] = Double.valueOf(long_prefix.get(c));
                                    }
                                    /*for (double item : prefix) {
                                        Prefixarr[b++] = item;
                                    }*/

                                    LNode long_Pnode = Lb_cop.get(m);
                                    if (Arrays.equals(Prefixarr, long_Prefixarr)) {
                                        grow_BaseP1NEW(Lb.get(j), L, long_Pnode);
                                        fl = true;
                                        break;
                                    }
                                }
                                if (!fl) {
                                    grow_BaseP1(Lb.get(j), L);

//                                    grow_BaseP11(Lb.get(j), L);
                                }
                            }


                            //L存的是作为前缀模式的支持度+索引位置，Lb.get(j)存的是作为后缀模式的支持度+索引位置
                            //  Lb.get(0)变成了 6->3->5->7->9->11->13->null  Lb.get(1)变成了 6->2->4->6->8->10->12->null
                            //L:6->3->5->7->9->11->13->null 作为前缀的支持度+索引位置

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
//                            Pre.add(fre.get(i));
//                            Suf.add(fre.get(j));
//                            cd_num = cd_num + 1;

                            if (slen < pattern.length) {
                                grow_BaseP1(Lb.get(j), L);
                            } else if (slen == pattern.length) {
                                if (Arrays.equals(Prefixarr, pattern)) {
                                    grow_BaseP1NEW(Lb.get(j), L, Pnode);
                                } else {

//                                    grow_BaseP11(Lb.get(j), L);

                                    grow_BaseP1(Lb.get(j), L);
                                }
                            } else if (slen > pattern.length) {
                                boolean fl = false;
                                for (int m = 0; m < COPfre_number; m++) {
                                    //Lb_cop存放位置链表  fre_COP:是频繁的共生

                                    List<Integer> long_prefix = fre_COP.get(m);
                                    int b = 0;
                                    Double[] long_Prefixarr = new Double[long_prefix.size()];
                                    for (int c = 0; c < long_prefix.size(); c++) {
                                        long_Prefixarr[c] = Double.valueOf(long_prefix.get(c));
                                    }
                                    for (double item : prefix) {
                                        Prefixarr[b++] = item;
                                    }

                                    LNode long_Pnode = Lb_cop.get(m);
                                    if (Arrays.equals(Prefixarr, long_Prefixarr)) {
                                        grow_BaseP1NEW(Lb.get(j), L, long_Pnode);
                                        fl = true;
                                        break;
                                    }
                                }
                                if (!fl) {

                                    grow_BaseP1(Lb.get(j), L);

//                                    grow_BaseP11(Lb.get(j), L);
                                }
                            }


                        }
                    }
                }
            }

        }
//    	Lb.clear();
//    	pos.clear();
//    	fre.clear();
        pattern_length += 1;

        return 0;

    }

    static int[] sort(List<Integer> src) {
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

    static void grow_BaseP1(LNode Ld, LNode L) {
        //L:6->3->5->7->9->11->13->null 作为前缀的支持度+索引位置
        // Lb.get(0)变成了 6->3->5->7->9->11->13->null  Lb.get(1)变成了 6->2->4->6->8->10->12->null
        //L存的是作为前缀模式的支持度+索引位置，Ld存的是作为后缀模式的支持度+索引位置

        LNode p = L;//p:6->3->5->7->9->11->13->null 作为前缀的支持度+索引位置
        LNode q = Ld;//q:6->3->5->7->9->11->13->null 作为后缀模式的支持度+索引位置
        Z.clear();//原来的Z:{3,5,7,9,11,13}

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
            element_num += 1;
        }

        L.data = L.data - Z.size();//L.data是此时的前缀长度
        Ld.data = Ld.data - Z.size();// Ld.data 是此时的后缀长度
        judge_fre(Z.size(), Cd, Z);//  Z.size()=0  Cd:(1,2,3)   Z：{}


    }

    static void grow_BaseP1NEW(LNode Ld, LNode L, LNode Pnode) {
        //L:6->3->5->7->9->11->13->null 作为前缀的支持度+索引位置
        // Lb.get(0)变成了 6->3->5->7->9->11->13->null  Lb.get(1)变成了 6->2->4->6->8->10->12->null
        //L存的是作为前缀模式的支持度+索引位置，Ld存的是作为后缀模式的支持度+索引位置
        LNode h = Pnode;

        LNode q = Ld;//q:6->3->5->7->9->11->13->null 作为后缀模式的支持度+索引位置

        W.clear();

        while (h.next != null && q.next != null) {
            if (q.next.data == h.next.data + 1) {
                W.add(q.next.data);
                h.next = h.next.next;
                q.next = q.next.next;
            } else if (h.next.data < q.next.data) {
                h = h.next;
            } else {
                q = q.next;
            }
            element_num += 1;
        }

        L.data = L.data - W.size();//L.data是此时的前缀长度
        Ld.data = Ld.data - W.size();// Ld.data 是此时的后缀长度
//        judge_fre(Z.size(), Cd, Z);//  Z.size()=0  Cd:(1,2,3)   Z：{}
        judge_freNEW(W.size(), Cd, W);
    }


    static void grow_BaseP2(int slen, LNode Ld, LNode L) {
        //Cd:(1,3,2)
        //Cd.size()-1=2,  Lb.get(j)是后缀的支持度和索引位置，L是前缀的支持度和索引位置
//slen=2 Ld:6->2->4->6->8->10->12->null
// L:6->3->5->7->9->11->13->null

        int lst, fri;
        LNode p = L;//p:6->3->5->7->9->11->13->null
        LNode q = Ld;//q:6->2->4->6->8->10->12->null

//        LNode h=Pnode;

        Z.clear();//原来的Z:{3,5,7,9,11,13}
        Z2.clear();//原来的Z2:{2,4,6,8,10,12}

//        W.clear();
//        W2.clear();

        while (p.next != null && q.next != null) {

            if (q.next.data == p.next.data + 1) {

                lst = q.next.data;//lst=4
                fri = lst - slen;//fri=4-2=2
                //有筛选
                if (in[lst - 1] > in[fri - 1]) {//S.get(3)=10 S.get(1)=8
                    Z.add(q.next.data);//Z:{4,6,8,12}
                } else if (in[lst - 1] < in[fri - 1]) {
                    Z2.add(q.next.data);//z2:{10}
                }
                p.next = p.next.next;
                q.next = q.next.next;

            } else if (p.next.data < q.next.data) {
                p = p.next;
            } else {
                q = q.next;
            }
            element_num += 1;

        }

        L.data = L.data - Z.size() - Z2.size();//L.data=6-4-1=1
        Ld.data = Ld.data - Z.size() - Z2.size();//Ld.data=6-4-1=1
        judge_fre(Z.size(), Cd, Z);//Z.size=4,  Cd:(1,3,2),  Z:{4,6,8,12}
        judge_fre(Z2.size(), Cd2, Z2);
    }

    static void grow_BaseP2NEW(int slen, LNode Ld, LNode L, LNode Pnode) {
        //Cd:(1,3,2)
        //Cd.size()-1=2,  Lb.get(j)是后缀的支持度和索引位置，L是前缀的支持度和索引位置
//slen=2 Ld:6->2->4->6->8->10->12->null
// L:6->3->5->7->9->11->13->null

        int lst, fri;

        LNode q = Ld;//q:6->2->4->6->8->10->12->null

        LNode h = Pnode;

        W.clear();
        W2.clear();

        while (h.next != null && q.next != null) {
            if (q.next.data == h.next.data + 1) {
                lst = q.next.data;
                fri = lst - slen;
                //有筛选
                if (in[lst - 1] > in[fri - 1]) {
                    W.add(q.next.data);
                } else if (in[lst - 1] < in[fri - 1]) {
                    W2.add(q.next.data);
                }
                h.next = h.next.next;
                q.next = q.next.next;
            } else if (h.next.data < q.next.data) {
                h = h.next;
            } else {
                q = q.next;
            }
            element_num += 1;
        }

        L.data = L.data - W.size() - W2.size();//L.data=6-4-1=1
        Ld.data = Ld.data - W.size() - W2.size();//Ld.data=6-4-1=1
        judge_freNEW(W.size(), Cd, W);
        judge_freNEW(W2.size(), Cd2, W2);
    }

    public static void judge_freNEW(int sup_num, List<Integer> Cd, List<Integer> Z) {//(5,(1,2),{3,5,7,9,11,13})
        // TODO Auto-generated method stub //(5,(2,1),{2,4,6,8,10,12})
        //Z.size=4,  Cd:(1,3,2),  Z:{4,6,8,12}
        if (sup_num >= minsup) {//5>=3

            List<Integer> Ztemp = new ArrayList<>();
            for (Integer integer : Z) {
                Ztemp.add(integer);//Ztemp:{3,5,7,9,11,13}
            }
//            Parr=Ztemp;
            PCOP.add(Ztemp);

            P.add(Ztemp);//P:{3,5,7,9,11,13}{2,4,6,8,10,12} P:Position
            //P:{4,6,8,12}
            List<Integer> Cdtemp = new ArrayList<>();
            for (Integer integer : Cd) {
                Cdtemp.add(integer);//Cdtemp:(1,2)
            }

           /* int i = 0;
            double[] Cdarr = new double[Cd.size()];
            for (double item : Cdtemp) {
                Cdarr[i++] = item;//Cdarr:(1,2)
            }
            pattern=Cdarr;*/
            LCOP.add(Cdtemp);

            L.add(Cdtemp);//L:(1,2)(2,1)

      /*      System.out.print("wz模式：");

            for (Integer Cdint : Cd) {
                System.out.print(Cdint + "  ");
            }
            System.out.print("  支持度为：" + sup_num);
            System.out.println();
            System.out.print("在字符串中出现的位置：");
            for (Integer Zint : Z) {
                System.out.print(Zint + "  ");
            }
            System.out.println(Z.size());
            System.out.println("-----------------");*/


//            COPfrequent_num++;

        }

    }

    public static void find() {
        int i = 0, j = 1;
        Cd.add(1);
        Cd.add(2);//Cd:{(1,2)}
        Cd2.add(2);
        Cd2.add(1);//Cd2:{(2,1)}
        while (j < in.length) {
            if (in[j] > in[i])   //12模式
            {
                Z.add(j + 1);//Z:{3,5,7,9,11,13}
            } else if (in[j] < in[i])                //21模式
            {
                Z2.add(j + 1);//Z2:{2,4,6,8,10,12}
            }
            i++;
            j++;
        }
        judge_fre(Z.size(), Cd, Z); //(6,(1,2),{3,5,7,9,11,13})
        Cd.clear();
        judge_fre(Z2.size(), Cd2, Z2);//(6,(2,1),{2,4,6,8,10,12})
        Cd2.clear();

        pattern_length += 2;

    }

    public static void judge_fre(int sup_num, List<Integer> Cd, List<Integer> Z) {//(5,(1,2),{3,5,7,9,11,13})
        // TODO Auto-generated method stub //(5,(2,1),{2,4,6,8,10,12})
        //Z.size=4,  Cd:(1,3,2),  Z:{4,6,8,12}
        if (sup_num >= minsup) {//5>=3

            List<Integer> Ztemp = new ArrayList<>();
            for (Integer integer : Z) {
                Ztemp.add(integer);//Ztemp:{3,5,7,9,11,13}
            }
            P.add(Ztemp);//P:{3,5,7,9,11,13}{2,4,6,8,10,12} P:Position
            //P:{4,6,8,12}
            List<Integer> Cdtemp = new ArrayList<>();
            for (Integer integer : Cd) {
                Cdtemp.add(integer);//Cdtemp:(1,2)
            }
            L.add(Cdtemp);//L:(1,2)(2,1)
            //l:(1,3,2)
          /*  System.out.print("频繁模式：");
            for (Integer Cdint : Cd) {
                System.out.print(Cdint + "  ");
            }
            System.out.print("  支持度为：" + sup_num);
			System.out.println();
            System.out.print("在字符串中出现的位置：");
            for (Integer Zint : Z) {
                System.out.print(Zint + "  ");
            }
            System.out.println(Z.size());
            System.out.println();*/

            if (Cd.size() == pattern.length) {
                int i = 0;
                Double[] Cdarr = new Double[Cd.size()];
                for (double item : Cd) {
                    Cdarr[i++] = item;//Cdarr:(1,2)
                }
                if (Arrays.equals(getOrder(Cdarr), getOrder(pattern))) {
//                int j = 0;
//                Integer[] Zarr = new Integer[Z.size()];
                    for (Integer item : Z) {
//                    Zarr[j++] = item;//Zarr:{3,5,7,9,11,13}
                        Parr.add(item);
                    }
                }

            }
//        else if (Cd.size() > pattern.length) {//Cd:(1,2)
//                //Cd:(1,3,2)
//                int i = 0;
//                double[] Cdarr = new double[Cd.size()];
//                for (double item : Cd) {
//                    Cdarr[i++] = item;//Cdarr:(1,2)
//                }
//                int j = 0;
//                Integer[] Zarr = new Integer[Z.size()];
//                for (Integer item : Z) {
//                    Zarr[j++] = item;//Zarr:{3,5,7,9,11,13}
//                }
//
//                Candidate candidateTo = new Candidate(Cdarr, Zarr);
//                candidateList.add(candidateTo);//candidateTo:(1,2),{3,5,7,9,11,13}
//            }

        }
    }

    private static double[] getOrder(double[] seq) {
        double[] arr = new double[seq.length];
        System.arraycopy(seq, 0, arr, 0, seq.length);
        double[] order = new double[arr.length];
        double[] temp = new double[arr.length];
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


    private static void patternFusionNew(Double[] P, List<Integer> PLocation, Map.Entry<String, List<Integer>> entryIn, LNode PNode) {
        int slen = P.length;
        String key = entryIn.getKey();
        Double[] Q = stringToArray(key);
        LNode QNode = getLNode(entryIn.getValue());
        if (PNode.data >= minsup && QNode.data >= minsup) {
            if (P[0].doubleValue() == Q[Q.length - 1].doubleValue()) {
                Double[] Cd = new Double[P.length + 1];
                Double[] Cd2 = new Double[P.length + 1];
                Cd[0] = P[0];
                Cd2[0] = P[0] + 1;
                Cd[slen] = P[0] + 1;
                Cd2[slen] = P[0];
                for (int t = 1; t < slen; t++) {
                    if (P[t] > Q[slen - 1]) {
                        //中间位置增长
                        //小的一行的中间位置和大的一行的最后一个数比较，大于+1，小于等于不变
                        Cd[t] = P[t] + 1;
                        Cd2[t] = P[t] + 1;
                    } else {
                        Cd[t] = P[t];//Cd:(1,3,2)
                        Cd2[t] = P[t];//Cd2:(2,1,3)
                    }
                }
//            LNode PNode = getLNode(PLocation);
//            LNode QNode = getLNode(entryIn.getValue());
                candNum += 2;
                grow_BaseP2(P.length, QNode, PNode, Cd, Cd2, false);
            } else if (P[0].doubleValue() < Q[Q.length - 1].doubleValue()) {
                Double[] Cd = new Double[P.length + 1];
                Cd[0] = P[0];//小的不变  （1,0,0）
                Cd[slen] = Q[slen - 1] + 1;//大的加一 1,0,3）
                for (int t = 1; t < slen; t++) {
                    if (P[t] > Q[slen - 1]) {
                        //中间位置增长
                        //小的一行的中间位置和大的一行的最后一个数比较，大于+1，小于等于不变
                        Cd[t] = P[t] + 1;

                    } else {
                        Cd[t] = P[t];
                    }
                }
//            LNode PNode = getLNode(PLocation);
//            LNode QNode = getLNode(entryIn.getValue());
                candNum++;
                grow_BaseP1(QNode, PNode, Cd, false);
            } else {
                Double[] Cd = new Double[P.length + 1];
                Cd[0] = P[0] + 1; // 大的加一
                Cd[slen] = Q[slen - 1]; // 小的不变
                for (int t = 0; t < slen - 1; t++) {
                    if (Q[t] > P[0]) {
                        // 中间位置增长
                        Cd[t + 1] = Q[t] + 1;
                    } else {
                        Cd[t + 1] = Q[t];
                    }
                }
//            LNode PNode = getLNode(PLocation);
//            LNode QNode = getLNode(entryIn.getValue());
                candNum++;
                grow_BaseP1(QNode, PNode, Cd, false);
            }
        }
    }

    private static void patternFusion(Double[] P, List<Integer> pList) {
        int slen = P.length;
        LNode PNode = getLNode(pList);
        for (Map.Entry<String, List<Integer>> entry : map.entrySet()) {
            String key = entry.getKey();
            Double[] Q = stringToArray(key);
            LNode QNode = getLNode(entry.getValue());
            if (PNode.data >= minsup && QNode.data >= minsup) {
                if (P[0].doubleValue() == Q[Q.length - 1].doubleValue()) {
                    Double[] Cd = new Double[P.length + 1];
                    Double[] Cd2 = new Double[P.length + 1];
                    Cd[0] = P[0];
                    Cd2[0] = P[0] + 1;
                    Cd[slen] = P[0] + 1;
                    Cd2[slen] = P[0];
                    for (int t = 1; t < slen; t++) {
                        if (P[t] > Q[slen - 1]) {
                            //中间位置增长
                            //小的一行的中间位置和大的一行的最后一个数比较，大于+1，小于等于不变
                            Cd[t] = P[t] + 1;
                            Cd2[t] = P[t] + 1;
                        } else {
                            Cd[t] = P[t];//Cd:(1,3,2)
                            Cd2[t] = P[t];//Cd2:(2,1,3)
                        }
                    }
//                LNode PNode = getLNode(pList);
//                LNode QNode = getLNode(entry.getValue());
                    candNum += 2;
                    grow_BaseP2(P.length, QNode, PNode, Cd, Cd2, true);
                } else if (P[0].doubleValue() < Q[Q.length - 1].doubleValue()) {
                    Double[] Cd = new Double[P.length + 1];
                    Cd[0] = P[0];//小的不变  （1,0,0）
                    Cd[slen] = Q[slen - 1] + 1;//大的加一 1,0,3）
                    for (int t = 1; t < slen; t++) {
                        if (P[t] > Q[slen - 1]) {
                            //中间位置增长
                            //小的一行的中间位置和大的一行的最后一个数比较，大于+1，小于等于不变
                            Cd[t] = P[t] + 1;

                        } else {
                            Cd[t] = P[t];
                        }
                    }
//                LNode PNode = getLNode(pList);
//                LNode QNode = getLNode(entry.getValue());
                    candNum++;
                    grow_BaseP1(QNode, PNode, Cd, true);
                } else {
                    Double[] Cd = new Double[P.length + 1];
                    Cd[0] = P[0] + 1; // 大的加一
                    Cd[slen] = Q[slen - 1]; // 小的不变
                    for (int t = 0; t < slen - 1; t++) {
                        if (Q[t] > P[0]) {
                            // 中间位置增长
                            Cd[t + 1] = Q[t] + 1;
                        } else {
                            Cd[t + 1] = Q[t];
                        }
                    }
//                LNode PNode = getLNode(pList);
//                LNode QNode = getLNode(entry.getValue());
                    candNum++;
                    grow_BaseP1(QNode, PNode, Cd, true);
                }
            }

        }
    }

    private static void grow_BaseP1(LNode qNode, LNode pNode, Double[] Cd, boolean isFirst) {
        List<Integer> Z = new ArrayList<>();
        LNode p = pNode;//p:6->3->5->7->9->11->13->null 作为前缀的支持度+索引位置
        LNode q = qNode;//q:6->3->5->7->9->11->13->null 作为后缀模式的支持度+索引位置

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
            element_num++;
        }
        pNode.data = pNode.data - Z.size();
        qNode.data = qNode.data - Z.size();
        if (isFirst) {
            if (Z.size() >= minsup) {
                freNum++;
//                System.out.println("共生模式：" + Arrays.toString(Cd) + ", sup:" + Z.size() + ": " + Z.toString());
                mapV2.put(Arrays.toString(Cd), Z);
            }
        } else {
            if (Z.size() >= minsup) {
                freNum++;
//                System.out.println("共生模式：" + Arrays.toString(Cd) + ", sup:" + Z.size() + ": " + Z.toString());
                mapV4.put(Arrays.toString(Cd), Z);
            }
        }
    }

    private static void grow_BaseP2(int slen, LNode qNode, LNode pNode, Double[] Cd, Double[] Cd2, boolean isFirst) {
        List<Integer> Z = new ArrayList<>();
        List<Integer> Z2 = new ArrayList<>();
        int lst, fri;
        LNode p = pNode;//p:6->3->5->7->9->11->13->null
        LNode q = qNode;//q:6->2->4->6->8->10->12->null

        while (p.next != null && q.next != null) {

            if (q.next.data == p.next.data + 1) {
                lst = q.next.data;//lst=4
                fri = lst - slen;//fri=4-2=2
                //有筛选
                if (in[lst - 1] > in[fri - 1]) {//S.get(3)=10 S.get(1)=8
                    Z.add(q.next.data);//Z:{4,6,8,12}
                } else if (in[lst - 1] < in[fri - 1]) {
                    Z2.add(q.next.data);//z2:{10}
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
        qNode.data = qNode.data - Z.size() - Z2.size();
        if (isFirst) {
            if (Z.size() >= minsup) {
                freNum++;
//                System.out.println("共生模式：" + Arrays.toString(Cd) + ", sup:" + Z.size() + ": " + Z.toString());
                mapV2.put(Arrays.toString(Cd), Z);
            }
            if (Z2.size() >= minsup) {
                freNum++;
//                System.out.println("共生模式：" + Arrays.toString(Cd2) + ", sup:" + Z2.size() + ": " + Z2.toString());
                mapV2.put(Arrays.toString(Cd2), Z2);
            }
        } else {
            if (Z.size() >= minsup) {
                freNum++;
//                System.out.println("共生模式：" + Arrays.toString(Cd) + ", sup:" + Z.size() + ": " + Z.toString());
                mapV4.put(Arrays.toString(Cd), Z);
            }
            if (Z2.size() >= minsup) {
                freNum++;
//                System.out.println("共生模式：" + Arrays.toString(Cd2) + ", sup:" + Z2.size() + ": " + Z2.toString());
                mapV4.put(Arrays.toString(Cd2), Z2);
            }
        }
    }

    private static LNode getLNode(List<Integer> pList) {
        LNode PNode = new LNode();
        PNode.data = pList.size();
        LNode p = new LNode();//p是节点
        LNode s = new LNode();//s是节点
        s = PNode;
        for (Integer val : pList) {
            p = new LNode();
            p.data = val;
            s.next = p;
            s = p;
        }
        s.next = null;
        return PNode;
    }

    private static Double[] stringToArray(String key) {
        key = key.substring(1, key.length() - 1);
        String[] str = key.split(",");
        Double[] arr = new Double[str.length];
        for (int i = 0; i < str.length; i++) {
            arr[i] = Double.valueOf(str[i].trim());
        }
        return arr;
    }

    private static Double[] getCompareOrder(Double[] sub, Double[] order, Double value, boolean isSuf) {
        if (Arrays.asList(sub).contains(value)) {
            return null;
        }
        double rank = 1;
        Double[] orderNew = new Double[order.length + 1];
        if (isSuf) {
            for (int i = 0; i < order.length; i++) {
                if (sub[i] > value) {
                    orderNew[i] = order[i] + 1;
                } else {
                    orderNew[i] = order[i];
                    rank++;
                }
            }
            orderNew[orderNew.length - 1] = rank;
            return orderNew;
        } else {
            for (int i = 0; i < order.length; i++) {
                if (sub[i] > value) {
                    orderNew[i + 1] = order[i] + 1;
                } else {
                    orderNew[i + 1] = order[i];
                    rank++;
                }
            }
            orderNew[0] = rank;
            return orderNew;
        }
    }

    private static Integer[] getPSufLocation(Double[] pSuf) {
       /*  List<Integer> subsetNumList =new ArrayList<>();
       for (int i = 0; i <= (in.length - pSuf.length); i++) {
            Double[] sub = new Double[pSuf.length];
            System.arraycopy(in, i, sub, 0, sub.length);
            Double[] pSufOrder=getOrder(pSuf);
            HashSet<Double> hashSet = new HashSet<Double>();
            for (int j = 0; j < sub.length; j++) {
                hashSet.add(sub[j]);
            }
            if (hashSet.size() == sub.length) {
                if (Arrays.equals(getOrder(sub), pSufOrder)) {
                    subsetNumList.add(i+pSuf.length);
                }
            } else {
                continue;
            }


        }
        Integer[] subsetNumArr = new Integer[subsetNumList.size()];
        subsetNumList.toArray(subsetNumArr);
        return subsetNumArr;*/

        Integer[] subsetNumArr;
        if (pSuf.length == 2) {
            int[] inBinaryArr = getBinary(in);
            int[] pBinaryArr = getBinary(pSuf);
            subsetNumArr = bndm(inBinaryArr, pBinaryArr);
//            subsetNumArr = getSubset(in, pSuf);
        } else {
            int[] inBinaryArr = getBinary(in);
            int[] pBinaryArr = getBinary(pSuf);
            int[] sortedP = new int[pBinaryArr.length];
            System.arraycopy(pBinaryArr, 0, sortedP, 0, sortedP.length);
            Arrays.sort(sortedP);
            int[] aux = new int[pBinaryArr.length];
            genAux(aux, sortedP, pBinaryArr);
            subsetNumArr = sbndm(inBinaryArr, pBinaryArr, aux, in);
        }
        Integer[] subsetNumArrNew;
        if (pSuf.length == 2) {
            subsetNumArrNew = subsetNumArr;
        } else {
            subsetNumArrNew = verificationStrategy(in, pSuf, subsetNumArr);
        }
        /*for (int i = 0; i < subsetNumArrNew.length; i++) {
            subsetNumArrNew[i] = subsetNumArrNew[i] + pSuf.length;
        }
*/
        return subsetNumArrNew;

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


    private static Integer[] verificationStrategy(Double[] in, Double[] pattern, Integer[] subsetNumArr) {
        List<Integer> subsetListNew = new ArrayList<>();
        List<SupportOrder> supportOrderList = new ArrayList<>();
        int index = 1;
        for (double order : pattern) {
            SupportOrder supportOrder = new SupportOrder(order, index++);
            supportOrderList.add(supportOrder);
        }
        supportOrderList.sort(Comparator.comparingDouble(SupportOrder::getOrder));
        int[] indexArr = new int[supportOrderList.size()];
        int sub = 0;
        for (SupportOrder supportOrder : supportOrderList) {
            indexArr[sub++] = supportOrder.index;
        }
        for (Integer value : subsetNumArr) {
            boolean flag = false;
            for (int i = 0; i < indexArr.length - 1; i++) {
                if (in[value - 1 + indexArr[i]] >= in[value - 1 + indexArr[i + 1]]) {
                    flag = true;
                    break;
                }
            }
            if (!flag) {
                subsetListNew.add(value + pattern.length);
            }
        }
        Integer[] subsetNumArrNew = new Integer[subsetListNew.size()];
        subsetListNew.toArray(subsetNumArrNew);
        return subsetNumArrNew;
    }

    private static Integer[] sbndm(int[] txt, int[] pat, int[] aux, Double[] s) {
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
                        if (s[cand - 1 + aux[k]] >= s[cand - 1 + aux[k + 1]]) {
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

    private static void genAux(int[] aux, int[] sortedP, int[] p) {
        for (int i = 0; i < p.length; i++) {
            for (int j = 0; j < p.length; j++) {
                if (sortedP[i] == p[j]) {
                    aux[i] = j + 1;
                }
            }
        }
    }

    private static int[] getBinary(Double[] arr) {
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

    private static Integer[] getSubset(Double[] in, Double[] pSuf) {
        Double[] pOrder = getOrder(pSuf);
        List<Integer> subsetNumList = new ArrayList<>();
        if (Arrays.equals(pOrder, oneTwo)) {
            for (int i = 0; i < in.length - 1; i++) {
                if (in[i + 1] > in[i]) {
                    subsetNumList.add(i);
                }
            }
        } else {
            for (int i = 0; i < in.length - 1; i++) {
                if (in[i + 1] < in[i]) {
                    subsetNumList.add(i);
                }
            }
        }
        Integer[] subsetNumArr = new Integer[subsetNumList.size()];
        subsetNumList.toArray(subsetNumArr);
        return subsetNumArr;
    }

    private static List<Integer> getOrderInt(Double[] seq) {
        Double[] arr = new Double[seq.length];
        System.arraycopy(seq, 0, arr, 0, seq.length);
        Double[] order = new Double[arr.length];
        Double[] temp = new Double[arr.length];
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
            arr[index] = (double) Integer.MIN_VALUE;
            order[index] = j + 1D;
        }
        List<Integer> list = new ArrayList<>();
        for (Double d : order){
            list.add(d.intValue());
        }
        return list;
    }

    private static Double[] getOrder(Double[] seq) {
        Double[] arr = new Double[seq.length];
        System.arraycopy(seq, 0, arr, 0, seq.length);
        Double[] order = new Double[arr.length];
        Double[] temp = new Double[arr.length];
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
            arr[index] = (double) Integer.MIN_VALUE;
            order[index] = j + 1D;
        }
        return order;
    }

    private static Double[] getPatternExtreme(Double[] p) {
        List<Double> list = new ArrayList<>();
        list.add(p[0]);
        for (int i = 1; i < p.length - 1; i++) {
            if ((p[i] >= p[i - 1] && p[i] > p[i + 1]) || (p[i] > p[i - 1] && p[i] >= p[i + 1])) {
                list.add(p[i]);
            } else if ((p[i] <= p[i - 1] && p[i] < p[i + 1]) || (p[i] < p[i - 1] && p[i] <= p[i + 1])) {
                list.add(p[i]);
            }
        }
        list.add(p[p.length - 1]);
        int i = 0;
        Double[] arr = new Double[list.size()];
        for (double item : list) {
            arr[i++] = item;
        }
        return arr;
    }

    private static Double[] getExtremePoint(Double[] input) {
        List<Double> list = new ArrayList<>();
        list.add(input[0]);
        int k = 1;
        for (int i = 1; i < input.length - 1; i++) {
            if ((input[i] >= input[i - 1] && input[i] > input[i + 1]) || (input[i] > input[i - 1] && input[i] >= input[i + 1])) {
                list.add(input[i]);
            } else if ((input[i] <= input[i - 1] && input[i] < input[i + 1]) || (input[i] < input[i - 1] && input[i] <= input[i + 1])) {
                list.add(input[i]);
            }
        }
        list.add(input[input.length - 1]);
        int i = 0;
        Double[] arr = new Double[list.size()];
        for (double item : list) {
            arr[i++] = item;
        }
        return arr;
    }

    static class SupportOrder {
        private double order;
        private Integer index;

        SupportOrder(double order, Integer index) {
            this.order = order;
            this.index = index;
        }

        public double getOrder() {
            return order;
        }

        public void setOrder(double order) {
            this.order = order;
        }

        public Integer getIndex() {
            return index;
        }

        public void setIndex(Integer index) {
            this.index = index;
        }
    }

    static class LNode {
        int data;
        LNode next = null;
        boolean flag = false;

    }
}
