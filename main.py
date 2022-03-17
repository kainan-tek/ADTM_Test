# import ctypes
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
from tkinter import ttk
from logsfile import Logger
import os
import re
import threading
from plotly.offline import plot
import plotly.graph_objects as go
import global_var as gl


class Main_GUI():
    def __init__(self, _log, _root):
        self.log = _log
        self.root = _root
        self.log.info("Starting to create UI for the tool.")

        self.init_var()
        self.create_root_frame()
        self.create_menu()
        self.create_main_frame()

    def init_var(self):
        self.draw_dict = {}
        self.gl_bg = "#e7eaed"
        self.key_words = ["inverval_max", "interval_min", "inverval_mean"]
        # self.min_pattern = re.compile(r"interval_min:(\d+) ms")      # interval_min:0 ms
        # self.mean_pattern = re.compile(r"inverval_mean:(\d+) ms")    # inverval_mean:8 ms
        self.max_pattern = re.compile(r"inverval_max:(\d+) ms")        # inverval_max:11 ms
        self.alsanode_pattern = re.compile(r"alsa node\((.*)\) adtm")  # alsa node(pcmMicRefIn_c) adtm

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
        log_label = tk.Label(self.main_f, text="Log File:", anchor="w", bg=self.gl_bg, font=label_font)
        log_label.place(x=10, y=10, width=70, height=35)

        self.log_entry = tk.Entry(self.main_f, font=("Courier New", 11))
        self.log_entry.place(x=80, y=10, width=320, height=35)
        self.log_entry.configure(state="readonly")

        log_bt = ttk.Button(self.main_f, text="Select", style="my.TButton", command=self.call_log_select_bt)
        log_bt.place(x=410, y=10, width=70, height=35)

        sep1_ = ttk.Separator(self.main_f, orient="horizontal")
        sep1_.place(x=10, y=65, width=480, height=3, bordermode="inside")

        psize_label = tk.Label(self.main_f, text="period time:", anchor="w", bg=self.gl_bg, font=label_font)
        psize_label.place(x=10, y=85, width=90, height=30)

        self.psize_entry = tk.Entry(self.main_f, font=("Courier New", 11))
        self.psize_entry.place(x=100, y=85, width=70, height=30)
        self.psize_entry.insert(0, 8)

        bsize_label = tk.Label(self.main_f, text="buffer time:", anchor="w", bg=self.gl_bg, font=label_font)
        bsize_label.place(x=190, y=85, width=90, height=30)

        self.bsize_entry = tk.Entry(self.main_f, font=("Courier New", 11))
        self.bsize_entry.place(x=280, y=85, width=70, height=30)
        self.bsize_entry.insert(0, 24)

        self.enimg_ckbt_var = tk.IntVar()
        self.enimg_ckbt = tk.Checkbutton(self.main_f, text='enable image', font=label_font,
                                         selectcolor="#C7EDCC", bg=self.gl_bg, variable=self.enimg_ckbt_var)
        self.enimg_ckbt.place(x=370, y=85, height=30)

        node_label = tk.Label(self.main_f, text="Alsa Node:", anchor="w", bg=self.gl_bg, font=label_font)
        node_label.place(x=10, y=135, width=90, height=35)

        self.node_combobox = ttk.Combobox(self.main_f)
        self.node_combobox.place(x=100, y=135, width=300, height=35)

        self.log_bt = ttk.Button(self.main_f, text="Draw", style="my.TButton", command=self.call_draw_bt)
        self.log_bt.place(x=410, y=135, width=70, height=35)

    def call_log_select_bt(self):
        all_log_list = []
        alsanode_list = []

        file_type = [('log files', '.txt'), ('all files', '.*')]
        log_file = tkinter.filedialog.askopenfilename(initialdir="",
                                                      title="Please select a log file:",
                                                      filetypes=file_type)
        if not log_file:
            self.log.info("No log file be selected")
            return False

        log_file = os.path.normpath(log_file)
        self.log_entry.configure(state="normal")
        self.log_entry.delete(0, "end")
        self.log_entry.insert(0, log_file)
        self.log_entry.configure(state="readonly")
        self.log.info("Log file: "+log_file)
        self.node_combobox["values"] = []
        self.node_combobox.delete(0, "end")

        try:
            with open(log_file, mode='r', encoding="utf-8", errors="ignore") as fp:
                all_log_list = fp.readlines()
        except Exception as e:
            self.log.error(f'Error of opening log file: {e}')
            tkinter.messagebox.showerror("Error", "Error of opening log file")
            return False

        for item in all_log_list:
            _alsanode = self.alsanode_pattern.findall(item)
            if _alsanode and _alsanode[0] not in alsanode_list:
                alsanode_list.append(_alsanode[0])
        if not alsanode_list:
            self.log.error("No alsa node be found in log file")
            tkinter.messagebox.showerror("Error", "No alsa node be found in log file")
            return False
        self.node_combobox["values"] = alsanode_list
        self.node_combobox.current(0)

    def call_draw_bt(self):
        tmp_flag = True
        tmp_str = ""

        log_file = self.log_entry.get().strip()
        alsa_node = self.node_combobox.get().strip()
        period_time = self.psize_entry.get().strip()
        buffer_time = self.bsize_entry.get().strip()
        if not os.path.exists(log_file):
            tmp_flag = False
            tmp_str = "No log file be selected"
        elif not alsa_node:
            tmp_flag = False
            tmp_str = "No alsa node be selected"
        elif not period_time:
            tmp_flag = False
            tmp_str = "No period time be found"
        elif not buffer_time:
            tmp_flag = False
            tmp_str = "No buffer time be found"
        if not tmp_flag:
            self.log.error(tmp_str)
            tkinter.messagebox.showerror("Error", tmp_str)
            return False

        self.draw_dict.clear()
        self.draw_dict["en_img"] = False
        self.draw_dict["log_file"] = log_file
        self.draw_dict["alsa_node"] = alsa_node
        try:
            self.draw_dict["period_time"] = int(period_time)
            self.draw_dict["buffer_time"] = int(buffer_time)
        except Exception:
            self.log.error("Check the type of period_time or buffer_time")
            tkinter.messagebox.showerror("Error", "Check the type of period_time or buffer_time")
            return False
        if self.enimg_ckbt_var.get():
            self.draw_dict["en_img"] = True

        draw_thread = threading.Thread(target=self.drawing_thread, daemon=True, name="Draw Thread")
        draw_thread.start()

    def drawing_thread(self):
        all_log_list = []
        target_log_list = []
        data_dict = {}
        try:
            with open(self.draw_dict["log_file"], mode='r', encoding="utf-8", errors="ignore") as fp:
                all_log_list = fp.readlines()
        except Exception:
            self.log.error("Error of opening log file")
            tkinter.messagebox.showerror("Error", "Error of opening log file")
            return False

        target_log_list = [item for item in all_log_list if re.search(
            self.draw_dict["alsa_node"], item, re.I) and self.key_words[0] in item]
        # print(target_log_list)
        if not target_log_list:
            self.log.error("No data be found in log file")
            tkinter.messagebox.showerror("Error", "No data be found in log file")
            return False
        actual_time_list = [int(self.max_pattern.findall(item)[0]) for item in target_log_list]
        if len(actual_time_list) > 10:
            del actual_time_list[:5]
            del actual_time_list[-5:]
        # print(actual_time_list)
        data_dict["x"] = list(range(0, len(actual_time_list), 1))
        data_dict["y1"] = [self.draw_dict["period_time"]] * len(actual_time_list)
        data_dict["y2"] = [self.draw_dict["buffer_time"]] * len(actual_time_list)
        data_dict["y3"] = actual_time_list

        trace_period = go.Scatter(x=data_dict["x"], y=data_dict["y1"], name="period_time",
                                  mode="markers+lines", line=dict(color="green"))
        trace_buffer = go.Scatter(x=data_dict["x"], y=data_dict["y2"], name="buffer_time",
                                  mode="markers+lines", line=dict(color="red"))
        trace_actual = go.Scatter(x=data_dict["x"], y=data_dict["y3"], name="actual_time",
                                  mode="markers+lines", line=dict(color="blue"))
        _data = [trace_period, trace_actual, trace_buffer]
        _layout = go.Layout(title=self.draw_dict["alsa_node"], xaxis=dict(
            title='unit: second'), yaxis=dict(title='unit: ms'), legend=dict(font_size=16))

        fig = go.Figure(data=_data, layout=_layout)
        if self.draw_dict["en_img"]:
            plot(fig, filename=f'adtm_test_{self.draw_dict["alsa_node"]}.html', image='jpeg',
                 image_width=1920, image_height=1080, image_filename=f'adtm_test_{self.draw_dict["alsa_node"]}')
        else:
            plot(fig, filename=f'adtm_test_{self.draw_dict["alsa_node"]}.html')

    def create_root_frame(self):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = int((sw - gl.Gui_Info["normal_size"][0]) / 2)
        y = int((sh - gl.Gui_Info["normal_size"][1]-60) / 2)

        self.root.title(gl.Gui_Info["proj"] + gl.Gui_Info["version"])
        # self.root.iconbitmap(os.path.join(Gui_Info["cwd"], Gui_Info["shortcut"]))

        self.root.geometry("%dx%d+%d+%d" % (gl.Gui_Info["normal_size"][0], gl.Gui_Info["normal_size"][1], x, y))
        self.root.minsize(gl.Gui_Info["normal_size"][0], gl.Gui_Info["normal_size"][1])
        self.root.maxsize(sw, sh)
        self.root.resizable(0, 0)

    def create_menu(self):
        menu_dict = {"File": ["Exit"],
                     "Logging": ["Open DebugLog"],
                     "Help": ["About"]
                     }

        menu_font = ("Times New Roman", 11)
        self.menubar = tk.Menu(self.root)
        file_menu = tk.Menu(self.menubar, font=menu_font, activeborderwidth=2, tearoff=False)
        file_menu.add_command(label=menu_dict["File"][0], command=self.menu_file_exit)
        self.menubar.add_cascade(label="File", menu=file_menu)

        logging_menu = tk.Menu(self.menubar, font=menu_font, activeborderwidth=2, tearoff=False)
        logging_menu.add_command(label=menu_dict["Logging"][0], command=self.menu_logging_debug)
        self.menubar.add_cascade(label="Logging", menu=logging_menu)
        # self.menubar.add_command(label = "Logging", command = self.__menu_log)

        help_menu = tk.Menu(self.menubar, font=menu_font, activeborderwidth=2, tearoff=False)
        help_menu.add_command(label=menu_dict["Help"][0], command=self.menu_help_about)
        self.menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=self.menubar)

    def menu_file_exit(self):
        self.log.info("GUI Tool is Closing")
        self.root.destroy()

    def menu_logging_debug(self):
        if "nt" in os.name:
            dbg_dirname = os.path.normpath(os.path.join(gl.Gui_Info["win_tmp"], gl.Gui_Info["dbg_reldir"]))
            os.startfile(dbg_dirname)
        else:
            dbg_dirname = os.path.join(os.path.expanduser('~'), gl.Gui_Info["dbg_reldir"])
            os.system('xdg-open "%s"' % dbg_dirname)

    def menu_help_about(self):
        tkinter.messagebox.showinfo("About", gl.About_Info)


if __name__ == "__main__":
    log = Logger()
    root = tk.Tk()
    # ctypes.windll.shcore.SetProcessDpiAwareness(1)
    # ScaleFactor=ctypes.windll.shcore.GetScaleFactorForDevice(0)
    # root.tk.call('tk', 'scaling', ScaleFactor/75)
    Main_GUI(log, root)
    root.mainloop()
