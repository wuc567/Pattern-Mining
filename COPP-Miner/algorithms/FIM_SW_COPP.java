package com.algo.copp.end;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.text.DecimalFormat;
import java.util.*;

public class FIM_SW_COPP {
	
	public int len = 2; // 用来表示每轮候选模式长度
	public int candiNum = 0; // 候选模式数量
    public int minsup = 0;
	public int tpk;
	public float density; // 密度约束
	
	public int fre_cop_num = 0; // 总的频繁对比保序模式数量
	public int frequent_num = 0;  //总的频繁保序模式数量
	public int fre_num = 0;
	public int scan_num = 1;//扫描序列次数
	public int read_num = 0;//访问序列次数
	
	static class seqdb {
		int id; // sequence id
		// 当前序列
		List<Float> S = new ArrayList<>();
		// 当前序列长度
		int seqlen;
		// 模式在该序列中的 支持度
		int support;
	} 
	
	List<List<seqdb>> sDB = new ArrayList<>();
	public int[] sequence_num = { 0, 0 };
	public List<List<Integer>> sequence_len = new ArrayList<>();
	
	// TOPK pattern
	class sorted_queue implements Comparable<sorted_queue> {
		// 当前候选模式
		String can;
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
	
	class ZIndex{
		// 当前序列长度
		int current_len; 
		// 出现数
		int count;
	}
	
	// 定义优先队列（按照CR的大小排序）
	PriorityQueue<sorted_queue> top_ps = new PriorityQueue<>();
	List<sorted_queue> oop = new ArrayList<>(); // 用来存放本轮生成的保序模式，每轮比较完之后就会清空
	
	public List<String> calculatePos() {
		
		// 用来存储正类中最终生成的模式
		List<String> resultPat = new ArrayList<>();
		// 用来存储最后的结果，key模式、value支持度
		Map<String, Integer> result = new HashMap<>();
		// 用来存储每条序列中，模式以及模式出现的元素值。key:序列sid、value:(key:模式、value:模式出现对应元素)
		Map<Integer, Map<String, List<String>>> map = new HashMap<>();
        
        while (true) {
        	// 用来存储生成的模式，为了遍历统计总支持度使用
    		List<String> patTemp = new ArrayList<>();
        	// 用来结束循环，如果没有新的频繁模式生成，终止循环
            boolean flag = false;
			int sid = 0;
			int current_len = 0;
	        for (; sid < sequence_num[0]; sid++) {
	        	List<Float> sTemp = sDB.get(0).get(sid).S;
	        	current_len = sTemp.size();
	        	float[] fs = new float[sTemp.size()];
	        	for (int k = 0; k < fs.length; k++) {
					fs[k] = sTemp.get(k);
				}
	        	// 得到一条序列中len长度模式的结果集
	        	Map<String, List<String>> inMap = new HashMap<>();
	        	if (len == 2) {
	        		inMap = getMap(fs, null, null, 0);
				} else {
					inMap = getMap(fs, map.get(sid), null, 0);
				}
	            candiNum += inMap.size();
	        	for (Map.Entry<String, List<String>> entry : inMap.entrySet()) {
	        		if (!patTemp.contains(entry.getKey())) {
	        			patTemp.add(entry.getKey());
					}
	            }
	            map.put(sid, inMap);
	        }
	        
	        for (String pat : patTemp) {
	        	int sum = 0;
	        	List<ZIndex> indexs = new ArrayList<>();
	        	for (Map.Entry<Integer, Map<String, List<String>>> entrys : map.entrySet()) {
	        		boolean exist = false;
		        	for (Map.Entry<String, List<String>> entry : entrys.getValue().entrySet()) {
		                if (entry.getKey().contains(pat)){
		                	// 如果序列中存在该模式，则存储模式在该条序列中的出现数
		                	ZIndex index = new ZIndex();
		                	index.current_len = sequence_len.get(0).get(entrys.getKey());
		                	index.count = entry.getValue().size();
		                	indexs.add(entrys.getKey(), index);
		                	sum += entry.getValue().size();
		                	exist = true;
		                    break;
		                } 
		            }
		        	if (!exist) {
		        		// 若不存在，则出现数记为0
	                	ZIndex index = new ZIndex();
	                	index.current_len = current_len;
	                	index.count = 0;
	                	indexs.add(entrys.getKey(), index);
					}
		        }
        		if (sum >= minsup) {
        			resultPat.add(pat);
        			flag = true;
        			boolean genoop = false;
	        		genoop = jugde_oop(sum,pat,indexs,0);
	        		if (genoop) {
	        			result.put(pat, sum);
					}
				}
				
	        	
			}
	        if (!flag) {
                break;
            }
	        len++;
	        
        }
        
        // 返回正类中生成的全部频繁模式
        return resultPat;
        
 	}
	
	public void calculateNeg(List<String> resultPat) {
		// 用来存储每条序列中，模式以及模式出现的元素值。key:序列sid、value:(key:模式、value:模式出现对应元素)
		Map<Integer, Map<String, List<String>>> map = new HashMap<>();
        while (resultPat.size() > 0) {
        	// 用来存储生成的模式，为了遍历统计总支持度使用
    		List<String> patTemp = new ArrayList<>();
			int sid = 0;
			int current_len = 0;
			while(resultPat.size() > 0) {
				// 按照当前len长度的模式去遍历，先从2长度开始，长度逐次递增
				String pat = resultPat.get(0);
				String key = pat;
				key = pat.replaceAll(" ", "");
		        key = key.substring(1, key.length() - 1);
		        String[] strOrder = key.split(",");
				if (strOrder.length == len) {
					patTemp.add(pat);
					resultPat.remove(pat);
				} else if (strOrder.length > len) {
					break;
				}
			}
	        for (; sid < sequence_num[1]; sid++) {
	        	List<Float> sTemp = sDB.get(1).get(sid).S;
	        	current_len = sTemp.size();
	        	float[] fs = new float[sTemp.size()];
	        	for (int k = 0; k < fs.length; k++) {
					fs[k] = sTemp.get(k);
				}
	        	// 得到一条序列中len长度模式的结果集
	        	Map<String, List<String>> inMap = new HashMap<>();
	        	if (len == 2) {
	        		inMap = getMap(fs, null, patTemp, 1);
				} else {
					inMap = getMap(fs, map.get(sid), patTemp, 1);
				}
	        	// 按照序列编号存储对应的结果值
	            map.put(sid, inMap);
	        }
	        
	        for (String pat : patTemp) {
	        	int sum = 0;
	        	List<ZIndex> indexs = new ArrayList<>();
	        	for (Map.Entry<Integer, Map<String, List<String>>> entrys : map.entrySet()) {
	        		boolean exist = false;
		        	for (Map.Entry<String, List<String>> entry : entrys.getValue().entrySet()) {
		                if (entry.getKey().contains(pat)){
		                	// 如果序列中存在该模式，则存储模式在该条序列中的出现数
		                	ZIndex index = new ZIndex();
		                	index.current_len = sequence_len.get(1).get(entrys.getKey());
		                	index.count = entry.getValue().size();
		                	indexs.add(entrys.getKey(), index);
		                	sum += entry.getValue().size();
		                	exist = true;
		                    break;
		                } 
		            }
		        	if (!exist) {
		        		// 若不存在，则出现数记为0
	                	ZIndex index = new ZIndex();
	                	index.current_len = current_len;
	                	index.count = 0;
	                	indexs.add(entrys.getKey(), index);
					}
		        }
	        	
	        	jugde_oop(sum,pat,indexs,1);
			}
	        len++;
        }
        
 	}
	
	/**
	 * 
	 * @param s 当前序列
	 * @param lastMap 上一轮模式生成的结果，比如当前模式长度为3，则lastMap即为2长度的生成结果
	 * @param patTemp 这个参数，是为了计算负类中的出现设置的
	 * @param lab
	 * @return
	 */
	private Map<String, List<String>> getMap(float[] s, Map<String, List<String>> lastMap, List<String> patTemp, int lab) {
        Map<String, List<String>> inMap = new HashMap<>();
        for (int i = 0; i <= s.length - len; i++) {
       	 	float[] sub = new float[len];
       	 	// 依次取len长度的字符
            System.arraycopy(s, i, sub, 0, len);
            // 计算当前子序列的相对顺序
            int[] subOrder = getOrder(sub, lastMap);
            if (subOrder == null) {
                continue;
            }
            // 如果当前候选模式集中不包含这个保序模式，则继续比较下一个子序列
            // 因为负类中的模式是根据正类中的模式结果去计算的，这样可以避免重复计算
            if (lab == 1 && !patTemp.contains(Arrays.toString(subOrder))) {
				continue;
			}
            if (inMap.get(Arrays.toString(subOrder)) == null) {
                List<String> subList = new ArrayList<>();
                subList.add(Arrays.toString(sub));
                inMap.put(Arrays.toString(subOrder), subList);
            } else {
                List<String> subList = inMap.get(Arrays.toString(subOrder));
                subList.add(Arrays.toString(sub));
                inMap.put(Arrays.toString(subOrder), subList);
                
            }
        }
        return inMap;
   }

   private int[] getOrder(float[] seq, Map<String, List<String>> map) {
   	Set<Double> set = new HashSet<>();
       for (double d : seq) {
           set.add(d);
       }
       if (set.size() != seq.length) {
           return null;
       }
       if (seq.length == 2){
           if (seq[0] > seq[1]){
               return new int[]{2, 1};
           } else {
               return new int[]{1, 2};
           }
       }

       float[] pre = new float[seq.length - 1];
       System.arraycopy(seq, 0, pre, 0, pre.length);

       String key = null;
       for (Map.Entry<String, List<String>> entry : map.entrySet()) {
           if (entry.getValue().contains(Arrays.toString(pre))){
               key = entry.getKey();
               break;
           }
       }

       if (key == null){
           return null;
       }
       key = key.replaceAll(" ", "");
       key = key.substring(1, key.length() - 1);
       String[] strOrder = key.split(",");
       int[] preOrder = new int[strOrder.length];
       for (int i = 0; i < strOrder.length; i++){
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
	
	private boolean jugde_oop(int zlen, String pat, List<ZIndex> indexs, int lab) {
		// TODO Auto-generated method stub
		boolean gen_op = false;
		float rsup = 0;
		if (zlen > 0 && indexs.size() > 0) {
			rsup = cal_rate(indexs, lab);
		}
    	
		if (lab == 0 && rsup > 0) {
			
			sorted_queue tmp_pat = new sorted_queue();
			int count = top_ps.size();
			if (count > 0) {
				tmp_pat = top_ps.peek();
			} else {
				tmp_pat.CR = 0;
				tmp_pat.can = "";
				tmp_pat.pos_sup = 0;
			}
			
			if ((count < tpk) || (count == tpk && rsup >= tmp_pat.CR)) {
				gen_op = true;
		    	
	    		sorted_queue queue = new sorted_queue();
	    		queue.can = pat;
	    		queue.pos_sup = rsup;
	    		// 记录本轮生成的保序模式
	    		oop.add(queue);
//		    		System.out.print("频繁保序模式："+pat);
//					System.out.print("，支持度为："+zlen);
//					System.out.println();
				frequent_num++;
				fre_num++;
			}
		}
		
    	if (lab == 1) {
    		for (sorted_queue qu : oop) {
				if (pat.equals(qu.can)) {
					qu.neg_sup = rsup;
				}
			}
		}
    	
    	return gen_op;
	}
	
	public float cal_rate(List<ZIndex> z3,int lab) {
		float rsup = 0;
    	float sup_number = 0;
    	for (int sid = 0; sid < sequence_num[lab]; sid++) {
    		float den = 0;
    		float current_len = z3.get(sid).current_len;
    		float support = z3.get(sid).count;
    		if (current_len > 0 && support > 0) {
				den = support / current_len;
				if (den > density) {
					sup_number++;
				}
			}
    	}
    	rsup = sup_number / sequence_num[lab];
		
        return rsup;
	}

	public void jugde_csp(){
		sorted_queue tmp_pat = new sorted_queue();
		float pos_sup,neg_sup;
		for(int i=0; i < oop.size(); i++){
			// 正类支持率
			pos_sup = oop.get(i).pos_sup; 
			neg_sup = oop.get(i).neg_sup;
			
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
				tmp_pat.can = "";
				tmp_pat.pos_sup = 0;
			}
			
			float CR = pos_sup - neg_sup;
			if (CR > 0) {
				fre_cop_num++;
				sorted_queue current_pat = new sorted_queue();
				current_pat.CR = CR;
				if ((current_pat.CR > tmp_pat.CR) || (top_ps.size() < tpk)) {
					current_pat.can = oop.get(i).can;
					current_pat.CR = CR;
					current_pat.pos_sup = pos_sup;
					top_ps.offer(current_pat); 
					if (top_ps.size() > tpk) {
						top_ps.remove(tmp_pat);
					}
				}
			}
		}
		oop.clear();
	}

	public void find(){
		
		// 计算正、负类中候选模式得位置、支持率和对比率 ，并记录结果，找到频繁保序模式 
		List<String> resultPat = calculatePos();
		// 只要正类中有频繁保序模式，就计算负类
		len = 2;
		calculateNeg(resultPat);
		
		// 判断是否为对比保序模式
		jugde_csp();
		
	}

	public void read_file(String filePath){
		List<Integer> pos_len = new ArrayList<>();
		
		List<Integer> neg_len =  new ArrayList<>();
		
		// 正类数据
		List<seqdb> pos = new ArrayList<>();
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
//				String[] valueStr = buffer.trim().split(",");
//				String[] valueStr = buffer.trim().split("	");
				String[] valueStr = buffer.trim().split("  ");
				
				float[] inS = new float[valueStr.length - 1];
				List<Float> sTemp = new ArrayList<>();
				
				float first = Float.parseFloat(valueStr[0]);
				for (int j = 1; j < (valueStr.length); j++) {
					inS[j-1] = Float.parseFloat(valueStr[j]);
				}
				
				// 数据提取极值点，压缩数据
				sTemp = extraction(inS);
				
				// 数据集中第一个元素为标签元素，通过1或2，0或1，-1和1来区分
				if (first == 1) {
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
    
    public void runAlgorithm(String filePath, float density2, int tpk2){
		density = density2;
		tpk = tpk2;
		long begintime = System.currentTimeMillis();
		read_file(filePath);
		
		find();
		
		int pos_fre_cop_num = fre_cop_num;
		int pos_frequent_num = frequent_num;
		int pos_cd_num = candiNum;
		
		len = 2; // 用来表示每轮候选模式长度
		fre_cop_num = 0; // 总的频繁对比保序模式数量
		frequent_num = 0;  //总的频繁保序模式数量
		fre_num = 0;
		candiNum = 0;//候选模式数量
		oop = new ArrayList<>(); // 用来存放本轮生成的保序模式，每轮比较完之后就会清空
		
		read_file_reverse();
		
		find();
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
		System.out.println("The number of candidate patterns: "+(pos_cd_num+candiNum));
	}

    
}
