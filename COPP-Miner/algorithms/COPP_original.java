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

public class COPP_original {
	public int tpk; //参数k
	public float density; // 密度约束，即参数minden
	
	public int fre_cop_num = 0; // 总的频繁对比保序模式数量
	public int frequent_num = 0;  //总的频繁保序模式数量
	public int fre_num = 0;
	public int cd_num = 2;//候选模式数量
	
	public int[] sequence_num = { 0, 0 };  // 统计正负类序列个数
	public List<List<Integer>> sequence_len = new ArrayList<>();
	List<List<seqdb>> sDB = new ArrayList<>();
	
	// TOPK pattern
	class sorted_queue implements Comparable<sorted_queue> {
		// 当前候选模式
		List<Integer> can	= new ArrayList<>();
		float CR;  // contrast rate
		float pos_sup; // 正类支持率
		float neg_sup; // 负类支持率

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
	
	class LNode{
		int data;
		LNode next = null;
	}
	
	class ZIndex{
		// 存放符合模式，末位的索引
		List<Integer> index = new ArrayList<>(); 
		// 索引长度
		int len;
	}
	
	class ZZCan{
		List<ZIndex> zin = new ArrayList<>();
		List<Integer> can	= new ArrayList<>();
		int support;
		float rsup;
	}
	
	static class seqdb {
		int id; // sequence id
		// 当前序列
		List<Float> S = new ArrayList<>();
		int seqlen;
		int support;
	} 
	
	List<sorted_queue> oop = new ArrayList<>(); // 用来存放本轮生成的候选模式，每轮比较完之后就会清空
	List<ZZCan> POS = new ArrayList<>(); //存放正类中末位的数组，用来存放正类中(1,2)、(2,1)模式的全部结果值（索引位置、支持度、对比率）
	List<ZZCan> NEG = new ArrayList<>(); //存放负类中末位的数组，用来存放负类中(1,2)、(2,1)模式的全部结果值（索引位置、支持度、对比率）
	List<List<Integer>> L = new ArrayList<>();//存放每次生成的频繁模式
	
	List<Integer> Cd	= new ArrayList<>(); //存放本次生成的候选模式
	List<Integer> Cd2 = new ArrayList<>();
	
	public void disp() {
		DecimalFormat decimalFormat=new DecimalFormat("0.000000");
		int i = 0;
		Formatter formatter2 = new Formatter();
		System.out.println("id" + "\t" + formatter2.format("%20s","contrast pattern") +"\t\t"+"contrast rate");
		
		while (!top_ps.isEmpty()) {
			Formatter formatter = new Formatter();
			// 右对齐输出
			System.out.println(i + "\t" + formatter.format("%20S",top_ps.peek().can.toString()) +"\t\t"+decimalFormat.format( top_ps.peek().CR));
			i++;
			top_ps.poll();
		}
		System.out.println();

	}
	
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
	
	public boolean grow_BaseP1(List<LNode> Ld, List<LNode> L, int lab){
		boolean oop = false;
		int zlen = 0;
		List<ZIndex> Z	= new ArrayList<>();
		for (int i = 0; i < Ld.size(); i++) {
			// p为前缀，q为后缀
			LNode p = L.get(i);
			LNode q = Ld.get(i);
			// 匹配索引位置集
			List<Integer> ztemp = new ArrayList<>();
			
			while(p.next != null && q.next != null){
				if (q.next.data == p.next.data + 1) {
					ztemp.add(q.next.data);
					p.next = p.next.next;
					q.next = q.next.next;
				} else if(p.next.data < q.next.data){
					p = p.next;
				} else {
					q = q.next;
				}
			}
			ZIndex zIndex = new ZIndex();
			zIndex.index = ztemp;
			zIndex.len = ztemp.size();
			zlen += ztemp.size();
			Z.add(zIndex);
			L.get(i).data = L.get(i).data - ztemp.size();
			Ld.get(i).data = Ld.get(i).data - ztemp.size();
		}
		
        if (lab == 0) {
        	oop = jugde_oop(zlen,Cd,Z,lab);
		} else {
			jugde_oop(zlen,Cd,Z,lab);
		}

		return oop;
	}

	public int[] grow_BaseP2(int slen, List<LNode> Ld, List<LNode> L, int lab, int[] opnum){
		boolean oop = false;
		boolean oop2 = false;
		List<ZIndex> Z	= new ArrayList<>(); 
		List<ZIndex> Z2 = new ArrayList<>(); 
		// 总支持度
		int zlen = 0;
		int z2len = 0;
		int lst, fri;
		for (int i = 0; i < Ld.size(); i++) {
			// p为前缀，q为后缀
			LNode p = L.get(i);
			LNode q = Ld.get(i);
			List<Integer> ztemp = new ArrayList<>();
	    	List<Integer> z2temp = new ArrayList<>();
			while (p.next != null && q.next != null) {
				if (q.next.data == p.next.data + 1) {
					lst = q.next.data;
					fri = lst - slen;
					seqdb seqTemp = sDB.get(lab).get(i);
					if (seqTemp.S.get(lst) > seqTemp.S.get(fri)){
						ztemp.add(q.next.data);
					} else if (seqTemp.S.get(lst) < seqTemp.S.get(fri)){
						z2temp.add(q.next.data);
					}
					p.next = p.next.next;
					q.next = q.next.next;
					
				} else if (p.next.data < q.next.data) {
					p = p.next;
				} else {
					q = q.next;
				}
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
			
			L.get(i).data = L.get(i).data - ztemp.size() - z2temp.size();
			Ld.get(i).data = Ld.get(i).data - ztemp.size() - z2temp.size();
		}
		
        if (lab == 0) {
        	opnum[0] = 0;
        	opnum[1] = 0;
    		oop = jugde_oop(zlen,Cd,Z,lab);
    		if (oop) {
    			opnum[0]++; // 说明Cd加入候选集，此时就需要去计算负类
			}
            oop2 = jugde_oop(z2len,Cd2,Z2,lab);
            if (oop2) {
            	opnum[1]++;  // 说明Cd2加入候选集，此时就需要去计算负类
			}
		} else {
			if (opnum[0] > 0) {
				jugde_oop(zlen,Cd,Z,lab);
			}
			if (opnum[1] > 0) {
				jugde_oop(z2len,Cd2,Z2,lab);
			}
		}
		
		return opnum;
	}
	
	public int generate_fre(){
		int slen = 0;
		
		List<Integer> Q = new ArrayList<>();
		List<Integer> R = new ArrayList<>();
		// 正类索引位置
		List<List<ZIndex>> posZin = new ArrayList<>();
		// 负类索引位置
		List<List<ZIndex>> negZin = new ArrayList<>();
		// 候选模式集
		List<List<Integer>> fre = new ArrayList<>();
		// 正类后缀索引链
		List<List<LNode>> Lps = new ArrayList<>();
		// 正类前缀索引链
		List<List<LNode>> Lpp = new ArrayList<>();
		// 负类后缀索引链
		List<List<LNode>> Lss = new ArrayList<>();
		// 负类前缀索引链
		List<List<LNode>> Lsp = new ArrayList<>();
		
		int[] q = new int[256];
		int[] r = new int[256];
		
		int j = 0;
		int fre_number = 0;
		int t = 0;
		int k = 0;
		//模式长度
		slen = L.get(0).size();
		// 候选模式集
		for (List<Integer> Ltemp : L) {
			List<Integer> fretemp = new ArrayList<>();
			for (Integer integer : Ltemp) {
				fretemp.add(integer);
			}
			fre.add(fretemp);
		}
		
		L.clear();
		
		fre_number = fre_num;
		fre_num = 0;
		
		for (ZZCan Ptemp : POS) {
			List<ZIndex> postemp = new ArrayList<>();
			for (ZIndex zin : Ptemp.zin) {
				postemp.add(zin);
			}
			posZin.add(postemp);
		}
		
		POS.clear();
		
		for (ZZCan Ntemp : NEG) {
			List<ZIndex> negtemp = new ArrayList<>();
			for (ZIndex zin : Ntemp.zin) {
				negtemp.add(zin);
			}
			negZin.add(negtemp);
		}
		
		NEG.clear();

        while (Cd.size() < slen + 1) {
			Cd.add(0);
		}
        
        while (Cd2.size() < slen + 1) {
			Cd2.add(0);
		}
        
        for(int s = 0; s < fre_number; s++){
        	List<ZIndex> pIndexs = posZin.get(s);
    		// 正类后缀索引链
        	List<LNode> Lb = new ArrayList<>();
    		for (int m = 0; m < pIndexs.size(); m++) {
    			ZIndex pIndex = pIndexs.get(m);
	        	LNode pb;
	        	LNode qb = new LNode();
	        	LNode temp = new LNode();
	        	int size = pIndex.len;
	        	temp.data = size;
	        	Lb.add(m, temp);
	        	qb = Lb.get(m);
	        	for (int d = 0; d < size; d++) {
	        		pb = new LNode();
	        		pb.data = pIndex.index.get(d);
	        		qb.next = pb;
	        		qb = pb;
				}
	        	qb.next = null;
    		}
    		Lps.add(s, Lb);
        }
        
        for(int s = 0; s < fre_number; s++){
        	List<ZIndex> nIndexs = negZin.get(s);
    		// 负类后缀索引链
        	List<LNode> Ls = new ArrayList<>();
    		for (int m = 0; m < nIndexs.size(); m++) {
    			ZIndex nIndex = nIndexs.get(m);
	        	LNode pb;
	        	LNode qb = new LNode();
	        	LNode temp = new LNode();
	        	int size = nIndex.len;
	        	temp.data = size;
	        	Ls.add(m, temp);
	        	qb = Ls.get(m);
	        	for (int d = 0; d < size; d++) {
	        		pb = new LNode();
	        		pb.data = nIndex.index.get(d);
	        		qb.next = pb;
	        		qb = pb;
				}
	        	qb.next = null;
    		}
    		Lss.add(s, Ls);
        }
        
        for (int i = 0; i < fre_number; i++) {
        	
        	// 求后缀
        	Q = fre.get(i).subList(1, fre.get(i).size());
    		q = sort(Q);
    		
    		List<LNode> Lp = new ArrayList<>();
    		List<ZIndex> pIndexs = posZin.get(i);
    		// 正类前缀索引链
    		for (int m = 0; m < pIndexs.size(); m++) {
    			ZIndex pIndex = pIndexs.get(m);
    			
    			// 创建链表
        		LNode p = new LNode();
        		LNode s = new LNode();
        		LNode L = new LNode();
        		int size = pIndex.len;
        		L.data = size;
        		Lp.add(m, L); 
	        	s = Lp.get(m);
        		for (k = 0; k < size; k++) {
    				p = new LNode();
    				p.data = pIndex.index.get(k);
    				s.next = p;
    				s = p;
    			}
        		s.next = null;
    		}
    		Lpp.add(Lp);
    		
    		
    		List<LNode> Ls = new ArrayList<>();
    		List<ZIndex> nIndexs = negZin.get(i);
    		// 负类前缀索引链
    		for (int m = 0; m < nIndexs.size(); m++) {
    			ZIndex nIndex = nIndexs.get(m);
    			
    			// 创建链表
        		LNode p = new LNode();
        		LNode s = new LNode();
        		LNode L = new LNode();
        		int size = nIndex.len;
        		L.data = size;
        		Ls.add(m, L); 
	        	s = Ls.get(m);
        		for (k = 0; k < size; k++) {
    				p = new LNode();
    				p.data = nIndex.index.get(k);
    				s.next = p;
    				s = p;
    			}
        		s.next = null;
    		}
    		
    		Lsp.add(Ls);
    		
    		for (j = 0; j < fre_number; j++) {
				// 求前缀
				R = fre.get(j).subList(0, fre.get(j).size()-1);
				r = sort(R);
				
				int[] opnum = {0,0};
				boolean oop = false;
				
				//前后缀相对顺序相同
				if (Arrays.equals(q, r)) {
                		                	
                	//最前最后位置相等，拼接成两个模式
                    if(fre.get(i).get(0) == fre.get(j).get(slen-1)){
                    	Cd.set(0, fre.get(i).get(0));
                    	Cd2.set(0, fre.get(i).get(0) + 1);
                    	Cd.set(slen, fre.get(i).get(0) + 1);
                    	Cd2.set(slen, fre.get(i).get(0));
                    	for (t = 1; t < slen; t++){
                    		if (fre.get(i).get(t) > fre.get(j).get(slen - 1)) {
								//中间位置增长
                    			Cd.set(t, fre.get(i).get(t) + 1);
                    			Cd2.set(t, fre.get(i).get(t) + 1);
							} else {
								Cd.set(t, fre.get(i).get(t));
                    			Cd2.set(t, fre.get(i).get(t));
							}
                    	}
                    	System.out.println(Cd.toString());
                    	System.out.println(Cd2.toString());
                    	cd_num = cd_num + 2;
                    	opnum = grow_BaseP2(Cd.size()-1, Lps.get(j), Lpp.get(i), 0, opnum);
                    	int sum = 0;
                		for (int num : opnum) {
                			sum += num;
                		}
                		if (sum > 0) {
                			grow_BaseP2(Cd.size()-1, Lss.get(j), Lsp.get(i), 1, opnum);
            				jugde_csp();
                		}
                    
                    } else if (fre.get(i).get(0) < fre.get(j).get(slen - 1)) {
						Cd.set(0, fre.get(i).get(0));
						Cd.set(slen, fre.get(j).get(slen - 1) + 1);
						for (t = 1; t < slen; t++) {
							if (fre.get(i).get(t) > fre.get(j).get(slen - 1)) {
                    			Cd.set(t, fre.get(i).get(t) + 1);
							} else {
								Cd.set(t, fre.get(i).get(t));
							}
						}
						System.out.println(Cd.toString());
						cd_num = cd_num + 1;

						oop = grow_BaseP1(Lps.get(j), Lpp.get(i), 0);
						if (oop) {
							grow_BaseP1(Lss.get(j), Lsp.get(i), 1);
							jugde_csp();
						}
						
					} else {
						Cd.set(0, fre.get(i).get(0) + 1); // 大的加一
						Cd.set(slen, fre.get(j).get(slen - 1)); // 小的不变
						for(t = 0;t < slen - 1; t++){
							if (fre.get(j).get(t) > fre.get(i).get(0)){
								// 中间位置增长
								Cd.set(t+1, fre.get(j).get(t) + 1);
							} else {
								Cd.set(t+1, fre.get(j).get(t));
							}
						}
						System.out.println(Cd.toString());
						cd_num = cd_num + 1;
						oop = grow_BaseP1(Lps.get(j), Lpp.get(i), 0);
						if (oop) {
							grow_BaseP1(Lss.get(j), Lsp.get(i), 1);
							jugde_csp();
						}
					}
                }
				
			}
    		
		}

    	return 0;
        
	}

	public float cal_rate(List<Integer> Cd, List<ZIndex> z3,int lab) {
		float rsup = 0;
    	float sup_number = 0;
    	List<Integer> lentemp = sequence_len.get(lab);
    	// 满足密度阈值的序列个数
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
		
		// 1、采用索引的方式计算支持度
        for (int sid = 0; sid < sequence_num[lab]; sid++) {
        	int i = 0, j = 1;
        	
        	List<Integer> ztemp = new ArrayList<>();
        	List<Integer> z2temp = new ArrayList<>();
        	List<Float> sTemp = sDB.get(lab).get(sid).S;
        	while (j < sTemp.size()){
    			//12模式
    			if (sTemp.get(j) > sTemp.get(i)) {
    				ztemp.add(j);
    			} else if (sTemp.get(j) < sTemp.get(i)){
    				//21模式
    				z2temp.add(j);
    			}
    			i++;
    			j++;
    		}

        	// 为了记录在每个序列中的索引值以及匹配的支持度
			ZIndex zIndex = new ZIndex();
			zIndex.index = ztemp;
			zIndex.len = ztemp.size();
			// (1,2)总的出现次数
			zlen += ztemp.size();
			Z.add(zIndex);
			
			ZIndex z2Index = new ZIndex();
			z2Index.index = z2temp;
			z2Index.len = z2temp.size();
			// (2,1)总的出现次数
			z2len += z2temp.size();
			Z2.add(z2Index);
        	
        }
        
        if (lab == 0) {
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
			if (opnum[0] > 0) {
				jugde_oop(zlen,Cd,Z,lab);
			}
			if (opnum[1] > 0) {
				jugde_oop(z2len,Cd2,Z2,lab);
			}
		}
        
        return opnum;
	}  
	
	private boolean jugde_oop(int zlen, List<Integer> cd, List<ZIndex> z, int lab) {
		boolean gen_op = false;
		float rsup = 0;
    	// 计算模式支持率
		if (zlen > 0 && z.size() > 0) {
			rsup = cal_rate(cd, z, lab);
		}
    	
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
				
				List<Integer> Cdtemp = new ArrayList<>();
				for (Integer integer : cd) {
					Cdtemp.add(integer);
				}
				
		    	ZZCan zc = new ZZCan();
				zc.can = Cdtemp;
				zc.zin = z;
				zc.rsup = rsup;
				zc.support = zlen;
				
				// 正类索引位置
	    		POS.add(zc);
	    		sorted_queue queue = new sorted_queue();
	    		queue.can = Cdtemp;
	    		queue.pos_sup = rsup;
	    		oop.add(queue);
	    		
	    		L.add(Cdtemp);
	    		
//		    	System.out.print("频繁保序模式："+Cdtemp.toString());
//				System.out.print("，支持度为："+zc.support);
//				System.out.print("，正类支持率为："+zc.rsup);
//				System.out.println();
				
				frequent_num++;
				fre_num++;
			}
		}
		
    	if (lab == 1) {
    		List<Integer> Cdtemp = new ArrayList<>();
			for (Integer integer : cd) {
				Cdtemp.add(integer);
			}
			
	    	ZZCan zc = new ZZCan();
			zc.can = Cdtemp;
			zc.zin = z;
			zc.rsup = rsup;
			zc.support = zlen;
    		// 负类索引位置
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
		// 只扫描本轮生成的保序模式即可，每轮都会清空
		for(int i=0; i < oop.size(); i++){
			
			List<Integer> Cdtemp = new ArrayList<>();
			for (Integer integer : oop.get(i).can) {
				Cdtemp.add(integer);
			}
			
			int count = top_ps.size();
			if (count > 0) {
				tmp_pat = top_ps.peek();
				for (sorted_queue ps : top_ps) {
					if (ps.CR < tmp_pat.CR) {
						tmp_pat = ps;
					}
				}
				
			} else {
				tmp_pat.CR = 0;
				tmp_pat.can = new ArrayList<>();
				tmp_pat.pos_sup = 0;
			}

			// 正类支持率
			pos_sup = oop.get(i).pos_sup; 
			neg_sup = oop.get(i).neg_sup;
			
			// 对比率 = a - b
			float CR = pos_sup - neg_sup;
			
			if (CR > 0) {
				// 对比保序模式数量加1
				fre_cop_num++;
				
				sorted_queue current_pat = new sorted_queue();
				current_pat.CR = CR;				
				
				if ((current_pat.CR > tmp_pat.CR) || (top_ps.size() < tpk)) {
					current_pat.can = Cdtemp;
					current_pat.CR = CR;
					current_pat.pos_sup = pos_sup;
					System.out.print("当前模式为："+Cdtemp.toString());
					System.out.println("CR："+CR);
					top_ps.offer(current_pat); 
					//保持top-k个元素
					if (top_ps.size() > tpk) {
						top_ps.remove(tmp_pat);
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
		
		opnum = calculate(0, opnum);
		int sum = 0;
		for (int num : opnum) {
			sum += num;
		}
		if (sum > 0) {
			calculate(1,opnum);
		}
		
		// 判断是否为对比保序模式
		jugde_csp();
		
		Cd.clear();
		Cd2.clear();
	}
	
	public void read_file(String filePath){
		List<Integer> pos_len = new ArrayList<>();
		
		List<Integer> neg_len =  new ArrayList<>();
		
		// 正类数据
		List<seqdb> pos = new ArrayList<>();
		// 负类数据
		List<seqdb> neg = new ArrayList<>();
		
		File file = new File(filePath);
        try {
            BufferedReader br = new BufferedReader(new FileReader(file));
			String buffer = "";
			while ((buffer = br.readLine()) != null) {
                if (buffer.isEmpty() == true
                        || buffer.charAt(0) == '#' || buffer.charAt(0) == '%'
                        || buffer.charAt(0) == '@') {
                    continue;
                }
				String[] valueStr = buffer.trim().split(",");
//				String[] valueStr = buffer.trim().split("	");
//                String[] valueStr = buffer.trim().split("  ");
				float[] inS = new float[valueStr.length - 1];
				List<Float> sTemp = new ArrayList<>();
				
				// 标签在第一列
				float first = Float.parseFloat(valueStr[0]);
				for (int j = 1; j < (valueStr.length); j++) {
					inS[j-1] = Float.parseFloat(valueStr[j]);
				}
				
				// 数据提取极值点，压缩数据
				sTemp = extraction(inS);
				if (first == 2) {
//				if (first == 4.0000000e+00 || first == 3.0000000e+00) {
					// 存储在负类库中
					seqdb negTemp = new seqdb();
					negTemp.S = sTemp;
					negTemp.seqlen = sTemp.size();
					neg.add(negTemp);
					neg_len.add(sTemp.size());
					sequence_num[1]++;
				} else {
					// 存储在正类库中
					seqdb posTemp = new seqdb();
					posTemp.S = sTemp;
					posTemp.seqlen = sTemp.size();
					pos.add(posTemp);
					pos_len.add(sTemp.size());
					sequence_num[0]++;
				}
				
			}
			br.close();
			// 0表示正类，1表示负类
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
		density = density2; // minden
		tpk = tpk2; // k
		long begintime = System.currentTimeMillis();
		read_file(filePath);
		
        find(); // 从2长度模式开始计算
		while(fre_num > 0){
			generate_fre(); // 模式融合策略
		}
		
		int pos_fre_cop_num = fre_cop_num; // 正向对比保序模式
		int pos_frequent_num = frequent_num; // 正向频繁保序模式
		int pos_cd_num = cd_num; // 正向候选模式数量
		
		System.out.println("正向候选模式为："+pos_cd_num);
		
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
		
		// 文件反转，计算负-正
		read_file_reverse();
		
		find();
		while(fre_num > 0){
			generate_fre();
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









