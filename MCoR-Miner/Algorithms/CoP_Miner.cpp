//���������ص���ƽ��Ч�ã�������ȡ�
#include <map>
#include <set>
#include <vector>
#include <string>
#include <iostream>
#include <stdlib.h>
#include <windows.h>
#include <fstream>
#include <stack>
#include <queue>
//#include<cmath>
using namespace std;
struct pattern
{
	string name;
	int support;
//	double utl;
};
vector <pattern > CoP;//�洢�����еĹ���ģʽ
vector <pattern > Max_CoP;//�洢�����е������ģʽ

stack <string > candidate;//�洢�����еĺ�ѡģʽ
vector <int > filter1;//���ù��ˣ�����Ϊ1��filter�����Ϊ0����ӦID��sequence�����˵���Ϊ1���м���
vector <int > filter;//���ù��ˣ����Ϊ0����ӦID��sequence�����˵���Ϊ1���м���

vector <string > SDB;

//map<char, double> utility;//ȷ��ÿ���ַ���Ч���ֵ�
struct sigma_pos
{
	char ch;
	vector <int>position;
	int fre;//��������ǣ��ж��Ƿ������չ��
};
//vector <sigma_pos> store;
#define Max_Pattern_Length 50

struct sigma_sdb
{
	int id;
	//ÿ���������Լ����е��ַ�����
	map<char, int> sigma;//ȷ��ÿ���ַ��洢��������ֵ�sigma['a']=1,sigma['c']=2,sigma['g']=3
	vector <sigma_pos> store;

};
vector <sigma_sdb> sdbstore;


void read_file()
{
	fstream file;
	char filename[256];
	cout << "---------------------------------------------------------------------------\nPlease input file name:";
	string buff;
	file.open("goods14.txt", ios::in);   //open sequence file
	int i = 0;
	while (getline(file, buff))
	{
		SDB.push_back (buff);
		i++;
		cout <<buff<<endl;
	}	
}

/*void initialutility()
{
	utility['a'] = 1;
	utility['g'] = 1;
	utility['c'] = 1;
	utility['t'] = 1;
	
	utility['a'] = 0.3;
	utility['g'] = 0.2;
	utility['c'] = 0.3;
	utility['t'] = 0.2;*/
	 /*utility['a']=1;
	 utility['b']=2;
	 utility['c']=0.3;
	 utility['d']=1;
	 utility['e']=3;
	 utility['f']=2;*/
	 /*utility['a']=0.2;
	 utility['c']=0.9;
	 utility['d']=0.4;
	 utility['e']=0.5;
	 utility['f']=0.5;
	 utility['g']=0.3;
	 utility['h']=0.8;
	 utility['i']=0.5;
	 utility['k']=0.5;
	 utility['l']=0.2;
	 utility['m']=0.8;
	 utility['n']=0.6;
	 utility['p']=0.6;
	 utility['q']=0.7;
	 utility['r']=0.6;
	 utility['s']=0.5;
	 utility['t']=0.5;
	 utility['v']=0.4;
	 utility['w']=0.8;
	 utility['y']=0.6;
}*/
void display_store(vector <sigma_pos> &store)
{
	int i,j;
	for (i=0;i<store.size ();i++)
	{
		cout <<store[i].ch <<":";
		for (j=0;j<store[i].position  .size ();j++)
		{
			cout <<store[i].position [j]<<"\t";		
		}
		cout <<endl;
	}
}
void scan_sequence(string sequence, vector <sigma_pos> &store, map<char, int> &sigma)//ȷ��ÿ���ַ��洢��������ֵ�sigma['a']=1,sigma['c']=2,sigma['g']=3
{//��ÿ�������е��ַ�����λ�ô洢�ˡ�
	int count=1, chno;//�ڼ����ַ�		
	for (int i=0;i<sequence.size ();i++)
	{
		if (sigma [sequence[i]]==0)//
		{//���ַ�
			sigma_pos current;
			sigma [sequence[i]]=count;
			count++;
			current.ch =sequence[i];
			current.position.push_back (i);
			store.push_back (current); 
		}
		else
		{//���ַ�
			chno=sigma [sequence[i]]-1;//��ȡ�����м����еڼ����ַ�
			store[chno].position .push_back (i);
		}
		//cout <<sequence[i]<< ":"<<sigma [sequence[i]]<<"\t"; //debug
	}
	//cout <<endl;
	//display_store(store);
}

struct item
{
	int ID;
	char ch;
	int frequence;
};
void display(vector <item> &itemset)
{
	int i;
	cout <<"itemset:\n";
	for (i=0; i<itemset.size ();i++)
	{
		cout <<"id:"<<itemset[i].ID <<"\t chare:"<<itemset[i].ch 
			<<"\t freq:"<<itemset[i].frequence  <<endl;
	}
}
void display (vector <char> &itemset,map<char, int> &allsig)
{
	int len=allsig.size ();
	int len1=itemset.size ();
	for (int i=0; i<len;i++)
		cout <<itemset[i]<<":\t"<<	allsig[itemset[i]]<<endl;
}
void scan_SDB(char first, vector <char> &allsigma, map<char, int> &frequence)
{
	int id;
	for (id=0;id<SDB.size ();id++)
	{	
		sigma_sdb tmp;
		tmp.id =id;
		//cout<<endl<<SDB[id]<<endl;
		//��ÿ�����н��д���tmp.sigma���ַ���
		scan_sequence(SDB[id], tmp.store, tmp.sigma);
		sdbstore.push_back (tmp);
	}
	//string sigma;//ÿ�����е��ַ���ƴ������
	vector <item> item_sequence;
	for (id=0;id<SDB.size ();id++)
	{
		int flag=0;
		for (int j=0;j<sdbstore[id].store.size ();j++)
		{
			//sigma+=sdbstore[id].store[j].ch;
			item tmp;
			tmp.ID = id;
			tmp.ch = sdbstore[id].store[j].ch;
			tmp.frequence = sdbstore[id].store[j].position .size ();
			if (tmp.ch ==first)
				flag=tmp.frequence;
			item_sequence.push_back (tmp);
		}
		filter1.push_back (flag);//flagҪô��0��Ҫô��first���е�Ƶ�ȣ�
	}
	//display (item_sequence);
	//cout<<sigma<<endl;
	//��������ַ��ĳ���Ƶ��
	for (int i=0;i<item_sequence.size ();i++)
	{
		char t=item_sequence[i].ch ;
		if (frequence [t]==0)
		{//���ַ�			
			frequence [t]=item_sequence[i].frequence ;
			allsigma.push_back (t);
		}
		else
			frequence [t]+=item_sequence[i].frequence ;
	}
	//display (allsigma,frequence);
}
int depthfirst_support(int node, int level, const string & cand, const  sigma_sdb &seq_store, 
					   int &mingap, int &maxgap, vector <int >& next, vector <int> &patternv, int *occurrence)
{	
	do
	{
		// find the first child of nd according to the gap;
		int childlevel=level;
		int val,child;
		do
		{
			char childch=cand[childlevel];//��õ�ǰģʽ��
			int childstore=patternv[childlevel];
			int childpos=next[childlevel];
			if (childpos==seq_store.store [childstore].position.size ())
				return -3;//�Ѿ�����������󣬱������������г����ˡ�
			next[childlevel]++;//������ǰ����
			child=seq_store.store [childstore].position [childpos];//Ѱ�ҵ�һ�����õĺ���
			val=child-node-1;
		} while (val<mingap);
		if (mingap<=val&&val<=maxgap)//�����϶Լ��
		{			
			//depthfirst_support(child, level+1, cand, seq_store, mingap, maxgap,  next, patternv);
			occurrence[level]=child;
			node=child;
			level=level+1;
		}
		else//�������Ҫ���л���
		{
			//��ǰ�����Ҫ�˻�
			next[childlevel]--;
			if (level-2<0)
				return -1;//��Ҫ����һ������
			int cparentpos=next[level-2]-1;
			int cparentstore=patternv[level-2];//??????????
			int cparent=seq_store.store [cparentstore].position [cparentpos];
			//depthfirst_support(cparent, level-1, cand, seq_store, mingap, maxgap,  next, patternv);
			node=cparent;
			level=level-1;
		}
	} while (level >0 &&level<cand.size ());
	if (level==cand.size ())
		return level;
	else if (level<=0)
		return -1;
}
int support_sequence (const string &cand,  sigma_sdb &seq_store, 
					  int &mingap, int &maxgap)
{//����һ��ģʽ��һ��������֧�ֶ�
	int sup=0;
	//cout <<seq_store.id <<endl;	
	vector <int> pv;//ģʽ��Ӧ�ڸ������д洢��λ�á�
	vector <int >next;	
	for (int i=0;i<cand.size ();i++)
	{
		next.push_back (0);//����ʼ��Ϊ0
	}
	for (i=0;i<cand.size ();i++)
	{
		int val=seq_store.sigma [cand[i]]-1;//sigma �ڴ洢��ʱ�����1�������Ҫ��ȥ1
		if (val==-1)//�������ַ����ڸ������г��֡�
			return 0;
		pv.push_back (val);
	}
	//vector <int > &rootposition=seq_store.store [pv[0]].position;//������
	int rootsize=seq_store.store [pv[0]].position.size ();
	vector <int> roots;
	for (i=0;i<rootsize;i++)
	{
		int root=seq_store.store [pv[0]].position[i];
		roots.push_back (root);
	}
	for (int len=0;len<rootsize;len++)//rootposition.size ()�洢�������ĸ���
	{//ÿ��������һ�ж�
		int root=roots[len];
		int level=1;
		int occurrence [Max_Pattern_Length]={0}; 
		occurrence[0]=root;
		next[level-1]=len+1;//nextָ����ÿ����һ����ʼ�ĵط������һ������occ��ÿ��next�ж�Ӧǰ������ݡ�
		int occ=depthfirst_support(root, level, cand, seq_store, mingap, maxgap, next, pv, occurrence);
		if (occ==cand.size ())
		{
			/*cout <<cand<<" an occurrence:";
			for (int i=0;i<cand.size ();i++)
			{//��ʾһ������
				int pos=occurrence[i];
				cout <<pos<<", ";
			}
			cout <<">>>"<<endl;*/
			sup++;
		}
		else if (occ==-3)
			break;
	}
	return sup;
}
int support_SDB_prefix (string &cand, int &mingap, int &maxgap)
{
	int sup=0;
	int len=cand.size ();
	if (len>=2)
	{
		for (int id=0;id<sdbstore.size ();id++)
		{
			int result;		
			result=support_sequence(cand, sdbstore[id], mingap, maxgap);
			filter.push_back (result);
			sup+=result;
			cout <<id<<":"<<result<<endl;
		}
	}
	else
	{//�����ַ�
		filter=filter1;
		for (int id=0;id<sdbstore.size ();id++)
			sup+=filter[id];
	}
			
	return sup;
}
int support_SDB (string &cand, int &mingap, int &maxgap)
{
	int sup=0;
	for (int id=0;id<sdbstore.size ();id++)
	{
		//if (filter[id]==1)//filter���˻���
		if (filter[id])//filter���˻���
			sup+=support_sequence(cand, sdbstore[id], mingap, maxgap);
	}
	return sup;
}

/*double maxutl(string &pattern)
{
	int len=pattern.size ();
	double maxvalue=utility[pattern[0]];
	for (int i=0;i<len;i++)
		if (maxvalue<utility[pattern[i]])
			maxvalue=utility[pattern[i]];
	return maxvalue;
}
double patternutl(string &pattern)
{
	int len=pattern.size ();
	double sumvalue=0;
	for (int i=0;i<len;i++)
		sumvalue+=utility[pattern[i]];
	return sumvalue;
}*/
void enumtree_allsigma(string prefix, vector <char> & allsigma, 
			  int &mingap, int &maxgap, double minconf)
{
	int candcount=0;
	do
	{
		int flag=0;
		for (int i=0;i<allsigma.size();i++)
		{
			string cand=prefix+allsigma[i] ;
			int sup=support_SDB(cand,mingap, maxgap);
			cout <<cand<<":"<<sup<<endl;
			int patternlen=cand.size ();			
		}
		if (candidate.empty () && flag==0)
			break;//ջ�ǿյģ����ҵ�ǰģʽû�г�ģʽ���Խ�ջ��
		prefix=candidate.top ();
		candidate.pop ();
	}while (1); //while (!candidate.empty ());  ����д���ԣ�����prefixû�д���
	cout <<"candidate="<<candcount<<endl;
}
void enumtree_BETsigma(string prefix, vector <char> & freq_sigma,
			vector <string> &freq_2pt, map<string, int> & freq_2freq,
			int &mingap, int &maxgap, double min_sup)
{
	int candcount=0;
	string cur_pattern=prefix;
	int prefixlen=prefix.size ();			
	do
	{
		int flag=0;
		for (int i=0;i<freq_sigma.size();i++)
		{
			char item=freq_sigma[i];
			string cand;
			cand=cur_pattern+item ;
			int cur_len=cur_pattern.size ();
			if (prefixlen<cur_len)
			{//˵����2�㼰���Ϻ�ѡģʽ����Ҫ�ж��Ƿ������BET��ʽ��֦
				string last2;
				//β���������Ӵ���
				char t=cur_pattern[cur_len-1];
				last2=last2+t+item;
				//�ж�last2�Ƿ���2���ȵ�Ƶ��ģʽ�У�������ڣ�����м�֦
				if (freq_2freq[last2]==0)
					continue;
			}
			int sup=support_SDB(cand,mingap, maxgap);
			//cout <<cand<<":"<<sup<<endl;  //debug
			if (sup>=min_sup)
			{
				flag=1;
				pattern tmp;
				tmp.name =cand;
				tmp.support =sup;
				CoP.push_back (tmp);
				candidate.push (cand);
				candcount++;
			}
		}
		if (flag==0)
		{//ʵ��screening���ԣ�Ѱ�������
			//flagΪ0���������к�ѡģʽ�����ǹ���ģʽ�����cur_pattern�������ģʽ��
			pattern tmp;
			tmp.name =cur_pattern;
			tmp.support =1;
			Max_CoP.push_back (tmp);
		}
		if (candidate.empty () && flag==0)
			break;//ջ�ǿյģ����ҵ�ǰģʽû�г�ģʽ���Խ�ջ��
		cur_pattern=candidate.top ();
		candidate.pop ();
	}while (1); //while (!candidate.empty ());  ����д���ԣ�����prefixû�д���
	cout <<"candidate="<<candcount<<endl;
}


void displayCoP(vector <pattern > &Patterns)
{
	int len=Patterns.size ();
	for (int i=0;i<len;i++)
	{
		cout <<Patterns[i].name<<":  "<<Patterns[i].support<<endl;//": "<<hau[i].utl<<endl;
	}
	cout <<len<<endl<<endl<<endl;
}
void	discover_frequent_sigma(
		vector <char> &allsigma, map<char, int> &frequence, double &min_sup, 
		vector <char> &freq_sigma, map<char, int> &freq_frequence )
{
	for (int i=0;i<allsigma.size ();i++)
	{
		if (frequence[allsigma[i]]>=min_sup)
		{
			char t=allsigma[i];
			freq_sigma.push_back (t);
			freq_frequence[t]=frequence[allsigma[i]];
		}
	}
}

void discover_frequent_2pattern(
		vector <char> & freq_sigma, map<char, int> & freq_frequence, double & min_sup,
		vector <string> & freq_2pt, map<string, int> & freq_2freq,
		int &mingap, int &maxgap, string &prefix)
{
	//����2���ȵ�Ƶ��ģʽ
	int candcount=0;
	int len=prefix.size ();
	if (len==1)
	{//���ǰ׺�ǵ����ַ�����Ҫ��һ����
		for (int i=0;i<freq_sigma.size ();i++)
			for (int j=0;j<freq_sigma.size ();j++)
			{
				char ti=freq_sigma[i], tj=freq_sigma[j];
				string cand;
				cand=cand+ti+tj;
				//cout <<"2 length candidate:"<<cand<<endl;
				int sup=support_SDB(cand,mingap, maxgap);
				if (sup>=min_sup)
				{
					freq_2pt.push_back (cand);
					freq_2freq[cand]=sup;
					candcount++;
					//cout <<"2 length candidate:"<<cand<<endl;  //debug
				}
			}
	}
	else
	{
		for (int i=0;i<freq_sigma.size ();i++)
			for (int j=0;j<freq_sigma.size ();j++)
			{
				char ti=freq_sigma[i], tj=freq_sigma[j];
				string cand;
				cand=cand+ti+tj;
				int result=prefix.find (cand);
				//cout <<"2 length candidate:"<<cand<<endl;
				if (result==-1)
				{//��ǰ�������Ӵ�����prefix��������Ҫ���㣻
					int sup=support_SDB(cand,mingap, maxgap);
					if (sup>=min_sup)
					{
						freq_2pt.push_back (cand);
						freq_2freq[cand]=sup;
						candcount++;
						//cout <<"2 length candidate:"<<cand<<endl;
					}
				}
				else
				{//cand��prefix�������У�������㣬��Ϊ����Apriori
					//cout<<"prefix�������У�������㣬��Ϊ����Apriori\n";
					freq_2pt.push_back (cand);
					freq_2freq[cand]=min_sup+1;//
				}
			}
	}//cout <<"2 length candidate="<<candcount<<endl;
}
void main()
{
	vector <char> allsigma;
	map<char, int> frequence;
	vector <char> freq_sigma;
	map<char, int> freq_frequence;
	vector <string> freq_2pt;
	map<string, int> freq_2freq;
	int mingap,maxgap;
	double min_conf;
	double min_sup;
	//string seq="acceaabaaccccdcbcca";
	read_file();//���ļ�
	//initialutility();//Ч��ֵ
	string prefix;
	cout <<"Please input min gap and max gap:";
	cin>>mingap>>maxgap;
	cout <<"Please input min support:";
	//int min_sup;
	cin>>min_sup;
	cout <<"Please input prefix string:";
	cin>>prefix;
	DWORD begintime = GetTickCount();//��ʼʱ��
	//scan_SDB(prefix[0],allsigma, frequence);
	//prefix_support=support_SDB_prefix(prefix,mingap, maxgap);
	//cout <<"support:"<<prefix_support<<endl;
	//min_sup=prefix_support*min_conf;
	//Ѱ��Ƶ������
	discover_frequent_sigma(allsigma,
				frequence, min_sup, freq_sigma, freq_frequence );
	//display(freq_sigma, freq_frequence);
	//Ѱ��Ƶ��2����ģʽ
	discover_frequent_2pattern(freq_sigma, freq_frequence, min_sup,
				freq_2pt,freq_2freq,mingap, maxgap, prefix);
	//enumtree_allsigma(prefix, allsigma,mingap, maxgap, minconf);
	enumtree_BETsigma(prefix, freq_sigma,freq_2pt,freq_2freq,mingap, maxgap, min_sup);
	DWORD endtime = GetTickCount();//222222222222
	cout << "ʱ�䣺" << endtime - begintime << "ms. \n";
	cout << "ȫ������Ƶ��ģʽ \n";
	displayCoP(CoP);
	cout << "�����Ƶ��ģʽ \n";
	displayCoP(Max_CoP);

}