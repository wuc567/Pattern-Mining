#include <map>
#include <set>
#include <vector>
#include <string>
#include <iostream>
#include <stdlib.h>
#include <windows.h>
#include <fstream>
#include <stack>
#include <math.h>
using namespace std;
#define N 20000  //The length of sequence
#define K 6000
#define M 1000

/*
char s[10]="hilkmftwv";
char mw[15]="rcqgpsynadeuox";
char sm[19]="hilkmftwvrcqgpsyn";
char m[20]="rcqgpsyn";

  char s[10]="HhIiJj";
char mw[25]="AaBbCcDdEeFfGg";
char sm[25]="EeFfGgHhIiJj";
char m[25]="EeFfGg";
*/



 char s[10]="HhIiJj";
char mw[25]="AaBbCcDdEeFfGg";
char sm[25]="EeFfGgHhIiJj";
char m[25]="EeFfGg";
struct seqdb                 
{
	int id;                  // sequence id
	char S[N];              // sequence
} sDB[K]; 

int mingap,maxgap;
char S[N];  //sequence
double minsup;
int NumbS;
vector <string> *freArr = new vector <string>[M];  //store frequent patterns
int frenum=0;
int compnum=0;

int belong(char c,char p[])
{
	int flag=0;
	for(int i=0;i<strlen(p);i++)
	{
		if(c==p[i])
		{
			flag=1;
			break;
		}
	}
	return flag;

}

void min_freItem()
{
	 map <string, int > counter;
	 string mine;
	 int sumlen=0;
	 for(int t = 0; t < NumbS; t++)
	 {
		strcpy(S,sDB[t].S);
		sumlen +=strlen(S);
		for(int i=0;i<strlen(S);i++)
		{
			if (belong(S[i],sm))
			{
				mine=S[i];
				counter[mine]++;
			}			
		}	 
	 }
	 for (map <string,int >::iterator the_iterator = counter.begin (); the_iterator!= counter.end (); )
	 {
		 if ((the_iterator->second+0.0)/sumlen < minsup)
		 {
			map <string, int >::iterator tmp = the_iterator;
			++tmp;
			counter.erase (the_iterator);
			the_iterator = tmp;
		 } 
		 else
		 {
			 freArr[0].push_back(the_iterator->first);  //add to freArr[0]
			 ++the_iterator;
			 //cout << the_iterator->first <<endl;
		 }
	}
}




//paraOffset 模式的位置   
int computeWildcardPatternOccurrences(string paraPattern,int paraStart,int paraOffset){
		if(paraOffset == paraPattern.size()) return 1;
		
		int tempCounter = 0;
		int len = strlen(S);
		
		for(int i = mingap + 1 ; i <= maxgap + 1; i ++){ 
			
			if(paraStart + i >= len) break;
					
			if(paraPattern[paraOffset] == S[paraStart + i]){
				tempCounter += computeWildcardPatternOccurrences(paraPattern,paraStart + i ,paraOffset + 1);
			}
			if(belong(S[paraStart + i],s))break; 		
		}
		
		return tempCounter;
	}
	
double computeWildcardPatternFrequency(string paraPattern){
		int tempCounter = 0;
		double sumFrequency=0;
		for(int t = 0; t < NumbS; t++)
			{
				if(strlen(sDB[t].S) > 0)
				{
					strcpy(S,sDB[t].S);
			
					int len = strlen(S);


					int limit = len - paraPattern.size() ; //use this will fater a little
				
					for(int i = 0 ; i < limit  ; i ++){
						
						if(paraPattern[0] != S[i]) continue;
						string tempPattern=paraPattern.substr(1,paraPattern.size()-1);
									
						tempCounter += computeWildcardPatternOccurrences(tempPattern,i,0);
					}
					//very imprtant !!!! this will influce the proc a lot , original version !
					//double tempFrequency = (tempCounter + 0.0) / (numInstances() * Math.pow(wildcardGapUpperBound - wildcardGapLowerBound + 1,paraPattern.length - 1));				
					double tempFrequency = (tempCounter + 0.0) / (len * pow(maxgap - mingap + 1,paraPattern.size() - 1));
					sumFrequency+=tempFrequency;
				}
			//cout<< sumFrequency/NumbS <<endl;
		}	
		return sumFrequency/NumbS;


	}


int gen_candidate()
{
	int level=1;
//	int tempLength=0;
	bool flag=false;
	while(freArr[level-1].size()>0){
		int size = freArr[level-1].size();
		for(int i=0;i<size;i++)
		{
			for(int j=0;j<freArr[0].size();j++)
			{
				string R="";
				string cand = freArr[level-1][i]+freArr[0][j];  //suffix pattern of freArr[level-1][i]
			//	cout<< cand <<endl;
				R=cand.substr(1,level);
				flag=false;
				for(int q = 0; q  < size;q ++){
					if(freArr[level-1][q]==R ){
						flag = true;
						break;
					}
				}
				double tempFrequency = 0.0;
			//计算模式的支持率
				if(flag)
				{
					tempFrequency = computeWildcardPatternFrequency(cand);	
					compnum++;
				}
						if(tempFrequency >= minsup){
							freArr[level].push_back(cand);
						//	cout<< " 支持度阈值:"<<minsup<<endl;
						//	cout<< cand <<endl;
						//	cout<< tempFrequency <<endl;
							//tempLength ++;		
				}
			}	
		}
		level++;
	}
	return level;
}

void read_file()
{
	fstream file;
	char filename[256];
	cout <<"---------------------------------------------------------------------------\nPlease input file name:";
	//cin>>filename;
	//cout <<filename<<endl;
	string buff;
	file.open("F:/NTP-Miner/NTP-DataSet/SP.txt",ios::in);   //open sequence file
//	file.open("C:/Users/Ripple/Desktop/SDB.txt",ios::in);   //open sequence file

	int i=0;
	while(getline(file, buff))
	{
		strcpy(sDB[i].S, buff.c_str());
		i++;
	}
	NumbS=i;
	// print sequence database
	//cout << "sDB and min_sup are as follows : " << endl;
	for(int t = 0; t < NumbS; t++)
	{
		sDB[t].id = t + 1;
		//cout << "\t(" << sDB[t].id << ",(" << sDB[t].S << "))" << endl;
	}
}

void main()
{


	read_file();
	cout<<"input the mingap,maxgap:"<<endl;
	cin>>mingap>>maxgap;
	//mingap=0,maxgap=3;
	cout<<"input the minsup:"<<endl;
	cin>>minsup;
	//minsup=900;
	DWORD begintime=GetTickCount();
	

	min_freItem();
	int level=gen_candidate();	
	DWORD endtime=GetTickCount();
	for(int i = 0; i<level; i++)
	{
		for(int j = 0; j<freArr[i].size();j++)
		{
			cout<<freArr[i][j]<<"   ";
			frenum++;
		}
		cout<<endl;
	}
	cout<<"The number of frequent patterns:"<<frenum<<endl;
	cout <<"The time-consuming:"<<endtime-begintime<<"ms. \n";
	cout <<"The number of calculation:"<<compnum<<" \n";
	
}
