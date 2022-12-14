package com.algo.copp.end;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Formatter;
import java.util.List;
import java.util.PriorityQueue;


/**
 * 启动程序前需要根据数据集的大小去修改一些值
 * final K、seqdb中的S
 * @author Admin
 *
 */
public class KMP_Based_COPP {
	
	public static List<Integer> μ = new ArrayList<>();
	public static List<Integer> π = new ArrayList<>();
	public static List<Float> S = new ArrayList<>(); // sequence 

	final int N = 600; // The length of sequence
	final int M = 30; // The length of pattern
	// 大数据集
//	final int K = 7000; // The sequence number of sequence database
	// 小数据集
	int K = 1000; // The sequence number of sequence database
	
	public int minsup = 0;
	public int tpk;
	public float density; // 密度约束
	public int fre_cop_num = 0; // 总的频繁对比保序模式数量
	int fre_num;
	int candidate_num = 0;
	int cd_num = 2;
	public int[][] F2 = new int[2][2]; // 2-长度频繁模式集

	public int[][] L2 = new int[2][2]; // 2-长度频繁模式集

	int frequent_num = 0;
	
	// 统计正负类序列个数
	int[] sequence_num = { 0, 0 };
	
	// TOPK pattern
	class sorted_queue implements Comparable<sorted_queue> {
		// 当前候选模式
		List<Integer> can	= new ArrayList<>();
		float CR;  // contrast rate
		float pos_sup;
		float neg_sup;

		@Override
		public int compareTo(sorted_queue s) {
			if (this.CR == s.CR) {
				return 0;
			} else if (this.CR < s.CR) {
				return -1;
			} else {
				return 1;
			}
		}
	}
	
	// 定义优先队列（按照CR的大小排序）
	PriorityQueue<sorted_queue> top_ps = new PriorityQueue<>();

	class seqdb {
		int id; // sequence id
		// 当前序列
		// 大数据集
//		float[] S = new float[15000];
		//中数据集
//		float[] S = new float[3000];
		//小数据集
		float[] S = new float[1000];
		// 当前序列长度
		int seqlen;
		// 模式在该序列中的 支持度
		int support;
	}

	seqdb[] sDB0 = new seqdb[K];

	{
		for (int i = 0; i < K; i++) {
			sDB0[i] = new seqdb();
		}
	}
	seqdb[][] sDB = new seqdb[2][K];
	{
		for (int i = 0; i < 2; i++) {
			for (int j = 0; j < K; j++) {
				sDB[i][j] = new seqdb();
			}
		}
	}
	
	public static class OrderStatisticTree {
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
		μ = computePrefixRep(pattern,m);
		π = computeFailureFunction(pattern,m);
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
	

	public float[] jugde_oop(int[] pattern2, int len, int lab) {
		List<Integer> pat = new ArrayList<>();
		for (int i = 0; i < pattern2.length; i++) {
			if (pattern2[i] == 0) {
				break;
			}
			pat.add(pattern2[i]);
		}
		float[] temp = new float[2];
		float rate = 0;
		float sup_number = 0;
		int support_sid = 0;
		int support_full = 0;
		// 1、采用模式匹配的方式计算支持度
		for (int sid = 0; sid < sequence_num[lab]; sid++) {

			int current_len = sDB[lab][sid].seqlen;
			// 模式p在某一个序列s中的支持度
			support_sid = KMPOrderMatcher(sDB[lab][sid].S, pattern2, current_len, len);

			sDB[lab][sid].support = support_sid;
			// 模式p在某一个序列数据库D中的支持度
			support_full += support_sid;
		}
		// 2、判断是否为频繁保序模式
		if (lab == 0 && support_full >= minsup) {
//			System.out.print("频繁保序模式："+pat.toString());
//			System.out.print("，支持度为："+support_full);
//			System.out.println();

			for (int sid = 0; sid < sequence_num[lab]; sid++) {
				float den = 0;
				float current_len = sDB[lab][sid].seqlen;
				float sup = sDB[lab][sid].support;
				if (current_len > 0) {
					den = sup / current_len;
					if (den > density) {
						sup_number++;
					}
				}
			}
			rate = sup_number / sequence_num[lab];
			temp[0] = support_full;
			temp[1] = rate;
		} 
		
		if (lab == 1) {
			for (int sid = 0; sid < sequence_num[lab]; sid++) {
				float den = 0;
				float current_len = sDB[lab][sid].seqlen;
				float sup = sDB[lab][sid].support;
				if (current_len > 0) {
					den = sup / current_len;
					if (den > density) {
						sup_number++;
					}
				}
			}
			rate = sup_number / sequence_num[lab];
			temp[0] = support_full;
			temp[1] = rate;
		}
		
		return temp;
	}

	public int generate_candF2() {
		int[] pattern = new int[2];
		float[] temp = new float[2];
		float pos_sup, neg_sup;
		float pos_rate, neg_rate, CR;
		int support_full = 0;
		int[][] C2 = { { 1, 2 }, { 2, 1 } };
		for (int j = 0; j < 2; j++) {
			support_full = 0;
			for (int h = 0; h < 2; h++) {
				pattern[h] = C2[j][h];
			}

			temp = jugde_oop(pattern, 2, 0);
			pos_sup = temp[0];
			pos_rate = temp[1];

			if (pos_rate > 0) {
				
				sorted_queue tmp_pat1 = new sorted_queue();
				int count1 = top_ps.size();
				if (count1 > 0) {
					tmp_pat1 = top_ps.peek();
				} else {
					tmp_pat1.CR = 0;
					tmp_pat1.can = new ArrayList<>();
					tmp_pat1.pos_sup = 0;
				}
				
				if ((count1 < tpk) || (count1 == tpk && pos_rate >= tmp_pat1.CR)) {
					for (int x = 0; x < 2; x++) {
						F2[j][x] = C2[j][x];
					}
					fre_num++;
					frequent_num++;
	
					temp = jugde_oop(pattern, 2, 1);
					neg_sup = temp[0];
					neg_rate = temp[1];
					
					CR = pos_rate - neg_rate;
					
					if (CR > 0) {
						fre_cop_num++;
						sorted_queue tmp_pat = new sorted_queue();
						int count = top_ps.size();
						if (count > 0) {
							tmp_pat = top_ps.peek();
						} else {
							tmp_pat.CR = 0;
							tmp_pat.can = new ArrayList<>();
							tmp_pat.pos_sup = 0;
						}
						
						for (int x = 0; x < 2; x++) {
							L2[j][x] = C2[j][x];
						}
						
						sorted_queue current_pat = new sorted_queue();
						current_pat.CR = CR;
						List<Integer> Cdtemp = new ArrayList<>();
						for (int i = 0; i < L2[j].length; i++) {
							if (L2[j][i] == 0)  break;
							Cdtemp.add(L2[j][i]);
						}
						
						if ((current_pat.CR > tmp_pat.CR) || (top_ps.size() < tpk)) {
							current_pat.can = Cdtemp;
							current_pat.CR = CR;
							current_pat.pos_sup = pos_sup;
							top_ps.offer(current_pat); 
							//保持top-k个元素
							if (top_ps.size() > tpk) {
								top_ps.poll();
							}
						}
					}
				}

			}

			for (int f = 0; f < 2; f++) {
				pattern[f] = 0;
			}

		}
		return 0;
	}
	
	int[] relative_order(int pat[]) {
		int k, slen;
		int level = 1;
		slen = pat.length;
		int[] sort_array = new int[slen];
		for (int i = 0; i < slen; i++) {
			k = pat[i];
			for (int x = 0; x < slen; x++) {
				if (k > pat[x]) {
					level++;
				}
			}
			sort_array[i] = level;
			level = 1;
		}
		return sort_array;
	}

	public int[][] generate_fre(int fre[][]) {
		if (frequent_num == 0) {
			return null;
		}
		int slen = 0;
		slen = fre[0].length;
		int[][] C = new int[2000][slen+1];
		int Q[] = new int[slen - 1];
		int R[] = new int[slen - 1];
		for (int i = 0; i < frequent_num; i++) {
			try {
				// 求后缀
				System.arraycopy(fre[i], 1, Q, 0, slen - 1);
			} catch (ArrayIndexOutOfBoundsException e) {
				System.out.println(e);
			}
			for (int j = 0; j < frequent_num; j++) {
				try {
					// 求前缀
					System.arraycopy(fre[j], 0, R, 0, slen - 1);
				} catch (ArrayIndexOutOfBoundsException e) {
					System.out.println(e);
				}
				
				if (Arrays.equals(relative_order(Q), relative_order(R))) {
					if (fre[i][0] == fre[j][slen - 1]) {
						C[candidate_num][0] = fre[i][0];
						C[candidate_num + 1][0] = fre[i][0] + 1;
						C[candidate_num][slen] = fre[i][0] + 1;
						C[candidate_num + 1][slen] = fre[i][0];
						for (int t = 1; t < slen; t++) {
							if (fre[i][t] > fre[j][slen - 1]) {
								// 中间位置增长
								C[candidate_num][t] = fre[i][t] + 1;
								C[candidate_num + 1][t] = fre[i][t] + 1;
							} else {
								C[candidate_num][t] = fre[i][t];
								C[candidate_num + 1][t] = fre[i][t];
							}
						}
						candidate_num += 2;
						cd_num += 2;
					} else if (fre[i][0] < fre[j][slen - 1]) // 第一个位置比最后一个位置小
					{

						C[candidate_num][0] = fre[i][0]; // 小的不变
						C[candidate_num][slen] = fre[j][slen - 1] + 1; // 大的加一
						for (int t = 1; t < slen; t++) {
							if (fre[i][t] > fre[j][slen - 1]) {
								C[candidate_num][t] = fre[i][t] + 1;

							} else {
								C[candidate_num][t] = fre[i][t];
							}
						}
						candidate_num += 1;
						cd_num += 1;
					} else {
						C[candidate_num][0] = fre[i][0] + 1; // 大的加一
						C[candidate_num][slen] = fre[j][slen - 1]; // 小的不变
						for (int t = 0; t < slen - 1; t++) {
							if (fre[j][t] > fre[i][0]) {
								C[candidate_num][t + 1] = fre[j][t] + 1; // 中间位置增长
							} else {
								C[candidate_num][t + 1] = fre[j][t];
							}
						}
						candidate_num += 1;
						cd_num += 1;
					}
				} else {
					;
				}
			}
		}
		
		int[][] ctemp = new int[candidate_num][slen+1];
		for (int k = 0; k < candidate_num; k++) {
			for (int k2 = 0; k2 < slen+1; k2++) {
				ctemp[k][k2] = C[k][k2];
			}
		}
		return ctemp;
	}

	public void Cancalute(int[][] C) {
		int[] pat = new int[2];
		float[] temp = new float[2];
		float pos_sup, neg_sup;
		float pos_rate, neg_rate,CR;
		int support_full = 0;
		int r = 0, len = 0;
		frequent_num = 0;
		while (candidate_num != 0) {
			while (r < C[0].length) {
				if (C[0][r] != 0){
					len++;
				} else {
					break;
				}
				r++;
			}
			pat= new int[len];
			int[][] F = new int[500][len]; // 频繁模式集
			int[][] L = new int[500][len]; // 频繁模式集
			
			for (int v = 0; v < candidate_num; v++) {

				support_full = 0;
				for (int h = 0; h < len; h++) {
					pat[h] = C[v][h];
				}

				// 计算正类支持率
				temp = jugde_oop(pat, len, 0);
				pos_sup = temp[0];
				pos_rate = temp[1];
				
				if (pos_rate > 0) {
					
					sorted_queue tmp_pat1 = new sorted_queue();
					int count1 = top_ps.size();
					if (count1 > 0) {
						tmp_pat1 = top_ps.peek();
					} else {
						tmp_pat1.CR = 0;
						tmp_pat1.can = new ArrayList<>();
						tmp_pat1.pos_sup = 0;
					}
					
					if ((count1 < tpk) || (count1 == tpk && pos_rate >= tmp_pat1.CR)) {
						for (int t = 0; t < len; t++) {
							F[frequent_num][t] = C[v][t];
						}
						// 计算负类支持率
						temp = jugde_oop(pat, len, 1);
						neg_sup = temp[0];
						neg_rate = temp[1];
						
						CR = pos_rate - neg_rate;

						if (CR > 0) {
							fre_cop_num++;
							sorted_queue tmp_pat = new sorted_queue();
							int count = top_ps.size();
							if (count > 0) {
								tmp_pat = top_ps.peek();
							} else {
								tmp_pat.CR = 0;
								tmp_pat.can = new ArrayList<>();
								tmp_pat.pos_sup = 0;
							}
							
							for (int t = 0; t < len; t++) {
								L[frequent_num][t] = C[v][t];
							}
							
							// 当前模式按照CR值进行存储 
							sorted_queue current_pat = new sorted_queue();
							current_pat.CR = CR;
							List<Integer> Cdtemp = new ArrayList<>();
							for (int i = 0; i < L[frequent_num].length; i++) {
								if (L[frequent_num][i] == 0) break;
								Cdtemp.add(L[frequent_num][i]);
							}
							
							if ((current_pat.CR > tmp_pat.CR) || (top_ps.size() < tpk)) {
								current_pat.can = Cdtemp;
								current_pat.CR = CR;
								current_pat.pos_sup = pos_sup;
								top_ps.offer(current_pat); 
								//保持top-k个元素
								if (top_ps.size() > tpk) {
									top_ps.poll();
								}
							}
						}
						fre_num++;
						frequent_num++;
					}
					
				}

				for (int f = 0; f < len; f++) {
					pat[f] = 0;
				}

			}
			
			int[][] Ftemp = new int[frequent_num][len];
			for (int i = 0; i < frequent_num; i++) {
				for (int j = 0; j < len; j++) {
					Ftemp[i][j] = F[i][j];
				}
			}
			
			r = 0;
			len = 0;
			candidate_num = 0;
			
			// 模式融合
			C = generate_fre(Ftemp);
			frequent_num = 0;
		}
	}

	public void read_file(String filePath){
		File file = new File(filePath);

		try {

			BufferedReader br = new BufferedReader(new FileReader(file));
			String buffer = "";
			int sDBLen = 0;
			List<Float> firstList = new ArrayList<>();
			List<String> endList = new ArrayList<>();
			List<Float> endfList = new ArrayList<>();
			while ((buffer = br.readLine()) != null) {
				if (buffer.isEmpty() == true || buffer.charAt(0) == '#' || buffer.charAt(0) == '%'
						|| buffer.charAt(0) == '@') {
					continue;
				}

//				String[] valueStr = buffer.trim().split(",");
//				String[] valueStr = buffer.trim().split("	");
				String[] valueStr = buffer.trim().split("  ");
				
				List<Float> sTemp = new ArrayList<>();

				float[] inS = new float[valueStr.length-1];
				// first 标签位在第一个位置
				float first = Float.parseFloat(valueStr[0]);
				firstList.add(first);
				for (int j = 1; j < (valueStr.length); j++) {
					String ssString = valueStr[j];
					float aaa = Float.parseFloat(ssString);
					
					inS[j-1] = aaa;
				}
				
				// 数据提取极值点，压缩数据
				sTemp = extraction(inS);
				for (int t = 0; t < sTemp.size(); t++) {
					sDB0[sDBLen].S[t] = sTemp.get(t);
				}
				sDB0[sDBLen].seqlen = sTemp.size();
				sDBLen++;
			}
			br.close();
			
			List<Integer> pos_len = new ArrayList<>();
			
			List<Integer> neg_len =  new ArrayList<>();
			
			for (int i = 0; i < sDBLen; i++) {
				// 数据集中第一个元素为标签元素，通过1或2，0或1，-1和1来区分
				float first = firstList.get(i);
				List<Float> stemp = new ArrayList<>();
				int len = sDB0[i].seqlen;
				
				if (first == 3) {
//				if (first == 1.0000000e+00 || first == 3.0000000e+00) {
					for (int j = 0; j < len; j++) {
						stemp.add(sDB0[i].S[j]);
					}
					for (int k = 0; k < stemp.size(); k++) {
						sDB[1][sequence_num[1]].S[k] = stemp.get(k);
					}
					sDB[1][sequence_num[1]].seqlen = len;
					neg_len.add(len);
					sequence_num[1]++;
				} else {
					for (int j = 0; j < len; j++) {
						stemp.add(sDB0[i].S[j]);
					}
					for (int k = 0; k < stemp.size(); k++) {
						sDB[0][sequence_num[0]].S[k] = stemp.get(k);
					}
					sDB[0][sequence_num[0]].seqlen = len;
					pos_len.add(len);
					sequence_num[0]++;
				}
			}
			
			System.out.println("positive sequence number: " + sequence_num[0]); 
			System.out.println("neggative sequence number: " + sequence_num[1]); 
		} catch (IOException e) {
			System.out.println("Error in closing the BufferedReader");
		}
	}
	
	public void read_file_reverse(){
		
		seqdb[][] sDBRe = new seqdb[2][K];
		{
			for (int i = 0; i < 2; i++) {
				for (int j = 0; j < K; j++) {
					sDBRe[i][j] = new seqdb();
				}
			}
		}
		for (int j = 0; j < sequence_num[0]; j++) {
			sDBRe[0][j] = sDB[0][j];
		}
		
		for (int j = 0; j < sequence_num[1]; j++) {
			sDBRe[1][j] = sDB[1][j];
		}
		
		if (sequence_num[0] <= sequence_num[1]) {
			K = sequence_num[1];
		} else {
			K = sequence_num[0];
		}
		
		for (int i = 0; i < 2; i++) {
			for (int j = 0; j < K; j++) {
				sDB[i][j] = new seqdb();
			}
		}
		
		for (int j = 0; j < sequence_num[1]; j++) {
			sDB[0][j] = sDBRe[1][j];
		}
		
		for (int j = 0; j < sequence_num[0]; j++) {
			sDB[1][j] = sDBRe[0][j];
		}
		
		int posnum = sequence_num[0];
		int negnum = sequence_num[1];
		
		sequence_num[0] = negnum;
		sequence_num[1] = posnum;
		
	}
	
	private List<Float> extraction(float[] in) {
        List<Float> list = new ArrayList<>();
        list.add(in[0]);
        for (int i = 1; i < in.length - 1; i++){
            if ((in[i] >= in[i - 1] && in[i] > in[i + 1]) || (in[i] > in[i - 1] && in[i] >= in[i + 1])){
                list.add(in[i]);
            } else if ((in[i] <= in[i - 1] && in[i] < in[i + 1]) || (in[i] < in[i - 1] && in[i] <= in[i + 1])){
                list.add(in[i]);
            }
        }
        list.add(in[in.length - 1]);
        return list;
    }
	
	public void disp() {
		DecimalFormat decimalFormat=new DecimalFormat("0.000000");
		int i = 0;
		while (!top_ps.isEmpty()) {
			// 右对齐输出
			Formatter formatter = new Formatter();
			System.out.print(i + "\t" + formatter.format("%20S",top_ps.peek().can.toString()) +"\t\t"+decimalFormat.format( top_ps.peek().CR));
			System.out.println();
			i++;
			top_ps.poll();
		}
		System.out.println();

	}

	public void runAlgorithm(String filePath, float density2, int tpk2) {
		density = density2;
		tpk = tpk2;
		long begintime = System.currentTimeMillis();
		read_file(filePath);
		
		generate_candF2();
		int [][] C = generate_fre(F2);
		Cancalute(C);
		
		int pos_fre_cop_num = fre_cop_num;
		int pos_frequent_num = frequent_num;
		int pos_cd_num = cd_num;
		
		μ = new ArrayList<>();
		π = new ArrayList<>();
		S = new ArrayList<>(); // sequence 
		
		fre_cop_num = 0; // 总的频繁对比保序模式数量
		fre_num = 0;
		frequent_num = 0;
		candidate_num = 0;
		cd_num = 2;
		F2 = new int[2][2]; // 2-长度频繁模式集
		L2 = new int[2][2]; // 2-长度频繁模式集

		read_file_reverse();
		
		generate_candF2();
		int [][] CRe = generate_fre(F2);
		Cancalute(CRe);
		
		System.out.println();
		disp();
		
		long endtime = System.currentTimeMillis();
		MemoryLogger.getInstance().checkMemory();
		/** memory of last execution */
		double maxMemory = MemoryLogger.getInstance().getMaxMemory();
		MemoryLogger.getInstance().reset();
		System.out.println("Maximum memory usage : " + maxMemory + " mb.");
		System.out.println("The time-consuming: " + (endtime - begintime) + "ms.");
		System.out.println("The number of frequent cop patterns: "+(pos_fre_cop_num+fre_cop_num));
		System.out.println("The number of frequent op patterns: "+(pos_frequent_num+frequent_num));
		System.out.println("The number of candidate patterns: "+(pos_cd_num+cd_num));
	}

}
