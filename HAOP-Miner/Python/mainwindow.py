import json
import time
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from haop_bf import haop_bf
from haop_df import haop_df

from pyparsing import col

from haop_miner import haop_miner
# from haop_nogap import haop_nogap
# from haop_pf import haop_pf
from sow_h import sow_h

HAOP_BF = 'HAOP-BF'
HAOP_DF = 'HAOP-DF'
HAOP_MINER = 'HAOP-Miner'
HAOP_NOGAP = 'HAOP-Nogap'
HAOP_PF = 'HAOP-PF'
SOW_H = 'SOW-H'

class TextFrame(ttk.Frame):
    def __init__(self, master : Tk, **kw):
        super().__init__(master, **kw)
        # wrap='none'|'word'|'char'
        self.text = Text(self)
        ys = ttk.Scrollbar(self, orient = 'vertical', command = self.text.yview)
        self.text['yscrollcommand'] = ys.set
        self.text.grid(row=0, column=0, sticky=NSEW)
        ys.grid(row=0, column=1, sticky=NS)

        for child in self.winfo_children():
            child.grid_configure(padx=3, pady=3)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def set(self, text : str):
        self.text.insert('end', text)


class TkMainwindow(ttk.Frame):
    def __init__(self, master : Tk, **kw):
        super().__init__(master, **kw)

        self.toolbar = ttk.Frame(self, padding='3 3 3 3')
        self.mainframe = ttk.Frame(self, padding='3 3 3 3')
        self.statusbar = ttk.Frame(self, padding='3 3 3 0')

        self.toolbar.grid(column=0, row=0, sticky=NSEW)
        self.mainframe.grid(column=0, row=1, sticky=NSEW)
        self.statusbar.grid(column=0, row=2, sticky=NSEW)
        self.grid(column=0, row=0, sticky=NSEW)

        self.master.option_add('*tearOff', FALSE)
        # Create Menubar
        win = self.winfo_toplevel()
        self.menubar = Menu(win)
        win['menu'] = self.menubar

        self.statusmsg = StringVar()
        self.statusLabel = Label(self.statusbar, textvariable=self.statusmsg)
        self.statusLabel.grid(column=0, row=0, sticky=SW)

        self.toolbar.rowconfigure(0, weight=1)
        self.statusbar.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
    
    def showmessage(self, msg : str):
        self.statusmsg.set(msg)


class Mainwindow(TkMainwindow):
    def __init__(self, master : Tk, **kw):
        super().__init__(master, **kw)

        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
        except:
            config = {'infile': '', 'outfile': '', 'method': HAOP_BF, 'minunity': 3600}

        print(config)

        ttk.Label(self.mainframe, text='算法选择: ').grid(row=0, column=0, sticky=E)
        self.methods = (
            HAOP_BF,
            HAOP_DF,
            HAOP_MINER,
            HAOP_NOGAP,
            HAOP_PF,
            SOW_H
        )

        self.methodVar = StringVar(value=config['method'])
        cbMethod = ttk.Combobox(self.mainframe, textvariable=self.methodVar, values=self.methods)
        cbMethod.grid(row=0, column=1, sticky=EW)
        # readonly
        cbMethod.state(["readonly"])
        # self.methodVar.set(HAOP_BF)
        cbMethod.bind('<<ComboboxSelected>>', lambda e : self.showmessage(self.methodVar.get()))

        ttk.Label(self.mainframe, text='输入文件: ').grid(row=1, column=0, sticky=E)
        self.infileVar = StringVar(value=config['infile'])
        infileEntry = ttk.Entry(self.mainframe, textvariable=self.infileVar)
        infileEntry.grid(row=1, column=1, sticky=EW)
        # infileEntry.state['readonly']
        ttk.Button(self.mainframe, text='...', command=self.select_infile).grid(row=1, column=2, sticky=EW)

        ttk.Label(self.mainframe, text='输出文件: ').grid(row=2, column=0, sticky=E)
        self.outfileVar = StringVar(value=config['outfile'])
        outfileEntry = ttk.Entry(self.mainframe, textvariable=self.outfileVar)
        outfileEntry.grid(row=2, column=1, sticky=EW)
        ttk.Button(self.mainframe, text='...', command=self.select_outfile).grid(row=2, column=2, sticky=EW)

        ttk.Label(self.mainframe, text='minunity: ').grid(row=3, column=0, sticky=E)
        self.minunityVar = DoubleVar(value=config['minunity'])
        ttk.Entry(self.mainframe, textvariable=self.minunityVar).grid(row=3, column=1, sticky=EW)

        self.text = TextFrame(self.mainframe)
        self.text.grid(row=4, column=0, columnspan=3, sticky=NSEW)

        buttonbox = ttk.Frame(self.mainframe)
        ttk.Button(buttonbox, text='运行', command=self.run).grid(row=0, column=0, sticky=E)
        ttk.Button(buttonbox, text='关闭', command=self.close).grid(row=0, column=1,sticky=E)
        buttonbox.grid(row=5, column=0, columnspan=3, sticky=NSEW)
        buttonbox.columnconfigure(0, weight=1)
        buttonbox.rowconfigure(0, weight=1)

        for child in self.mainframe.winfo_children():
            child.grid_configure(padx=3, pady=3)

        self.mainframe.columnconfigure(1, weight=1)
        self.mainframe.rowconfigure(4, weight=1)
        

        master.title('Mainwindow')
        self.master.geometry('600x400')
        self.showmessage('Ready.')

    def select_infile(self):
        self.infileVar.set(filedialog.askopenfilename())

    def select_outfile(self):
        self.outfileVar.set(filedialog.asksaveasfilename())

    def close(self):
        config = {
            'infile': self.infileVar.get(), 
            'outfile': self.outfileVar.get(), 
            'method': self.methodVar.get(),
            'minunity': self.minunityVar.get()
        }
        with open('config.json', 'w') as f:
            json.dump(config, f)
        self.master.quit()

    def run(self):
        msg = f'------------{time.asctime()}------------\n'
        method = self.methodVar.get()
        filename = self.infileVar.get()
        minunity = self.minunityVar.get()
        
        if method == HAOP_BF:
            f_level, freArr, elapsed_time, compnum = haop_bf(filename, minunity)   
        elif method == HAOP_DF:
            frequent, elapsed_time, compnum = haop_df(filename, minunity)
        elif method == HAOP_MINER:
            f_level, freArr, elapsed_time, compnum = haop_miner(filename, minunity)
        elif method == HAOP_NOGAP:
            f_level, freArr, elapsed_time, compnum = haop_nogap(filename, minunity)
        elif method == HAOP_PF:
            f_level, freArr, elapsed_time, compnum = haop_pf(filename, minunity)
        elif method == SOW_H:
            f_level, freArr, elapsed_time, compnum = sow_h(filename, minunity)

        if method in (HAOP_BF, HAOP_MINER, HAOP_NOGAP, HAOP_PF, SOW_H):
            frenum = 0
            with open(self.outfileVar.get(), 'w') as f:
                for i in range(f_level):
                    text = ', '.join(freArr[i]) + '\n'
                    f.write(text)
                    frenum += len(freArr[i])     
                    msg += text
        else:
            frenum = len(frequent)
            with open(self.outfileVar.get(), 'w') as f:
                text = ', '.join(frequent.keys())
                f.write(text)
                msg += text

        msg += f'算法: {method}.\n'
        msg += f'输入文件: {self.infileVar.get()}\n'
        msg += f'输出文件: {self.outfileVar.get()}\n'
        msg += f'耗时: {elapsed_time} ms.\n'
        msg += f'总数为: {frenum}.\n'
        msg += f'候选总数为: {compnum}.\n'
           
        self.text.set(msg)



if __name__ == '__main__':
    root = Tk()
    Mainwindow(root)
    root.mainloop()