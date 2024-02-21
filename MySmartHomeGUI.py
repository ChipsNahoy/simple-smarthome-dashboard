import customtkinter
from customtkinter import *
import MySmartHomeService as sv
import time
import threading

set_appearance_mode("dark")
set_default_color_theme("blue")


class gui(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Smart Home Access")
        self.geometry("500x623")
        self.minsize(500, 623)

        # misc
        self.login_state = 0
        self.stop_thread = False
        self.t_num = 0
        self.thread_list = []

        # configure root (1x3)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 3 frames inside root
        self.login_f = CTkFrame(master=self, height=200, corner_radius=0)
        self.login_f.grid(row=0, column=0, sticky="nswe")

        self.mode_f = CTkFrame(master=self)
        self.mode_f.grid(row=1, column=0, sticky="nswe", padx=20, pady=(20, 10))

        self.ctrl_f = CTkFrame(master=self)
        self.ctrl_f.grid(row=2, column=0, sticky="nswe", padx=20, pady=(10, 20))

        # configure login frame (2x6)
        self.login_f.grid_columnconfigure(1, weight=1)
        self.login_f.grid_rowconfigure(5, weight=1)

        # login frame stays up all time
        self.title = CTkLabel(master=self.login_f, text='My Smart Home')
        self.title.grid(row=0, column=1, columnspan=2, pady=5)

        self.l_un = CTkLabel(master=self.login_f, text='Username')
        self.l_un.grid(row=1, column=1)
        self.l_pw = CTkLabel(master=self.login_f, text='Password')
        self.l_pw.grid(row=2, column=1)
        self.e_un = CTkEntry(master=self.login_f)
        self.e_un.grid(row=1, column=2, padx=(0, 10), sticky="we")
        self.e_pw = CTkEntry(master=self.login_f, show="*")
        self.e_pw.grid(row=2, column=2, padx=(0, 10), sticky="we")
        self.log_bttn = CTkButton(master=self.login_f, text='Login', command=self.login)
        self.log_bttn.grid(row=3, column=1, columnspan=2, pady=5)
        self.data = CTkLabel(master=self.login_f, text='')
        self.data.grid(row=4, column=1, columnspan=2, rowspan=2, pady=5)

        # configure mode frame (3x1)
        self.login_f.grid_columnconfigure(3, weight=1)
        self.login_f.grid_rowconfigure(0, weight=1)

        # mode frame, disable all button until successful login
        self.mode_lab = CTkLabel(master=self.mode_f, text='Mode')
        self.mode_lab.grid(row=0, column=0, sticky="w")
        self.mode_rbttn_var = IntVar(
            value=sv.check_tool('auto_mode', 'mode'))  # There might be a problem with the check_tool function
        self.mode_rbttn_m = CTkRadioButton(master=self.mode_f, text='Manual', variable=self.mode_rbttn_var, value=0,
                                           command=self.change_mode)
        self.mode_rbttn_m.grid(row=0, column=1, padx=20, sticky="w")
        self.mode_rbttn_a = CTkRadioButton(master=self.mode_f, text='Auto', variable=self.mode_rbttn_var, value=1,
                                           command=self.change_mode)
        self.mode_rbttn_a.grid(row=0, column=2, padx=20, sticky="w")
        self.guest_mode = CTkCheckBox(master=self.mode_f, text='Guest',
                                      command=self.change_guest_mode)
        self.guest_mode.grid(row=0, column=3, padx=20, sticky="w")

        # configure control frame (3x9)
        self.ctrl_f.grid_columnconfigure(1, weight=1)
        self.ctrl_f.grid_rowconfigure(10, weight=1)

        # control frame, disable all button until successful login and when automatic
        # Room 1 with lights, ac, music
        self.bed_lab = CTkLabel(master=self.ctrl_f, text='Bedroom')
        self.bed_lab.grid(row=0, column=0, pady=(10, 20))
        self.lbed_sw = CTkSwitch(master=self.ctrl_f, text="Lights",
                                 command=lambda: sv.change_condition('bedroom', 'light', self.e_un.get()))
        self.lbed_sw.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.acbed_sw = CTkSwitch(master=self.ctrl_f, text="Air Conditioner",
                                  command=lambda: sv.change_condition('bedroom', 'ac', self.e_un.get()))
        self.acbed_sw.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.spbed_sw = CTkSwitch(master=self.ctrl_f, text="Speaker",
                                  command=lambda: sv.change_condition('bedroom', 'music', self.e_un.get()))
        self.spbed_sw.grid(row=3, column=0, padx=20, pady=10, sticky="w")

        # Room 2 with lights and music
        self.bath_lab = CTkLabel(master=self.ctrl_f, text='Bathroom')
        self.bath_lab.grid(row=5, column=0, pady=(30, 20))
        self.lbath_sw = CTkSwitch(master=self.ctrl_f, text="Lights",
                                  command=lambda: sv.change_condition('bathroom', 'light', self.e_un.get()))
        self.lbath_sw.grid(row=6, column=0, padx=20, pady=10, sticky="w")
        self.spbath_sw = CTkSwitch(master=self.ctrl_f, text="Speaker",
                                   command=lambda: sv.change_condition('bathroom', 'music', self.e_un.get()))
        self.spbath_sw.grid(row=7, column=0, padx=20, pady=10, sticky="w")

        # Room 3 with lights, ac, music
        self.kit_lab = CTkLabel(master=self.ctrl_f, text='Kitchen')
        self.kit_lab.grid(row=0, column=1, pady=(10, 20), sticky="w")
        self.lkit_sw = CTkSwitch(master=self.ctrl_f, text="Lights",
                                 command=lambda: sv.change_condition('kitchen', 'light', self.e_un.get()))
        self.lkit_sw.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        self.ackit_sw = CTkSwitch(master=self.ctrl_f, text="Air Conditioner",
                                  command=lambda: sv.change_condition('kitchen', 'ac', self.e_un.get()))
        self.ackit_sw.grid(row=2, column=1, padx=20, pady=10, sticky="w")
        self.spkit_sw = CTkSwitch(master=self.ctrl_f, text="Speaker",
                                  command=lambda: sv.change_condition('kitchen', 'music', self.e_un.get()))
        self.spkit_sw.grid(row=3, column=1, padx=20, pady=10, sticky="w")

        # Room 4 with lights, ac, music
        self.liv_lab = CTkLabel(master=self.ctrl_f, text='Living Room')
        self.liv_lab.grid(row=5, column=1, pady=(30, 20), sticky="w")
        self.lliv_sw = CTkSwitch(master=self.ctrl_f, text="Lights",
                                 command=lambda: sv.change_condition('livingroom', 'light', self.e_un.get()))
        self.lliv_sw.grid(row=6, column=1, padx=20, pady=10, sticky="w")
        self.acliv_sw = CTkSwitch(master=self.ctrl_f, text="Air Conditioner",
                                  command=lambda: sv.change_condition('livingroom', 'ac', self.e_un.get()))
        self.acliv_sw.grid(row=7, column=1, padx=20, pady=10, sticky="w")
        self.spliv_sw = CTkSwitch(master=self.ctrl_f, text="Speaker",
                                  command=lambda: sv.change_condition('livingroom', 'music', self.e_un.get()))
        self.spliv_sw.grid(row=8, column=1, padx=20, pady=10, sticky="w")

        # Admin Window
        self.ad_f = CTkFrame(master=self)

        self.ad_f.grid_columnconfigure(1, weight=1)
        self.ad_f.grid_rowconfigure(6, weight=1)

        self.ad_title = CTkLabel(master=self.ad_f, text='Admin Control')
        self.ad_title.grid(row=0, column=0, columnspan=2, sticky='we')
        self.user = CTkLabel(master=self.ad_f, text='Username')
        self.user.grid(row=1, column=0)
        self.email = CTkLabel(master=self.ad_f, text='Email')
        self.email.grid(row=2, column=0)
        self.pw = CTkLabel(master=self.ad_f, text='Password')
        self.pw.grid(row=3, column=0)
        self.assure = CTkLabel(master=self.ad_f, text='Re-enter Password')
        self.assure.grid(row=4, column=0)
        self.e_user = CTkEntry(master=self.ad_f)
        self.e_user.grid(row=1, column=1, padx=(0, 10), sticky="we")
        self.e_email = CTkEntry(master=self.ad_f)
        self.e_email.grid(row=2, column=1, padx=(0, 10), sticky="we")
        self.e_pass = CTkEntry(master=self.ad_f)
        self.e_pass.grid(row=3, column=1, padx=(0, 10), sticky="we")
        self.e_assure = CTkEntry(master=self.ad_f)
        self.e_assure.grid(row=4, column=1, padx=(0, 10), sticky="we")
        self.ad_bttn = CTkButton(master=self.ad_f, text='Change Password',
                                 command=lambda: self.change_pass(self.e_email.get(), self.e_pass.get(),
                                                                  self.e_assure.get(), self.e_un.get()))
        self.ad_bttn.grid(row=5, column=0, columnspan=2, pady=5)
        self.back_button = CTkButton(master=self.ad_f, text='Back', command=lambda: self.ad_f.grid_forget())
        self.back_button.grid(row=6, column=0, columnspan=2, pady=5)

        self.disable_mode()
        self.disable_ctrl()

    def login(self):
        login_stat, role = sv.login(self.e_un.get(), self.e_pw.get())
        if login_stat:
            self.login_state = 1
            self.data.configure(text=f"Hello, \n{self.e_un.get()}")
            self.check_role(role)
        else:
            self.login_state = 0
            self.data.configure(text='Login Failed!')
            self.disable_mode()
            self.disable_ctrl()

    def check_role(self, role):
        if role == 'parent':
            self.enable_mode()
            self.refresh_conds()
        elif role == 'child':
            self.disable_mode()
            self.refresh_conds()
        elif role == 'guest' and self.guest_mode.get():
            self.disable_mode()
            self.refresh_conds()
        elif role == 'admin':
            self.disable_mode()
            self.disable_ctrl()
            self.show_admin_frame()
        else:
            self.disable_mode()
            self.disable_ctrl()

    def refresh_conds(self):
        if self.mode_rbttn_var.get() and self.login_state:  # Tidak bisa masuk ke kondisi ini (get selalu 0)
            self.disable_ctrl()
            sv.start_threading()
            self.start_auto_threads()
        else:
            sv.stop_threading()
            self.stop_auto_threads()
            self.enable_ctrl()

    def change_mode(self):
        sv.change_mode(self.mode_rbttn_var.get())
        self.refresh_conds()

    def change_guest_mode(self):
        sv.change_guest_mode(self.guest_mode.get(), self.e_un.get())
        self.refresh_conds()

    def disable_ctrl(self):
        self.lbed_sw.configure(state="disabled")
        self.acbed_sw.configure(state="disabled")
        self.spbed_sw.configure(state="disabled")
        self.lbath_sw.configure(state="disabled")
        self.spbath_sw.configure(state="disabled")
        self.lkit_sw.configure(state="disabled")
        self.ackit_sw.configure(state="disabled")
        self.spkit_sw.configure(state="disabled")
        self.lliv_sw.configure(state="disabled")
        self.acliv_sw.configure(state="disabled")
        self.spliv_sw.configure(state="disabled")

    def enable_ctrl(self):
        self.lbed_sw.configure(state="normal")
        self.acbed_sw.configure(state="normal")
        self.spbed_sw.configure(state="normal")
        self.lbath_sw.configure(state="normal")
        self.spbath_sw.configure(state="normal")
        self.lkit_sw.configure(state="normal")
        self.ackit_sw.configure(state="normal")
        self.spkit_sw.configure(state="normal")
        self.lliv_sw.configure(state="normal")
        self.acliv_sw.configure(state="normal")
        self.spliv_sw.configure(state="normal")

    def disable_mode(self):
        self.mode_rbttn_a.configure(state="disabled")
        self.mode_rbttn_m.configure(state="disabled")
        self.guest_mode.configure(state="disabled")

    def enable_mode(self):
        self.mode_rbttn_a.configure(state="normal")
        self.mode_rbttn_m.configure(state="normal")
        self.guest_mode.configure(state="normal")

    def show_admin_frame(self):
        self.ad_f.grid(row=0, column=0, rowspan=3, sticky='nswe')

    def change_pass(self, em, pw, rpw, editor_un):
        if pw == rpw and pw != '':
            self.ad_f.grid_forget()
            sv.change_pass(em, pw, editor_un)
            print(pw)

    def check_db(self):
        while True:
            if self.stop_thread:
                break
            bedroom = {'light': self.lbed_sw, 'ac': self.acbed_sw, 'music': self.spbed_sw}
            bathroom = {'light': self.lbath_sw, 'music': self.spbath_sw}
            kitchen = {'light': self.lkit_sw, 'ac': self.ackit_sw, 'music': self.spkit_sw}
            livingroom = {'light': self.lliv_sw, 'ac': self.acliv_sw, 'music': self.spliv_sw}
            r_list = [bedroom, kitchen, livingroom, bathroom]
            r_str_list = ['bedroom', 'kitchen', 'livingroom', 'bathroom']
            for i, j in enumerate(r_list):
                for tool, switch in j.items():
                    if sv.check_tool(r_str_list[i], tool):
                        switch.configure(state="normal")
                        switch.select()
                        switch.configure(state="disabled")
                    else:
                        switch.configure(state="normal")
                        switch.deselect()
                        switch.configure(state="disabled")
            time.sleep(1)

    def start_auto_threads(self):
        if not len(self.thread_list):
            my_thread = threading.Thread(target=self.check_db, name='thread{}'.format(self.t_num))
            self.thread_list.append(my_thread)
            self.t_num += 1
            my_thread.start()

    def stop_auto_threads(self):
        self.stop_thread = True
        for i in self.thread_list:
            i.join()
        self.thread_list = []
        self.stop_thread = False
