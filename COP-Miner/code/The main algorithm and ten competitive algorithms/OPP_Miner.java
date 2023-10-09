package COP_Mining;

import newalgorithm.MemoryLogger;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.stream.Collectors;

public class OPP_Miner {

    private static Map<Integer, Integer> map = new HashMap<>();
    private static double[] input;
    private static boolean flag;
    private static int allFreCount = 0;
    private static int candCount = 0;
    private static int coFreCount = 0;
    private static int coFreSeqCount = 0;
    private static int coSimSeqCount = 0;
    //    private static Set<String> freSet = new HashSet<>();
    private static List<FreItemset> freItemsetList;
    private static int candidateCount;

    public static void main(String[] args) throws Exception {
        long startTime = System.currentTimeMillis();
        getInArr();
        System.out.println("候选模式的总数是:" + candCount);
        System.out.println("共生频繁模式的总数为:" + coFreCount);
        System.out.println("---------------------------------------------------");
        printCostTime(startTime);
//        System.out.println("频繁模式的总数是:" + allFreCount);

//        System.out.println("共生频繁子序列的总数为:" + coFreSeqCount);
//        System.out.println("满足支持度及相似度阈值的共生子序列总为:" + coSimSeqCount);
//        System.out.println("---------------------------------------------------");
//        System.out.println("---------------------------------------------------");

    }


    private static List<CoOccurrence> getFimSwMethod(double[] in, double[] pattern, int supportTv) {
        candidateCount = 0;
        int length = 2;
        Map<String, FimTemp> lastMap = new HashMap<>();
        List<Candidate> candidateList = new ArrayList<>();
        while (length <= in.length) {
            Map<String, FimTemp> inMap = new HashMap<>();
            boolean flag = false;
            for (int i = 0; i <= in.length - length; i++) {
                double[] sub = new double[length];
                System.arraycopy(in, i, sub, 0, length);
                int[] subOrder = getOrder(sub, lastMap);
                if (subOrder == null) {
                    continue;
                }
                if (inMap.get(Arrays.toString(subOrder)) == null) {
                    List<String> subList = new ArrayList<>();
                    subList.add(Arrays.toString(sub));
                    FimTemp fimTemp = new FimTemp();
                    fimTemp.setAppears(subList);
                    List<Integer> list = new ArrayList<>();
                    list.add(i);
                    fimTemp.setSupportList(list);
                    inMap.put(Arrays.toString(subOrder), fimTemp);
                } else {
                    FimTemp fimTemp = inMap.get(Arrays.toString(subOrder));
                    List<String> subList = fimTemp.getAppears();
                    List<Integer> list = fimTemp.getSupportList();
                    subList.add(Arrays.toString(sub));
                    list.add(i);
                    inMap.put(Arrays.toString(subOrder), new FimTemp(subList, list));
                    if (subList.size() + 1 >= supportTv) {
                        flag = true;
                    }
                }
            }
            candidateCount += inMap.size();
            inMap = inMap.entrySet().stream().filter(x -> x.getValue().getAppears().size() >= supportTv).collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
            AtomicBoolean isCo = new AtomicBoolean(false);
            inMap = inMap.entrySet().stream().peek(x -> {
                double[] p = toArray(x.getKey());
                freItemsetList.add(new FreItemset(p, x.getValue().getAppears().size()));
                if (p.length == pattern.length + 1) {
                    isCo.set(true);
                }
            }).collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
            if (isCo.get()) {
                inMap = inMap.entrySet().stream().peek(x -> {
                    Integer[] supportArr = new Integer[x.getValue().getSupportList().size()];
                    candidateList.add(new Candidate(toArray(x.getKey()), x.getValue().getSupportList().toArray(supportArr)));
                }).collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
            }
            if (isCo.get()) {
                break;
            }
            lastMap = inMap;
            if (!flag) {
                break;
            }
            length++;
        }

        if (candidateList.size() == 0) {
            return null;
        }
        if (candidateList.get(0).itemset.length != pattern.length + 1) {
            return null;
        }
        List<CoOccurrence> coOccurrenceList = new ArrayList<>();
        for (Candidate candidate : candidateList) {
            double[] itemset = getItemset(candidate.itemset, pattern);
            if (Arrays.equals(getOrder(itemset), getOrder(pattern))) {
                List<double[]> appearList = new ArrayList<>();
                List<double[]> subModes = new ArrayList<>();
                for (int index : candidate.support) {
                    int end = map.get(index + pattern.length);
                    int start = map.get(index);
                    double[] appear = new double[end - start + 1];
                    System.arraycopy(input, start, appear, 0, appear.length);
                    appearList.add(appear);

                    int len;
                    if (flag) {
                        end = map.get(index + pattern.length - 1);
                        len = end - start + 1;
                    } else {
                        start = map.get(index + 1);
                        len = end - start + 1;
                    }
                    double[] subMode = new double[len];
                    System.arraycopy(input, start, subMode, 0, subMode.length);
                    subModes.add(subMode);
                }
                coOccurrenceList.add(new CoOccurrence(candidate.itemset, appearList, subModes));
            }
        }
        return coOccurrenceList;
    }

    private static int[] getOrder(double[] seq, Map<String, FimTemp> map) {
        Set<Double> set = new HashSet<>();
        for (double d : seq) {
            set.add(d);
        }
        if (set.size() != seq.length) {
            return null;
        }
        if (seq.length == 2) {
            if (seq[0] > seq[1]) {
                return new int[]{2, 1};
            } else {
                return new int[]{1, 2};
            }
        }

        double[] pre = new double[seq.length - 1];
        System.arraycopy(seq, 0, pre, 0, pre.length);

        String key = null;
        for (Map.Entry<String, FimTemp> entry : map.entrySet()) {
            if (entry.getValue().getAppears().contains(Arrays.toString(pre))) {
                key = entry.getKey();
            }
        }

        if (key == null) {
            return null;
        }
        key = key.replaceAll(" ", "");
        key = key.substring(1, key.length() - 1);
        String[] strOrder = key.split(",");
        int[] preOrder = new int[strOrder.length];
        for (int i = 0; i < strOrder.length; i++) {
            preOrder[i] = Integer.parseInt(strOrder[i]);
        }


        List<Integer> list = new ArrayList<>();
        double newIndex = seq[seq.length - 1];
        int[] order = new int[seq.length];
        for (int i = 0; i < pre.length; i++) {
            if (newIndex > pre[i]) {
                order[i] = preOrder[i];
                list.add(preOrder[i]);
            } else {
                order[i] = preOrder[i] + 1;
            }
        }
        if (list.size() != 0) {
            list.sort(Comparator.reverseOrder());
            order[order.length - 1] = list.get(0) + 1;
        } else {
            order[order.length - 1] = 1;
        }
        return order;
    }

    private static List<CoOccurrence> getMtaMethod(double[] in, double[] pattern, int supportTv) {
        List<double[]> resList = new ArrayList<double[]>() {{
            add(new double[]{1, 2});
            add(new double[]{2, 1});
        }};
        List<Candidate> candidateList = new ArrayList<>();
        while (!resList.isEmpty()) {
            List<double[]> supList = new ArrayList<>();
            for (double[] p : resList) {
                double[] temp = new double[p.length];
                List<Integer> supportList = new ArrayList<>();
                for (int i = 0; i < in.length - temp.length + 1; i++) {
                    System.arraycopy(in, i, temp, 0, temp.length);
                    Set<Double> set = new HashSet<>();
                    for (double d : temp) {
                        set.add(d);
                    }
                    if (set.size() != temp.length) {
                        continue;
                    }
                    int index = 0;
                    boolean flag = true;
                    outer:
                    while (index < temp.length) {
                        int μt = 0;
                        int μp = 0;
                        double tIndex = temp[index];
                        double pIndex = p[index];
                        for (int j = 0; j < index + 1; j++) {
                            if (tIndex >= temp[j]) {
                                μt++;
                            }
                            if (pIndex >= p[j]) {
                                μp++;
                            }
                            if (μt != μp) {
                                flag = false;
                                break outer;
                            }
                        }
                        index++;
                    }
                    if (flag) {
                        supportList.add(i);
                    }
                }
                if (supportList.size() >= supportTv) {
                    supList.add(p);
                    freItemsetList.add(new FreItemset(p, supportList.size()));
                    if (p.length == pattern.length + 1) {
                        Integer[] supportArr = new Integer[supportList.size()];
                        candidateList.add(new Candidate(p, supportList.toArray(supportArr)));
                    }
                }
            }
            if (supList.size() > 0 && supList.get(0).length == pattern.length + 1) {
                break;
            }
            resList = patternFusion(supList);
            candidateCount += resList.size();
        }
        if (candidateList.size() == 0) {
            return null;
        }
        if (candidateList.get(0).itemset.length != pattern.length + 1) {
            return null;
        }
        List<CoOccurrence> coOccurrenceList = new ArrayList<>();
        for (Candidate candidate : candidateList) {
            double[] itemset = getItemset(candidate.itemset, pattern);
            if (Arrays.equals(getOrder(itemset), getOrder(pattern))) {
                List<double[]> appearList = new ArrayList<>();
                List<double[]> subModes = new ArrayList<>();
                for (int index : candidate.support) {
                    int end = map.get(index + pattern.length);
                    int start = map.get(index);
                    double[] appear = new double[end - start + 1];
                    System.arraycopy(input, start, appear, 0, appear.length);
                    appearList.add(appear);

                    int len;
                    if (flag) {
                        end = map.get(index + pattern.length - 1);
                        len = end - start + 1;
                    } else {
                        start = map.get(index + 1);
                        len = end - start + 1;
                    }
                    double[] subMode = new double[len];
                    System.arraycopy(input, start, subMode, 0, subMode.length);
                    subModes.add(subMode);
                }
                coOccurrenceList.add(new CoOccurrence(candidate.itemset, appearList, subModes));
            }
        }
        return coOccurrenceList;
    }

    private static List<CoOccurrence> getIndexMethodNoPrune(double[] in, double[] pattern, int supportTv) {
        List<Candidate> candidateList = getInitialList(in);
        candidateList = candidateList.stream().filter(x -> x.support.length >= supportTv).collect(Collectors.toList());
        for (Candidate candidate : candidateList) {
            freItemsetList.add(new FreItemset(candidate.itemset, candidate.support.length));
        }
        candidateList = getSupportNewNoPrune(in, candidateList);
        candidateCount += candidateList.size();
        candidateList = candidateList.stream().filter(x -> x.support.length >= supportTv).collect(Collectors.toList());
        for (Candidate candidate : candidateList) {
            freItemsetList.add(new FreItemset(candidate.itemset, candidate.support.length));
        }
        while (candidateList.size() != 0 && candidateList.get(0).itemset.length < pattern.length + 1) {
            candidateList.stream().peek(x -> {
                x.setSupportPre(x.getSupport());
                x.setSupportSuf(x.getSupport());
            }).collect(Collectors.toList());
            candidateList = getSupportNewNoPrune(in, candidateList);
            candidateCount += candidateList.size();
            candidateList = candidateList.stream().filter(x -> x.support.length >= supportTv).collect(Collectors.toList());
            for (Candidate candidate : candidateList) {
                freItemsetList.add(new FreItemset(candidate.itemset, candidate.support.length));
            }
        }
        if (candidateList == null || candidateList.size() == 0) {
            return null;
        }
        List<CoOccurrence> coOccurrenceList = new ArrayList<>();
        for (Candidate candidate : candidateList) {
            double[] itemset = getItemset(candidate.itemset, pattern);
            if (Arrays.equals(getOrder(itemset), getOrder(pattern))) {
                List<double[]> appearList = new ArrayList<>();
                List<double[]> subModes = new ArrayList<>();
                for (int index : candidate.support) {
                    int start = map.get(index - pattern.length - 1);
                    int end = map.get(index - 1);
                    double[] appear = new double[end - start + 1];
                    System.arraycopy(input, start, appear, 0, appear.length);
                    appearList.add(appear);

                    int len;
                    if (flag) {
                        end = map.get(index - 2);
                        len = end - start + 1;
                    } else {
                        start = map.get(index - pattern.length);
                        len = end - start + 1;
                    }
                    double[] subMode = new double[len];
                    System.arraycopy(input, start, subMode, 0, subMode.length);
                    subModes.add(subMode);
                }
                coOccurrenceList.add(new CoOccurrence(candidate.itemset, appearList, subModes));
            }
        }
        return coOccurrenceList;
    }

    private static List<Candidate> getSupportNewNoPrune(double[] in, List<Candidate> candidateList) {
        List<Candidate> candidates = new ArrayList<>();
        for (Candidate candidate : candidateList) {
            for (Candidate candidateToo : candidateList) {
                List<double[]> resList = getFusion(candidate.itemset, candidateToo.itemset);
                if (Arrays.equals(candidate.itemset, candidateToo.itemset)) {
                    Integer[] supportArr = getSupportSame(candidate.supportPre, candidateToo.supportSuf);
                    //prune(candidate, candidateToo);
                    if (supportArr.length > 0) {
                        Candidate candidateNew = new Candidate(resList.get(0), supportArr);
                        candidates.add(candidateNew);
                    }
                } else {
                    List<Integer[]> supportList = getSupport(in, candidate.supportPre, candidateToo.supportSuf, candidate.itemset.length);
                    //prune(candidate, candidateToo);
                    if (supportList.size() > 0 && supportList.get(0).length > 0) {
                        Candidate candidateNew = new Candidate(resList.get(resList.size() == 1 ? 0 : 1), supportList.get(0));
                        candidates.add(candidateNew);
                    }
                    if (supportList.size() > 1 && supportList.get(1).length > 0) {
                        Candidate candidateNew = new Candidate(resList.get(0), supportList.get(1));
                        candidates.add(candidateNew);
                    }
                }
            }
        }
        return candidates;
    }

    private static double[] getPatternExtreme(double[] p) {
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
        double[] arr = new double[list.size()];
        for (double item : list) {
            arr[i++] = item;
        }
        return arr;
    }

    private static double[] getExtremePoint(double[] input) {
        List<Double> list = new ArrayList<>();
        list.add(input[0]);
        map.put(0, 0);
        int k = 1;
        for (int i = 1; i < input.length - 1; i++) {
            if ((input[i] >= input[i - 1] && input[i] > input[i + 1]) || (input[i] > input[i - 1] && input[i] >= input[i + 1])) {
                list.add(input[i]);
                map.put(k++, i);
            } else if ((input[i] <= input[i - 1] && input[i] < input[i + 1]) || (input[i] < input[i - 1] && input[i] <= input[i + 1])) {
                list.add(input[i]);
                map.put(k++, i);
            } else {
                map.put(-1, i);
            }
        }
        list.add(input[input.length - 1]);
        map.put(k, input.length - 1);
        int i = 0;
        double[] arr = new double[list.size()];
        for (double item : list) {
            arr[i++] = item;
        }
        return arr;
    }

    private static List<Approximate> getSimilarity(List<CoOccurrence> coOccurrences, double[] pattern, double similarityTv) {
        if (coOccurrences == null) {
            return null;
        }
        List<double[]> subList = new ArrayList<>();
        coOccurrences.stream().peek(x -> subList.addAll(x.subModes)).collect(Collectors.toList());
        List<Approximate> approximates = getApproximateSimilarityList(subList, pattern, similarityTv);
        approximates.sort(Comparator.comparingDouble(Approximate::getSimilarity));
        return approximates;
    }

    private static List<Approximate> getApproximateSimilarityList(List<double[]> subList, double[] pattern, double similarityTv) {
        List<Approximate> approximates = new ArrayList<>();
        double[] paStatute = getStatute(pattern, false);
        for (double[] arr : subList) {
            double[] arrStatute = getStatute(arr, false);
            //double similarity = getProximity(paStatute, arrStatute);
            double similarity = getProximityByDtw(paStatute, arrStatute);
            if (similarity <= similarityTv) {
                Approximate approximate = new Approximate(similarity, arr);
                approximates.add(approximate);
            }
        }
        return approximates;
    }

    private static double getProximityByDtw(double[] x, double[] y) {
        double[][] dis = new double[y.length][x.length];
        for (int i = 0; i < x.length; i++) {
            if (i == 0) {
                dis[0][i] = getDistance(x[i], y[0]);
            } else {
                dis[0][i] = getDistance(x[i], y[0]) + dis[0][i - 1];
            }
        }

        for (int i = 0; i < y.length; i++) {
            if (i == 0) {
                dis[i][0] = getDistance(x[0], y[i]);
            } else {
                dis[i][0] = getDistance(x[0], y[i]) + dis[i - 1][0];
            }
        }

        for (int i = 1; i < y.length; i++) {
            for (int j = 1; j < x.length; j++) {
                dis[i][j] = getDistance(x[j], y[i]) + Math.min(dis[i - 1][j], Math.min(dis[i][j - 1], dis[i - 1][j - 1]));
            }
        }
        return dis[y.length - 1][x.length - 1];
    }

    private static double getDistance(double x, double y) {
        if (x >= y) {
            return x - y;
        } else {
            return y - x;
        }
    }

    private static double getProximity(double[] paStatute, double[] arrStatute) {
        double similarity = 0;
        for (int i = 0; i < paStatute.length; i++) {
            if (paStatute[i] >= arrStatute[i]) {
                similarity += paStatute[i] - arrStatute[i];
            } else {
                similarity += arrStatute[i] - paStatute[i];
            }
        }
        return similarity;
    }

    private static double[] getStatute(double[] arr, boolean symbiosis) {
        if (symbiosis) {
            double[] arrNew = new double[arr.length - 1];
            System.arraycopy(arr, 0, arrNew, 0, arr.length - 1);
            double[] temp = new double[arr.length - 1];
            System.arraycopy(arr, 0, temp, 0, arr.length - 1);
            Arrays.sort(temp);
            double min = temp[0];
            double max = temp[temp.length - 1];
            for (int i = 0; i < arr.length - 1; i++) {
                arrNew[i] = (arrNew[i] - min) / (max - min);
            }
            double[] arrNewS = new double[arr.length];
            System.arraycopy(arrNew, 0, arrNewS, 0, arrNew.length);
            arrNewS[arrNewS.length - 1] = arr[arr.length - 1];
            return arrNewS;
        } else {
            double[] arrNew = new double[arr.length];
            System.arraycopy(arr, 0, arrNew, 0, arr.length);
            double[] temp = new double[arr.length];
            System.arraycopy(arr, 0, temp, 0, arr.length);
            Arrays.sort(temp);
            double min = temp[0];
            double max = temp[temp.length - 1];
            for (int i = 0; i < arr.length; i++) {
                arrNew[i] = (arrNew[i] - min) / (max - min);
            }
            return arrNew;
        }
    }

    private static void printApproximate(List<Approximate> approximates) {
        if (approximates == null || approximates.size() == 0) {
//            System.out.println("无满足支持度及相似度阈值的子(共生)序列：");
//            System.out.println("---------------------------------------------------");
            return;
        }
        System.out.println("满足支持度及相似度阈值的子(共生)序列：");
        for (Approximate approximate : approximates) {
            System.out.print(approximate.getSimilarity() + ", ");
            printArray(approximate.getProximity());
        }
        System.out.println("满足支持度及相似度阈值的共生子序列个数为：" + approximates.size());
        coSimSeqCount += approximates.size();
        System.out.println("---------------------------------------------------");
    }

    private static List<CoOccurrence> getEnumeration(double[] in, double[] pattern, int supportTv) throws Exception {
        List<double[]> resList = new ArrayList<double[]>() {{
            add(new double[]{1, 2});
            add(new double[]{2, 1});
        }};
        List<Candidate> candidateList = null;
        while (resList.size() > 0 && resList.get(0).length <= pattern.length + 1) {
            candidateList = new ArrayList<>();
            for (double[] candidateArr : resList) {
                int[] inBinaryArr = getBinary(in);
                int[] pBinaryArr = getBinary(candidateArr);
                //Integer[] subsetNumArr = getSubset(inBinaryArr, pBinaryArr);
                Integer[] subsetNumArr;
                if (pattern.length == 2) {
                    subsetNumArr = bndm(inBinaryArr, pBinaryArr);
                } else {
                    int[] sortedP = new int[pBinaryArr.length];
                    System.arraycopy(pBinaryArr, 0, sortedP, 0, sortedP.length);
                    Arrays.sort(sortedP);
                    int[] aux = new int[pBinaryArr.length];
                    genAux(aux, sortedP, pBinaryArr);
                    subsetNumArr = sbndm(inBinaryArr, pBinaryArr, aux, in);
                }

                Integer[] subsetNumArrNew = verificationStrategy(in, candidateArr, subsetNumArr);
                if (subsetNumArrNew.length >= supportTv) {
                    candidateList.add(new Candidate(candidateArr, subsetNumArrNew));
                    freItemsetList.add(new FreItemset(candidateArr, subsetNumArrNew.length));
                }
            }
            resList = candidateList.stream().map(Candidate::getItemset).collect(Collectors.toList());
            resList = enumerationFusion(resList);
            candidateCount += resList.size();
        }
        if (candidateList == null || candidateList.size() == 0) {
            return null;
        }
        List<CoOccurrence> coOccurrenceList = new ArrayList<>();
        for (Candidate candidate : candidateList) {
//            double[] itemset = new double[pattern.length];
//            System.arraycopy(candidate.itemset, 0, itemset, 0, itemset.length);
            double[] itemset = getItemset(candidate.itemset, pattern);
            if (Arrays.equals(getOrder(itemset), getOrder(pattern))) {
                List<double[]> appearList = new ArrayList<>();
                List<double[]> subModes = new ArrayList<>();
                for (int index : candidate.support) {
                    int end = map.get(index + pattern.length);
                    int start = map.get(index);
                    double[] appear = new double[end - start + 1];
                    System.arraycopy(input, start, appear, 0, appear.length);
                    appearList.add(appear);

                    int len;
                    if (flag) {
                        end = map.get(index + pattern.length - 1);
                        len = end - start + 1;
                    } else {
                        start = map.get(index + 1);
                        len = end - start + 1;
                    }
                    double[] subMode = new double[len];
                    System.arraycopy(input, start, subMode, 0, subMode.length);
                    subModes.add(subMode);

//                    int end = map.get(index + pattern.length - 1);
//                    index = map.get(index);
//                    if (index > 0){
//                        double[] appear = new double[end - index + 2];
//                        System.arraycopy(input, index - 1, appear, 0, appear.length);
//                        appearList.add(appear);
//                    }
//                    if (end < input.length - 1){
//                        double[] appear = new double[end - index + 2];
//                        System.arraycopy(input, index, appear, 0, appear.length);
//                        appearList.add(appear);
//                    }
//                    double[] subMode = new double[end - index + 1];
//                    System.arraycopy(input, index, subMode, 0, subMode.length);
//                    subModes.add(subMode);
                }

                coOccurrenceList.add(new CoOccurrence(candidate.itemset, appearList, subModes));
            }
        }
        return coOccurrenceList;
    }

    private static Integer[] sbndm(int[] txt, int[] pat, int[] aux, double[] s) {
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

    private static List<double[]> enumerationFusion(List<double[]> list) {
        List<double[]> resList = new ArrayList<>();
        for (double[] p : list) {
            for (int i = 1; i <= p.length + 1; i++) {
                double[] t = new double[p.length + 1];
                for (int j = 1; j <= p.length; j++) {
                    if (p[j - 1] >= i) {
                        t[j - 1] = p[j - 1] + 1;
                    } else {
                        t[j - 1] = p[j - 1];
                    }
                }
                t[t.length - 1] = i;
                resList.add(t);
            }
        }
        return resList;
    }

    private static List<CoOccurrence> getIndexMethod(double[] in, double[] pattern, int supportTv) {
        List<Candidate> candidateList = getInitialList(in);
        candidateList = candidateList.stream().filter(x -> x.support.length >= supportTv).collect(Collectors.toList());
        for (Candidate candidate : candidateList) {
            freItemsetList.add(new FreItemset(candidate.itemset, candidate.support.length));
        }
        candidateList = getSupportNew(in, candidateList);
        candidateCount += candidateList.size();
        candidateList = candidateList.stream().filter(x -> x.support.length >= supportTv).collect(Collectors.toList());
        for (Candidate candidate : candidateList) {
            freItemsetList.add(new FreItemset(candidate.itemset, candidate.support.length));
        }
        while (candidateList.size() != 0 && candidateList.get(0).itemset.length < pattern.length + 1) {
            candidateList.stream().peek(x -> {
                x.setSupportPre(x.getSupport());
                x.setSupportSuf(x.getSupport());
            }).collect(Collectors.toList());
            candidateList = getSupportNew(in, candidateList);
            candidateCount += candidateList.size();
            candidateList = candidateList.stream().filter(x -> x.support.length >= supportTv).collect(Collectors.toList());
            for (Candidate candidate : candidateList) {
                freItemsetList.add(new FreItemset(candidate.itemset, candidate.support.length));
            }
        }
        if (candidateList == null || candidateList.size() == 0) {
            return null;
        }
        for (Candidate candidate : candidateList) {
            System.out.println(Arrays.toString(candidate.itemset) + ":" + candidate.support.length + ":" + Arrays.toString(candidate.support));
        }
        List<CoOccurrence> coOccurrenceList = new ArrayList<>();
        for (Candidate candidate : candidateList) {
//            double[] itemset = new double[pattern.length];
//            System.arraycopy(candidate.itemset, 0, itemset, 0, itemset.length);
            double[] itemset = getItemset(candidate.itemset, pattern);
            if (Arrays.equals(getOrder(itemset), getOrder(pattern))) {
                List<double[]> appearList = new ArrayList<>();
                List<double[]> subModes = new ArrayList<>();
                for (int index : candidate.support) {
//                    int end = map.get(index + pattern.length);
//                    index = map.get(index);
//                    double[] appear = new double[end - index + 1];
//                    System.arraycopy(input, index, appear, 0, appear.length);
//                    appearList.add(appear);
//                    subModes.add(appear);

                    int start = map.get(index - pattern.length - 1);
                    int end = map.get(index - 1);
                    double[] appear = new double[end - start + 1];
                    System.arraycopy(input, start, appear, 0, appear.length);
                    appearList.add(appear);

                    int len;
                    if (flag) {
                        end = map.get(index - 2);
                        len = end - start + 1;
                    } else {
                        start = map.get(index - pattern.length);
                        len = end - start + 1;
                    }
                    double[] subMode = new double[len];
                    System.arraycopy(input, start, subMode, 0, subMode.length);
                    subModes.add(subMode);

//                    int start = map.get(index - pattern.length);
//                    index = map.get(index - 1);
//                    if (index > 0){
//                        double[] appear = new double[index - start + 2];
//                        System.arraycopy(input, start - 1, appear, 0, appear.length);
//                        appearList.add(appear);
//                    }
//                    if (index < input.length - 1){
//                        double[] appear = new double[index - start + 2];
//                        System.arraycopy(input, start, appear, 0, appear.length);
//                        appearList.add(appear);
//                    }
//
//                    double[] subMode = new double[index - start + 1];
//                    System.arraycopy(input, start, subMode, 0, subMode.length);
//                    subModes.add(subMode);
                }
                coOccurrenceList.add(new CoOccurrence(candidate.itemset, appearList, subModes));
            }
        }
        return coOccurrenceList;
    }

    private static List<Candidate> getSupportNew(double[] in, List<Candidate> candidateList) {
        List<Candidate> candidates = new ArrayList<>();
        for (Candidate candidate : candidateList) {
            for (Candidate candidateToo : candidateList) {
                List<double[]> resList = getFusion(candidate.itemset, candidateToo.itemset);
                if (Arrays.equals(candidate.itemset, candidateToo.itemset)) {
                    Integer[] supportArr = getSupportSame(candidate.supportPre, candidateToo.supportSuf);
                    prune(candidate, candidateToo);
                    if (supportArr.length > 0) {
                        Candidate candidateNew = new Candidate(resList.get(0), supportArr);
                        candidates.add(candidateNew);
                    }
                } else {
                    List<Integer[]> supportList = getSupport(in, candidate.supportPre, candidateToo.supportSuf, candidate.itemset.length);
                    prune(candidate, candidateToo);
                    if (supportList.size() > 0 && supportList.get(0).length > 0) {
                        Candidate candidateNew = new Candidate(resList.get(resList.size() == 1 ? 0 : 1), supportList.get(0));
                        candidates.add(candidateNew);
                    }
                    if (supportList.size() > 1 && supportList.get(1).length > 0) {
                        Candidate candidateNew = new Candidate(resList.get(0), supportList.get(1));
                        candidates.add(candidateNew);
                    }
                }
            }
        }
        return candidates;
    }

    private static List<Integer[]> getSupport(double[] in, Integer[] lp, Integer[] lq, int length) {
        if (lp == null || lq == null) {
            return new ArrayList<>();
        }
        List<Integer> rList = new ArrayList<>();
        List<Integer> hList = new ArrayList<>();
        for (int item : lp) {
            for (int value : lq) {
                if (item + 1 == value) {
                    if (in[value - length - 1] < in[value - 1]) {
                        rList.add(value);
                    } else if (in[value - length - 1] > in[value - 1]) {
                        hList.add(value);
                    }
                }
            }
        }
        Integer[] r = new Integer[rList.size()];
        rList.toArray(r);
        Integer[] h = new Integer[hList.size()];
        hList.toArray(h);
        return new ArrayList<Integer[]>() {{
            add(r);
            add(h);
        }};
    }

    private static void prune(Candidate candidate, Candidate candidateToo) {
        if (candidate.supportPre == null || candidateToo.supportSuf == null) {
            return;
        }
        List<Integer> preList = Arrays.asList(candidate.supportPre);
        List<Integer> Pp = new ArrayList<>(preList);
        List<Integer> sufList = Arrays.asList(candidateToo.supportSuf);
        List<Integer> Sq = new ArrayList<>(sufList);
        for (Integer value : candidate.getSupportPre()) {
            for (Integer item : candidateToo.getSupportSuf()) {
                if (value + 1 == item) {
                    Pp.remove(value);
                    Sq.remove(item);
                }
            }
        }
        Integer[] supportPre = new Integer[Pp.size()];
        Pp.toArray(supportPre);
        candidate.setSupportPre(supportPre);
        Integer[] supportSuf = new Integer[Sq.size()];
        Sq.toArray(supportSuf);
        candidateToo.setSupportSuf(supportSuf);
    }

    private static Integer[] getSupportSame(Integer[] lp, Integer[] lq) {
        if (lp == null || lq == null) {
            return new Integer[0];
        }
        List<Integer> supportList = new ArrayList<>();
        for (int item : lp) {
            for (int value : lq) {
                if (item + 1 == value) {
                    supportList.add(value);
                }
            }
        }
        Integer[] supportArr = new Integer[supportList.size()];
        supportList.toArray(supportArr);
        return supportArr;
    }

    private static List<double[]> getFusion(double[] p, double[] q) {
        List<double[]> resList = new ArrayList<>();
        int m = q.length;
        //先求出suffixorder(p)与prefixorder(q)
        double[] suffixp = new double[p.length - 1];
        double[] prefixq = new double[q.length - 1];

        //得出suffix(p)与prefix(q)
        System.arraycopy(p, 1, suffixp, 0, p.length - 1);
        System.arraycopy(q, 0, prefixq, 0, q.length - 1);

        double[] suffixorder = new double[p.length - 1];
        double[] prefixorder = new double[q.length - 1];

        if (suffixp.length == 1) {
            suffixorder[0] = 1;
            prefixorder[0] = 1;
        } else {
            suffixorder = getOrder(suffixp);
            prefixorder = getOrder(prefixq);
        }

        if (Arrays.equals(suffixorder, prefixorder) && !Arrays.equals(suffixp, prefixq)) {
            double[] t = new double[p.length + 1];
            if (p[0] < q[m - 1]) {
                t[0] = p[0];
                t[m] = q[m - 1] + 1;
                for (int i = 1; i < t.length - 1; i++) {
                    if (p[i] > q[m - 1]) {
                        t[i] = p[i] + 1;
                    } else {
                        t[i] = p[i];
                    }
                }
            } else {
                t[0] = p[0] + 1;
                t[m] = q[m - 1];
                for (int i = 0; i < t.length - 1; i++) {
                    if (q[i] > p[0]) {
                        t[i + 1] = q[i] + 1;
                    } else {
                        t[i + 1] = q[i];
                    }
                }
            }
            resList.add(t);
        }

        if (Arrays.equals(suffixorder, prefixorder) && Arrays.equals(suffixp, prefixq)) {
            double[] t = new double[p.length + 1];
            double[] k = new double[p.length + 1];

            t[0] = p[0] + 1;
            t[m] = p[0];
            for (int i = 1; i < t.length - 1; i++) {
                if (p[i] > p[0]) {
                    t[i] = p[i] + 1;
                } else {
                    t[i] = p[i];
                }
            }
            resList.add(t);

            k[0] = p[0];
            k[m] = p[0] + 1;
            for (int i = 1; i < k.length - 1; i++) {
                if (p[i] > p[0]) {
                    k[i] = p[i] + 1;
                } else {
                    k[i] = p[i];
                }
            }
            resList.add(k);
        }
        return resList;
    }

    private static List<Candidate> getInitialList(double[] in) {
        List<Candidate> candidateList = new ArrayList<>();
        List<Integer> supportList = new ArrayList<>();
        List<Integer> supportListTo = new ArrayList<>();
        for (int i = 0; i < in.length - 1; i++) {
            if (in[i + 1] > in[i]) {
                supportList.add(i + 1 + 1);
            } else if (in[i + 1] < in[i]) {
                supportListTo.add(i + 1 + 1);
            }
        }
        Integer[] supportArr = new Integer[supportList.size()];
        supportList.toArray(supportArr);
        Candidate candidate = new Candidate(new double[]{1, 2}, supportArr);
        candidateList.add(candidate);
        Integer[] supportArrTo = new Integer[supportListTo.size()];
        supportListTo.toArray(supportArrTo);
        Candidate candidateTo = new Candidate(new double[]{2, 1}, supportArrTo);
        candidateList.add(candidateTo);
        candidateList.stream().peek(x -> {
            x.setSupportPre(x.getSupport());
            x.setSupportSuf(x.getSupport());
        }).collect(Collectors.toList());
        return candidateList;
    }

    private static void printCostTime(long startTime) {
        System.out.println("花费总时间为:" + (System.currentTimeMillis() - startTime) + "ms");
//        System.out.println("---------------------------------------------------");
        MemoryLogger.getInstance().checkMemory();
        double maxMemory = MemoryLogger.getInstance().getMaxMemory();
        System.out.println("最大内存占用: " + maxMemory + " Mb");
    }

    private static void printCoOccurrence(List<CoOccurrence> coOccurrences) {

        if (freItemsetList == null || freItemsetList.size() == 0) {
//            System.out.println("无频繁模式！！！");
        }
//        System.out.println("频繁模式：");
        int freCount = 0;
        for (FreItemset freItemset : freItemsetList) {
//            System.out.println(Arrays.toString(freItemset.itemset) + " sup: " + freItemset.support);
            freCount++;
        }
//        System.out.println("频繁模式的个数是:" + freCount);
//        System.out.println("候选模式的个数是:" + candidateCount);

        allFreCount += freCount;
        candCount += candidateCount;

        if (coOccurrences == null || coOccurrences.size() == 0) {
//            System.out.println("无满足支持度的共生模式！！！");
            return;
        }
//        System.out.println("满足支持度的共生模式：");
//        for (CoOccurrence coOccurrence : coOccurrences){
//            printArray(coOccurrence.model);
//        }
//        System.out.println("共生频繁模式的个数为:" + coOccurrences.size());
        coFreCount += coOccurrences.size();
//        System.out.println("---------------------------------------------------");
        int total = 0;
//        System.out.println("满足支持度的共生出现为：");
        for (CoOccurrence coOccurrence : coOccurrences) {
            for (double[] arr : coOccurrence.appearList) {
//                printArray(arr);
                total++;
            }
        }
//        System.out.println("共生频繁子序列的个数为:" + total);
        coFreSeqCount += total;
//        System.out.println("---------------------------------------------------");
    }

    private static List<CoOccurrence> getPatternMatching(double[] in, double[] pattern, int supportTv) throws Exception {
        List<double[]> resList = new ArrayList<double[]>() {{
            add(new double[]{1, 2});
            add(new double[]{2, 1});
        }};
        List<Candidate> candidateList = new ArrayList<>();
        List<Candidate> candidateListNew = new ArrayList<>();
        //List<Candidate> candidates;
        while (resList.size() > 0) {
//            candidateList = new ArrayList<>();
            candidateListNew = new ArrayList<>();
            for (double[] candidateArr : resList) {
                int[] inBinaryArr = getBinary(in);
                int[] pBinaryArr = getBinary(candidateArr);
                //Integer[] subsetNumArr = getSubset(inBinaryArr, pBinaryArr);
                Integer[] subsetNumArr;
                if (candidateArr.length == 2) {
                    subsetNumArr = bndm(inBinaryArr, pBinaryArr);
                } else {
                    int[] sortedP = new int[pBinaryArr.length];
                    System.arraycopy(pBinaryArr, 0, sortedP, 0, sortedP.length);
                    Arrays.sort(sortedP);
                    int[] aux = new int[pBinaryArr.length];
                    genAux(aux, sortedP, pBinaryArr);
                    subsetNumArr = sbndm(inBinaryArr, pBinaryArr, aux, in);
                }
                Integer[] subsetNumArrNew = verificationStrategy(in, candidateArr, subsetNumArr);
                if (subsetNumArrNew.length >= supportTv) {
                    if (candidateArr.length > pattern.length){
                        candidateList.add(new Candidate(candidateArr, subsetNumArrNew));
                    }
                    candidateListNew.add(new Candidate(candidateArr, subsetNumArrNew));
                    freItemsetList.add(new FreItemset(candidateArr, subsetNumArrNew.length));
                }
            }
            resList = candidateListNew.stream().map(Candidate::getItemset).collect(Collectors.toList());
            if (resList.size() > 0) {
                resList = patternFusion(resList);
                candidateCount += resList.size();
            } else {
                break;
            }
        }
        if (candidateList == null || candidateList.size() == 0) {
            return null;
        }
//        candCount +=candidateList.size();
//        if (candidateList.get(0).itemset.length != pattern.length + 1) {
//            return null;
//        }
        List<CoOccurrence> coOccurrenceList = new ArrayList<>();
        for (Candidate candidate : candidateList) {
            double[] itemset = getItemset(candidate.itemset, pattern);
            if (Arrays.equals(getOrder(itemset), getOrder(pattern))) {
                List<double[]> appearList = new ArrayList<>();
                List<double[]> subModes = new ArrayList<>();
                if (!flag){
                    continue;
                }
                for (int index : candidate.support) {
                    int end = map.get(index + candidate.itemset.length - 1);
                    int start = map.get(index);
                    double[] appear = new double[end - start + 1];
                    System.arraycopy(input, start, appear, 0, appear.length);
                    appearList.add(appear);

                    int len;
                    if (flag) {
                        end = map.get(index + candidate.itemset.length - 2);
                        len = end - start + 1;
                    } else {
                        start = map.get(index + 1);
                        len = end - start + 1;
                    }
                    double[] subMode = new double[len];
                    System.arraycopy(input, start, subMode, 0, subMode.length);
                    subModes.add(subMode);
                }
                coOccurrenceList.add(new CoOccurrence(candidate.itemset, appearList, subModes));
            }
        }
        return coOccurrenceList;
    }

    private static double[] getItemset(double[] item, double[] pattern) {
        double[] itemset = new double[pattern.length];
        System.arraycopy(item, 0, itemset, 0, itemset.length);
        if (Arrays.equals(getOrder(itemset), getOrder(pattern))) {
            flag = true;
            return itemset;
        }
        System.arraycopy(item, 1, itemset, 0, itemset.length);
        flag = false;
        return itemset;
    }

    private static List<double[]> patternFusion(List<double[]> list) {

        List<double[]> resList = new ArrayList<>();

        for (double[] p : list) {
            for (double[] q : list) {
                int m = q.length;
                //先求出suffixorder(p)与prefixorder(q)
                double[] suffixp = new double[p.length - 1];
                double[] prefixq = new double[q.length - 1];

                //得出suffix(p)与prefix(q)
                System.arraycopy(p, 1, suffixp, 0, p.length - 1);
                System.arraycopy(q, 0, prefixq, 0, q.length - 1);

                double[] suffixorder = new double[p.length - 1];
                double[] prefixorder = new double[q.length - 1];

                if (suffixp.length == 1) {
                    suffixorder[0] = 1;
                    prefixorder[0] = 1;
                } else {
                    suffixorder = getOrder(suffixp);
                    prefixorder = getOrder(prefixq);
                }

                if (Arrays.equals(suffixorder, prefixorder) && !Arrays.equals(suffixp, prefixq)) {
                    double[] t = new double[p.length + 1];
                    if (p[0] < q[m - 1]) {
                        t[0] = p[0];
                        t[m] = q[m - 1] + 1;
                        for (int i = 1; i < t.length - 1; i++) {
                            if (p[i] > q[m - 1]) {
                                t[i] = p[i] + 1;
                            } else {
                                t[i] = p[i];
                            }
                        }
                    } else {
                        t[0] = p[0] + 1;
                        t[m] = q[m - 1];
                        for (int i = 0; i < t.length - 1; i++) {
                            if (q[i] > p[0]) {
                                t[i + 1] = q[i] + 1;
                            } else {
                                t[i + 1] = q[i];
                            }
                        }
                    }
                    resList.add(t);
                }

                if (Arrays.equals(suffixorder, prefixorder) && Arrays.equals(suffixp, prefixq)) {
                    double[] t = new double[p.length + 1];
                    double[] k = new double[p.length + 1];

                    t[0] = p[0] + 1;
                    t[m] = p[0];
                    for (int i = 1; i < t.length - 1; i++) {
                        if (p[i] > p[0]) {
                            t[i] = p[i] + 1;
                        } else {
                            t[i] = p[i];
                        }
                    }
                    resList.add(t);

                    k[0] = p[0];
                    k[m] = p[0] + 1;
                    for (int i = 1; i < k.length - 1; i++) {
                        if (p[i] > p[0]) {
                            k[i] = p[i] + 1;
                        } else {
                            k[i] = p[i];
                        }
                    }
                    resList.add(k);
                }
            }
        }
        return resList;
    }

    private static int[] getOrder(int[] seq) {
        int[] arr = new int[seq.length];
        System.arraycopy(seq, 0, arr, 0, seq.length);
        int[] order = new int[arr.length];
        int[] temp = new int[arr.length];
        System.arraycopy(arr, 0, temp, 0, arr.length);
        Arrays.sort(temp);

        for (int j = 0; j < arr.length; j++) {
            int min = temp[temp.length - 1] + 1;
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

    private static Integer[] verificationStrategy(double[] in, double[] candidateArr, Integer[] subsetNumArr) {
        List<Integer> subsetListNew = new ArrayList<>();
        List<SupportOrder> supportOrderList = new ArrayList<>();
        int index = 1;
        for (double order : candidateArr) {
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

    private static Integer[] getSubset(int[] inBinaryArr, int[] pBinaryArr) {
        List<Integer> subsetNumList = new ArrayList<>();
        if (inBinaryArr.length <= pBinaryArr.length) {
            return new Integer[0];
        } else {
            for (int i = 0; i < inBinaryArr.length; i++) {
                if (i + pBinaryArr.length <= inBinaryArr.length) {
                    int[] sub = new int[pBinaryArr.length];
                    System.arraycopy(inBinaryArr, i, sub, 0, pBinaryArr.length);
                    if (Arrays.equals(sub, pBinaryArr)) {
                        subsetNumList.add(i);
                    }
                } else {
                    break;
                }
            }
        }
        Integer[] subsetNumArr = new Integer[subsetNumList.size()];
        subsetNumList.toArray(subsetNumArr);
        return subsetNumArr;
    }

    private static int[] getBinary(double[] arr) {
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

    private static int[] getBinary(int[] arr) {
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

    private static void getInArr() throws Exception {

//        SDB1
//        File file = new File("E:/Dataset/CinCECGTorso_TEST.txt");
//        File file = new File("E:/Dataset/CinCECGTorso_TEST(20).txt");

        //SDB2
//        File file = new File("E:/Dataset/NonInvasiveFetalECGThorax1_TEST.txt");
//        File file = new File("E:/Dataset/NonInvasiveFetalECGThorax1_TEST_(90).txt");

//        SDB3
//        File file = new File("E:/Dataset/FreezerRegularTrain_TEST.txt");
//        File file = new File("E:/Dataset/FreezerRegularTrain_TEST（350）.txt");

//        SDB4
//        File file = new File("E:/Dataset/FiveCitiesTempData.txt");


//        File file = new File("E:/Dataset/PRSA_Data_Nongzhanguan.txt");


//        SDB5
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
//        SDB6
//        File file = new File("E:/Dataset/Crude Oil.txt");

//        SDB7
//        File file = new File("E:/Dataset/FiveCitiesTempData.txt");
//        File file = new File("E:/Dataset/Meat_TEST.txt");
//        File file = new File("E:/Dataset/ToeSegmentation1_TRAIN.txt");

//        SDB8
//        File file = new File("E:/Dataset/股票.txt");
//        File file = new File("E:/Dataset/PRSA_Data.txt");
//        File file = new File("E:/Dataset/Data-Stock.txt");

//        File file = new File("E:/Dataset/BeijingPM2.5.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5_2.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5_3.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5_4.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5_5.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5_6.txt");

//        File file = new File("E:/Dataset/ChengduPM2.5.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5.txt");
//        File file = new File("E:/Dataset/PRSA_Data.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_HeartRate.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_PRInterval.txt");
//        File file = new File("E:/Dataset/KURIAS-ECG_PAxis.txt");

//                File file = new File("E:/Dataset/BeijingPM2.5_3.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5_5.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5_7.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5_9.txt");
//        File file = new File("E:/Dataset/BeijingPM2.5_11.txt");


//        File file = new File("E:/Dataset/天气.txt");
//        File file = new File("E:/Dataset/分类/ShapeletSim_TEST.txt");


//                File file = new File("E:/Dataset/分类/ShapeletSim_TEST.txt");
//        File file = new File("E:/Dataset/分类/ShapeletSim_TEST270.txt");
//        File file = new File("E:/Dataset/分类/ShapeletSim_TEST450.txt");
//        File file = new File("E:/Dataset/分类/ShapeletSim_TEST630.txt");
//        File file = new File("E:/Dataset/分类/ShapeletSim_TEST810.txt");
//        File file = new File("E:/Dataset/分类/ShapeletSim_TEST990.txt");


//        COVID-19
//        File file = new File("E:/Dataset/分类/CSSE COVID-19 Dataset.txt");
//        File file = new File("E:/DD/Beef_TEST.txt");
//        File file = new File("E:/Dataset/分类/Car_TEST.txt");
//        File file = new File("E:/Dataset/分类/ShapeletSim_TEST.txt");
//        File file = new File("E:/Dataset/PRSA_Data.txt");
//        File file = new File("E:/Dataset/1WTl-2.txt");

//        File file = new File("E:/Dataset/分类/CSSE COVID-19.txt");
//        File file = new File("E:/Dataset/分类/BTC.txt");
//        File file = new File("E:/Dataset/分类/Beef_TEST.txt");
//        File file = new File("E:/Dataset/Meat_TEST.txt");

        BufferedReader br = new BufferedReader(new FileReader(file));
        String s;
        //使用readLine方法，一次读一行
        while ((s = br.readLine()) != null) {
            freItemsetList = new ArrayList<>();
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
            double[] in = new double[inList.size()];
            int i = 0;
            for (double inLine : inList) {
                in[i++] = inLine;
            }
            input = in;
            readLine();
//            System.gc();
        }
        br.close();
    }

    private static void readLine() throws Exception {
        map = new HashMap<>();
        candidateCount = 2;
        int supportTv = 6000;
        double similarityTv = 0.5;

//        double[] p = new double[]{1.0, 2.0};
//       double[] p = new double[]{4,5,2,3};

//       double[] p = new double[]{1,3,2,5};
//        double[] p = new double[]{1,3,2,5,4,7};
//        double[] p = new double[]{1,3,2,5,4,7,6,9};
//         double[] p = new double[]{3,4,1,2};


//        double[] p = new double[]{1,3,2,5};
//        double[] p = new double[]{1,6,3,5};
//        double[] p = new double[]{1,6,3,5,2,4};
//     double[] p = new double[]{1,3,2,5};
//        double[] p = new double[]{1,3,2,5,4,7};
//        double[] p = new double[]{1,3,2,5,4,7,6,9};

//         double[] p = new double[]{4,5,2,3};
//         double[] p = new double[]{4,5,2,3,1,6};
//         double[] p = new double[]{1.0, 5.0, 2.0, 6.0, 3.0, 4.0};
//       double[] p = new double[]{1.0, 5.0, 3.0, 4.0, 2.0, 6.0};

//    double[] p = new double[]{4,5,2,3,1,9,7,8};

         double[] p = new double[]{1,3,2,5,4,6};
//         double[] p = new double[]{1,3,2,5,4,7,6,9};

//        double[] p = new double[]{3,6,4,5,1,2};
//                double[] p = new double[]{1,3,2,5,4,6};
//       double[] p = new double[]{1.0, 4.0, 3.0,6.0,5.0, 2.0};
//         double[] p = new double[]{4.0, 3.0, 6.0, 2.0, 5.0, 1.0};

//         double[] p = new double[]{1,3,2,5};
//      double[] p = new double[]{1,3,2,5,4,7};
//         double[] p = new double[]{1,3,2,5,4,7,6,8};
//         double[] p = new double[]{2,3,1,8};
//        double[] p = new double[]{2,3,1,8,6,7};
//         double[] p = new double[]{2,3,1,8,6,7,4,5};

//        double[] p = new double[]{2.0, 3.0,1.0};
//        double[] p = new double[]{1.0, 4.0,2.0,3.0};
//        double[] p = new double[]{1,3,2,5,4};
//       double[] p = new double[]{2,4,1,5,3};
//         double[] p = new double[]{5,6,3,4,1,2};
//        double[] p = new double[]{1,3,2,5,4,7,6};
//      double[] p = new double[]{1,3,2,5,4,7,6,8};

//       double[] p = new double[]{1,3,2,5,4,6};
//     double[] p = new double[]{3.0, 4.0, 1.0, 7.0, 5.0, 6.0, 2.0};
//       double[] p = new double[]{3.0, 4.0, 1.0, 7.0, 5.0, 6.0, 2.0,8.0};
//        double[] p = new double[]{6.0, 7.0, 4.0, 5.0, 2.0, 3.0};
//        double[] p = new double[]{7,8,5,6,3,4,1,2};
//        double[] p = new double[]{8,7,3,2,4,1,5,6};

//        double[] p = new double[]{1, 2};
//        double[] p = new double[]{2,1,4,3};
//        double[] p = new double[]{2,1,4,3,6,5};
//        double[] p = new double[]{2,1,4,3,6,5,8,7};


        double[] pattern = getPatternExtreme(p);
        double[] in = getExtremePoint(input);
        //只有1是对的
        int version =1;
        List<CoOccurrence> coOccurrences;
        switch (version) {
            case 1:
            default:
                coOccurrences = getPatternMatching(in, pattern, supportTv);
                break;
            case 2:
                coOccurrences = getIndexMethod(in, pattern, supportTv);
                break;
            case 3:
                coOccurrences = getEnumeration(in, pattern, supportTv);
                break;
            case 4:
                coOccurrences = getIndexMethodNoPrune(in, pattern, supportTv);
                break;
            case 5:
                coOccurrences = getMtaMethod(in, pattern, supportTv);
                break;
            case 6:
                coOccurrences = getFimSwMethod(in, pattern, supportTv);
                break;
        }
        printCoOccurrence(coOccurrences);
        //共生模式相似度阈值过滤并排序
//        List<Approximate> approximates = getSimilarity(coOccurrences, p, similarityTv);
//        printApproximate(approximates);
        //输出算法运行时间
        // printCostTime(startTime);
    }

    private static void printArray(double[] arr) {
        for (double i : arr) {
            System.out.print(i + " ");
        }
        System.out.println();
    }

    private static double[] toArray(String s) {
        if (s == null) {
            return null;
        }
        s = s.replaceAll(" ", "");
        s = s.substring(1, s.length() - 1);
        String[] str = s.split(",");
        double[] arr = new double[str.length];
        for (int i = 0; i < str.length; i++) {
            arr[i] = Double.parseDouble(str[i]);
        }
        return arr;
    }

    static class CoOccurrence {
        private double[] model;
        private List<double[]> appearList;
        private List<double[]> subModes;

        public CoOccurrence(double[] model, List<double[]> appearList, List<double[]> subModes) {
            this.model = model;
            this.appearList = appearList;
            this.subModes = subModes;
        }

        public double[] getModel() {
            return model;
        }

        public void setModel(double[] model) {
            this.model = model;
        }

        public List<double[]> getAppearList() {
            return appearList;
        }

        public void setAppearList(List<double[]> appearList) {
            this.appearList = appearList;
        }

        public List<double[]> getSubModes() {
            return subModes;
        }

        public void setSubModes(List<double[]> subModes) {
            this.subModes = subModes;
        }
    }

    static class SupportOrder {
        private double order;
        private Integer index;

        public SupportOrder(double order, Integer index) {
            this.order = order;
            this.index = index;
        }

        public double getOrder() {
            return order;
        }

        public void setOrder(Integer order) {
            this.order = order;
        }

        public Integer getIndex() {
            return index;
        }

        public void setIndex(Integer index) {
            this.index = index;
        }
    }

    static class Candidate {
        private double[] itemset;
        private Integer[] support;
        private Integer[] supportPre;
        private Integer[] supportSuf;

        public Candidate(double[] itemset, Integer[] support) {
            this.itemset = itemset;
            this.support = support;
        }

        public double[] getItemset() {
            return itemset;
        }

        public void setItemset(double[] itemset) {
            this.itemset = itemset;
        }

        public Integer[] getSupport() {
            return support;
        }

        public void setSupport(Integer[] support) {
            this.support = support;
        }

        public Integer[] getSupportPre() {
            return supportPre;
        }

        public void setSupportPre(Integer[] supportPre) {
            this.supportPre = supportPre;
        }

        public Integer[] getSupportSuf() {
            return supportSuf;
        }

        public void setSupportSuf(Integer[] supportSuf) {
            this.supportSuf = supportSuf;
        }
    }

    static class Approximate {
        private double similarity;
        private double[] proximity;

        public Approximate(double similarity, double[] proximity) {
            this.similarity = similarity;
            this.proximity = proximity;
        }

        public double getSimilarity() {
            return similarity;
        }

        public void setSimilarity(double similarity) {
            this.similarity = similarity;
        }

        public double[] getProximity() {
            return proximity;
        }

        public void setProximity(double[] proximity) {
            this.proximity = proximity;
        }
    }

    static class FreItemset {
        private double[] itemset;
        private Integer support;

        public FreItemset(double[] itemset, Integer support) {
            this.itemset = itemset;
            this.support = support;
        }

        public double[] getItemset() {
            return itemset;
        }

        public void setItemset(double[] itemset) {
            this.itemset = itemset;
        }

        public Integer getSupport() {
            return support;
        }

        public void setSupport(Integer support) {
            this.support = support;
        }
    }

    static class FimTemp {
        List<String> appears;
        List<Integer> supportList;

        public FimTemp() {
        }

        public FimTemp(List<String> appears, List<Integer> supportList) {
            this.appears = appears;
            this.supportList = supportList;
        }

        public List<String> getAppears() {
            return appears;
        }

        public void setAppears(List<String> appears) {
            this.appears = appears;
        }

        public List<Integer> getSupportList() {
            return supportList;
        }

        public void setSupportList(List<Integer> supportList) {
            this.supportList = supportList;
        }
    }
}

