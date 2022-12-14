package com.algo.copp.end;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.Formatter;
import java.util.List;
import java.util.PriorityQueue;

public class COPP_extra {
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
		int len;
	}
	
	class ZZCan implements Comparable<ZZCan> {
		// 各个序列中的模式索引位置
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
	List<ZZCan> POS = new ArrayList<>(); //存放正类中末位的数组用来存放正类中(1,2)、(2,1)模式的全部结果值（索引位置、支持度、对比率）
	List<ZZCan> NEG = new ArrayList<>(); //存放负类中末位的数组用来存放负类中(1,2)、(2,1)模式的全部结果值（索引位置、支持度、对比率）
	List<List<Integer>> L = new ArrayList<>();//存放每次生成的频繁模式
	
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
	
	public boolean grow_BaseP1(List<LNode> Ld, List<LNode> L, int lab){
		boolean oop = false;
		int zlen = 0;
		List<ZIndex> Z	= new ArrayList<>();
		for (int i = 0; i < Ld.size(); i++) {
			// p为前缀，q为后缀
			LNode p = L.get(i);
			LNode q = Ld.get(i);
		
			List<Integer> ztemp = new ArrayList<>();
			
			while(p.next != null && q.next != null){
				if (q.next.data == p.next.data + 1) {
					read_num = read_num + 1; // 比较次数
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
		List<ZIndex> Z	= new ArrayList<>(); //存放(1,...,2)模式本次生成的末位数组，不是真正的1,2关系，只是表示比较大小关系
		List<ZIndex> Z2 = new ArrayList<>(); //存放(2,...,1)模式本次生成的末位数组
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
					read_num = read_num + 1; // 比较次数
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
	
	// 模式拼接
	public int generate_fre(){
		int slen = 0;
		
		List<Integer> Q = new ArrayList<>();
		List<Integer> R = new ArrayList<>();
		// 正类索引位置
		List<List<ZIndex>> posZin = new ArrayList<>();
		// 负类索引位置
		List<List<ZIndex>> negZin = new ArrayList<>();
		// 频繁保序模式
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

		// 对生成的候选模式按照支持度降序排序
		Collections.sort(POS, new Comparator<ZZCan>() {
		    public int compare(ZZCan z1, ZZCan z2) {
		        return z2.compareTo(z1);
		    }
		});
		
		for (ZZCan pTemp : POS) {
			// 候选模式集
			List<Integer> cdTemp = pTemp.can;
			List<Integer> fretemp = new ArrayList<>();
			for (Integer integer : cdTemp) {
				fretemp.add(integer);
			}
			fre.add(fretemp);
			
			List<ZIndex> postemp = new ArrayList<>();
			for (ZIndex zin : pTemp.zin) {
				postemp.add(zin);
			}
			posZin.add(postemp);
			
			for (ZZCan nTemp : NEG) {
				if (nTemp.can.equals(cdTemp)) {
					List<ZIndex> negtemp = new ArrayList<>();
					for (ZIndex zin : nTemp.zin) {
						negtemp.add(zin);
					}
					negZin.add(negtemp);
					NEG.remove(nTemp);
					break;
				}
				
			}
			
		}
		
		POS.clear();
		NEG.clear();
		
		//模式长度
		slen = fre.get(0).size();
		
		fre_number = fre_num;
		fre_num = 0;
		
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
				
				if (Arrays.equals(q, r)) {
                		                	
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
								//中间位置增长
                    			Cd.set(t, fre.get(i).get(t) + 1);
							} else {
								Cd.set(t, fre.get(i).get(t));
							}
						}
						
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
		int zlen = 0; // (1,2)模式总支持度
		int z2len = 0;// (2,1)模式总支持度
		
		List<ZIndex> Z	= new ArrayList<>(); // 存放(1,2)模式本次生成的末位索引位置
		List<ZIndex> Z2 = new ArrayList<>(); // 存放(2,1)模式本次生成的末位索引位置
		
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
        	opnum[0] = 0;
        	opnum[1] = 0;
    		// 判断模式Cd是否为保序模式
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
		// TODO Auto-generated method stub
		boolean gen_op = false;
		float rsup = 0;
    	// 计算模式支持率
		if (zlen > 0 && z.size() > 0) {
			rsup = cal_rate(cd, z, lab);
		}
    	
		if (lab == 0) {
			if (rsup > 0) {
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
		    		queue.support = zlen;
		    		// 记录本轮生成的保序模式
		    		oop.add(queue);
					L.add(Cdtemp);
//			    	System.out.print("频繁保序模式："+Cdtemp.toString());					
//					System.out.print("，支持度为："+zc.support);
//					System.out.println();
					
					frequent_num++;
					fre_num++;
				}
				
				
			}
			
		} else {
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
		for(int i=0; i < oop.size(); i++){
			pos_sup = oop.get(i).pos_sup; 
			neg_sup = oop.get(i).neg_sup;
			
			
			int count = top_ps.size();
			if (count > 0) {
				tmp_pat = top_ps.peek();
			} else {
				tmp_pat.CR = 0;
				tmp_pat.can = new ArrayList<>();
				tmp_pat.pos_sup = 0;
			}
			
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
			List<String> endList = new ArrayList<>();
			List<Float> endfList = new ArrayList<>();
			int max = 0;
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
				
				// first 标签位在第一个位置
				for (int j = 0; j < (valueStr.length); j++) {
					String ssString = valueStr[j];
					float aaa = Float.parseFloat(ssString);
					sTemp.add(aaa);
				}
				
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
				float first = sDB0.get(i).S.get(0);
				List<Float> stemp = new ArrayList<>();
				int len = sDB0.get(i).seqlen;
				
				if (first == 2) {
//				if (first == 1.0000000e+00 || first == 2.0000000e+00) {
					for (int j = 1; j < len; j++) {
						stemp.add(sDB0.get(i).S.get(j));
					}
					seqdb negTemp = new seqdb();
					negTemp.S = stemp;
					negTemp.seqlen = len - 1;
					neg.add(negTemp);
					neg_len.add(len-1);
					sequence_num[1]++;
				} else {
					for (int j = 1; j < len; j++) {
						stemp.add(sDB0.get(i).S.get(j));
					}
					seqdb posTemp = new seqdb();
					posTemp.S = stemp;
					posTemp.seqlen = len - 1;
					pos.add(posTemp);
					pos_len.add(len - 1);
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
	
	public void runAlgorithm(String filePath, float density2, int tpk2){
		
		density = density2;
		tpk = tpk2;
		long begintime = System.currentTimeMillis();
		read_file(filePath);
		
        find();
		while(fre_num > 0){
			generate_fre();
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









