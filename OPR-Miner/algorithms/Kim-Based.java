package com.algo.test;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;
import java.net.URL;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Scanner;

public class OrderPreservingMining {
	
	public static List<Integer> μ = new ArrayList<>();
	public static List<Integer> π = new ArrayList<>();
	public static List<Float> S = new ArrayList<>(); // sequence 
	
	final static int TXT_SIZE = 50000;
    final static int PATTERN_SIZE = 10000;
    final static int MAX_LINE = 60000;
    final static int MAXSIZE = 50000;
    final static int Max = 256;
    static int MAX = 50000;
    static int count;
    static int candidate_num = 0;
    static int compnum = 2;
    public static int minsup;
    public static int [][] F2=new int[900][900]; // 2-长度频繁模式集
    static int [][] F=new int[900][900]; // 频繁模式集
    static int [][] C=new int[20000][20000]; // 候选模式集
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
    static float[] sDB = new float[60000];
    static int seqlen;
	
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
	     * @param x 支点
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
	     * @param x 当前节点
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
	     * @param z 待删除节点
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
//				i = i - π.get(q-1);
				i = i - k + 1;
				q = 0;
				k = 0;
				tree = new OrderStatisticTree();
			}
			
		}
		
		return support;
		
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
            support_full = KMPOrderMatcher(sDB, pattern, seqlen, 2);
            /*System.out.println("候选计算模式：");
            System.out.print("(");
            for(int x=0;x<2;x++){
                System.out.print(C2[j][x]);
                if(x<1)System.out.print(",");
            }
            System.out.print(")");
            System.out.println("#support:"+support_full);*/
            if(support_full>=minsup){
                count++;
                frequent_num++;
//                System.out.println("保序模式：");
                System.out.print("(");
                for(int x=0;x<2;x++){
                    F2[j][x]=C2[j][x];
                    System.out.print(F2[j][x]);
                    if(x<1)System.out.print(",");
                }
                System.out.print(")");
                System.out.println("#support:"+support_full);
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
                support_full = KMPOrderMatcher(sDB, pattern, seqlen, len);
                /*System.out.println("候选模式：");
                System.out.print("(");
                for(int t=0;t<len;t++){
                    System.out.print(C[v][t]);
                    if(t<len-1)System.out.print(",");
                }
                System.out.print(")");
                System.out.println("#support:"+support_full);*/
                if(support_full>=minsup) {
                    count++;
//                    System.out.println("保序模式：");
                    System.out.print("(");
                    for(int t=0;t<len;t++){
                        F[frequent_num][t]=C[v][t];
                        System.out.print(F[frequent_num][t]);
                        if(t<len-1)System.out.print(",");
                    }
                    System.out.print(")");
                    frequent_num++;
                    System.out.println("#support:"+support_full);
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
        int n=0;
        BufferedReader br = null;
        try {
            br = new BufferedReader(new FileReader(filePath));
            String contentLine;
            List<String> arr1 = new ArrayList<>();

            while ((contentLine = br.readLine()) != null)
            {
            	if (!contentLine.equals("NA")) {
            		arr1.add(contentLine);
				}
            }
            for(int k=0;k<arr1.size();k++){
                sDB[k]=Float.parseFloat(arr1.get(k));
                n++;
            }
            seqlen=n;
        } catch (IOException e) {
            System.out.println("Error in closing the BufferedReader");
        }
    }
	
	public static String fileToPath(String filename) throws UnsupportedEncodingException {
        URL url = OrderPreservingMining.class.getResource(filename);
        return java.net.URLDecoder.decode(url.getPath(),"UTF-8");
    }
	
	
	public static void main(String[] args) throws IOException {
		// TODO Auto-generated method stub
//		int[] series = {11,15,33,21,24,50,29,36,73,85,63,69,79,88,44,62};
//		int[] series = {11,15,33,21,24,50,29,36,73,85,63,69,79,33,42,73,57,63,87,95,79,88,44,62};
//		int[] pattern = {33,42,73,57,63,87,95,79};
		
//		System.out.println("please enter a minimum support threshold minsup: ");
//		minsup = new Scanner(System.in).nextInt();
		minsup = 14;
		long dwBeginTime = System.currentTimeMillis();
		String filePath = fileToPath("SDB8.txt");
		read_file(filePath);
        generate_candF2(pattern);
        generate_fre(F2);
        Cancalute(pattern);
        long dwEndTime = System.currentTimeMillis();
        System.out.println("Time cost:" + (dwEndTime - dwBeginTime));
        System.out.println("Frequent num:"+count);
		System.out.println("Candidate num:"+compnum);
		System.out.println();
		
	}

}
