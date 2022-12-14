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

public class COPP_enum {
	
	public int tpk;
	public float density; // 密度约束
	public int fre_cop_num = 0; // 总的频繁对比保序模式数量
	public int frequent_num = 0;  //总的频繁保序模式数量
	public int fre_num = 0;
	public int cd_num = 2;//候选模式数量
	public int scan_num = 1;//扫描序列次数
	public int read_num = 0;//访问序列次数
	public int[] sequence_num = { 0, 0 };
	public List<List<Integer>> sequence_len = new ArrayList<>();
	
	List<List<seqdb>> sDB = new ArrayList<>();
	
	// TOPK pattern
	class sorted_queue implements Comparable<sorted_queue> {
		// 当前候选模式
		List<Integer> can	= new ArrayList<>();
		float CR;  // contrast rate
		int support; // 支持度
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
	
	PriorityQueue<sorted_queue> top_ps = new PriorityQueue<>();
	
	class LNode{
		int data;
		LNode next = null;
	}
	
	class ZIndex{
		List<Integer> index = new ArrayList<>(); 
		// 索引长度
		int len;
	}
	
	class ZZCan implements Comparable<ZZCan> {
		List<ZIndex> zin = new ArrayList<>();
		List<Integer> can	= new ArrayList<>();
		int support;
		float rsup;
		@Override
		public int compareTo(ZZCan zz) {
			if (this.support == zz.support) {
				return 0;
			} else if (this.support < zz.support) {
				return -1;
			} else {
				return 1;
			}
		}
	}
	
	static class seqdb {
		int id; // sequence id
		List<Float> S = new ArrayList<>();
		int seqlen;
		int support;
	} 
	
	List<seqdb> sDB0 = new ArrayList<>();
	
	List<sorted_queue> oop = new ArrayList<>(); // 用来存放本轮生成的保序模式，每轮比较完之后就会清空
	List<ZZCan> POS = new ArrayList<>(); //存放频繁的保序模式在正类中末位的数组用来存放正类中(1,2)、(2,1)模式的全部结果值（索引位置、支持度、对比率）
	List<ZZCan> NEG = new ArrayList<>(); //存放频繁的保序模式在负类中末位的数组用来存放负类中(1,2)、(2,1)模式的全部结果值（索引位置、支持度、对比率）
	List<List<Integer>> L = new ArrayList<>();//存放每次生成的频繁保序模式
	// 注意posPc negPc Lc是存放本次生成的模式，不管是否为频繁
	List<List<ZIndex>> posPc = new ArrayList<>(); // 正类长度为m的索引下标集合
	List<List<ZIndex>> negPc = new ArrayList<>(); // 负类长度为m的索引下标集合
	List<List<Integer>> Lc = new ArrayList<>(); // 长度为m的模式集合
	
	List<Integer> Cd	= new ArrayList<>(); //存放本次生成的候选模式
	List<Integer> Cd2 = new ArrayList<>();
	
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
	
	public int[] sort(List<Integer> src){
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
	
	
	public boolean grow_BaseP1(List<ZIndex> Ld, List<LNode> L, int lab, boolean oop){
		
		int zlen = 0;
		// 记录模式索引位置
		List<ZIndex> Z	= new ArrayList<>();
		for (int i = 0; i < Ld.size(); i++) {
			
			LNode p = L.get(i);
			List<Integer> q = Ld.get(i).index;
			int size = Ld.get(i).len;
			int m = 0;
			List<Integer> ztemp = new ArrayList<>();
			
			while(p.next != null && m < size){
				if (q.get(m) == p.next.data + 1) {
					read_num = read_num + 1; // 比较次数
					ztemp.add(q.get(m));
					p.next = p.next.next;
					m++;
				} else if(p.next.data < q.get(m)){
					p = p.next;
				}else {
					m++;
				}
			}
			// 为了记录在每个序列中的索引值以及匹配的支持度
			ZIndex zIndex = new ZIndex();
			zIndex.index = ztemp;
			zIndex.len = ztemp.size();
			zlen += ztemp.size();
			Z.add(zIndex);
			
			L.get(i).data = L.get(i).data - ztemp.size();
		}
		
        if (lab == 0) {
        	posPc.add(Z);
        		oop = jugde_oop(zlen,Cd,Z,lab);
		} else {
			negPc.add(Z);
			if (oop) {
				jugde_oop(zlen,Cd,Z,lab);
			}
		}

		return oop;
	}

	public boolean grow_BaseP2(int slen, List<ZIndex> Ld, List<LNode> L, int flag, int lab, boolean oop){
		List<ZIndex> Z	= new ArrayList<>(); //存放(1,...,2)模式本次生成的末位数组，不是真正的1,2关系，只是表示比较大小关系
		int zlen = 0;
		int lst, fri;
		for (int i = 0; i < Ld.size(); i++) {
			// p为前缀，q为后缀
			LNode p = L.get(i);
			List<Integer> q = Ld.get(i).index;
			int size = Ld.get(i).len;
			int m = 0;

			List<Integer> ztemp = new ArrayList<>();
			while (p.next != null && m < size) {
				if (q.get(m) == p.next.data + 1) {
					read_num = read_num + 1; // 比较次数
					lst = q.get(m);
					fri = lst - slen;
					
					seqdb seqTemp = sDB.get(lab).get(i);
					if (flag == 1) {
						if (seqTemp.S.get(lst) > seqTemp.S.get(fri)){
							ztemp.add(q.get(m));
							p.next = p.next.next;
						} 
					} else if (seqTemp.S.get(lst) < seqTemp.S.get(fri)) {
						ztemp.add(q.get(m));
						p.next = p.next.next;
					}
					m++;
					
				} else if (p.next.data < q.get(m)) {
					p = p.next;
				} else {
					m++;
				}
			}
			
			ZIndex zIndex = new ZIndex();
			zIndex.index = ztemp;
			zIndex.len = ztemp.size();
			// (1,2)总的出现次数
			zlen += ztemp.size();
			Z.add(zIndex);
		
			L.get(i).data = L.get(i).data - ztemp.size();
		}
		
        if (lab == 0) {
        	posPc.add(Z);
        	oop = jugde_oop(zlen,Cd,Z,lab);
		} else {
			negPc.add(Z);
			if (oop) {
				jugde_oop(zlen,Cd,Z,lab);
			}
		}
		
		return oop;
	}
	
	// 模式拼接
	public int enumerate(){
		
		// 长度为m的模式集合
		List<List<Integer>> Lcd = new ArrayList<>();
		List<List<ZIndex>> posPcd = new ArrayList<>();
		List<List<ZIndex>> negPcd = new ArrayList<>();
		
		// 频繁保序模式
		List<List<Integer>> Ld = new ArrayList<>();
		List<List<ZIndex>> posPd = new ArrayList<>();
		List<List<ZIndex>> negPd = new ArrayList<>();
		
		for (List<Integer> Ltemp : Lc) {
			List<Integer> fretemp = new ArrayList<>();
			for (Integer integer : Ltemp) {
				fretemp.add(integer);
			}
			Lcd.add(fretemp);
		}
		
		Lc.clear();
		
		for (List<ZIndex> ztemp : posPc) {
			posPcd.add(ztemp);
		}
		
		posPc.clear();
		
		for (List<ZIndex> ztemp : negPc) {
			negPcd.add(ztemp);
		}
		
		negPc.clear();
		
		for (List<Integer> Ltemp : L) {
			List<Integer> fretemp = new ArrayList<>();
			for (Integer integer : Ltemp) {
				fretemp.add(integer);
			}
			Ld.add(fretemp);
		}
		
		L.clear();
		
		for (ZZCan Ptemp : POS) {
			List<ZIndex> postemp = new ArrayList<>();
			for (ZIndex zin : Ptemp.zin) {
				postemp.add(zin);
			}
			posPd.add(postemp);
		}
		
		POS.clear();
		
		for (ZZCan Ntemp : NEG) {
			List<ZIndex> negtemp = new ArrayList<>();
			for (ZIndex zin : Ntemp.zin) {
				negtemp.add(zin);
			}
			negPd.add(negtemp);
		}
		
		NEG.clear();
		
		int i = 0;
		int j = 0;
		int f = 0;
		int k = 0;
		int temp;
		int slen = Ld.get(0).size();//模式长度
		
		while (Cd.size() < slen + 1) {
			Cd.add(0);
		}
		
		int size = Lcd.size();
		List<Integer> Q = new ArrayList<>();
		int[] q = new int[256];
		int[] r = new int[256];
		
		fre_num = 0;
		
		while(i < Ld.size()){
			
			List<ZIndex> pIndexs = posPd.get(i);
    		// 正类索引链
        	List<LNode> pos = new ArrayList<>();
    		for (int m = 0; m < pIndexs.size(); m++) {
    			ZIndex pIndex = pIndexs.get(m);
	        	LNode pb;
	        	LNode qb = new LNode();
	        	LNode ptem = new LNode();
	        	int plen = pIndex.len;
	        	ptem.data = plen;
	        	pos.add(m, ptem);
	        	qb = pos.get(m);
	        	for (int d = 0; d < plen; d++) {
	        		pb = new LNode();
	        		pb.data = pIndex.index.get(d);
	        		qb.next = pb;
	        		qb = pb;
				}
	        	qb.next = null;
    		}
    		
    		List<ZIndex> nIndexs = negPd.get(i);
    		// 负类索引链
        	List<LNode> neg = new ArrayList<>();
    		for (int m = 0; m < nIndexs.size(); m++) {
    			ZIndex nIndex = nIndexs.get(m);
	        	LNode pb;
	        	LNode qb = new LNode();
	        	LNode ntem = new LNode();
	        	int nlen = nIndex.len;
	        	ntem.data = nlen;
	        	neg.add(m, ntem);
	        	qb = neg.get(m);
	        	for (int d = 0; d < nlen; d++) {
	        		pb = new LNode();
	        		pb.data = nIndex.index.get(d);
	        		qb.next = pb;
	        		qb = pb;
				}
	        	qb.next = null;
    		}
			
			for (temp = 1; temp <= slen + 1; temp++) {
				//生成超模式
				for (j = 0; j < slen; j++) {
					if (Ld.get(i).get(j) < temp) {
						Cd.set(j, Ld.get(i).get(j));
					} else {
						Cd.set(j, Ld.get(i).get(j) + 1);
					}
				}
				Cd.set(slen, temp);
				List<Integer> Cdtemp = new ArrayList<>();
				for (Integer integer : Cd) {
					Cdtemp.add(integer);
				}
				Lc.add(Cdtemp);
				cd_num = cd_num + 1;
				
				// 求后缀
	        	Q = Cd.subList(1, Cd.size());
	        	q = sort(Q);
	        	for (k = 0; k < size; k++) {
					r = sort(Lcd.get(k));
					boolean oop = false;
					//相对顺序相同
					if (Arrays.equals(q, r)) {
						// 一样
						if (Ld.get(i).get(0) != Lcd.get(k).get(slen - 1)) {
							oop = grow_BaseP1(posPcd.get(k), pos, 0, oop);
							grow_BaseP1(negPcd.get(k), neg, 1, oop);
							if (oop) {
								jugde_csp();
							} 
						} else {
							if (Cd.get(0) < Cd.get(slen)) {
								oop = grow_BaseP2(slen, posPcd.get(k), pos, 1, 0, oop);
								grow_BaseP2(slen, negPcd.get(k), neg, 1, 1, oop);
								if (oop) {
									jugde_csp();
								}
							} else {
								oop = grow_BaseP2(slen, posPcd.get(k), pos, 2, 0, oop);
								grow_BaseP2(slen, negPcd.get(k), neg, 2, 1, oop);
								if (oop) {
									jugde_csp();
								}
							}
							
						}
						
					}
				}
			}
			i++;
		}

    	return 0;
        
	}
	
	public float cal_rate(List<Integer> Cd, List<ZIndex> z3,int lab) {
		float rsup = 0;
    	float sup_number = 0;
    	List<Integer> lentemp = sequence_len.get(lab);
    	for (int sid = 0; sid < lentemp.size(); sid++) {
    		float den = 0;
    		float current_len = lentemp.get(sid);
    		float support = z3.get(sid).len;
    		if (current_len > 0 && support > 0) {
				den = support / current_len;
				// 3、计算密度值，判断是否满足密度约束
				if (den > density) {
					sup_number++;
				}
			}
    	}
    	// 4、计算支持率
    	rsup = sup_number / sequence_num[lab];
		
        return rsup;
	}

	public int[] calculate(int lab, int[] opnum) {
		boolean oop = false;
		boolean oop2 = false;
		int zlen = 0;
		int z2len = 0;
		
		List<ZIndex> Z	= new ArrayList<>(); //存放(1,2)模式本次生成的末位数组
		List<ZIndex> Z2 = new ArrayList<>(); // 存放(2,1)模式本次生成的末位数组
		
        for (int sid = 0; sid < sequence_num[lab]; sid++) {
        	int i = 0, j = 1;
        	
        	List<Integer> ztemp = new ArrayList<>();
        	List<Integer> z2temp = new ArrayList<>();
        	List<Float> sTemp = sDB.get(lab).get(sid).S;
        	while (j < sTemp.size()){
        		read_num = read_num + 1; // 比较次数
    			if (sTemp.get(j) > sTemp.get(i)) {
    				ztemp.add(j);
    			} else if (sTemp.get(j) < sTemp.get(i)){
    				z2temp.add(j);
    			}
    			i++;
    			j++;
    		}

			ZIndex zIndex = new ZIndex();
			zIndex.index = ztemp;
			zIndex.len = ztemp.size();
			zlen += ztemp.size();
			Z.add(zIndex);
			
			ZIndex z2Index = new ZIndex();
			z2Index.index = z2temp;
			z2Index.len = z2temp.size();
			z2len += z2temp.size();
			Z2.add(z2Index);
        	
        }
        
        if (lab == 0) {
        	posPc.add(Z);
        	posPc.add(Z2);
        	opnum[0] = 0;
        	opnum[1] = 0;
    		oop = jugde_oop(zlen,Cd,Z,lab);
    		if (oop) {
    			opnum[0]++;
			}
            oop2 = jugde_oop(z2len,Cd2,Z2,lab);
            if (oop2) {
            	opnum[1]++;
			}
		} else {
			negPc.add(Z);
			negPc.add(Z2);
			if (opnum[0] > 0) {
				jugde_oop(zlen,Cd,Z,lab);
			}
			if (opnum[1] > 0) {
				jugde_oop(z2len,Cd2,Z2,lab);
			}
		}
        
        return opnum;

 	}
	
	public boolean jugde_oop(int zlen, List<Integer> cd, List<ZIndex> z, int lab) {
		boolean gen_op = false;
		float rsup = 0;
		if (zlen > 0 && z.size() > 0) {
			rsup = cal_rate(cd, z, lab);
		}
    	
		List<Integer> Cdtemp = new ArrayList<>();
		for (Integer integer : cd) {
			Cdtemp.add(integer);
		}
		
    	ZZCan zc = new ZZCan();
		zc.can = Cdtemp;
		zc.zin = z;
		zc.rsup = rsup;
		zc.support = zlen;
    	
    	if (lab == 0 && rsup > 0) {
    		
    		sorted_queue tmp_pat = new sorted_queue();
			int count = top_ps.size();
			if (count > 0) {
				tmp_pat = top_ps.peek();
			} else {
				tmp_pat.CR = 0;
				tmp_pat.can = new ArrayList<>();
				tmp_pat.pos_sup = 0;
			}
			
			if ((count < tpk) || (count == tpk && rsup >= tmp_pat.CR)) {
			
	    		gen_op = true;
	    		// 正类索引位置
	    		POS.add(zc);
	    		sorted_queue queue = new sorted_queue();
	    		queue.can = Cdtemp;
	    		queue.pos_sup = rsup;
	    		// 记录本轮生成的保序模式
	    		oop.add(queue);
	    		
				L.add(Cdtemp);
				
				frequent_num++;
				fre_num++;
			}
		} 
    	
    	if (lab == 1) {
    		NEG.add(zc);
    		for (sorted_queue qu : oop) {
				if (Cdtemp.toString().equals(qu.can.toString())) {
					qu.neg_sup = rsup;
				}
			}
		}
    	
    	return gen_op;
	}
	
	public void jugde_csp(){
		sorted_queue tmp_pat = new sorted_queue();
		float pos_sup,neg_sup;
		for(int i=0; i < oop.size(); i++){
			// 正类支持率
			pos_sup = oop.get(i).pos_sup; 
			
			int count = top_ps.size();
			if (count > 0) {
				tmp_pat = top_ps.peek();
			} else {
				tmp_pat.CR = 0;
				tmp_pat.can = new ArrayList<>();
				tmp_pat.pos_sup = 0;
			}
			
			neg_sup = oop.get(i).neg_sup;
			
			// 对比率 = a - b
			float CR = pos_sup - neg_sup;
			if (CR > 0) {
				fre_cop_num++;
				// 当前模式按照CR值进行存储 
				sorted_queue current_pat = new sorted_queue();
				current_pat.CR = CR;
				List<Integer> Cdtemp = new ArrayList<>();
				for (Integer integer : oop.get(i).can) {
					Cdtemp.add(integer);
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
		oop.clear();
	}

	public void find(){

		int[] opnum = {0,0};
		Cd.add(1);
		Cd.add(2);
		Cd2.add(2);
		Cd2.add(1);
		List<Integer> Cdtemp = new ArrayList<>();
		for (Integer integer : Cd) {
			Cdtemp.add(integer);
		}
		
		List<Integer> Cdtemp2 = new ArrayList<>();
		for (Integer integer : Cd2) {
			Cdtemp2.add(integer);
		}
		
		Lc.add(Cdtemp);
		Lc.add(Cdtemp2);
		
		opnum = calculate(0,opnum);
		int sum = 0;
		for (int num : opnum) {
			sum += num;
		}
		if (sum > 0) {
			calculate(1,opnum);
		}
		
		jugde_csp();
		Cd.clear();
		Cd2.clear();
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
                if (buffer.isEmpty() == true
                        || buffer.charAt(0) == '#' || buffer.charAt(0) == '%'
                        || buffer.charAt(0) == '@') {
                    continue;
                }
				String[] valueStr = buffer.trim().split(",");
//                String[] valueStr = buffer.trim().split("	");
//                String[] valueStr = buffer.trim().split("  ");
                
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
				
				seqdb seq = new seqdb();
				seq.S = sTemp;
				sDB0.add(seq);
				
				sDB0.get(sDBLen).seqlen = sTemp.size();
				sDBLen++;
			}
			br.close();
			
			List<Integer> pos_len = new ArrayList<>();
			
			List<Integer> neg_len =  new ArrayList<>();
			
			// 正类数据
			List<seqdb> pos = new ArrayList<>();
			// 负类数据
			List<seqdb> neg = new ArrayList<>();
			
			for (int i = 0; i < sDBLen; i++) {
				// 数据集中第一个元素为标签元素，通过1或2，0或1，-1和1来区分
				float first = firstList.get(i);
//				float first = sDB0.get(i).S.get(0);
				List<Float> stemp = new ArrayList<>();
				int len = sDB0.get(i).seqlen;
				
				if (first == 2) {
//				if (first == 1.0000000e+00 || first == 3.0000000e+00) {
					for (int j = 0; j < len; j++) {
						stemp.add(sDB0.get(i).S.get(j));
					}
					seqdb negTemp = new seqdb();
					negTemp.S = stemp;
					negTemp.seqlen = stemp.size();
					neg.add(negTemp);
					
					neg_len.add(stemp.size());
					sequence_num[1]++;
				} else {
					for (int j = 0; j < len; j++) {
						stemp.add(sDB0.get(i).S.get(j));
					}
					seqdb posTemp = new seqdb();
					posTemp.S = stemp;
					posTemp.seqlen = stemp.size();
					pos.add(posTemp);
					
					pos_len.add(stemp.size());
					sequence_num[0]++;
				}
			}
			sDB.add(0, pos);
			sDB.add(1, neg);
			sequence_len.add(0, pos_len);
			sequence_len.add(1, neg_len);
			System.out.println("positive sequence number: " + sequence_num[0]); // output the sequence number of sDB1
			System.out.println("neggative sequence number: " + sequence_num[1]); // output the sequence number of sDB2
        } catch (IOException e) {
            System.out.println("Error in closing the BufferedReader");
        }

	}
	
	public void read_file_reverse(){
		List<seqdb> posList = sDB.get(0);
		List<seqdb> negList = sDB.get(1);
		
		sDB.add(0, negList);
		sDB.add(1, posList);
		
		List<Integer> poslen = sequence_len.get(0);
		List<Integer> neglen = sequence_len.get(1);
		
		sequence_len.add(0, neglen);
		sequence_len.add(1, poslen);
		
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
	
	public void runAlgorithm(String filePath, float density2, int tpk2){
		
		density = density2;
		tpk = tpk2;
		long begintime = System.currentTimeMillis();
		read_file(filePath);
		
        find();
		while(fre_num > 0){
			enumerate();
		}
		
		int pos_fre_cop_num = fre_cop_num;
		int pos_frequent_num = frequent_num;
		int pos_cd_num = cd_num;
		
		fre_cop_num = 0; // 总的频繁对比保序模式数量
		frequent_num = 0;  //总的频繁保序模式数量
		fre_num = 0;
		cd_num = 2;//候选模式数量
		oop = new ArrayList<>(); // 用来存放本轮生成的保序模式，每轮比较完之后就会清空
		POS = new ArrayList<>(); //存放正类中末位的数组用来存放正类中(1,2)、(2,1)模式的全部结果值（索引位置、支持度、对比率）
		NEG = new ArrayList<>(); //存放负类中末位的数组用来存放负类中(1,2)、(2,1)模式的全部结果值（索引位置、支持度、对比率）
		L = new ArrayList<>();//存放每次生成的频繁模式
		
		Cd	= new ArrayList<>(); //存放本次生成的候选模式
		Cd2 = new ArrayList<>();
		
		read_file_reverse();
		
		find();
		while(fre_num > 0){
			enumerate();
		}
		System.out.println();
		disp();
		
		long endtime = System.currentTimeMillis();
		MemoryLogger.getInstance().checkMemory();
		/** memory of last execution */
		double maxMemory = MemoryLogger.getInstance().getMaxMemory();
		MemoryLogger.getInstance().reset();
		System.out.println("Maximum memory usage : " + maxMemory + " mb.");
		System.out.println("The time-consuming: "+(endtime - begintime)+"ms.");
		System.out.println("The number of frequent cop patterns: "+(pos_fre_cop_num+fre_cop_num));
		System.out.println("The number of frequent op patterns: "+(pos_frequent_num+frequent_num));
		System.out.println("The number of candidate patterns: "+(pos_cd_num+cd_num));
	}
	
}









