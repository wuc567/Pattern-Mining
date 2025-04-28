package algorithms;

        import java.io.*;
        import java.util.*;

//2024.7.9 对线性拟合部分进行修改（主要是索引），KMP2文件比KMP运行要好
public class OUTO_kmp {
    public static List<Integer> μ = new ArrayList<>();
    public static List<Integer> π = new ArrayList<>();
    public static List<Float> S = new ArrayList<>(); // sequence
    public static List<List<Integer>> Fre=new ArrayList<>();
    public static List<List<Integer>> Fre_index=new ArrayList<>();

    final static int TXT_SIZE = 80000;
    final static int PATTERN_SIZE = 10000;
    final static int MAX_LINE = 80000;
    final static int MAXSIZE = 80000;
    final static int Max = 256;
    static int MAX = 80000;
    static int count;
    static int candidate_num = 0;
    static int compnum = 2;
    static int OUTO_num=0;

    public static int [][] F2=new int[900][900]; // 2-长度频繁模式集
    static int [][] F=new int[900][900]; // 频繁模式集
    static int [][] C=new int[2000][2000]; // 候选模式集
    static int Snum;
    static int frequent_num = 0;
    static int LEN = 0;
    static float[] text = new float[TXT_SIZE]; // 时间序列数据s
    public static int[] pattern = new int[PATTERN_SIZE]; // 模式p
    static int[] sorted_pat = new int[PATTERN_SIZE]; // 排序后的模式p
    static int[] index = new int[PATTERN_SIZE]; // 辅助索引 index[i]
    static int[] trans_text = new int[TXT_SIZE-2];
    static int[] trans_pattern = new int[PATTERN_SIZE-2];
    static int pattern_num = 0;
    static PrintWriter myPw;
    static float[] sDB = new float[100000];
    static int seqlen;


    static float fitt =5;

    static float xishu= 2.5F;

    public static float DTW;

    public static int minsup=200;
    //1:40, 2:205, 3:380, 4:340, 5:320, 6:500, 7:1030, 8:1220

    public static void main(String[] args) throws IOException {
   long dwBeginTime = System.currentTimeMillis();
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

         //1改编文件 原始序列长度=2496  fit=2， minsup=500，xishu=2.5
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

        read_file(fileName);
        generate_candF2(pattern);
        generate_fre(F2);
        Cancalute(pattern);
        Fre=judge_maxfreoop(Fre,Fre_index);
        for (int i = 0; i < Fre.size(); i++) {
            List<Integer> pattern = Fre.get(i);
            List<Integer> pattern_index = Fre_index.get(i);
            // System.out.println("pattern:  "+pattern+"   "+pattern_index);
            judge_OUTO(pattern,pattern_index);
        }
        long dwEndTime = System.currentTimeMillis();
        MemoryLogger.getInstance().checkMemory();
        /** memory of last execution */
        double maxMemory = MemoryLogger.getInstance().getMaxMemory();
        MemoryLogger.getInstance().reset();
        System.out.println("频繁模式的个数:"+count);
        System.out.println("候选模式的个数:"+compnum);
        System.out.println("最大频繁模式的个数:"+Fre.size());
        System.out.println("OUTO num:"+OUTO_num);
        System.out.println("Maximum memory usage : " + maxMemory + " mb.");
        System.out.println("Time cost:" + (dwEndTime - dwBeginTime));
        System.out.println();

    }



    public static class OrderStatisticTree {
        /**
         * 颜色
         */
        public enum Color { RED, BLACK};

        /**
         * 数据节点
         */
        public static class Node {
            float key;
            Node parent; //父节点
            Node left; //左子节点
            Node right; //右子节点
            Color color; //节点颜色
            int size; //所在子树节点的数量
            public Node(float key2) {
                this.key = key2;
            }

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
         * @param x 待查找节点
         * @return 节点x在树中从小到大排序的序号。
         */
        public int rank(Node x) {
            int r = x.left.size + 1; //当前节点在以x为根的子树中的序号是左子树的节点个数加1
            Node y = x;
            while(y != root) {
                if(y == y.parent.right) { //如果y是右子节点
                    r = r + y.parent.left.size + 1; //序号需要加上左兄弟子树的数量，再加父节点
                }
                y = y.parent;
            }
            return r;
        }

        /**
         * 左旋转。
         * @param x 支点
         */
        private void leftRotate(Node x) {
            Node y = x.right; // y是x的右子节点
            x.right = y.left; // y的左子树转换成x的右子树
            if (y.left != nil)
                y.left.parent = x;
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
         * //@param x 支点
         */
        private void rightRotate(Node y) {
            Node x = y.left; // x是y的右子节点
            y.left = x.right; // x的右子树转换成y的左子树
            if (x.right != nil)
                x.right.parent = y;
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
         * @param k 节点的键值
         * @return 返回键值为k的节点
         */
        public Node search(float k) {
            return search(root, k);
        }

        /**
         * 采用递归法查找键值为k的节点。
         * @param x 当前节点
         * @param k 节点的键值
         * @return 返回键值为k的节点
         */
        private Node search(Node x, float k) {
            if(x == nil || k == x.key) {
                return x;
            } else if(k < x.key) {
                return search(x.left, k);
            } else {
                return search(x.right, k);
            }
        }

        /**
         * 采用迭代法查找键值为k的节点。
         * //@param x 当前节点
         * @param k 节点的键值
         * @return 返回键值为k的节点
         */
        public Node iterativeSearch(float k) {
            return iterativeSearch(root, k);
        }

        /**
         * 采用迭代法查找键值为k的节点。
         * @param x 当前节点
         * @param k 节点的键值
         * @return 返回键值为k的节点
         */
        private Node iterativeSearch(Node x, float k) {
            while(x != nil && k != x.key) {
                if(k < x.key) {
                    x = x.left;
                } else {
                    x = x.right;
                }
            }
            return x;
        }

        /**
         * 返回树的最小键值的节点。
         * @return 最小键值的节点
         */
        public Node minimum() {
            return minimum(root);
        }

        /**
         * 返回树的最小键值的节点。
         * @param x 当前节点
         * @return 最小键值的节点
         */
        private Node minimum(Node x) {
            while(x.left != nil) {
                x = x.left;
            }
            return x;
        }

        /**
         * 返回树的最大键值的节点。
         * @return 最大键值的节点
         */
        public Node maximum() {
            return maximum(root);
        }

        /**
         * 返回树的最大键值的节点。
         * @param x 当前节点
         * @return 最大键值的节点
         */
        private Node maximum(Node x) {
            while(x.right != nil) {
                x = x.right;
            }
            return x;
        }

        /**
         * 返回指定节点x的后继节点。
         * @param x 当前节点
         * @return x的后继节点；如果x具有最大键值，返回null
         */
        public Node successor(Node x) {
            if(x.right != nil) {
                return minimum(x.right);
            }
            Node y = x.parent;
            while(y != nil && x == y.right) {
                x = y;
                y = y.parent;
            }
            return y;
        }

        /**
         * 返回指定节点x的前驱节点。
         * @param x 当前节点
         * @return x的前驱节点；如果x具有最小键值，返回null
         */
        public Node predecessor(Node x) {
            if(x.left != nil) {
                return maximum(x.left);
            }
            Node y = x.parent;
            while(y != nil && x == y.left) {
                x = y;
                y = y.parent;
            }
            return y;
        }

        /**
         * 插入节点。
         * @param z 待插入节点
         */
        public void insert(Node z) {
            Node y = nil; //当前节点的父节点
            Node x = root; //当前节点
            while(x != nil) { //迭代查寻z应该所在的位置
                y = x;
                y.size++; //沿着查找路径，将z的所有先辈的size加1
                if(z.key < x.key) {
                    x = x.left;
                } else {
                    x = x.right;
                }
            }
            z.parent = y;
            z.size = 1; //z是叶节点
            if(y == nil) {
                root = z; //如果没有父节点，则插入的节点是根节点。
            } else if(z.key < y.key) {
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
         * @param z 待插入节点
         */
        public void insertFixup(Node z) {
            while(z.parent.color == Color.RED) { //违反条件4，并且保证z有爷爷
                if(z.parent == z.parent.parent.left) { //z的父节点是左子节点
                    Node y = z.parent.parent.right;
                    if(y.color == Color.RED) { //如果z的叔叔是红
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
                    if(y.color == Color.RED) {
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
            while(p != nil) {
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

            if(y.color == Color.BLACK) {
                deleteFixup(x);
            }
            return y;
        }

        /**
         * 按红黑树规则进行调整。
         * //@param z 待删除节点
         */
        private void deleteFixup(Node x) {
            while (x != nil && x != root && x.color == Color.BLACK) {
                if (x == x.parent.left) {
                    Node w = x.parent.right;
                    if (w == nil)
                        return;
                    if (w.color == Color.RED) {
                        w.color = Color.BLACK;
                        x.parent.color = Color.RED;
                        leftRotate(x.parent);
                        w = x.parent.right;
                    }
                    if (w == nil)
                        return;
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
                    if (w == nil)
                        return;
                    if (w.color == Color.RED) {
                        w.color = Color.BLACK;
                        x.parent.color = Color.RED;
                        rightRotate(x.parent);
                        w = x.parent.left;
                    }
                    if (w == nil)
                        return;
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

    public static List<Integer> computePrefixRep(int[] pattern, int m){
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

    public static int[] sort(List<Integer> src){
        int k, slen = 0, y = 0;
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

    public static List<Integer> computeFailureFunction(int[] pattern, int m){
        List<Integer> πTemp = new ArrayList<>();
//		int m = pattern.length;
        int k = 0;
        if (m >= 2) {
            πTemp.add(0, 0);
            πTemp.add(1, 1);
        }
        for(int q = 2; q < m; q++){
            int position = 0;
            for(k = 0; k < q; k++){
                List<Integer> pre = new ArrayList<>();
                List<Integer> suf = new ArrayList<>();
                for(int j = 0; j <= k; j++){
                    pre.add(pattern[j]);
                }
                for(int j = q-k; j <= q; j++){
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

    public static int KMPOrderMatcher(float[] series, int[] pattern, int n, int m){
        int support = 0;
//		int n = series.length;
//		int m = pattern.length;
        List<Integer> p_index=new ArrayList<>();
        μ = computePrefixRep(pattern,m);
		/*System.out.print("μ[P]: ");
		for (Integer r : μ) {
			System.out.print(r+",");
		}
		System.out.println();*/
        π = computeFailureFunction(pattern,m);
		/*System.out.print("π[P]: ");
		for (Integer r : π) {
			System.out.print(r+",");
		}
		System.out.println();*/
        OrderStatisticTree tree = new OrderStatisticTree();
        int q = 0;
        int r = 0;
        float key;
        int i = 0;
        int k = 0;
        for(; i < n; i++){
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
            while(q > 0 && r != μ.get(q)){
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
                p_index.add(i+1);
//				i = i - π.get(q-1);
                i = i - k + 1;
                q = 0;
                k = 0;
                tree = new OrderStatisticTree();
            }

        }
        Fre_index.add(p_index);
        return support;

    }


    public static float calculateVariance(List<Float> timeSeries) {

        float sum = 0;
        for (float value : timeSeries) {
            sum += value;
        }
        float mean = sum / timeSeries.size();

        // 计算每个样本点与平均值的差的平方
        float squaredDiffSum = 0;
        for (float value : timeSeries) {
            squaredDiffSum += Math.pow(value - mean, 2);
        }

        // 计算总体方差
        float variance =squaredDiffSum / (timeSeries.size());

        //标准差
        float svariance= (float) Math.sqrt(variance);
        // System.out.println("标准差: " + svariance);


        return svariance;
    }



    public static int generate_candF2(int pattern[])
    {
        int i,j,support_full=0,k=0;
        // 长度为2的候选模式
        int[][] C2 ={{1,2},{2, 1}};
        // 计算候选模式支持度并输出频繁模式
        for(j=0;j<2;j++)
        {
            for (int h=0;h<2;h++){
                pattern[h]=C2[j][h];
            }
            // 支持度计算
            support_full = KMPOrderMatcher(sDB, pattern, sDB.length, 2);
            /*System.out.println("候选计算模式：");
            System.out.print("(");
            for(int x=0;x<2;x++){
                System.out.print(C2[j][x]);
                if(x<1)System.out.print(",");
            }
            System.out.print(")");
            System.out.println("#support:"+support_full);*/
            if(support_full>=minsup){
                List<Integer> p=new ArrayList<>();
                count++;
                frequent_num++;
//                System.out.println("保序模式：");
                //System.out.print("(");
                for(int x=0;x<2;x++){
                    F2[j][x]=C2[j][x];
                    //System.out.print(F2[j][x]);
                    //if(x<1)System.out.print(",");
                    p.add(pattern[x]);
                 }
                Fre.add(p);
                //System.out.print(")");
                //System.out.println("#support:"+support_full);
            }
            for(int f=0;f<2;f++){
                pattern[f]=0;
            }
        }
        return 0;
    }

    /**
     * 模式融合，生成候选模式
     * 遍历F中与p相同长度的模式q，根据模式融合策略将p和q融合为候选模式c。
     * @param fre
     * @return
     */
    public static int generate_fre(int fre[][]){
        if(frequent_num==0){
            return 0;
        }
        int slen=0,y=0;
        while(y<50){
            if(fre[0][y]!=0)
                slen++;
            y++;
        }
        int[] Q = new int[slen-1];
        int[] R = new int[slen-1];

        for(int i=0;i<frequent_num;i++)
        {
            try{
                // 求后缀
                System.arraycopy(fre[i], 1, Q, 0, slen-1);
                // 求后缀
            }catch(ArrayIndexOutOfBoundsException e){
                System.out.println(e);
            }
            for(int j=0;j<frequent_num;j++){
                try{
                    //求前缀
                    System.arraycopy(fre[j], 0, R, 0, slen-1);
                }catch(ArrayIndexOutOfBoundsException e){
                    System.out.println(e);
                }
                List<Integer> QList = new ArrayList<>();
                List<Integer> RList = new ArrayList<>();
                for (Integer q : Q) {
                    QList.add(q);
                }

                for (Integer r : R) {
                    RList.add(r);
                }

                //前后缀相对顺序相同
                if(Arrays.equals(sort(QList),sort(RList))){
                    //最前最后位置相等，拼接成两个模式
                    if(fre[i][0]==fre[j][slen-1])
                    {
                        C[candidate_num][0]=fre[i][0];
                        C[candidate_num+1][0]=fre[i][0]+1;
                        C[candidate_num][slen]=fre[i][0]+1;
                        C[candidate_num+1][slen]=fre[i][0];
                        for(int t=1;t<slen;t++){
                            if(fre[i][t]>fre[j][slen-1]){
                                //中间位置增长
                                C[candidate_num][t]=fre[i][t]+1;
                                C[candidate_num+1][t]=fre[i][t]+1;
                            }else{
                                C[candidate_num][t]=fre[i][t];
                                C[candidate_num+1][t]=fre[i][t];
                            }
                        }
                        candidate_num+=2;
                        compnum+=2;
                    }else if(fre[i][0]<fre[j][slen-1])    //第一个位置比最后一个位置小
                    {

                        C[candidate_num][0]=fre[i][0];              //小的不变
                        C[candidate_num][slen]=fre[j][slen-1]+1;  //大的加一

                        for(int t=1;t<slen;t++){
                            if(fre[i][t]>fre[j][slen-1]){
                                //fre[i][t]+=1;   //中间位置增长
                                C[candidate_num][t]=fre[i][t]+1;

                            }else{
                                C[candidate_num][t]=fre[i][t];
                            }
                        }
                        candidate_num+=1;
                        compnum+=1;
                    }else{
                        C[candidate_num][0]=fre[i][0]+1;              //大的加一
                        C[candidate_num][slen]=fre[j][slen-1];       //小的不变
                        for(int t=0;t<slen-1;t++){
                            if(fre[j][t]>fre[i][0]){
                                C[candidate_num][t+1]=fre[j][t]+1;   //中间位置增长
                            }else{
                                C[candidate_num][t+1]=fre[j][t];
                            }
                        }
                        candidate_num+=1;
                        compnum+=1;
                    }
                }else{;}
            }
        }
        return 0;
    }

    /**
     * 生成频繁模式集F
     * @param pat 候选模式
     */
    public static void Cancalute(int pat[]) {

        int support_full;
        int r=0,len=0;
        frequent_num=0;
        while(candidate_num!=0){
            while(r<C.length){
                if(C[0][r]!=0)
                    len++;
                r++;
            }
            for(int v=0;v<candidate_num;v++) {

                for (int h=0;h<len;h++){
                    pat[h]=C[v][h];
                }
                // 计算支持度
                support_full = KMPOrderMatcher(sDB, pattern, sDB.length, len);
                /*System.out.println("候选模式：");
                System.out.print("(");
                for(int t=0;t<len;t++){
                    System.out.print(C[v][t]);
                    if(t<len-1)System.out.print(",");
                }
                System.out.print(")");
                System.out.println("#support:"+support_full);*/
                if(support_full>=minsup) {
                    List<Integer> p=new ArrayList<>();
                    count++;
//                    System.out.println("保序模式：");
                    // System.out.print("(");
                    for(int t=0;t<len;t++){
                        F[frequent_num][t]=C[v][t];
                        p.add(pattern[t]);
                        // System.out.print(F[frequent_num][t]);
                        // if(t<len-1)System.out.print(",");
                    }
                    //System.out.print(")");
                    Fre.add(p);
                    frequent_num++;
                    //System.out.println("#support:"+support_full);
                }
            }
            r=0;len=0;
            for(int i=0;i<C.length;i++){
                for(int j=0;j<C[i].length;j++){
                    C[i][j]=0;
                }
            }
            candidate_num=0;
            // 模式融合
            generate_fre(F);
            for(int i=0;i<F.length;i++){
                for(int j=0;j<F[i].length;j++){
                    F[i][j]=0;
                }
            }
            frequent_num=0;
        }
    }

    /**
     * 将文件读入到float[]数组中
     * @throws IOException
     */
    public static void read_file(String filePath) throws IOException {
        long begintime = System.currentTimeMillis();
        File file = new File(filePath);

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

                //初始数据列表
                List<Float> rawdataTemp = new ArrayList<>();

                //rawdataTemp存储的是一行数据
                //valueStrings.length是每行数据个数
                //使用逗号,分割该行数据到valueStrings数组中。
                //将每个字符串转换为Double类型，并添加到rawdataTemp列表中。
                for (int j = 0; j < valueStrings.length; j++) {
                    String value = valueStrings[j].trim( ); // 去除字符串两端的空白字符
                    if (!value.isEmpty()) {
                        sDB[j] = Float.parseFloat(valueStrings[j]);
                        rawdataTemp.add(sDB[j]);
                    }
                }


                //提取极值点的列表
                List<Float> extremepointsTemp = new ArrayList<>();
                List<Integer> extremepointsTempIndex = new ArrayList<>();

                //最终关键点集合
                List<Float> finalextremepointsTemp = new ArrayList<>();
                List<Integer> finalextremepointsTempIndex = new ArrayList<>();


                extremepointsTempIndex=extraction(sDB);

                boolean hasnewExtremePoints = true;
                int i = 0;
                List<Float> newExtremePoint = null;
                List<Integer> newExtremePointIndex = null;

                for (Integer extremepointindex : extremepointsTempIndex) {
                    finalextremepointsTempIndex.add(extremepointindex);
                }
                //此处只输出了一条序列的极值点
                while (hasnewExtremePoints && i < extremepointsTempIndex.size()-1 ) {
                    //  System.out.println("main中极值点个数"+extremepointsTempIndex.size());
//                    hasnewExtremePoints = false;

                    int startIndex = extremepointsTempIndex.get(i);
                    int endIndex = extremepointsTempIndex.get(i + 1);

                    float startValue = sDB[startIndex];
                    float endValue = sDB[endIndex];

                    //执行递归和拟合
                    newExtremePointIndex = recursiveFit(sDB, extremepointsTempIndex, startIndex, endIndex, startValue, endValue);

                    if (!newExtremePointIndex.isEmpty()) {
                        // 如果有新的极值点添加到列表中，更新标志位
                        hasnewExtremePoints = true;

                    }
                    for (Integer index : newExtremePointIndex) {
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

                List<Float> A = new ArrayList<>();
                for (Integer b : B) {
                    S.add(sDB[b]);
                    A.add(sDB[b]);
                }
                //   System.out.println("A: " + A);//A是单条序列
                S=A;

                //4. 最大拟合差
                System.out.println("S个数: " +  S.size());
                float ddtw=calculateVariance(S);
                DTW=xishu*ddtw;

                System.out.println("DTW: "+DTW);
            }
        } catch (IOException e) {
            System.err.println("无法读取文件: " + filePath);
            e.printStackTrace();
        }
    }


    /**
     * 提取极值点 数组从0开始存储,n个数字,0——n-1
     * @param in
     * @return
     */
    private static List<Integer> extraction(float[] in) {
        List<Float> list = new ArrayList<>();
        List<Integer> list_index=new ArrayList<>();
        list.add(in[0]);
        list_index.add(0);
        for (int i = 1; i < in.length - 1; i++){
            if ((in[i] >= in[i - 1] && in[i] > in[i + 1]) || (in[i] > in[i - 1] && in[i] >= in[i + 1])){
                list.add(in[i]);
                list_index.add(i);
            } else if ((in[i] <= in[i - 1] && in[i] < in[i + 1]) || (in[i] < in[i - 1] && in[i] <= in[i + 1])){
                list.add(in[i]);
                list_index.add(i);
            }
        }
        list.add(in[in.length - 1]);
        list_index.add(in.length - 1);
        return list_index;
    }



    //单条序列中相邻两个极值点之间的，判断有无新的极值点,返回新的点的位置索引
    private static List<Integer> recursiveFit(float[] sDB,List<Integer> extremepointsTempIndex,int startIndex, int endIndex,float startValue,float endValue) {
        List<Float> newExtremePoint = new ArrayList<>();
        float data=-1;
        List<Integer> newExtremePointIndex = new ArrayList<>();
        int index=-1;

        float maxfitabsValue = 0;
        int maxFitIndex = -1;

        if (endIndex - startIndex <= 1) {
            // 停止拟合
            return newExtremePointIndex;
        }
//        System.out.println("区间[" + "s" + startIndex + "," + "s" + endIndex + "]拟合值:");


        for (int j = startIndex + 1; j < endIndex; j++) {
            float fitDataValue = linearInterpolation(j, startIndex, endIndex, startValue, endValue);
            float originalDataValue = sDB[j];


            float fitAbsValue = Math.abs(fitDataValue - originalDataValue);

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
            newExtremePointIndex.add(index);
        }

        if (maxFitIndex == -1) {
            return newExtremePointIndex;
        }

        return newExtremePointIndex;
    }


    public static float linearInterpolation(int currentIndex, int startIndex, int endIndex, float startValue,
                                            float endValue) {
        float t = (float) (currentIndex - startIndex) / (endIndex - startIndex);
        return startValue + t * (endValue - startValue);
    }



    //判断是否是最大频繁保序模式，模式支持度为sup_num,模式Cd,对应位置索引Z
    private static List<List<Integer>> judge_maxfreoop(List<List<Integer>>Fre,List<List<Integer>>Fre_index) {
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



    //@param Cd 本轮生成的候选模式，且频繁
    //*@param Z 索引集合
    //outlying pattern,判断每个频繁保序模式，其是否存在异常出现出现
    private static void judge_OUTO(List<Integer> Cd, List<Integer> Z) {
        int number = 0;

        List<Float> subSequence = new ArrayList<>();//存储单个子序列
        List<List<Float>> SequenceList = new ArrayList<>();//存储所有子序列
        List<Float> means = new ArrayList<>();//存储所有均值
        List<Float> meanss = new ArrayList<>();//存储所有均值
        List<Float> de = new ArrayList<>();//存储所有标准差
        List<Float> des = new ArrayList<>();//存储所有标准差

        // Step 1: 提取所有子序列均值
        for (Integer endIndex : Z) {
            for (int k = 0; k < Cd.size(); k++) {
                //index 是第一个子序列在S中的初始位置（首位）索引
                int index = endIndex - Cd.size() + k;
                float a = sDB[index+2];
                subSequence.add(a);
            }
            float mean =calculateMean(subSequence);
            float devation=calculateVariance(subSequence);
            means.add(mean);
            meanss.add(mean);
            de.add(devation);
            des.add(devation);
            SequenceList.add(new ArrayList<>(subSequence));
            subSequence.clear();
        }

        //System.out.println("子序列集合： "+SequenceList);

        // Step 2: 计算均值四分位数和四分位距
        float mQ1 = calculatePercentile(means, 25);
        float mQ3 = calculatePercentile(means, 75);
        float mIQR = 1.5f*(mQ3 - mQ1);

        //计算标准差四分位数和四分位距
        float dQ1 = calculatePercentile(de, 25);
        float dQ3 = calculatePercentile(de, 75);
        float dIQR = 1.5f*(dQ3 - dQ1);


        // Step 4: 判断每个子序列均值是否在区间内，如果不在区间内，则与其他子序列进行DTW计算
        for (int i = 0; i < SequenceList.size(); i++) {

            float mean = meanss.get(i);
            float devation =des.get(i);
            //System.out.println("均值： "+mean);

            //均值判断是否可能为OUTO
            if (!isWithinBounds(mean, mQ1 - mIQR, mQ3 + mIQR)||
                    (isWithinBounds(mean, mQ1 - mIQR, mQ3 + mIQR)&&!isWithinBounds(devation, dQ1 -dIQR, dQ3 + dIQR))) {

                int num =0;
                List<Float> A = SequenceList.get(i);
                // System.out.println("异常子序列： "+A);
                num++;

                for (int j = 0; j < SequenceList.size(); j++) {
                    if (i != j) {
                        List<Float> B = SequenceList.get(j);
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
                    List<List<Float>> lop = new ArrayList<>();
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

    public static boolean isWithinBounds(float value, float lowerBound, float upperBound) {
        return value >= lowerBound && value <= upperBound;
    }



    // 计算均值
    public static float calculateMean(List<Float> list) {
        float sum = 0;
        for (float num : list) {
            sum += num;
        }
        return sum / list.size();
    }

    // 计算百分位数
    public static float calculatePercentile(List<Float> sortedList, float percentile) {
        Collections.sort(sortedList);
        int index = (int) Math.ceil(percentile / 100.0 * sortedList.size()) - 1;
        return sortedList.get(index);
    }


    //计算相同保序模式下两个出现的DTW距离--首先要数据归一化
    public static float calculateDTWDistance(List<Float> A, List<Float> B) {
        int i, j;
        float max = 999;
        Float a[] = A.toArray(new Float[0]);
        Float b[] = B.toArray(new Float[0]);
        int NUM1 = a.length + 1;// 加1是因为计算是有a[i-1]
        int NUM2 = b.length + 1;// 加1是因为计算是有b[j-1]

        float[][] distance = new float[NUM1][NUM2];
        float[][] output = new float[NUM1][NUM2];

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

    public static float calculateAverage(List<Float> timeSeries) {
        // 计算样本平均值
        float sum = 0;
        for (float value : timeSeries) {
            sum += value;
        }
        float mean = sum / timeSeries.size();
        System.out.println("均值: " + mean);
        return mean;
    }


}