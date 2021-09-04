import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import tkinter.scrolledtext
from tkinter import ttk
from logsfile import Logger
import os
import re
import threading
import subprocess
import plotly.graph_objs as go
from global_var import Gui_Info
from global_var import About_Info
from parse_file import Parse_Json


class Main_GUI():
    def __init__(self, _log, _root):
        self.log = _log
        self.root = _root
        self.log.info("Starting to create UI for the tool.")

        self.init_var()
        self.create_root_frame()
        self.create_menu()
        self.create_main_frame()
        self.init_task()

    def init_var(self):
        self.json_dict = {}
        self.draw_dict = {}
        self.gl_bg = "#e7eaed"
        Gui_Info["cwd"] = os.getcwd()
        Gui_Info["json_file"] = os.path.join(Gui_Info["cwd"], Gui_Info["json_file"])
        self.min_pattern = re.compile(r"interval_min:(.*) ms,")  # interval_min:0 ms,
        self.max_pattern = re.compile(r"inverval_max:(.*) ms,")  # inverval_max:11 ms,
        self.mean_pattern = re.compile(r"inverval_mean:(.*) ms!")  # inverval_mean:8 ms!

        # ****************  set gui theme style  *********************
        ttk.Style().configure("TButton", font=("Times New Roman", 12, "bold"))
        ttk.Style().map("TButton", foreground=[('active', 'blue')], background=[('pressed', '!disabled', '#3d4350')])

        ttk.Style().configure("TNotebook.Tab", font=("Times New Roman", 11, "bold"), padding=[5, 5])
        ttk.Style().map("TNotebook.Tab", foreground=[('focus', 'blue')])

    def create_main_frame(self):
        self.tab = ttk.Notebook(self.root)
        self.main_f = tk.Frame(self.tab, bg=self.gl_bg)
        self.sub1_f = tk.Frame(self.tab, bg=self.gl_bg)
        self.tab.add(self.main_f, text="Main")
        self.tab.add(self.sub1_f, text="User Guide")
        self.tab.pack(expand=True, fill="both")
        self.tab.select(self.main_f)

        label_font = ("Times New Roman", 12, "bold")
        cfg_label = tk.Label(self.main_f, text="Cfg File:", anchor="w", bg=self.gl_bg, font=label_font)
        cfg_label.place(x=10, y=10, width=70, height=35)

        self.cfg_entry = tk.Entry(self.main_f, bg="#e4f9e0", font=("Courier New", 11))
        self.cfg_entry.place(x=80, y=10, width=300, height=35)
        self.cfg_entry.insert(0, Gui_Info["json_file"])
        self.cfg_entry["state"] = "disable"

        cfg_bt = ttk.Button(self.main_f, text="Load", style="my.TButton", command=self.call_cfg_load_bt)
        cfg_bt.place(x=390, y=10, width=70, height=35)

        log_label = tk.Label(self.main_f, text="Log File:", anchor="w", bg=self.gl_bg, font=label_font)
        log_label.place(x=10, y=55, width=70, height=35)

        self.log_entry = tk.Entry(self.main_f, font=("Courier New", 11))
        self.log_entry.place(x=80, y=55, width=300, height=35)

        log_bt = ttk.Button(self.main_f, text="Select", style="my.TButton", command=self.call_log_select_bt)
        log_bt.place(x=390, y=55, width=70, height=35)

        sep_ = ttk.Separator(self.main_f, orient="horizontal")
        sep_.place(x=10, y=110, width=580, height=2, bordermode="inside")

        psize_label = tk.Label(self.main_f, text="period time:", anchor="w", bg=self.gl_bg, font=label_font)
        psize_label.place(x=10, y=130, width=90, height=30)

        self.psize_entry = tk.Entry(self.main_f, font=("Courier New", 11))
        self.psize_entry.place(x=100, y=130, width=70, height=30)
        self.psize_entry.insert(0, 8)

        bsize_label = tk.Label(self.main_f, text="buffer time:", anchor="w", bg=self.gl_bg, font=label_font)
        bsize_label.place(x=220, y=130, width=90, height=30)

        self.bsize_entry = tk.Entry(self.main_f, font=("Courier New", 11))
        self.bsize_entry.place(x=310, y=130, width=70, height=30)
        self.bsize_entry.insert(0, 24)

        Filter_label = tk.Label(self.main_f, text="Test Point:", anchor="w", bg=self.gl_bg, font=label_font)
        Filter_label.place(x=10, y=180, width=90, height=35)

        self.filter_combobox = ttk.Combobox(self.main_f)
        self.filter_combobox.place(x=100, y=180, width=280, height=35)

        self.log_bt = ttk.Button(self.main_f, text="Draw", style="my.TButton", command=self.call_draw_select_bt)
        self.log_bt.place(x=390, y=180, width=70, height=35)

    def init_task(self):
        json_ops = Parse_Json(Gui_Info["json_file"])
        ret = json_ops.file_read()
        if not ret[0].value == 0:
            self.log.error('Error type: %s' % ret[0].name)
            tkinter.messagebox.showerror("Error", "Error type: %s" % ret[0].name)
            return False
        self.json_dict = ret[1]

        json_list = []
        [json_list.append(item) for item in self.json_dict if self.json_dict[item]]
        if not json_list:
            self.log.warning('No available test point in the cfg file, Please check the cfg file')
            tkinter.messagebox.showwarning(
                "Warning", "No available test point in the cfg file\n\nPlease check the cfg file")
            return False
        self.filter_combobox["values"] = json_list
        self.filter_combobox.current(0)

    def call_cfg_load_bt(self):
        file_type = [('json files', '.json'), ('all files', '.*')]
        json_file = tkinter.filedialog.askopenfilename(initialdir=Gui_Info["cwd"],
                                                       title="Please select a cfg file:",
                                                       filetypes=file_type)
        if not json_file:
            self.log.info("No cfg file be selected")
            return False
        json_file = os.path.normpath(json_file)
        self.log.info("Cfg file: "+json_file)

        json_ops = Parse_Json(json_file)
        ret = json_ops.file_read()
        if not ret[0].value == 0:
            self.log.error('Error type: %s' % ret[0].name)
            tkinter.messagebox.showerror("Error", "Error type: %s" % ret[0].name)
            return False

        self.cfg_entry["state"] = "normal"
        self.cfg_entry.delete(0, "end")
        self.cfg_entry.insert(0, json_file)
        self.cfg_entry["state"] = "disable"

        self.json_dict = ret[1]
        Gui_Info["json_file"] = json_file

        json_list = []
        [json_list.append(item) for item in self.json_dict if self.json_dict[item]]
        if not json_list:
            self.log.warning('No available test point in the cfg file, Please check the cfg file')
            tkinter.messagebox.showwarning(
                "Warning", "No available test point in the cfg file\n\nPlease check the cfg file")
            return False
        self.filter_combobox["values"] = json_list
        self.filter_combobox.current(0)

    def call_log_select_bt(self):
        file_type = [('log files', '.txt'), ('all files', '.*')]
        log_file = tkinter.filedialog.askopenfilename(initialdir="",
                                                      title="Please select a log file:",
                                                      filetypes=file_type)
        if not log_file:
            self.log.info("No log file be selected")
            return False

        log_file = os.path.normpath(log_file)
        self.log_entry.delete(0, "end")
        self.log_entry.insert(0, log_file)
        self.log.info("Log file: "+log_file)

    def call_draw_select_bt(self):
        tmp_flag = True
        tmp_str = ""

        log_file = self.log_entry.get().strip()
        test_point = self.filter_combobox.get().strip()
        period_time = self.psize_entry.get().strip()
        buffer_time = self.bsize_entry.get().strip()
        if not os.path.exists(log_file):
            tmp_flag = False
            tmp_str = "No log file be selected"
        elif not test_point:
            tmp_flag = False
            tmp_str = "No test point be selected"
        elif not period_time:
            tmp_flag = False
            tmp_str = "No period time be found"
        elif not buffer_time:
            tmp_flag = False
            tmp_str = "No buffer time be found"
        if not tmp_flag:
            tkinter.messagebox.showerror("Error", tmp_str)
            return False

        self.draw_dict.clear()
        self.draw_dict["log_file"] = log_file
        self.draw_dict["test_point"] = test_point
        try:
            self.draw_dict["period_time"] = int(period_time)
            self.draw_dict["buffer_time"] = int(buffer_time)
        except Exception:
            tkinter.messagebox.showerror("Error", "Check the type of period_time or buffer_time")
            return False

        draw_thread = threading.Thread(target=self.drawing_thread, daemon=True, name="Draw Thread")
        draw_thread.start()

    def drawing_thread(self):
        all_log_list = []
        target_log_list = []
        try:
            with open(self.draw_dict["log_file"], mode='r', encoding="utf-8") as fp:
                all_log_list = fp.readlines()
        except Exception:
            tkinter.messagebox.showerror("Error", "Error of opening log file")
            return False

        [target_log_list.append(item) for item in all_log_list if self.draw_dict["test_point"]
         in item and "inverval_max" in item]
        # print(target_log_list)
        actual_time_list = [int(self.max_pattern.findall(item)[0]) for item in target_log_list]
        # print(actual_time_list)
        data_len = len(target_log_list)
        x_list = [i for i in range(data_len)]
        period_time_list = [8 for item in target_log_list]
        buffer_time_list = [24 for item in target_log_list]

        trace_period = dict(x=x_list,
                            y=period_time_list,
                            mode='lines+markers',
                            name='period_time',
                            line=dict(color="green"))
        trace_buffer = dict(x=x_list,
                            y=buffer_time_list,
                            mode='lines+markers',
                            name='buffer_time',
                            line=dict(color="red"))
        trace_actual = dict(x=x_list,
                            y=actual_time_list,
                            mode='lines+markers',
                            name='actual_time',
                            line=dict(color="blue"))
        _layout = dict(title=self.draw_dict["test_point"], xaxis=dict(title='s'), yaxis=dict(title='ms'))

        _data = [trace_period, trace_actual, trace_buffer]
        fig = go.Figure(data=_data, layout=_layout)
        fig.show()

    def create_root_frame(self):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = int((sw - Gui_Info["normal_size"][0]) / 2)
        y = int((sh - Gui_Info["normal_size"][1]-60) / 2)

        self.root.title(Gui_Info["proj"] + Gui_Info["version"])
        # self.root.iconbitmap(os.path.join(Gui_Info["cwd"], Gui_Info["shortcut"]))

        self.root.geometry("%dx%d+%d+%d" % (Gui_Info["normal_size"][0], Gui_Info["normal_size"][1], x, y))
        self.root.minsize(Gui_Info["normal_size"][0], Gui_Info["normal_size"][1])
        self.root.maxsize(sw, sh)
        self.root.resizable(0, 0)

    def create_menu(self):
        menu_dict = {"File": ["Open Cfg", "Exit"],
                     "Logging": ["Open DebugLog"],
                     "Help": ["About"]
                     }

        menu_font = ("Times New Roman", 11)
        self.menubar = tk.Menu(self.root)
        file_menu = tk.Menu(self.menubar, font=menu_font, activeborderwidth=2, tearoff=False)
        file_menu.add_command(label=menu_dict["File"][0], command=self.menu_file_open)
        file_menu.add_separator()
        file_menu.add_command(label=menu_dict["File"][1], command=self.menu_file_exit)
        self.menubar.add_cascade(label="File", menu=file_menu)

        logging_menu = tk.Menu(self.menubar, font=menu_font, activeborderwidth=2, tearoff=False)
        logging_menu.add_command(label=menu_dict["Logging"][0], command=self.menu_logging_debug)
        self.menubar.add_cascade(label="Logging", menu=logging_menu)
        # self.menubar.add_command(label = "Logging", command = self.__menu_log)

        help_menu = tk.Menu(self.menubar, font=menu_font, activeborderwidth=2, tearoff=False)
        help_menu.add_command(label=menu_dict["Help"][0], command=self.menu_help_about)
        self.menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=self.menubar)

    # Menu File
    def menu_file_load(self):
        self.log.info("Starting to load json file.")
        self.call_load_test_file()

    def menu_file_open(self):
        self.log.info("Starting to open json file.")
        subprocess.Popen("notepad %s" % Gui_Info["json_file"], shell=True)
        # os.system("notepad %s" % Gui_Info["json_file"])

    def menu_file_exit(self):
        self.log.info("GUI Tool is Closing")
        self.root.destroy()

    # Menu Logging
    def menu_logging_debug(self):
        os.makedirs(Gui_Info["debug_dir"], mode=0o777, exist_ok=True)
        subprocess.Popen("start %s" % Gui_Info["debug_dir"], shell=True)
        # os.system("start %s" % Gui_Info["debug_dir"])

    def menu_help_about(self):
        tkinter.messagebox.showinfo("About", About_Info)


if __name__ == "__main__":
    log = Logger()
    root = tk.Tk()
    Main_GUI(log, root)
    root.mainloop()
