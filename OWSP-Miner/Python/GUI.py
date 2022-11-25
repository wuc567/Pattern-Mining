import tkinter as tk
from tkinter import *
import tkinter.filedialog
from tkinter.filedialog import *
import time
from tkinter import scrolledtext
from tkinter import ttk
from Miner import *
from BFOOF import *
from DFROF import *
from BFROF import *
root = tk.Tk()
root.title('OWSP')

root.geometry('800x600')
label= tk.Label(root, text='OWSP',font=('Arial',30),width=0,
                height=0)
label.place(x=350,y=0)
m = 220
#选择算法
L00 = tk.Label(root, text='选择算法',width=0,height=0,font=('Arial',12)).place(x=m,y=80+10)
L0 = tk.StringVar()
L0Chosen = ttk.Combobox(root,width=18,textvariable=L0,state='readonly')
L0Chosen['values']=('Miner','BF-ROF','DF-ROF','BF-OOF')
L0Chosen.place(x=m+80,y=80+10)


#上传
L1 = tk.Label(root, text='上传序列',width=0,height=0,font=('Arial',12)).place(x=m,y=80+40)
enter1 = tk.Entry(root, width=20)
enter1.place(x=m+80,y=80+40)
def sc():
    filename = askopenfilename(initialdir='f:', filetypes=[('All Files', '*')])
    f = open(filename,'r')
    f.close()
    enter1.delete(0,END)
    enter1.insert(0,filename)
button2 = tk.Button(root, text='上传文本路径',width=12,height=0,command=sc)
button2.place(x=m+250,y=75+40)

#保存
L2 = tk.Label(root, text='保存文本',width=0,height=0,font=('Arial',12)).place(x=m,y=110+40)
enter2 = tk.Entry(root, width=20)
enter2.place(x=m+80,y=110+40)
def bc():
    filename = askopenfilename(initialdir='f:', filetypes=[('All Files', '*')])
    enter2.delete(0,END)
    enter2.insert(0, filename)
button3 = tk.Button(root, text='保存文本路径',width=12,height=1,command=bc)
button3.place(x=m+250,y=105+40)

#阈值
L3 = tk.Label(root, text='最小阈值',width=0,height=0,font=('Arial',12)).place(x=m,y=140+40)
enter3 = tk.Entry(root, width=20)
enter3.place(x=m+80,y=140+40)


L4 = tk.Label(root, text='弱间隙字符',width=0,height=0,font=('Arial',12)).place(x=m-10,y=170+40)
enter4 = tk.Entry(root, width=20)
enter4.place(x=m+80,y=170+40)

L5 = scrolledtext.ScrolledText(root,width=50,height=20)
L5.place(x=200,y=250)

def start():
    L5.delete('1.0', 'end')
    patten = L0.get()
    h = enter4.get()
    yyz = enter3.get()
    ss = open(enter1.get(),'r')
    s = ss.read()
    old = time.time()
    if patten == 'Miner':
        result1, result2,mm = mainn(s,h,int(yyz))
        L5.insert(END, 'Miner' + '\n')
    elif patten == 'BF-OOF':
        result1, result2,mm = mainnnnn(s, h, int(yyz))
        L5.insert(END, 'OOF' + '\n')
    elif patten == 'DF-ROF':
        result1, result2,mm = mainnn(s, h, int(yyz))
        L5.insert(END, 'Df' + '\n')
    elif patten == 'BF-ROF':
        result1, result2,mm= mainnnn(s, h, int(yyz))
        L5.insert(END, 'Bf' + '\n')
    now = time.time()
    t = open(enter2.get(),'w')
    m = 0

    for i in range(len(result1)):
        t.write('计算模型长度：'+str(len(result1[i][0]))+'   '+str(len(result1[i]))+'\n')
        L5.insert(END, '计算模型长度：'+str(len(result1[i][0]))+'\n')
        m = m+len(result1[i])
        for j in range(len(result1[i])):
            t.write('计算模型  '+str(result1[i][j])+':'+str(result2[i][j])+'、')
            L5.insert(END,result1[i][j])
            if j != len(result1[i])-1:
                L5.insert(END,'、')
        t.write('\n')
        L5.insert(END, '\n')
    if patten == 'Miner' or patten == 'DF-ROF' or patten == 'BF-ROF' or patten == 'BF-OOF':
        t.write('\n'+'候选集：'+str(mm))
        L5.insert(END,'\n'+'候选集总数：'+str(mm))
    t.close()


button4 = tk.Button(root, text='开始',width=12,height=1,command=start)
button4.place(x=m+250,y=165+40)


root.mainloop()