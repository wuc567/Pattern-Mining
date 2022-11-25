# include <afxwin.h>
# include <iostream>
# include <string>
# include <vector>
# include <fstream>
# include <map>
using namespace std;
#define K 1000    //The sequence number of sequence database
#define M 100   //The length of pattern
#define N 20000  //The length of sequence
struct seqdb                 
{
	int id;                  // sequence id
	char S[N];              // sequence
} sDB[K];                 // sequence database
  
int nn;
char eSet[60] ;             //store all frequent items
int minsup;             
//int minlen,maxlen;   //length constraint
int mingap,maxgap; //gap constraint
int NumbS;
struct Pos
{
	vector <int> pos;    //position
};
struct ISupSet            // support set od pattern
{
	int id;               // id
	vector <Pos> poset;     // position set
};

//vector <ISupSet> I, Iseq, IPLus, IPLUS;   

struct Freq_ptn            // frequent pattern
{
	int length;
	vector <char> ptn;
};
vector <Freq_ptn> Fre;    // frequent pattern set

struct All_Fre    //frequent pattern with length
{
	int length;           
	vector <Freq_ptn> Fre;    
};
vector <All_Fre> AllFre;    // all frequent pattern set
struct sub_ptn_struct   //a[0,3]c => start[min,max]end
{
	char start,end;		
	int min,max;
};
vector <sub_ptn_struct> sub_ptn;
int ptn_len; 
char S[N];
int compnum = 0;

void min_freItem()
{
	map <string, int > counter; 
	string mine;
	for(int t = 0; t < NumbS; t++)
	{
		strcpy(S,sDB[t].S);
		for(int i=0;i<strlen(S);i++)
		{
			if ((S[i]>='a'&&S[i]<='z')||(S[i]>='A'&&S[i]<='Z'))
			{
				mine=S[i];
				counter[mine]++;
			}	
		}
	}
	nn = 0;
	for (map <string,int >::iterator the_iterator = counter.begin (); the_iterator!= counter.end (); ++the_iterator)
	{
		eSet[nn++] = the_iterator->first.at(0);
	}
}

// print P
void disp_P(vector <char> p)    
{
	int plen, m;
	cout << " = " ;
	plen = p.size(); 
	for(m = 0; m < plen; m++)
		cout << p[m];
	cout << endl;
}

//print sub_ptn[ptn_len]
void disp_pattern(vector <sub_ptn_struct> sub_ptn) 
{
	ptn_len = sub_ptn.size();
	for(int i = 0; i < ptn_len; i++)
	    cout << sub_ptn[i].start << '\t' << sub_ptn[i].min << '\t' << sub_ptn[i].max << '\t' <<sub_ptn[i].end << endl;
}

//compute support set I(P[0]) in sDB
int SizeOneSup(seqdb sDB[M], vector <char> &P, vector <ISupSet> &I)
{
	int i, l, len, plen; 
	plen = P.size();
	int support = 0;

	if(plen == 1)
	{
		for(i = 0; i < NumbS; i++)
		{
			for(l = 0; l < strlen(sDB[i].S); l++)   
			{
				I.resize(i + 1);
				if(sDB[i].S[l] == P[plen - 1])
				{			
					len = I[i].poset.size();
					I[i].poset.resize(len + 1);
					I[i].poset[len].pos.resize(1);
					I[i].id = sDB[i].id;				
					I[i].poset[len].pos[0] = l;
					support++;
				}
			}
		}
	}
	return support;
}

//print Fre
void disp_Fre(vector <Freq_ptn> Fre)   
{
	int fsum, flen, i = 0, j;
	cout << "Fre = {  ";
	fsum = Fre.size();
	if(fsum >1)
	{
		for(i = 0; i < fsum - 1; i++)
		{	
			flen = Fre[i].ptn.size();
			for(j = 0; j < flen; j++)
			{
				cout << Fre[i].ptn[j];
			}
			cout << "  ,  ";
		}
	}
	if(i == fsum - 1)
	{
		flen = Fre[i].ptn.size();
		for(j = 0; j < flen; j++)
		{
			cout << Fre[i].ptn[j];
		}
		cout << "  }";
	}
	cout << endl << endl;
}

//Find the maximum of two numbers
int imax(int x, int y)    
{
	int z;
	if(x > y)	z = x;
	else		z = y;
	return (z);
}

//compute mininum loaction that satisfy gap constraint
int next(seqdb &seq, char p, int max, int a, int b)
{
	int i = imax(max+1, a);
	bool flag = false;
	for(; i <= b; i++)
	{
		if(seq.S[i] == p)
		{
			flag = true;
			break;
		}			
	}
	if(flag == true)
		return i;
	else
		return -1;
}

int INSgrow_Gap(seqdb sDB[M], vector <sub_ptn_struct> &sub_ptn, vector <ISupSet> &I, vector <ISupSet> &IPLUS)
{
	compnum++;
	//IPLUS.resize(0);
	int support=0;
	int i;
	ptn_len = sub_ptn.size();
	char p = sub_ptn[ptn_len - 1].end;
	IPLUS.resize(I.size());
	IPLUS = I;
	for(i = 0; i < NumbS; i++)
	{
		if(strlen(sDB[i].S) > 0)
		{	
			int ptn_len;
			ptn_len = sub_ptn.size();
			for(int j = 0;j<IPLUS[i].poset.size();j++)
			{
				Pos apos = IPLUS[i].poset[j];
				int len = apos.pos.size();
				if(len == sub_ptn.size())
				{
					int max = apos.pos[len - 1]; // max: last value of position of previous one
					int a = 0, b = 0, l = -1;
					a = max + sub_ptn[ptn_len - 1].min +1;
					b = max + sub_ptn[ptn_len - 1].max +1;
					int lens=strlen(sDB[i].S);
					b=(b>(lens-1))?(lens-1):b;
					if(a > strlen(sDB[i].S))
						continue;
					if(max <= b)
					{
						l = next(sDB[i], p, max, a, b);   // l: mininum loaction that satisfy gap constraint
					}
					if(l != -1 && l <= b)
					{
					//	if( (l - IPLUS[i].poset[j].pos[0] + 1) < minlen || (l - IPLUS[i].poset[j].pos[0] + 1) > maxlen )  //whether satisfy length constraint
					//	{
					//		continue;
					//	} 
						for( int m = j; m >= 0 ; m--)
						{
							if(IPLUS[i].poset[m].pos[len] == l) // overlap, exit
							{
								m++;
								break;   
							}
							if(m == 0)  //match, exit
							{
								int Iqlen = IPLUS[i].poset[j].pos.size();    // the number of positions
								IPLUS[i].poset[j].pos.resize(Iqlen + 1);
								IPLUS[i].poset[j].pos[Iqlen] = l;          
								support++;
								break;
							}
						}
					}
				}
			}
		}
	}
	return support;
}


void mineFre(int support,seqdb sDB[M], vector <char> &P, vector <ISupSet> &I)
{
	vector <char> Q;
	if(support >= minsup)     // P is frequent
	{
		int fsum, plen;
		fsum = Fre.size();
		Fre.resize(fsum + 1);
		plen = P.size();
		Fre[fsum].length = plen;
		Fre[fsum].ptn.resize(plen);
		Fre[fsum].ptn = P;         // add P into frequent set
		int t;
		Q.resize(plen);
		for(t = 0; t < plen; t++)
		{
			Q[t] = P[t];
		}
		for(int e = 0; e < nn; e++) 
		{
			int qlen = P.size()+1;
			Q.resize(qlen);
			Q[qlen-1] = eSet[e];
			sub_ptn.resize(qlen-1);
			int k = 0;
			for(; k < qlen-1; k++)
			{
				sub_ptn[k].start = Q[k];
				sub_ptn[k].min = mingap;
				sub_ptn[k].max = maxgap;
				sub_ptn[k].end = Q[k + 1];
			}
		//	compnum++;
			vector <ISupSet> IPLUS;
			int support=INSgrow_Gap(sDB, sub_ptn, I, IPLUS);   // compute IPLUS
			mineFre(support, sDB, Q, IPLUS);
		}
		
	}
}


void transform(vector <Freq_ptn> &Fre)
{
	//AllFre.resize(0);
	int length, AFlen, Fsum, Flen, i, j;
	Fsum = Fre.size();
	if(Fsum > 1)            
	{
		length = Fre[0].length;
		for(i = 1; i < Fsum; i++)
		{
			if(Fre[i].length > length)
				length = Fre[i].length;
		}
	}
	AllFre.resize(length);        
	for(i = 0; i < length; i++)          
	{
		AllFre[i].length = i + 1;
		AllFre[i].Fre.resize(0);
	}
	
	for(i = 0; i < length; i++)
	{
		for(j = 0; j < Fsum; j++)
		{
			if(Fre[j].length == AllFre[i].length)
			{
				AFlen = AllFre[i].Fre.size();
				AllFre[i].Fre.resize(AFlen + 1);
				Flen = Fre[j].ptn.size();
				AllFre[i].Fre[AFlen].ptn.resize(Flen);
				AllFre[i].Fre[AFlen].ptn = Fre[j].ptn;
			}
		}
	}
}


void disp_AllFre(vector <All_Fre> &AllFre)      // print all frequent pattern
{
	cout << "All Frequent Patterns are as follows: " << endl;
	int total = 0;
	int t, AFsum, length;
	AFsum = AllFre.size();
	for(t = 0; t < AFsum; t++)
	{
		length = AllFre[t].length;
		cout << "The length is " << length << endl;

		int fsum, flen, i, j;
		fsum = AllFre[t].Fre.size();
		flen = AllFre[t].Fre[0].ptn.size();
		if(flen == 1)
		{
			for(i = 0; i < fsum; i++)
			{	
		
				cout << AllFre[t].Fre[i].ptn[0] << "\t";
			}
			total += fsum;

		}
		else if(flen > 1)
		{
			for(i = 0; i < fsum; i++)
			{
				for(j = 0; j < flen; j++)
				{
					cout << AllFre[t].Fre[i].ptn[j];
				}
				cout << "\t";
			}
			total += fsum;

		}
		cout << endl;
		cout << "The Number of Length " << length << " is " << fsum << endl; 
	}
	cout << "The Total of AllFre is " << total << endl; 
}

void read_file()
{
	fstream file;
	//string buff;
	//file.open("SDB6.txt",ios::in);   //open sequence file
	char filename[256];
	cout <<"\nPlease input file name:";
	//cin>>filename;
	//cout <<filename<<endl;
	string buff;
	//file.open(filename,ios::in);   //open sequence file
	file.open("SDB5.txt",ios::in);   //open sequence file

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
	//	cout << "\t(" << sDB[t].id << ",(" << sDB[t].S << "))" << endl;
	}
}
void main()
{
	read_file();
	//cout<<"input the minlen,maxlen:"<<endl;
	//cin>>minlen>>maxlen;
	//cout<<"input the mingap,maxgap:"<<endl;
	//cin>>mingap>>maxgap;
	mingap = 0;
	maxgap = 30;
	//cout<<"input the minsup:"<<endl;
	//cin>>minsup;
	minsup = 5000;
	DWORD starttime = GetTickCount();
	min_freItem();   //cout frequent items and store item[]
    Fre.resize(0);      // in
	int e;
	for(e = 0; e < nn; e++)    // each item
	{
		vector <char> P;
		vector <ISupSet> I;
		
		//P.resize(0);
		//int plen;
		//plen = P.size();
		P.resize(1);
		P[0] = eSet[e];     // p[0] = eSet[e]
		int support=SizeOneSup(sDB, P,I);  //  compute support set I(P[0]) in sDB
		mineFre(support, sDB, P, I);    // mining all frequent pattern
	}
	DWORD endtime = GetTickCount();
	disp_Fre(Fre);
	transform(Fre);
	disp_AllFre(AllFre);
	cout<<"The number of frequent patterns:"<<Fre.size()<<endl;
	cout<< "Time-consuming is : " << endtime-starttime << "ms." <<endl;
	cout<< "The number of calculation: " <<compnum<<endl;
}

