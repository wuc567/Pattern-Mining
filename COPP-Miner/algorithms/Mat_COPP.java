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
public class Mat_COPP {

	final int N = 600; // The length of sequence
	final int M = 30; // The length of pattern
	// 大数据集
//	final int K = 7000; // The sequence number of sequence database
	// 小数据集
	int K = 1000; // The sequence number of sequence database
	
	final int TXT_SIZE = 50000;
	final int PATTERN_SIZE = 10000;
	final int MAX_LINE = 60000;
	final int MAXSIZE = 50000;
	
	final int Max = 256;
	int MAX = 50000;
	
	public int minsup = 0;
	public int tpk;
	public float density; // 密度约束
	
	public int fre_cop_num = 0; // 总的频繁对比保序模式数量
	int fre_num = 0;
	int candidate_num = 0;
	int cd_num = 2;
	public int[][] F2 = new int[2][2]; // 2-长度频繁模式集

	public int[][] L2 = new int[2][2]; // 2-长度频繁模式集

	int frequent_num = 0;
	float[] text = new float[TXT_SIZE]; // 时间序列数据s
//	public int[] pattern = new int[PATTERN_SIZE]; // 模式p
	int[] sorted_pat = new int[PATTERN_SIZE]; // 排序后的模式p
	int[] index = new int[PATTERN_SIZE]; // 辅助索引 index[i]
	int[] trans_text = new int[TXT_SIZE - 2];
	int[] trans_pattern = new int[PATTERN_SIZE - 2];
	int pattern_num = 0;
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
		// 中数据集
//		float[] S = new float[3000];
		// 小数据集，设置太大会报内存溢出的错误
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

	/**
	 * 1、根据过滤验证策略计算模式指出 1、将模式p中的数字按升序排列，将模式p中第i位的数字的位置记为index[i]。
	 * 2、根据规则将模式p和时间序列s，按照二进制表示 3、根据过滤和验证策略去进行剪枝
	 * @param text   序列s的数据
	 * @param pattern 模式p
	 * @param current_len 序列长度
	 * @param pattern_size 模式长度
	 * @param sid
	 * @param lab
	 * @return 候选模式的出现数
	 */
	public int support_FVP(float text[], int pattern[], float current_len, int pattern_size, int lab, int sid) {
		int i;
		for (i = 0; i < pattern_size; i++) {
			sorted_pat[i] = pattern[i];
		}
		// 模式p升序排序
		sort(sorted_pat, pattern_size);
		// 生成辅助索引表
		gen_index(index, pattern, pattern_size);
		// 将时间序列数据按照规则转换成二进制表示
		transform_text(text, current_len - 1);
		// 将模式按照规则转换成二进制表示
		transform_pattern(pattern, pattern_size - 1);
		if (pattern_size == 2) {
			BNDM(trans_text, trans_pattern, current_len - 1, pattern_size - 1, lab, sid);
		} else {
			SBNDM(trans_text, trans_pattern, current_len - 1, pattern_size - 1, lab, sid);
		}
		return pattern_num;
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
		for (int sid = 0; sid < sequence_num[lab]; sid++) {

			float current_len = sDB[lab][sid].seqlen;
			support_sid = support_FVP(sDB[lab][sid].S, pattern2, current_len, len, lab, sid);

			sDB[lab][sid].support = support_sid;
			support_full += support_sid;
		}
		if (lab == 0 && support_full >= minsup) {
			
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
		// 长度为2的候选模式
		int[][] C2 = { { 1, 2 }, { 2, 1 } };
		// 计算候选模式支持度并输出频繁模式
		for (int j = 0; j < 2; j++) {
			support_full = 0;
			for (int h = 0; h < 2; h++) {
				pattern[h] = C2[j][h];
			}

			// 计算正类支持率
			temp = jugde_oop(pattern, 2, 0);
			pos_sup = temp[0];
			pos_rate = temp[1];

			// 正类中频繁出现的趋势，在负类中不频繁的趋势
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

	int[] sort(int[] sorted_pattern, int length) {
		for (int i = 0; i < length - 1; i++) {
			int min = i;
			for (int j = i + 1; j < length; j++) {
				if (sorted_pattern[j] < sorted_pattern[min]) {
					min = j;
				}
			}
			if (sorted_pattern[i] > sorted_pattern[min]) {
				int temp = sorted_pattern[i];
				sorted_pattern[i] = sorted_pattern[min];
				sorted_pattern[min] = temp;
			}
		}
		int[] result = new int[length];
		try {
			System.arraycopy(sorted_pattern, 0, result, 0, sorted_pattern.length);
		} catch (ArrayIndexOutOfBoundsException e) {

		}
		return result;
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
		int slen = 0, y = 0;
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
				// 前后缀相对顺序相同
				if (Arrays.equals(relative_order(Q), relative_order(R))) {
					// 最前最后位置相等，拼接成两个模式
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
								// fre[i][t]+=1; //中间位置增长
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

	/**
	 * OPP-Miner算法，生成频繁模式集F
	 * @param pat 候选模式
	 */
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

	/**
	 * bi = 1, 如果sj < sj+1 (1 ≤ j ≤ n − 1) 
	 * bi = 0, 如果 sj > sj+1 (1 ≤ j ≤ n − 1)
	 * @param trans_text 
	 * @param txt 时间序列数据
	 * @param g 序列长度
	 * @return 
	 */
	void transform_text(float txt[], float g) {
		int loop = 0;
		for (loop = 0; loop < g; loop++) {
			if (txt[loop] < txt[loop + 1]) {
				trans_text[loop] = 1;
			} else {
				trans_text[loop] = 0;
			}
		}
	}
	

	/**
	 * ai = 1, 如果pi < pi+1 (1 ≤ i ≤ n − 1) 
	 * ai = 0, 如果 pi > pi+1 (1 ≤ i ≤ n − 1)
	 * @param pat 模式P
	 * @param pattern 
	 * @param pat_length 模式长度
	 */
	void transform_pattern(int pat[], int pat_length) {
		int loop = 0;
		for (loop = 0; loop < pat_length; loop++) {
			if (pat[loop] < pat[loop + 1]) {
				trans_pattern[loop] = 1;
			} else {
				trans_pattern[loop] = 0;
			}
		}
	}

	/**
	 * 
	 * @param txt 时间序列s
	 * @param pat 模式p
	 * @param index 
	 * @param g 序列长度
	 * @param pat_length 模式长度
	 * @param sid
	 * @param lab
	 */
	void BNDM(int txt[], int pat[], float g, int pat_length, int lab, int sid) {
		pattern_num = 0;
		int flag = 0, f = 0;
		int B[] = new int[Max];
		int pos = 0;
		// <<左移运算符，num << 1,相当于num乘以2; a|=b的意思就是把a和b按位或然后赋值给a
		for (int i = 0; i < pat_length; i++)
			B[pat[i]] |= 1 << (pat_length - i - 1);
		while (pos <= g - pat_length) {
			int j = pat_length - 1;
			int last = pat_length;
			int D = Integer.parseUnsignedInt("4294967295");
			while (D != 0) {
				if (pos + j < 0) {
					D = D & B[txt[0]];
				} else {
					D = D & B[txt[pos + j]];
				}
				if ((D & (1 << (pat_length - 1))) != 0) {
					if (j > 0)
						last = j;
					else {
						int len_cand = pos + pat_length;
						int x, k = 0;
						int cand = pos;
						for (x = pos; x < len_cand; x++) {
							if (sDB[lab][sid].S[cand - 1 + index[k]] >= sDB[lab][sid].S[cand - 1 + index[k + 1]]) {
								f = 0;
								break;
							} else {
								f = 1;
							}
							k++;
						}
						if (f > 0) {
							flag = 1;
							pattern_num++;
						}
					}
				}
				j--;
				D = D << 1;

			}
			pos += last;
		}
	}

	void SBNDM(int txt[], int pat[], float g, int pat_length, int lab, int sid) {
		int pos, D, j, q;
		pattern_num = 0;
		int flag = 0, f = 0;
		int B[] = new int[Max];
		for (j = 0; j < pat_length; j++) {
			B[pat[j]] = B[pat[j]] | (1 << (pat_length - j - 1));
		}
		pos = pat_length - 1;
		while (pos <= g - 1) {
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
				} while (D != 0);

				if (j == pos) {
					int len_cand = j + pat_length;
					int x = 0;
					int k = 0;
					int cand = j;
					for (x = j; x < len_cand; x++) {
						if (sDB[lab][sid].S[cand - 1 + index[k]] >= sDB[lab][sid].S[cand - 1 + index[k + 1]]) {
							f = 0;
							break;
						} else {
							f = 1;
						}
						k++;
					}
					if (f > 0) {
						flag = 1;
						pattern_num++;
					}
					pos = pos + 1;
				}
			}
			pos = pos + pat_length - 1;
		}
	}

	/**
	 * 生成辅助索引表 例如：p=[3,4,5,1,2] 排序后sorted=[1,2,3,4,5] 辅助索引index=[4,5,1,2,3]
	 * @param pattern 
	 * @param pattern 
	 * @param pattern2 
	 * @param arr
	 * @param length
	 * @return 
	 */
	void gen_index(int index[], int[] pattern, int length) {
		int i, j;
		for (i = 0; i < length; i++) {
			for (j = 0; j < length; j++) {
				if (sorted_pat[i] == pattern[j]) {
					index[i] = j + 1;
				}
			}
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
		// 保留原来数据
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
		
		// 将现有数据清空，然后将0 1 的数据交换
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
//        list.add(in[1]);
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
		
		// 先计算正类中的保序模式，并存储正类对比率大于给定阈值的模式
		generate_candF2();
		int [][] C = generate_fre(F2);
		Cancalute(C);
		
		int pos_fre_cop_num = fre_cop_num;
		int pos_frequent_num = frequent_num;
		int pos_cd_num = cd_num;
		
		System.out.println("正向候选模式："+pos_cd_num);
		
		pattern_num = 0;
		fre_cop_num = 0; // 总的频繁对比保序模式数量
		fre_num = 0;
		frequent_num = 0;
		candidate_num = 0;
		cd_num = 2;
		F2 = new int[2][2]; // 2-长度频繁模式集
		L2 = new int[2][2]; // 2-长度频繁模式集
		
		read_file_reverse();
		
		// 先计算正类中的保序模式，并存储正类对比率大于给定阈值的模式
		generate_candF2();
		int [][] CRe = generate_fre(F2);
		Cancalute(CRe);
		
		System.out.println();
		disp();
		long endtime = System.currentTimeMillis();
		MemoryLogger.getInstance().checkMemory();
		/** memory of last execution */
		double maxMemory = MemoryLogger.getInstance().getMaxMemory();
		System.out.println("Maximum memory usage : " + maxMemory + " mb.");
		System.out.println("The time-consuming: " + (endtime - begintime) + "ms.");
		System.out.println("The number of frequent cop patterns: "+(pos_fre_cop_num+fre_cop_num));
		System.out.println("The number of frequent op patterns: "+(pos_frequent_num+frequent_num));
		System.out.println("The number of candidate patterns: "+(pos_cd_num+cd_num));
	}

}
