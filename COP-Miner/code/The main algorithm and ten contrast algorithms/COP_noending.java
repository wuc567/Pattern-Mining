package COP_Mining;

import newalgorithm.MemoryLogger;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.*;
import java.util.stream.Collectors;

public class COP_noending {

    private static Double[] input;
    private static Double[] in;
    //SDB1
//    private static Double[] p = new Double[]{1.0, 5.0, 2.0, 6.0, 3.0, 4.0};

// SDB2
//    private static Double[] p = new Double[]{1.0, 5.0, 3.0, 4.0, 2.0, 6.0};

//SDB3
//private static Double[] p = new Double[]{1.0, 5.0, 2.0, 6.0, 3.0, 4.0};

//SDB4
//private static Double[] p = new Double[]{1.0, 4.0, 3.0,6.0,5.0, 2.0};

//SDB5
//private static Double[] p = new Double[]{1.0, 3.0, 2.0, 5.0, 4.0, 6.0};

//SDB6
//private static Double[] p = new Double[]{3.0, 6.0, 4.0, 5.0, 1.0, 2.0};

//SDB7
//private static Double[] p = new Double[]{1.0, 3.0, 2.0, 5.0, 4.0, 6.0};

//SDB8
//    private static Double[] p = new Double[]{1.0, 3.0, 2.0, 5.0, 4.0, 6.0};

//    private static Double[] p = new Double[]{1.0,4.0,2.0,3.0};
//private static Double[] p = new Double[]{3.0, 1.0, 2.0, 4.0, 5.0};

//private static Double[] p = new Double[]{1.0, 6.0, 3.0, 7.0, 4.0, 5.0, 2.0};


//    private static Double[] p = new Double[]{2.0, 3.0, 1.0, 6.0, 4.0, 5.0};


    //    private static Double[] p = new Double[]{5D, 3D, 7D, 13D};
    //private static Double[] p = new Double[]{5.0,2.0,4.0};
//private static Double[] p = new Double[]{5.0,2.0,4.0,1.0};
//    private static Double[] p = new Double[]{1D, 4D, 2D, 3D};
//    private static Double[] p = new Double[]{1D,3D,4D,2D,6D,7D,5D,8D};
//    private static Double[] p = new Double[]{2.0, 5.0, 1.0, 4.0, 3.0};
//    private static Double[] p = new Double[]{1D,3D,2D,5D,4D,6D};
//    private static Double[] p = new Double[]{2D,3D,1D,6D,4D,5D};
//    private static Double[] p = new Double[]{5D,6D,3D,4D,1D,2D};
//    private static Double[] p = new Double[]{1D, 3D, 2D, 5D, 4D, 6D};
//private static Double[] p = new Double[]{4D,5D,2D,3D,1D,6D};
//    private static Double[] p = new Double[]{1.0, 4.0, 3.0,6.0,5.0, 2.0};
//    private static Double[] p = new Double[]{4.0, 3.0, 6.0, 2.0, 5.0, 1.0};
//    private static Double[] p = new Double[]{1.0, 3.0, 2.0, 5.0, 4.0, 6.0};
//    private static Double[] p = new Double[]{1.0, 3.0, 2.0, 6.0, 4.0, 5.0};
//    private static Double[] p = new Double[]{1.0,4.0, 2.0, 3.0};


    //SDB1  SDB3
//    private static Double[] p = new Double[]{1.0, 5.0, 2.0, 6.0, 3.0, 4.0};


//        private static Double[] p = new Double[]{1.0, 5.0, 2.0};
//    private static Double[] p = new Double[]{1.0, 5.0, 2.0, 6.0};
//    private static Double[] p = new Double[]{1.0, 5.0, 2.0, 6.0, 3.0};
//    private static Double[] p = new Double[]{1.0, 5.0, 2.0, 6.0, 3.0, 4.0};
//    private static Double[] p = new Double[]{1.0, 6.0, 3.0, 7.0, 4.0, 5.0, 2.0};


//        private static Double[] p = new Double[]{1.0, 3.0, 2.0};
//    private static Double[] p = new Double[]{1.0, 3.0, 2.0, 4.0};
//    private static Double[] p = new Double[]{1.0, 3.0, 2.0, 5.0, 4.0};
    private static Double[] p = new Double[]{1.0, 3.0, 2.0, 5.0, 4.0, 6.0};
//    private static Double[] p = new Double[]{1.0, 4.0, 2.0, 6.0, 5.0, 7.0, 3.0};


    //SDB2
//    private static Double[] p = new Double[]{1.0, 5.0, 3.0, 4.0, 2.0, 6.0};

//    private static Double[] p = new Double[]{1.0, 5.0, 3.0};
//    private static Double[] p = new Double[]{1.0, 5.0, 3.0, 4.0};
//    private static Double[] p = new Double[]{1.0, 5.0, 3.0, 4.0, 2.0};
//    private static Double[] p = new Double[]{1.0, 5.0, 3.0, 4.0, 2.0, 6.0};
//    private static Double[] p = new Double[]{1.0, 6.0, 4.0, 5.0, 2.0, 7.0, 3.0};

//sdb4
//        private static Double[] p = new Double[]{3.0, 6.0, 4.0, 5.0, 1.0, 2.0};

//    private static Double[] p = new Double[]{3.0, 6.0, 4.0};
//    private static Double[] p = new Double[]{3.0, 6.0, 4.0, 5.0};
//    private static Double[] p = new Double[]{3.0, 6.0, 4.0, 5.0, 1.0};
//    private static Double[] p = new Double[]{3.0, 6.0, 4.0, 5.0, 1.0, 2.0};
//    private static Double[] p = new Double[]{3.0, 7.0, 4.0, 5.0, 1.0, 2.0,6.0};


//    private static Double[] p = new Double[]{2D,1D,4D,3D,6D,5D};
//    private static Double[] p = new Double[]{1D,3D,2D,5D,4D,6D};
//    private static Double[] p = new Double[]{1.0, 4.0, 2.0, 5.0, 3.0, 7.0};

    //    private static Double[] p = new Double[]{2D,1D,4D,3D,6D,5D,8D,7D};

    //    private static Double[] p = new Double[]{3.0, 1.0, 4.0,2.0};
//private static Double[] p = new Double[]{1.0,4.0,2.0,3.0};
//    private static Double[] p = new Double[]{1.0, 3.0, 2.0, 4.0};
//private static Double[] p = new Double[]{2.0, 1.0, 3.0};
//    private static Double[] p = new Double[]{1.0, 3.0, 2.0};


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
//        File file = new File("E:/Dataset/KURIAS-ECG_HeartRate.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_PAxis.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_PRInterval.txt");
//        File file = new File("E:/Dataset/S&P 500.txt");
//        File file = new File("E:/Dataset/ChengduPM2.5.txt");
//        File file = new File("E:/Dataset/GuangZhou_Temp.txt");
//        File file = new File("E:/Dataset/Alabama_Confirmed.txt");
        File file = new File("D:/Dataset/NYSE440_440.txt");


//        File file = new File("E:/Dataset/NYSE1.txt");
//        File file = new File("E:/Dataset/NYSE2.txt");
//        File file = new File("E:/Dataset/NYSE3.txt");
//        File file = new File("E:/Dataset/NYSE4.txt");
//        File file = new File("E:/Dataset/NYSE5.txt");
//        File file = new File("E:/Dataset/NYSE6.txt");
//        File file = new File("E:/Dataset/NYSE7.txt");
//        File file = new File("E:/Dataset/NYSE8.txt");


//                File file = new File("E:/Dataset/KURIAS_HeartRate训练集.txt");
//        File file = new File("E:/Dataset/KURIAS_HeartRate测试集.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_PAxis训练集.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_PAxis测试集.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_PRInterval训练集.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_PRInterval测试集.txt");
//                File file = new File("E:/Dataset/S&P 500训练集.txt");
//        File file = new File("E:/Dataset/S&P 500测试集.txt");
//                File file = new File("E:/Dataset/ChengduPM2.5训练集.txt");
//        File file = new File("E:/Dataset/ChengduPM2.5测试集.txt");
//        File file = new File("E:/Dataset/GuangZhouTemp训练集.txt");
//        File file = new File("E:/Dataset/GuangZhouTemp测试集.txt");
//        File file = new File("E:/Dataset/Alabama_Confirmed训练集.txt");
//        File file = new File("E:/Dataset/Alabama_Confirmed测试集.txt");
//        File file = new File("E:/Dataset/Online-Retail训练集.txt");
//        File file = new File("E:/Dataset/Online-Retail测试集.txt");
//        File file = new File("E:/Dataset/Brent.txt");
//        File file = new File("E:/Dataset/NYSE训练集.txt");
//                File file = new File("E:/Dataset/NYSE测试集.txt");





//        File file = new File("E:/Dataset/分类/CinCECGTorso_TRAIN.txt");
//        File file = new File("E:/Dataset/ChengduPM2.5.txt");
//        File file = new File("E:/Dataset/分类/ShapeletSim_TEST.txt");
//        File file = new File("E:/Dataset/test.txt");

//        File file = new File("E:/Dataset/Data-Stock.txt");
//        File file = new File("E:/Dataset/Online-Retail.txt");
//        File file = new File("E:/Dataset/Increase rate.txt");
//        File file = new File("E:/Dataset/Alabama_Confirmed.txt");

//        File file = new File("E:/Dataset/分类/BTC1训练集.txt");
//        File file = new File("E:/Dataset/分类/BTC1测试集.txt");
//        File file = new File("E:/Dataset/1-WTI-2训练集.txt");
//        File file = new File("E:/Dataset/1-WTI-2测试集.txt");

//                File file = new File("E:/Dataset/KURIAS-ECG_PAxis1训练集.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_PAxis.txt");

//        File file = new File("E:/Dataset/分类/CSSE8测试集.txt");

//        File file = new File("E:/Dataset/分类/BTC.txt");
//        File file = new File("E:/Dataset/分类/Beef_TEST.txt");
//        File file = new File("E:/Dataset/分类/Car_TEST.txt");
//        File file = new File("E:/Dataset/FiveCitiesTempData.txt");
//        File file = new File("E:/Dataset/ChengduPM2.5.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5.txt");

//        File file = new File("E:/Dataset/1ChengduPM.txt");
//        File file = new File("E:/Dataset/2ChengduPM.txt");
//        File file = new File("E:/Dataset/1ChengDuTEMP (2).txt");
//       File file = new File("E:/Dataset/2ChengDuTEMP.txt");
//        File file = new File("E:/Dataset/2GuangZhouTEMP.txt");


//        File file = new File("E:/Dataset/BeijingPM2.5_3.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5_5.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5_7.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5_9.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5_11.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5.txt");


//        File file = new File("E:/Dataset/PRSA_Data.txt");


//        File file = new File("E:/Dataset/分类/ShapeletSim_TEST.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5.txt");
//        File file = new File("E:/Dataset/PRSA_Data.txt");
//        File file = new File("E:/Dataset/ToeSegmentation1_TRAIN.txt");
//        File file = new File("E:/Dataset/Crude Oil.txt");
//        File file = new File("E:/Dataset/PRSA_Data_Nongzhanguan.txt");
//        File file = new File("E:/Dataset/Italian-temperature.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_database.txt");
//        File file = new File("E:/Dataset/ChengduPM2.5.txt");

//        File file = new File("E:/Dataset/S&P 500.txt");
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
        for (Integer val : subsetNumArr) {
            Double[] sub = new Double[pSuf.length];
            System.arraycopy(in, val - pSuf.length, sub, 0, sub.length);
            //求P的出现
            if (val > pSuf.length) {
               /* Double[] patternOrder = getCompareOrder(sub, getOrder(pSuf), in[val - pSuf.length - 1], false);
                if (patternOrder != null) {
                    if (Arrays.equals(pOrder, patternOrder)) {
                        pList.add(val);
                    }
                }*/
                Double[] pOrderSuf = new Double[pOrder.length - 1]; //1 4 3
                System.arraycopy(pOrder, 1, pOrderSuf, 0, pOrderSuf.length);
                Double[] pSufOrder = getOrder(pSuf); //1 3 2
                double maxUnChanged = Double.valueOf(Integer.MIN_VALUE);
                double minChanged = Double.valueOf(Integer.MAX_VALUE);
                int maxIndex = -1;
                int minIndex = pSufOrder.length;
                for (int i = 0; i < pOrderSuf.length; i++) {
                    if (pSufOrder[i].doubleValue() == pOrderSuf[i].doubleValue()) {
                        if (pSufOrder[i].doubleValue() > maxUnChanged) {
                            maxUnChanged = pSufOrder[i].doubleValue();
                            maxIndex = i;
                        }
                    }
                    if (pSufOrder[i].doubleValue() < pOrderSuf[i].doubleValue()) {
                        if (pSufOrder[i].doubleValue() < minChanged) {
                            minChanged = pSufOrder[i].doubleValue();
                            minIndex = i;
                        }
                    }
                }
                if (maxIndex == -1) {
                    if (in[val - pSuf.length - 1] < sub[minIndex]) {
                        pList.add(val);
                    }
                } else if (minIndex == pSufOrder.length) {
                    if (in[val - pSuf.length - 1] > sub[maxIndex]) {
                        pList.add(val);
                    }
                } else {
                    if (in[val - pSuf.length - 1] > sub[maxIndex] && in[val - pSuf.length - 1] < sub[minIndex]) {
                        pList.add(val);
                    }
                }
            }

            //求pSuf后缀出现
            if (val < in.length) {
                Double[] pSufSufOrder = getBinarySearchOrder(sub, getOrder(pSuf), in[val]);

//                Double[] pSufSufOrder = getCompareOrder(sub, getOrder(pSuf), in[val], true);
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
                /*if (PSufLocation == null || PSufLocation.size() == 0) {
                    continue;
                }*/
                Map<String, List<Integer>> mapIn = new HashMap<>();
                for (Integer val : PSufLocation) {
                    Double[] sub = new Double[PSuf.length];
                    System.arraycopy(in, val - PSuf.length, sub, 0, sub.length);
                    //求PSuf后缀出现
                    if (val < in.length) {
                        Double[] PSufSufOrder = getBinarySearchOrder(sub, getOrder(PSuf), in[val]);
//                        Double[] PSufSufOrder = getCompareOrder(sub, getOrder(PSuf), in[val], true);
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

    private static Double[] getBinarySearchOrder(Double[] sub, Double[] order, Double value) {
        if (Arrays.asList(sub).contains(value)) {
            return null;
        }
        Double[] orderNew = new Double[order.length + 1];
        System.arraycopy(order, 0, orderNew, 0, order.length);

        Double[] subNew = new Double[sub.length + 1];
        System.arraycopy(sub, 0, subNew, 0, sub.length);
        subNew[subNew.length - 1] = value;
        Arrays.sort(subNew);
//        if (value < subNew[0]){
//            for (int i = 0; i < order.length; i++){
//                orderNew[i] = orderNew[i] + 1;
//            }
//            orderNew[orderNew.length - 1] = 1D;
//            return orderNew;
//        }
//        if (value > subNew[subNew.length - 1]){
//            orderNew[orderNew.length - 1] = Double.valueOf(orderNew.length);
//            return orderNew;
//        }

        int low = 0;
        int high = subNew.length - 1;
        int index = 0;
        while (low <= high) {
            int mid = (low + high) / 2;
            if (value < subNew[mid].doubleValue()) {
                high = mid - 1;
            } else if (value > subNew[mid].doubleValue()) {
                low = mid + 1;
            } else if (value.equals(subNew[mid].doubleValue())) {
                index = mid;
                break;
            }
        }
        for (int i = 0; i < order.length; i++) {
            if (orderNew[i] > index) {
                orderNew[i] = orderNew[i] + 1;
            }
        }
        orderNew[orderNew.length - 1] = Double.valueOf(index + 1);
        return orderNew;
    }


    private static void patternFusionNew(Double[] P, List<Integer> PLocation, Map.Entry<String, List<Integer>> entryIn, LNode PNode) {
        int slen = P.length;
        String key = entryIn.getKey();
        Double[] Q = stringToArray(key);
        LNode QNode = getLNode(entryIn.getValue());
        //ending
//        if (PNode.data >= minsup && QNode.data >= minsup) {
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
//        }
    }

    private static void patternFusion(Double[] P, List<Integer> pList) {
        int slen = P.length;
        LNode PNode = getLNode(pList);
        for (Map.Entry<String, List<Integer>> entry : map.entrySet()) {
            String key = entry.getKey();
            Double[] Q = stringToArray(key);
            LNode QNode = getLNode(entry.getValue());
//            if (PNode.data >= minsup && QNode.data >= minsup) {
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
//            }

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
//            subsetNumArr = bndm(inBinaryArr, pBinaryArr);
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
                    subsetNumList.add(i + 2);
                }
            }
        } else {
            for (int i = 0; i < in.length - 1; i++) {
                if (in[i + 1] < in[i]) {
                    subsetNumList.add(i + 2);
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
}
