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

public class COPP_prun {
	
	public int tpk;
	public float density; // 密度约束
	
	public int fre_cop_num = 0; // 总的频繁对比保序模式数量
	public int frequent_num = 0;  //总的频繁模式数量
	public int fre_num = 0;
	public int cd_num = 2;//候选模式数量
	// 统计正负类序列个数
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
		// 存放符合模式，末位的索引
		List<Integer> index = new ArrayList<>(); 
		// 索引长度
		int len;
	}
	
	class ZZCan implements Comparable<ZZCan> {
		List<ZIndex> zin = new ArrayList<>();
		List<Integer> can	= new ArrayList<>();
		int support;
		// 模式支持率
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
	
	List<sorted_queue> oop = new ArrayList<>(); // 用来存放本轮生成的保序模式，每轮比较完之后就会清空
	List<ZZCan> POS1 = new ArrayList<>(); //存放正类中末位的数组，用来存放正类中(1,2)、(2,1)模式的全部结果值（索引位置、支持度、对比率）
	List<ZZCan> POS2 = new ArrayList<>();
	List<ZZCan> NEG1 = new ArrayList<>(); //存放负类中末位的数组，用来存放负类中(1,2)、(2,1)模式的全部结果值（索引位置、支持度、对比率）
	List<ZZCan> NEG2 = new ArrayList<>();
	
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
	
	public boolean grow_BaseP1(List<LNode> Ld, List<LNode> L, int lab, int group){
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
					ztemp.add(q.next.data);
					p.next = p.next.next;
					q.next = q.next.next;
				} else if(p.next.data < q.next.data){
					p = p.next;
				} 
				else {
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
        	oop = jugde_oop(zlen,Cd,Z,lab,group);
		} else {
			jugde_oop(zlen,Cd,Z,lab,group);
		}

		return oop;
	}

	public int[] grow_BaseP2(int slen, List<LNode> Ld, List<LNode> L, int lab, int[] opnum, int group){
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
				} 
				else {
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
    		oop = jugde_oop(zlen,Cd,Z,lab,group);
    		if (oop) {
    			opnum[0]++;
			}
            oop2 = jugde_oop(z2len,Cd2,Z2,lab,group);
            if (oop2) {
            	opnum[1]++;
			}
		} else {
			if (opnum[0] > 0) {
				jugde_oop(zlen,Cd,Z,lab,group);
			}
			if (opnum[1] > 0) {
				jugde_oop(z2len,Cd2,Z2,lab,group);
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
		List<List<List<ZIndex>>> posZin = new ArrayList<>();
		List<List<ZIndex>> posZin1 = new ArrayList<>();
		List<List<ZIndex>> posZin2 = new ArrayList<>();
		// 负类索引位置
		List<List<List<ZIndex>>> negZin = new ArrayList<>();
		List<List<ZIndex>> negZin1 = new ArrayList<>();
		List<List<ZIndex>> negZin2 = new ArrayList<>();
		// 候选模式集
		List<List<List<Integer>>> fre = new ArrayList<>();
		List<List<Integer>> fre1 = new ArrayList<>();
		List<List<Integer>> fre2 = new ArrayList<>();
		// 正类后缀索引链
		List<List<List<LNode>>> Lps = new ArrayList<>();
		List<List<LNode>> Lps1 = new ArrayList<>();
		List<List<LNode>> Lps2 = new ArrayList<>();
		// 负类后缀索引链
		List<List<List<LNode>>> Lns = new ArrayList<>();
		List<List<LNode>> Lns1 = new ArrayList<>();
		List<List<LNode>> Lns2 = new ArrayList<>();
		
		int[] q = new int[256];
		int[] r = new int[256];
		
		int j = 0;
		int fre_number = 0;
		int t = 0;
		int k = 0;

		// 对生成的候选模式按照支持度降序排序
		Collections.sort(POS1, new Comparator<ZZCan>() {
		    public int compare(ZZCan z1, ZZCan z2) {
		        return z2.compareTo(z1);
		    }
		});
		
		Collections.sort(POS2, new Comparator<ZZCan>() {
		    public int compare(ZZCan z1, ZZCan z2) {
		        return z2.compareTo(z1);
		    }
		});
		
		for (ZZCan pTemp : POS1) {
			// 候选模式集
			List<Integer> cdTemp = pTemp.can;
			List<Integer> fretemp = new ArrayList<>();
			for (Integer integer : cdTemp) {
				fretemp.add(integer);
			}
			fre1.add(fretemp);
			
			List<ZIndex> postemp = new ArrayList<>();
			for (ZIndex zin : pTemp.zin) {
				postemp.add(zin);
			}
			posZin1.add(postemp);
			
			for (ZZCan nTemp : NEG1) {
				if (nTemp.can.equals(cdTemp)) {
					List<ZIndex> negtemp = new ArrayList<>();
					for (ZIndex zin : nTemp.zin) {
						negtemp.add(zin);
					}
					negZin1.add(negtemp);
					NEG1.remove(nTemp);
					break;
				}
				
			}
			
		}
		fre.add(fre1);
		posZin.add(posZin1);
		negZin.add(negZin1);
		POS1.clear();
		NEG1.clear();
		
		for (ZZCan pTemp : POS2) {
			// 候选模式集
			List<Integer> cdTemp = pTemp.can;
			List<Integer> fretemp = new ArrayList<>();
			for (Integer integer : cdTemp) {
				fretemp.add(integer);
			}
			fre2.add(fretemp);
			
			List<ZIndex> postemp = new ArrayList<>();
			for (ZIndex zin : pTemp.zin) {
				postemp.add(zin);
			}
			posZin2.add(postemp);
			
			for (ZZCan nTemp : NEG2) {
				if (nTemp.can.equals(cdTemp)) {
					List<ZIndex> negtemp = new ArrayList<>();
					for (ZIndex zin : nTemp.zin) {
						negtemp.add(zin);
					}
					negZin2.add(negtemp);
					NEG2.remove(nTemp);
					break;
				}
				
			}
			
		}
		fre.add(fre2);
		posZin.add(posZin2);
		negZin.add(negZin2);
		POS2.clear();
		NEG2.clear();
		
		//模式长度
		if (fre1.size() > 0) {
			slen = fre1.get(0).size();
		} else if (fre2.size() > 0) {
			slen = fre2.get(0).size();
		}
		
		fre_number = fre_num;
		fre_num = 0;

        while (Cd.size() < slen + 1) {
			Cd.add(0);
		}
        
        while (Cd2.size() < slen + 1) {
			Cd2.add(0);
		}
        
        for(int s = 0; s < fre1.size(); s++){
        	List<ZIndex> pIndexs = posZin1.get(s);
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
    		Lps1.add(s, Lb);
        }
        Lps.add(Lps1);
        
        for(int s = 0; s < fre2.size(); s++){
        	List<ZIndex> pIndexs = posZin2.get(s);
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
    		Lps2.add(s, Lb);
        }
        Lps.add(Lps2);
        
        for(int s = 0; s < fre1.size(); s++){
        	List<ZIndex> nIndexs = negZin1.get(s);
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
    		Lns1.add(s, Ls);
        }
        Lns.add(Lns1);
        
        for(int s = 0; s < fre2.size(); s++){
        	List<ZIndex> nIndexs = negZin2.get(s);
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
    		Lns2.add(s, Ls);
        }
        Lns.add(Lns2);
        
        int gg = 1; // gg表示先从二组作为后缀开始，稍后gg-1
        for (int group = 0; group < 2; group++) { // gg表示先从一组和二组融合开始，即一组先作为前缀，二组作为后缀
        	List<List<Integer>> freTemp = fre.get(group);
        	List<List<ZIndex>> posZinTemp = posZin.get(group);
        	List<List<ZIndex>> negZinTemp = negZin.get(group);
        	
        	// 正类前缀索引链
    		List<List<LNode>> Lpp = new ArrayList<>();
    		// 负类前缀索引链
    		List<List<LNode>> Lnp = new ArrayList<>();
        	
        	for (int i = 0; i < fre.get(group).size(); i++) {
            	// 求后缀
            	Q = freTemp.get(i).subList(1, freTemp.get(i).size());
        		q = sort(Q);
        		
        		List<LNode> Lp = new ArrayList<>();
        		List<ZIndex> pIndexs = posZinTemp.get(i);
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
        		
        		List<LNode> Ln = new ArrayList<>();
        		List<ZIndex> nIndexs = negZinTemp.get(i);
        		// 负类前缀索引链
        		for (int m = 0; m < nIndexs.size(); m++) {
        			ZIndex nIndex = nIndexs.get(m);
        			
        			// 创建链表
            		LNode p = new LNode();
            		LNode s = new LNode();
            		LNode L = new LNode();
            		int size = nIndex.len;
            		L.data = size;
            		Ln.add(m, L); 
    	        	s = Ln.get(m);
            		for (k = 0; k < size; k++) {
        				p = new LNode();
        				p.data = nIndex.index.get(k);
        				s.next = p;
        				s = p;
        			}
            		s.next = null;
        		}
        		
        		Lnp.add(Ln);
        		
        		List<List<Integer>> freTempSu = fre.get(gg);
    			List<List<LNode>> LpsTemp = Lps.get(gg);
        		List<List<LNode>> LnsTemp = Lns.get(gg);
        		int ggsize = fre.get(gg).size();
        		for (j = 0; j < ggsize; j++) {
    				// 求前缀
    				R = freTempSu.get(j).subList(0, freTempSu.get(j).size()-1);
    				r = sort(R);
    				
    				int[] opnum = {0,0};
    				boolean oop = false;
    				
    				if (Arrays.equals(q, r)) {
                    		                	
                        if(freTemp.get(i).get(0) == freTempSu.get(j).get(slen-1)){
                        	Cd.set(0, freTemp.get(i).get(0));
                        	Cd2.set(0, freTemp.get(i).get(0) + 1);
                        	Cd.set(slen, freTemp.get(i).get(0) + 1);
                        	Cd2.set(slen, freTemp.get(i).get(0));
                        	for (t = 1; t < slen; t++){
                        		if (freTemp.get(i).get(t) > freTempSu.get(j).get(slen - 1)) {
                        			Cd.set(t, freTemp.get(i).get(t) + 1);
                        			Cd2.set(t, freTemp.get(i).get(t) + 1);
    							} else {
    								Cd.set(t, freTemp.get(i).get(t));
                        			Cd2.set(t, freTemp.get(i).get(t));
    							}
                        	}
                        	cd_num = cd_num + 2;
                        	opnum = grow_BaseP2(Cd.size()-1, LpsTemp.get(j), Lpp.get(i), 0, opnum, group);
                        	int sum = 0;
                    		for (int num : opnum) {
                    			sum += num;
                    		}
                    		if (sum > 0) {
                    			grow_BaseP2(Cd.size()-1, LnsTemp.get(j), Lnp.get(i), 1, opnum, group);
                				jugde_csp();
                    		}
                        
                        } else if (freTemp.get(i).get(0) < freTempSu.get(j).get(slen - 1)) {
    						Cd.set(0, freTemp.get(i).get(0));
    						Cd.set(slen, freTempSu.get(j).get(slen - 1) + 1);
    						for (t = 1; t < slen; t++) {
    							if (freTemp.get(i).get(t) > freTempSu.get(j).get(slen - 1)) {
    								//中间位置增长
                        			Cd.set(t, freTemp.get(i).get(t) + 1);
    							} else {
    								Cd.set(t, freTemp.get(i).get(t));
    							}
    						}
    						cd_num = cd_num + 1;

    						oop = grow_BaseP1(LpsTemp.get(j), Lpp.get(i), 0, group);
    						if (oop) {
    							grow_BaseP1(LnsTemp.get(j), Lnp.get(i), 1, group);
    							jugde_csp();
    						}
    						
    					} else {
    						Cd.set(0, freTemp.get(i).get(0) + 1); // 大的加一
    						Cd.set(slen, freTempSu.get(j).get(slen - 1)); // 小的不变
    						for(t = 0;t < slen - 1; t++){
    							if (freTempSu.get(j).get(t) > freTemp.get(i).get(0)){
    								// 中间位置增长
    								Cd.set(t+1, freTempSu.get(j).get(t) + 1);
    							} else {
    								Cd.set(t+1, freTempSu.get(j).get(t));
    							}
    						}
    						cd_num = cd_num + 1;
    						oop = grow_BaseP1(LpsTemp.get(j), Lpp.get(i), 0, group);
    						if (oop) {
    							grow_BaseP1(LnsTemp.get(j), Lnp.get(i), 1, group);
    							jugde_csp();
    						}
    					}
                    }
    				
    			}
        	}
        	gg = gg - 1;
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
    		oop = jugde_oop(zlen,Cd,Z,lab,0);
    		if (oop) {
    			opnum[0]++;
			}
            oop2 = jugde_oop(z2len,Cd2,Z2,lab,1);
            if (oop2) {
            	opnum[1]++;
			}
		} else {
			if (opnum[0] > 0) {
				jugde_oop(zlen,Cd,Z,lab,0);
			}
			if (opnum[1] > 0) {
				jugde_oop(z2len,Cd2,Z2,lab,1);
			}
		}
        
        return opnum;
	}
	
	public boolean jugde_oop(int zlen, List<Integer> cd, List<ZIndex> z, int lab, int group) {
		// TODO Auto-generated method stub
		boolean gen_op = false;
		float rsup = 0;
    	// 计算模式支持率
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
    	
    	if (lab == 0) {
    		
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
	    		if (group == 0) {
					// 正类索引位置
		    		POS1.add(zc);
				} else {
					POS2.add(zc);
				}
	    		sorted_queue queue = new sorted_queue();
	    		queue.can = Cdtemp;
	    		queue.pos_sup = rsup;
	    		oop.add(queue);
	    		
//	    		System.out.print("频繁保序模式："+Cdtemp.toString());
//				System.out.print("，支持度为："+zc.support);
//				System.out.println();
				
				frequent_num++;
				fre_num++;
			}
		} else {
			if (group == 0) {
				// 负类索引位置
	    		NEG1.add(zc);
			} else {
				NEG2.add(zc);
			}
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
				
				if ((top_ps.size() < tpk)) {
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
				
				float first = Float.parseFloat(valueStr[0]);
				for (int j = 1; j < (valueStr.length); j++) {
					inS[j-1] = Float.parseFloat(valueStr[j]);
				}
				
				// 数据提取极值点，压缩数据
				sTemp = extraction(inS);
				
				// 数据集中第一个元素为标签元素，通过1或2，0或1，-1和1来区分
				if (first == 2) {
//				if (first == 1.0000000e+00 || first == 3.0000000e+00) {
					seqdb negTemp = new seqdb();
					negTemp.S = sTemp;
					negTemp.seqlen = sTemp.size();
					neg.add(negTemp);
					neg_len.add(sTemp.size());
					sequence_num[1]++;
				} else {
					seqdb posTemp = new seqdb();
					posTemp.S = sTemp;
					posTemp.seqlen = sTemp.size();
					pos.add(posTemp);
					pos_len.add(sTemp.size());
					sequence_num[0]++;
				}
				
			}
			br.close();
			
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
	
	/**
	 * 将源文件翻转，正负类互换
	 * 因为计算完正-负，还需要再计算负-正
	 * @param filePath
	 */
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
			generate_fre();
		}

		int pos_fre_cop_num = fre_cop_num;
		int pos_frequent_num = frequent_num;
		int pos_cd_num = cd_num;
		
//		System.out.println("正向计算候选模式数量为: "+(pos_cd_num));
		
		fre_cop_num = 0; // 总的频繁对比保序模式数量
		frequent_num = 0;  //总的频繁保序模式数量
		fre_num = 0;
		cd_num = 2;//候选模式数量
		oop = new ArrayList<>(); // 用来存放本轮生成的保序模式，每轮比较完之后就会清空
		POS1 = new ArrayList<>(); //存放正类中末位的数组用来存放正类中(1,2)、(2,1)模式的全部结果值（索引位置、支持度、对比率）
		POS2 = new ArrayList<>();
		NEG1 = new ArrayList<>(); //存放负类中末位的数组用来存放负类中(1,2)、(2,1)模式的全部结果值（索引位置、支持度、对比率）
		NEG2 = new ArrayList<>();
		
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









