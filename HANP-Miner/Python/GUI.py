import tkinter
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from HANP_Miner import HANP_Miner
# from HANP_df import HANP_df
from HANP_nogap import HANP_nogap
from HANP_bf import HANP_bf
from NOSEP import NOSEP

filename = ''
outputfilename = 'result_file.txt'

def select_file():
    global filename
    filename = askopenfilename(title="DataSet Source", initialdir="D", filetypes=[("text", ".txt")])
    show["text"] = filename.split('\\')[-1].split('/')[-1]

def select_outputfile():
    global outputfilename
    outputfilename = askopenfilename(title="Result Output", initialdir="D", filetypes=[("text", ".txt")])
    show_o["text"] = outputfilename.split('\\')[-1].split('/')[-1]

flag = 0

def select_algorithm():
    global flag
    s = v.get()
    if s == 'HANP-Miner':
        flag = 1
        v2.set(2500)
        v3.set(0)
        v4.set(3)
        print('Function: ' + s)
    elif s == 'HANP-df':
        flag = 2
        v2.set(2500)
        v3.set(0)
        v4.set(3)
        print('Function: ' + s)
    elif s == 'HANP-bf':
        flag = 3
        v2.set(2500)
        v3.set(0)
        v4.set(3)
        print('Function: ' + s)
    elif s == 'HANP-nogap':
        flag = 4
        v2.set(2500)
        v3.set(0)
        v4.set(0)
        print('Function: ' + s)
    elif s == 'NOSEP':
        flag = 5
        v2.set(900)
        v3.set(0)
        v4.set(3)
        print('Function: ' + s)


def get_Threshold(event):
    pass


def run_procedure(event):
    global flag
    text01.delete(0.0, tkinter.END)
    if flag == 0:
        messagebox.showinfo("Topic", "You haven't chosen the algorithm. Please choose the algorithm before running.")
        return
    elif show['text'] == '' or show['text'] == 'file':
        messagebox.showinfo("Topic", "You haven't chosen the data source. Please choose the data source before running.")
        return
    elif show_o['text'] == '' or show_o['text'] == 'file':
        messagebox.showinfo("Topic", "You haven't chosen the output file. Please choose the output file before running.")
        return
    try:
        if flag == 1:
            text01.insert('1.0','Runing...\n')
            HANP_Miner(filename, v3.get(), v4.get(), v2.get(), outputfilename)
        elif flag == 2:
            text01.insert('1.0', 'Runing...\n')
            HANP_df(filename, v3.get(), v4.get(), v2.get(), outputfilename)
        elif flag == 3:
            text01.insert('1.0', 'Runing...\n')
            HANP_bf(filename, v3.get(), v4.get(), v2.get(), outputfilename)
        elif flag == 4:
            text01.insert('1.0', 'Runing...\n')
            HANP_nogap(filename, v2.get(), outputfilename)
        elif flag == 5:
            text01.insert('1.0', 'Runing...\n')
            NOSEP(filename, v3.get(), v4.get(), v2.get(), outputfilename)
    except Exception as e:
        messagebox.showinfo("Exception or Error during Running", e.args)
    else:
        with open(outputfilename, 'r') as file:
            result = file.read()
            text01.insert('2.0',result)
    flag = 0


if __name__ == '__main__':
    root = Tk()
    root.geometry("700x650")
    root.resizable(False, False)
    root.title("HANP-Miner")
    label00 = Label(root, text="HANP-Miner", height=2, width=20, fg="blue", bg="green",
                    font=("Times New Roman", 18, "bold", "italic"))
    label00.grid(row=0, column=1)

    label01 = Label(root, text="Algorithm", font=("Times New Roman", 10))
    label01.grid(row=1, column=0, ipadx=0)
    label01["width"] = 22

    label02 = Label(root, text="DataSet Source", font=("Times New Roman", 10))
    label02.grid(row=2, column=0, ipadx=0)
    label02["width"] = 22

    label03 = Label(root, text="Min.support", font=("Times New Roman", 10))
    label03.grid(row=3, column=0, ipadx=0)
    label03["width"] = 22

    label04 = Label(root, text="Min.Gap", font=("Times New Roman", 10))
    label04.grid(row=4, column=0, ipadx=0)
    label04["width"] = 22

    label05 = Label(root, text="Max.Gap", font=("Times New Roman", 10))
    label05.grid(row=5, column=0, ipadx=0)
    label05["width"] = 22

    v = StringVar(root)
    v.set("HANP-Miner")
    om = OptionMenu(root, v, "HANP-Miner", "HANP-nogap", "HANP-bf", "HANP-df", "NOSEP")
    om["width"] = 25
    om.grid(row=1, column=1)

    btn01 = Button(root, text="Choose", command=select_algorithm, width=5)
    btn01.grid(row=1, column=2)

    btn02 = Button(root, text="Select", command=select_file, width=5)
    btn02.grid(row=2, column=2)

    show = Label(root, width=40, height=1, relief="raised")
    show.grid(row=2, column=1)
    show["text"] = "file"

    v2 = IntVar()
    v2.set(2500)
    entry02 = Entry(textvariable=v2, width=40)
    entry02.grid(row=3, column=1)
    entry02.bind("<Return>", get_Threshold)

    v3 = IntVar()
    v3.set(0)
    entry03 = Entry(textvariable=v3, width=40)
    entry03.grid(row=4, column=1)

    v4 = IntVar()
    v4.set(3)
    entry04 = Entry(textvariable=v4, width=40)
    entry04.grid(row=5, column=1)

    btn03 = Button(root, text="Update")
    btn03.grid(row=3, column=2)
    btn03["width"] = 5
    btn03.bind("<Button-1>", get_Threshold)

    btn03 = Button(root, text="Update")
    btn03.grid(row=4, column=2)
    btn03["width"] = 5
    btn03.bind("<Button-1>", get_Threshold)

    btn03 = Button(root, text="Update")
    btn03.grid(row=5, column=2)
    btn03["width"] = 5
    btn03.bind("<Button-1>", get_Threshold)

    label08 = Label(root, text="Result Output", font=("Times New Roman", 10))
    label08.grid(row=6, column=0, ipadx=0)
    label08["width"] = 22

    show_o = Label(root, width=40, height=1, relief="raised")
    show_o.grid(row=6, column=1)
    show_o["text"] = 'result_file.txt'

    btn06 = Button(root, text="Select", command=select_outputfile, width=5)
    btn06.grid(row=6, column=2)

    btn04 = Button(root, text="Run", relief="groove")
    btn04.grid(row=7, column=1)
    btn04["width"] = 20
    btn04.bind("<Button-1>", run_procedure)

    text01 = Text(root, width=50, height=20, relief="raised", font=("Times New Roman", 12, "bold", "italic"))
    text01.grid(row=8, column=1)

    root.mainloop()
