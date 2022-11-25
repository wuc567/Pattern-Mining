import re
import threading
from tkinter import *
from tkinter.filedialog import askopenfilename, askdirectory

import nosep_a
import ntp_Miner, ntp_bf, ntp_df, gsgrow_a


def select_input_file():
    global input_filename
    input_filename = askopenfilename(title="选择输入文件", initialdir="D", filetypes=[("文本文档", ".txt")])
    input_show["text"] = input_filename


def select_output_file():
    global output_filepath
    output_filepath = askdirectory(title="选择输出位置")
    output_show["text"] = output_filepath


def select_algorithm():
    text01.delete(1.0, END)
    s = v.get()
    text01.insert(END, "当前选择算法为：" + s + "\n")
    text01.insert(END, "参数解释：\n")
    text01.insert(END, "strong参数为强字符集，请输入您关心的字符，默认参数为蛋白质数据集参数。\n")
    text01.insert(END, "middle参数为中字符集，请输入您不确定是否关心的字符，默认参数为蛋白质数据集参数。\n")
    text01.insert(END, "week参数为弱字符集，请输入您不关心的字符，默认参数为蛋白质数据集参数。\n")
    text01.insert(END, "mingap参数为最小间隙，值越大挖掘出的模式字符间的间隙就越大。\n")
    text01.insert(END, "maxgap参数为最大间隙，请确保maxgap大于等于mingap。\n")
    text01.insert(END, "minsup参数为最小支持度，值越大挖掘出的模式就越少、越频繁。\n")


def run_procedure(event):
    text01.delete(1.0, END)
    if not check():
        return
    thread = threading.Thread(target=run)
    thread.start()
    # a(filename, s, m, w, min_gap, max_gap, min_sup).solve(text01)


def check():
    global input_filename, output_filepath
    s = entry03.get()
    m = entry04.get()
    w = entry05.get()
    min_gap = entry06.get()
    max_gap = entry07.get()
    min_sup = entry08.get()
    if input_filename == "":
        text01.insert(END, "请选择输入文件！\n")
        return False
    if output_filepath == "":
        text01.insert(END, "请选择输出文件位置！\n")
        return False
    if re.match("^.+$", s) is None:
        text01.insert(END, "请输入强字符集！\n")
        return False
    if re.match("^.+$", m) is None:
        text01.insert(END, "请输入中字符集！\n")
        return False
    if re.match("^.+$", w) is None:
        text01.insert(END, "请输入弱字符集！\n")
        return False
    if re.match("^\d+$", min_gap) is None:
        text01.insert(END, "最小间隙格式错误，请输入数字！\n")
        return False
    if re.match("^\d+$", max_gap) is None:
        text01.insert(END, "最大间隙格式错误，请输入数字！\n")
        return False
    if int(min_gap) > int(max_gap):
        text01.insert(END, "最大间隙应大于等于最小间隙，请检查后重新输入！\n")
        return False
    if re.match("^\d+$", min_sup) is None:
        text01.insert(END, "最小支持度格式错误，请输入数字！\n")
        return False
    return True


def run():
    s = entry03.get()
    m = entry04.get()
    w = entry05.get()
    min_gap = int(entry06.get())
    max_gap = int(entry07.get())
    min_sup = int(entry08.get())
    a = alg[v.get()]
    a(input_filename, output_filepath, s, m, w, min_gap, max_gap, min_sup).solve(text01)


input_filename = ""
output_filepath = ""
alg = {
    "NTP-Miner": ntp_Miner.NTP_Miner,
    "NTP-bf": ntp_bf.NTP_bf,
    "NTP-df": ntp_df.NTP_df,
    "GSgrow-a": gsgrow_a.GSgrow_a,
    "NOSEP-a": nosep_a.NOSEP_a
}

if __name__ == '__main__':
    root = Tk()
    root.iconbitmap
    root.geometry("500x600")
    root.resizable(False, False)
    root.title("无重叠三支序列模式挖掘工具")
    label00 = Label(root, text="NTP-Miner", height=2, width=30, fg="blue", bg="green",
                    font=("Times New Roman", 18, "bold", "italic"))
    label00.grid(row=0, column=0, columnspan=3)

    label01 = Label(root, text="Choose an algorithm", font=("Times New Roman", 10))
    label01.grid(row=1, column=0, ipadx=0)
    label01["width"] = 22

    label02 = Label(root, text="Choose input file", font=("Times New Roman", 10))
    label02.grid(row=2, column=0, ipadx=0)
    label02["width"] = 22

    label03 = Label(root, text="Choose output file path", font=("Times New Roman", 10))
    label03.grid(row=3, column=0, ipadx=0)
    label03["width"] = 22

    label04 = Label(root, text="strong", font=("Times New Roman", 10))
    label04.grid(row=4, column=0, ipadx=0)
    label04["width"] = 22

    label05 = Label(root, text="middle", font=("Times New Roman", 10))
    label05.grid(row=5, column=0, ipadx=0)
    label05["width"] = 22

    label06 = Label(root, text="week", font=("Times New Roman", 10))
    label06.grid(row=6, column=0, ipadx=0)
    label06["width"] = 22

    label07 = Label(root, text="min_gap", font=("Times New Roman", 10))
    label07.grid(row=7, column=0, ipadx=0)
    label07["width"] = 22

    label08 = Label(root, text="max_gap", font=("Times New Roman", 10))
    label08.grid(row=8, column=0, ipadx=0)
    label08["width"] = 22

    label09 = Label(root, text="min_sup", font=("Times New Roman", 10))
    label09.grid(row=9, column=0, ipadx=0)
    label09["width"] = 22

    v = StringVar(root)
    v.set("NTP-Miner")
    om = OptionMenu(root, v, "NTP-Miner", "NTP-bf", "NTP-df", "GSgrow-a", "NOSEP-a")
    om["width"] = 25
    om.grid(row=1, column=1)

    btn01 = Button(root, text="?", command=select_algorithm, width=5)
    btn01.grid(row=1, column=2, padx=4)

    btn02 = Button(root, text="...", command=select_input_file, width=5)
    btn02.grid(row=2, column=2, padx=4)

    btn03 = Button(root, text="...", command=select_output_file, width=5)
    btn03.grid(row=3, column=2, padx=4)

    input_show = Label(root, width=40, height=1, relief="raised")
    input_show.grid(row=2, column=1)
    input_show["text"] = "文件名"

    output_show = Label(root, width=40, height=1, relief="raised")
    output_show.grid(row=3, column=1)
    output_show["text"] = "输出文件位置"

    v3 = StringVar()
    v3.set("hilkmftwv")
    entry03 = Entry(textvariable=v3, width=40)
    entry03.grid(row=4, column=1)

    v4 = StringVar()
    v4.set("rcqgpsyn")
    entry04 = Entry(textvariable=v4, width=40)
    entry04.grid(row=5, column=1)

    v5 = StringVar()
    v5.set("adeuox")
    entry05 = Entry(textvariable=v5, width=40)
    entry05.grid(row=6, column=1)

    v6 = IntVar()
    v6.set(0)
    entry06 = Entry(textvariable=v6, width=40)
    entry06.grid(row=7, column=1)

    v7 = IntVar()
    v7.set(3)
    entry07 = Entry(textvariable=v7, width=40)
    entry07.grid(row=8, column=1)

    v8 = IntVar()
    v8.set(500)
    entry08 = Entry(textvariable=v8, width=40)
    entry08.grid(row=9, column=1)

    btn04 = Button(root, text="Run Algorithm", relief="groove")
    btn04.grid(row=10, column=0, columnspan=3, pady=6)
    btn04["width"] = 20
    btn04.bind("<Button-1>", run_procedure)

    text01 = Text(root, width=55, height=13, relief="raised", font=("Times New Roman", 12, "bold", "italic"))
    text01.grid(row=11, column=0, columnspan=3, padx=5, pady=5)
    root.mainloop()
