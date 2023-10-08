package COP_Mining;

import newalgorithm.MemoryLogger;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.*;
import java.util.stream.Collectors;

public class COP_kom {

    private static Double[] input;
    private static Double[] in;
//    private static Double[] p = new Double[]{3.0, 6.0, 4.0, 5.0, 1.0, 2.0};
//private static Double[] p = new Double[]{1D,3D,2D,5D,4D,6D};
//private static Double[] p = new Double[]{4D,5D,2D,3D,1D,6D};
//private static Double[] p = new Double[]{1.0, 5.0, 2.0, 6.0, 3.0, 4.0};
//private static Double[] p = new Double[]{1.0, 5.0, 3.0, 4.0, 2.0, 6.0};
//private static Double[] p = new Double[]{1.0, 4.0, 3.0,6.0,5.0, 2.0};
//private static Double[] p = new Double[]{4.0, 3.0, 6.0, 2.0, 5.0, 1.0};

//    private static Double[] p = new Double[]{5D, 3D, 7D, 13D};
    //private static Double[] p = new Double[]{5.0,2.0,4.0};
//private static Double[] p = new Double[]{5.0,2.0,4.0,1.0};
//private static Double[] p = new Double[]{2D,3D,1D,4D};
//    private static Double[] p = new Double[]{1D,4D,2D,3D};
//private static Double[] p = new Double[]{1.0, 5.0, 2.0};
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

//    private static Double[] p = new Double[]{2D,1D,4D,3D,6D,5D,8D,7D};
    private static Double[] pattern = getPatternExtreme(p);

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
//        File file = new File("E:/Dataset/分类/CinCECGTorso_TRAIN.txt");
//        File file = new File("E:/Dataset/ChengduPM2.5.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5.txt");
//        File file = new File("E:/Dataset/PRSA_Data.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_HeartRate.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_PRInterval.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_PAxis.txt");

//        File file = new File("E:/Dataset/分类/ShapeletSim_TEST.txt");
//        File file = new File("E:/Dataset/test.txt");

//        File file = new File("E:/Dataset/1WTl-2.txt");

//        File file = new File("E:/Dataset/分类/CSSE COVID-19.txt");
//        File file = new File("E:/Dataset/分类/BTC.txt");
//        File file = new File("E:/Dataset/分类/Beef_TEST.txt");
//        File file = new File("E:/Dataset/分类/Car_TEST.txt");
//        File file = new File("E:/Dataset/FiveCitiesTempData.txt");
//        File file = new File("E:/Dataset/Data-Stock.txt");
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
//        File file = new File("E:/Dataset/分类/ShapeletSim_TEST.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5.txt");
//        File file = new File("E:/Dataset/PRSA_Data.txt");
//        File file = new File("E:/Dataset/ToeSegmentation1_TRAIN.txt");

//        File file = new File("E:/Dataset/test.txt");
//        File file = new File("E:/Dataset/Meat_TEST.txt");

        BufferedReader br = new BufferedReader(new FileReader(file));
        String s;
        //使用readLine方法，一次读一行
        while ((s = br.readLine()) != null) {
            List<Double> inList = new ArrayList<>();
            s = s.trim();
            String[] str = s.split(" ");
            String[] strArr = new String[str.length - 1];
            System.arraycopy(str, 1, strArr, 0, strArr.length);
            for (String s1 : strArr) {
                if (!" ".equals(s1) && !s1.isEmpty()) {
                    inList.add(Double.parseDouble(s1));
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
//            System.out.println("共生频繁模式的总数为：" + freNum);

        }
        br.close();
    }

    /*private static void readLine() {
        map = new HashMap<>();
        mapV2 = new HashMap<>();
//        mapV3 = new HashMap<>();
        mapV4 = new HashMap<>();
        Double[] pSuf = new Double[pattern.length - 1];
        System.arraycopy(pattern, 1, pSuf, 0, pSuf.length);
//        Integer[] subsetNumArr = getPSufLocation(pSuf);
        List<Integer> subsetNumArr = KMPOrderMatcher(in, getOrderList(pSuf));
        if (subsetNumArr.size() < minsup){
//            System.out.println("P后缀不满足支持度！！！");
            return;
        }
        List<Integer> pList = new ArrayList<>();
        for (Integer val : subsetNumArr){
            Double[] sub = new Double[pSuf.length];
            System.arraycopy(in, val - pSuf.length, sub, 0, sub.length);
            //求P的出现
            if (val > pSuf.length){
                Double[] patternOrder = getCompareOrder(sub, getOrder(pSuf), in[val - pSuf.length - 1], false);
                if (patternOrder != null){
                    if (Arrays.equals(pOrder, patternOrder)){
                        pList.add(val);
                    }
                }
            }

            //求pSuf后缀出现
            if (val < in.length){
                Double[] pSufSufOrder = getCompareOrder(sub, getOrder(pSuf), in[val], true);
                if (pSufSufOrder != null){
                    List<Integer> list = map.get(Arrays.toString(pSufSufOrder));
                    if (list != null){
                        list.add(val + 1);
                        map.put(Arrays.toString(pSufSufOrder), list);
                    } else {
                        list = new ArrayList<>();
                        list.add(val + 1);
                        map.put(Arrays.toString(pSufSufOrder), list);
                    }
                }
            }
        }
        map = map.entrySet().stream().filter(x -> x.getValue().size() >= minsup).collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
        patternFusion(pOrder, pList);
        while (mapV2 != null && mapV2.size() > 0){
            for (Map.Entry<String, List<Integer>> entry : mapV2.entrySet()){
                String key = entry.getKey();
                Double[] P = stringToArray(key);
                List<Integer> PLocation = entry.getValue();
                Double[] PSuf = new Double[P.length - 1];
                System.arraycopy(P, 1, PSuf, 0, PSuf.length);
                List<Integer> PSufLocation = map.get(Arrays.toString(getOrder(PSuf)));
                if (PSufLocation == null || PSufLocation.size() == 0){
                    continue;
                }
                Map<String, List<Integer>> mapIn = new HashMap<>();
                for (Integer val : PSufLocation){
                    Double[] sub = new Double[PSuf.length];
                    System.arraycopy(in, val - PSuf.length, sub, 0, sub.length);
                    //求PSuf后缀出现
                    if (val < in.length){
                        Double[] PSufSufOrder = getCompareOrder(sub, getOrder(PSuf), in[val], true);
                        if (PSufSufOrder != null){
                            List<Integer> list = mapIn.get(Arrays.toString(PSufSufOrder));
                            if (list != null){
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
                map.putAll(mapIn);
                for (Map.Entry<String, List<Integer>> entryIn : mapIn.entrySet()){
                    patternFusionNew(P, PLocation, entryIn);
                }
            }
            mapV2 = mapV4;
            mapV4 = new HashMap<>();
//            map = mapV3;
//            mapV3 = new HashMap<>();
        }

        int i = 0;
    }*/

    private static void readLine() {
        map = new HashMap<>();
        mapV2 = new HashMap<>();
        mapV3 = new HashMap<>();
        mapV4 = new HashMap<>();
        occMap = new HashMap<>();
        Double[] pSuf = new Double[pattern.length - 1];
        System.arraycopy(pattern, 1, pSuf, 0, pSuf.length);
        List<Integer> subsetNumArr = KMPOrderMatcher(in, getOrderList(pSuf));
        if (subsetNumArr.size()< minsup) {
//            System.out.println("P后缀不满足支持度！！！");
            return;
        }
        List<Integer> pList = new ArrayList<>();
        for (Integer val : subsetNumArr) {
            Double[] sub = new Double[pSuf.length];
            System.arraycopy(in, val - pSuf.length, sub, 0, sub.length);
            //求P的出现
            if (val > pSuf.length) {
                Double[] patternOrder = getCompareOrder(sub, getOrder(pSuf), in[val - pSuf.length - 1], false);
                if (patternOrder != null) {
                    if (Arrays.equals(pOrder, patternOrder)) {
                        pList.add(val);
                    }
                }
            }

            //求pSuf后缀出现
            if (val < in.length) {
                Double[] pSufSufOrder = getCompareOrder(sub, getOrder(pSuf), in[val], true);
                if (pSufSufOrder != null) {
                    List<Integer> list = map.get(Arrays.toString(pSufSufOrder));
                    if (list != null) {
                        list.add(val + 1);
                        map.put(Arrays.toString(pSufSufOrder), list);
                    } else {
                        list = new ArrayList<>();
                        list.add(val + 1);
                        map.put(Arrays.toString(pSufSufOrder), list);
                    }
                }
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
                if (PSufLocation == null || PSufLocation.size() == 0) {
                    continue;
                }
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


    private static List<Integer> getOrderList(Double[] pSuf) {
        Double[] order = getOrder(pSuf);
        List<Integer> list = new ArrayList<>();
        for (Double d : order){
            list.add(d.intValue());
        }
        return list;
    }

    /*private static void patternFusionNew(Double[] P, List<Integer> PLocation, Map.Entry<String, List<Integer>> entryIn) {
        int slen = P.length;
        String key = entryIn.getKey();
        Double[] Q = stringToArray(key);
        if (P[0].doubleValue() == Q[Q.length - 1].doubleValue()){
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
            LNode PNode = getLNode(PLocation);
            LNode QNode = getLNode(entryIn.getValue());
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
            LNode PNode = getLNode(PLocation);
            LNode QNode = getLNode(entryIn.getValue());
            candNum ++;
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
            LNode PNode = getLNode(PLocation);
            LNode QNode = getLNode(entryIn.getValue());
            candNum ++;
            grow_BaseP1(QNode, PNode, Cd, false);
        }
    }
*/

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


/*    private static void patternFusion(Double[] P, List<Integer> pList) {
        int slen = P.length;
        for (Map.Entry<String, List<Integer>> entry : map.entrySet()){
            String key = entry.getKey();
            Double[] Q = stringToArray(key);
            if (P[0].doubleValue() == Q[Q.length - 1].doubleValue()){
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
                LNode PNode = getLNode(pList);
                LNode QNode = getLNode(entry.getValue());
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
                LNode PNode = getLNode(pList);
                LNode QNode = getLNode(entry.getValue());
                candNum ++;
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
                LNode PNode = getLNode(pList);
                LNode QNode = getLNode(entry.getValue());
                candNum ++;
                grow_BaseP1(QNode, PNode, Cd, true);
            }
        }
    }*/

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
        if (isFirst){
            if (Z.size() >= minsup){
                freNum++;
//                System.out.println("共生模式：" + Arrays.toString(Cd) + ", sup:" + Z.size() + ": " + Z.toString());
                mapV2.put(Arrays.toString(Cd), Z);
            }
        } else {
            if (Z.size() >= minsup){
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
        if (isFirst){
            if (Z.size() >= minsup){
                freNum++;
//                System.out.println("共生模式：" + Arrays.toString(Cd) + ", sup:" + Z.size() + ": " + Z.toString());
                mapV2.put(Arrays.toString(Cd), Z);
            }
            if (Z2.size() >= minsup){
                freNum++;
//                System.out.println("共生模式：" + Arrays.toString(Cd2) + ", sup:" + Z2.size() + ": " + Z2.toString());
                mapV2.put(Arrays.toString(Cd2), Z2);
            }
        } else {
            if (Z.size() >= minsup){
                freNum++;
//                System.out.println("共生模式：" + Arrays.toString(Cd) + ", sup:" + Z.size() + ": " + Z.toString());
                mapV4.put(Arrays.toString(Cd), Z);
            }
            if (Z2.size() >= minsup){
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
        for (Integer val : pList){
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
        for (int i = 0; i < str.length; i++){
            arr[i] = Double.valueOf(str[i].trim());
        }
        return arr;
    }

    private static Double[] getCompareOrder(Double[] sub, Double[] order, Double value, boolean isSuf) {
        if (Arrays.asList(sub).contains(value)){
            return null;
        }
        double rank = 1;
        Double[] orderNew = new Double[order.length + 1];
        if (isSuf){
            for (int i = 0; i < order.length; i++){
                if (sub[i] > value){
                    orderNew[i] = order[i] + 1;
                } else {
                    orderNew[i] = order[i];
                    rank++;
                }
            }
            orderNew[orderNew.length - 1] = rank;
            return orderNew;
        } else {
            for (int i = 0; i < order.length; i++){
                if (sub[i] > value){
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

    public static List<Integer> KMPOrderMatcher(Double[] series, List<Integer> enumOne) {
        int[] enumArr = new int[enumOne.size()];
        for (int i = 0; i < enumOne.size(); i++){
            enumArr[i] = enumOne.get(i);
        }
        int n = series.length;
        int m = enumArr.length;
        List<Integer> supportList = new ArrayList<>();
        List<Integer> μ = new ArrayList<>();
        List<Integer> π = new ArrayList<>();
        int support = 0;
//		int n = series.length;
//		int m = pattern.length;
        μ = computePrefixRep(enumArr, m);
		/*System.out.print("μ[P]: ");
		for (Integer r : μ) {
			System.out.print(r+",");
		}
		System.out.println();*/
        π = computeFailureFunction(enumArr, m);
		/*System.out.print("π[P]: ");
		for (Integer r : π) {
			System.out.print(r+",");
		}
		System.out.println();*/
        OrderStatisticTree tree = new OrderStatisticTree();
        int q = 0;
        int r = 0;
        double key;
        int i = 0;
        int k = 0;
        for (; i < n; i++) {
            key = series[i];

            if (tree.search(key) == tree.nil) {
                tree.insert(new OrderStatisticTree.Node(key));
                r = tree.rank(tree.search(key));
                k++;
            } else {
                i = i - k;
                q = -1;
                k = 0;
                tree = new OrderStatisticTree();
            }
            while (q > 0 && r != μ.get(q)) {
//				i = i - π.get(q-1) - 1;
                i = i - k + 1;
                q = -1;
                k = 0;
                tree = new OrderStatisticTree();
            }
            q = q + 1;
            if (q == m) {
//				System.out.println("pattern occurs at position "+(i+1));
                support++;
                supportList.add(i + 1);
//				i = i - π.get(q-1);
                i = i - k + 1;
                q = 0;
                k = 0;
                tree = new OrderStatisticTree();
            }

        }

        return supportList;

    }

    public static List<Integer> computePrefixRep(int[] pattern, int m) {
        List<Integer> rank = new ArrayList<>();
//		int m = pattern.length;
        OrderStatisticTree tree = new OrderStatisticTree();
        rank.add(0, 1);
        int key = pattern[0];
        if (tree.search(key) == tree.nil) {
            tree.insert(new OrderStatisticTree.Node(key));
        }
        for (int i = 1; i < m; i++) {
            key = pattern[i];
            if (key == 0) {
                break;
            }
            if (tree.search(key) == tree.nil) {
                tree.insert(new OrderStatisticTree.Node(key));
            }
            rank.add(i, tree.rank(tree.search(key)));
        }

        return rank;
    }

    public static List<Integer> computeFailureFunction(int[] pattern, int m) {
        List<Integer> πTemp = new ArrayList<>();
//		int m = pattern.length;
        int k = 0;
        if (m >= 2) {
            πTemp.add(0, 0);
            πTemp.add(1, 1);
        }
        for (int q = 2; q < m; q++) {
            int position = 0;
            for (k = 0; k < q; k++) {
                List<Integer> pre = new ArrayList<>();
                List<Integer> suf = new ArrayList<>();
                for (int j = 0; j <= k; j++) {
                    pre.add(pattern[j]);
                }
                for (int j = q - k; j <= q; j++) {
                    suf.add(pattern[j]);
                }
                int[] preRank = new int[pre.size()];
                int[] sufRank = new int[suf.size()];
                preRank = sort(pre);
                sufRank = sort(suf);
                if (!Arrays.equals(preRank, sufRank)) {
                    position = k;
                    break;
                }
            }
            if (k >= q) {
                position = k;
            }
            πTemp.add(q, position);
        }

        return πTemp;
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

    private static Integer[] getPSufLocation(Double[] pSuf) {
        Integer[] subsetNumArr;
        if (pSuf.length == 2) {
            //subsetNumArr = bndm(inBinaryArr, pBinaryArr);
            subsetNumArr = getSubset(in, pSuf);
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
        for(int i = 0; i < subsetNumArrNew.length; i++){
            subsetNumArrNew[i] = subsetNumArrNew[i] + pSuf.length;
        }
        return subsetNumArrNew;
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
                subsetListNew.add(value);
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

    public static class OrderStatisticTree {
        /**
         * 颜色
         */
        public enum Color {RED, BLACK}

        ;

        /**
         * 数据节点
         */
        public static class Node {
            double key;
            Node parent; //父节点
            Node left; //左子节点
            Node right; //右子节点
            Color color; //节点颜色
            int size; //所在子树节点的数量

            public Node(double key2) {
                this.key = key2;
            }

            @Override
            public String toString() {
                return String.valueOf(key);
            }
        }

        public static Node root; //根节点
        public static Node nil; //空节点

        /**
         * 构造函数
         */
        public OrderStatisticTree() {
            nil = new Node(-1);
            nil.color = Color.BLACK;
            root = nil;
        }

        /**
         * 计算节点x的序号。
         *
         * @param x 待查找节点
         * @return 节点x在树中从小到大排序的序号。
         */
        public int rank(Node x) {
            int r = x.left.size + 1; //当前节点在以x为根的子树中的序号是左子树的节点个数加1
            Node y = x;
            while (y != root) {
                if (y == y.parent.right) { //如果y是右子节点
                    r = r + y.parent.left.size + 1; //序号需要加上左兄弟子树的数量，再加父节点
                }
                y = y.parent;
            }
            return r;
        }

        /**
         * 左旋转。
         *
         * @param x 支点
         */
        private void leftRotate(Node x) {
            Node y = x.right; // y是x的右子节点
            x.right = y.left; // y的左子树转换成x的右子树
            if (y.left != nil) {
                y.left.parent = x;
            }
            y.parent = x.parent; // 用y替换x的位置
            if (x.parent == nil) {
                root = y;
            } else if (x == x.parent.left) {
                x.parent.left = y;
            } else {
                x.parent.right = y;
            }

            y.left = x; // 将x设置为y的左子节点
            x.parent = y;
            y.size = x.size; //y替代x的位置
            x.size = x.left.size + x.right.size + 1; //重新计算x
        }

        /**
         * 右旋转。
         *
         * @param y 支点
         */
        private void rightRotate(Node y) {
            Node x = y.left; // x是y的右子节点
            y.left = x.right; // x的右子树转换成y的左子树
            if (x.right != nil) {
                x.right.parent = y;
            }
            x.parent = y.parent; // 用x替换y的位置
            if (y.parent == nil) {
                root = x;
            } else if (y == y.parent.left) {
                y.parent.left = x;
            } else {
                y.parent.right = x;
            }

            x.right = y; // 将y设置为x的右子节点
            y.parent = x;
            x.size = y.size; //x替换y的位置
            y.size = y.left.size + y.right.size + 1; //重新计算y
        }

        /**
         * 采用递归法查找键值为k的节点。
         *
         * @param k 节点的键值
         * @return 返回键值为k的节点
         */
        public Node search(double k) {
            return search(root, (double) k);
        }

        /**
         * 采用递归法查找键值为k的节点。
         *
         * @param x 当前节点
         * @param k 节点的键值
         * @return 返回键值为k的节点
         */
        private Node search(Node x, double k) {
            if (x == nil || k == x.key) {
                return x;
            } else if (k < x.key) {
                return search(x.left, k);
            } else {
                return search(x.right, k);
            }
        }

        /**
         * 采用迭代法查找键值为k的节点。
         *
         * @param k 节点的键值
         * @return 返回键值为k的节点
         */
        public Node iterativeSearch(float k) {
            return iterativeSearch(root, k);
        }

        /**
         * 采用迭代法查找键值为k的节点。
         *
         * @param x 当前节点
         * @param k 节点的键值
         * @return 返回键值为k的节点
         */
        private Node iterativeSearch(Node x, float k) {
            while (x != nil && k != x.key) {
                if (k < x.key) {
                    x = x.left;
                } else {
                    x = x.right;
                }
            }
            return x;
        }

        /**
         * 返回树的最小键值的节点。
         *
         * @return 最小键值的节点
         */
        public Node minimum() {
            return minimum(root);
        }

        /**
         * 返回树的最小键值的节点。
         *
         * @param x 当前节点
         * @return 最小键值的节点
         */
        private Node minimum(Node x) {
            while (x.left != nil) {
                x = x.left;
            }
            return x;
        }

        /**
         * 返回树的最大键值的节点。
         *
         * @return 最大键值的节点
         */
        public Node maximum() {
            return maximum(root);
        }

        /**
         * 返回树的最大键值的节点。
         *
         * @param x 当前节点
         * @return 最大键值的节点
         */
        private Node maximum(Node x) {
            while (x.right != nil) {
                x = x.right;
            }
            return x;
        }

        /**
         * 返回指定节点x的后继节点。
         *
         * @param x 当前节点
         * @return x的后继节点；如果x具有最大键值，返回null
         */
        public Node successor(Node x) {
            if (x.right != nil) {
                return minimum(x.right);
            }
            Node y = x.parent;
            while (y != nil && x == y.right) {
                x = y;
                y = y.parent;
            }
            return y;
        }

        /**
         * 返回指定节点x的前驱节点。
         *
         * @param x 当前节点
         * @return x的前驱节点；如果x具有最小键值，返回null
         */
        public Node predecessor(Node x) {
            if (x.left != nil) {
                return maximum(x.left);
            }
            Node y = x.parent;
            while (y != nil && x == y.left) {
                x = y;
                y = y.parent;
            }
            return y;
        }

        /**
         * 插入节点。
         *
         * @param z 待插入节点
         */
        public void insert(Node z) {
            Node y = nil; //当前节点的父节点
            Node x = root; //当前节点
            while (x != nil) { //迭代查寻z应该所在的位置
                y = x;
                y.size++; //沿着查找路径，将z的所有先辈的size加1
                if (z.key < x.key) {
                    x = x.left;
                } else {
                    x = x.right;
                }
            }
            z.parent = y;
            z.size = 1; //z是叶节点
            if (y == nil) {
                root = z; //如果没有父节点，则插入的节点是根节点。
            } else if (z.key < y.key) {
                y.left = z;
            } else {
                y.right = z;
            }
            z.left = nil;
            z.right = nil;
            z.color = Color.RED;
            insertFixup(z);
        }

        /**
         * 按红黑树规则进行调整。
         *
         * @param z 待插入节点
         */
        public void insertFixup(Node z) {
            while (z.parent.color == Color.RED) { //违反条件4，并且保证z有爷爷
                if (z.parent == z.parent.parent.left) { //z的父节点是左子节点
                    Node y = z.parent.parent.right;
                    if (y.color == Color.RED) { //如果z的叔叔是红
                        z.parent.color = Color.BLACK; //将z的父亲和叔叔设为黑
                        y.color = Color.BLACK;
                        z.parent.parent.color = Color.RED; //z的爷爷设为红
                        z = z.parent.parent; //迭代
                    } else { //如果z的叔叔是黑
                        if (z == z.parent.right) { //如果z是右子节点，左旋
                            z = z.parent;
                            leftRotate(z);
                        }
                        z.parent.color = Color.BLACK; //z的父亲为黑(叔叔为黑)
                        z.parent.parent.color = Color.RED; //z的爷爷为红
                        rightRotate(z.parent.parent); // 右旋
                    }
                } else { //z的父节点是右子节点，反向对称
                    Node y = z.parent.parent.left;
                    if (y.color == Color.RED) {
                        z.parent.color = Color.BLACK;
                        y.color = Color.BLACK;
                        z.parent.parent.color = Color.RED;
                        z = z.parent.parent;
                    } else {
                        if (z == z.parent.left) {
                            z = z.parent;
                            rightRotate(z);
                        }
                        z.parent.color = Color.BLACK;
                        z.parent.parent.color = Color.RED;
                        leftRotate(z.parent.parent);
                    }
                }
            }
            root.color = Color.BLACK; //满足条件2
        }

        /**
         * 删除节点。
         *
         * @param z 待删除节点
         */
        public Node delete(Node z) {
            Node y = null;
            Node x = null;
            if (z.left == nil || z.right == nil) {
                y = z;
            } else {
                y = successor(z);
            }

            if (y.left != nil) {
                x = y.left;
            } else {
                x = y.right;
            }

            x.parent = y.parent;

            if (y.parent == nil) {
                root = x;
            } else if (y == y.parent.left) {
                y.parent.left = x;
            } else {
                y.parent.right = x;
            }

            Node p = y.parent; //调整y所有父节点的size
            while (p != nil) {
                p.size--;
                p = p.parent;
            }

            if (y != z) { // 如果z包含两个子节点，用y替换z的位置
                y.parent = z.parent;
                if (z.parent != nil) {
                    if (z == z.parent.left) {
                        z.parent.left = y;
                    } else {
                        z.parent.right = y;
                    }
                } else {
                    root = y;
                }
                z.left.parent = y;
                y.left = z.left;
                z.right.parent = y;
                y.right = z.right;
                y.size = y.left.size + y.right.size + 1; //重新计算y的size
            }

            if (y.color == Color.BLACK) {
                deleteFixup(x);
            }
            return y;
        }

        /**
         * 按红黑树规则进行调整。
         *
         * @param x 待删除节点
         */
        private void deleteFixup(Node x) {
            while (x != nil && x != root && x.color == Color.BLACK) {
                if (x == x.parent.left) {
                    Node w = x.parent.right;
                    if (w == nil) {
                        return;
                    }
                    if (w.color == Color.RED) {
                        w.color = Color.BLACK;
                        x.parent.color = Color.RED;
                        leftRotate(x.parent);
                        w = x.parent.right;
                    }
                    if (w == nil) {
                        return;
                    }
                    if (w.left.color == Color.BLACK && w.right.color == Color.BLACK) {
                        w.color = Color.RED;
                        x = x.parent;
                    } else {
                        if (w.right.color == Color.BLACK) {
                            w.left.color = Color.BLACK;
                            w.color = Color.RED;
                            rightRotate(w);
                            w = x.parent.right;
                        }

                        w.color = x.parent.color;
                        x.parent.color = Color.BLACK;
                        w.right.color = Color.BLACK;
                        leftRotate(x.parent);
                        x = root;
                    }
                } else {
                    Node w = x.parent.left;
                    if (w == nil) {
                        return;
                    }
                    if (w.color == Color.RED) {
                        w.color = Color.BLACK;
                        x.parent.color = Color.RED;
                        rightRotate(x.parent);
                        w = x.parent.left;
                    }
                    if (w == nil) {
                        return;
                    }
                    if (w.right.color == Color.BLACK && w.left.color == Color.BLACK) {
                        w.color = Color.RED;
                        x = x.parent;
                    } else {
                        if (w.left.color == Color.BLACK) {
                            w.right.color = Color.BLACK;
                            w.color = Color.RED;
                            leftRotate(w);
                            w = x.parent.left;
                        }
                        w.color = x.parent.color;
                        x.parent.color = Color.BLACK;
                        w.left.color = Color.BLACK;
                        rightRotate(x.parent);
                        x = root;

                    }
                }
            }
            x.color = Color.BLACK;
        }

    }
}
