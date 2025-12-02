import customtkinter as ctk
from tkinter import messagebox
from ui.travel_app import TravelApp
from tkinter import messagebox, filedialog, LEFT, RIGHT, Y, X, BOTH
from database import verify_account, add_account
from ui.travel_app import TravelApp, LANG

# --- Lớp Cửa sổ Đăng nhập ---
class LoginWindow:
    def __init__(self, master, language="vi"):
        self.master = master
        self.language = language
        self.master.title(LANG[self.language]["login_title"])
        self.master.geometry("500x400")
        self.master.resizable(False, False)

        main_frame = ctk.CTkFrame(self.master, corner_radius=30, fg_color="#f5f7fa")
        main_frame.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkLabel(main_frame, text=LANG[self.language]["login_header"], font=("Arial", 22, "bold"), text_color="#222").pack(pady=20)
        ctk.CTkLabel(main_frame, text=LANG[self.language]["username"], text_color="#222").pack(anchor="w", pady=(5,0))
        self.username_entry = ctk.CTkEntry(main_frame, width=250)
        self.username_entry.pack(pady=5)
        ctk.CTkLabel(main_frame, text=LANG[self.language]["password"], text_color="#222").pack(anchor="w", pady=(5,0))
        self.password_entry = ctk.CTkEntry(main_frame, width=250, show="*")
        self.password_entry.pack(pady=5)

        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        ctk.CTkButton(btn_frame, text="🔓 " + LANG[self.language]["login"], command=self.login, width=120, fg_color="#27ae60", hover_color="#2ecc71").pack(side=LEFT, padx=10)
        ctk.CTkButton(btn_frame, text="❌ " + LANG[self.language]["exit"], command=self.master.quit, width=120, fg_color="#e74c3c", hover_color="#c0392b").pack(side=LEFT, padx=10)
        ctk.CTkButton(btn_frame,text="📝 "+ LANG[self.language]["register"],command=self.open_register_window,width=120,fg_color="#2980b9",hover_color="#6ab04c").pack(side=LEFT, padx=10)

        self.lang_btn = ctk.CTkButton(main_frame, text="🇻🇳" if self.language == "vi" else "🇬🇧", width=40, command=self.toggle_language, fg_color="#fff", text_color="#222")
        self.lang_btn.pack(pady=5)

    def toggle_language(self):
        # Chuyển đổi ngôn ngữ
        self.language = "en" if self.language == "vi" else "vi"
        self.master.destroy()
        root = ctk.CTk()
        LoginWindow(root, self.language)
        root.mainloop()

    def open_register_window(self):
        # Mở cửa sổ đăng ký
        reg_win = ctk.CTkToplevel(self.master)
        reg_win.title("Đăng ký tài khoản")
        reg_win.geometry("400x350")
        reg_win.grab_set() # Giữ focus
        reg_win.lift()
        reg_win.attributes("-topmost", True)

        ctk.CTkLabel(reg_win, text="ĐĂNG KÝ", font=("Arial", 20, "bold")).pack(pady=15)
        username_var = ctk.StringVar()
        password_var = ctk.StringVar()
        role_var = ctk.StringVar(value="user") # Mặc định là user

        ctk.CTkLabel(reg_win, text="Tài khoản:").pack(anchor="w", padx=30)
        ctk.CTkEntry(reg_win, textvariable=username_var).pack(fill='x', padx=30, pady=5)
        ctk.CTkLabel(reg_win, text="Mật khẩu:").pack(anchor="w", padx=30)
        ctk.CTkEntry(reg_win, textvariable=password_var, show="*").pack(fill='x', padx=30, pady=5)
        ctk.CTkLabel(reg_win, text="Vai trò:").pack(anchor="w", padx=30)
        # Chỉ cho phép đăng ký user
        role_cb = ttk.Combobox(reg_win, textvariable=role_var, values=["user"], state="readonly")
        role_cb.pack(fill='x', padx=30, pady=5)

        def register():
            username = username_var.get().strip()
            password = password_var.get().strip()
            role = role_var.get()
            if not username or not password:
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!", parent=reg_win)
                return
            if add_account(username, password, role):
                messagebox.showinfo("Thành công", "Đăng ký thành công!", parent=reg_win)
                reg_win.destroy()
            else:
                messagebox.showerror("Lỗi", "Tài khoản đã tồn tại!", parent=reg_win)

        ctk.CTkButton(reg_win, text="Đăng ký", command=register, fg_color="#27ae60", hover_color="#2ecc71").pack(pady=20)


    def login(self):
        # Xử lý đăng nhập
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showerror(LANG[self.language]["error"], LANG[self.language]["fill_all"])
            return
        role = verify_account(username, password)
        if role:
            # Xóa các widget của cửa sổ login
            for widget in self.master.winfo_children():
                widget.destroy()
            # Mở cửa sổ chính của ứng dụng
            TravelApp(self.master, username, role, self.language)
        else:
            messagebox.showerror(LANG[self.language]["error"], LANG[self.language]["login_fail"])