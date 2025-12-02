import customtkinter as ctk
from tkinter import messagebox, filedialog, LEFT, RIGHT, X, BOTH
from tkinter import ttk
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import os
from ui.suggestion_popup import SuggestionPopup
import numpy as np

from database import (
    init_db, get_accounts, save_accounts, add_account, verify_account,
    save_trip, get_all_trips, get_trips_by_user, delete_trip, update_trip,
    save_timeline, get_trips_with_timeline_by_user,  # Sử dụng hàm này thay vì load_pois
    save_booking_to_db, get_bookings_by_user, get_all_bookings,
    update_booking_status, delete_booking,
    add_notification, get_notifications, mark_notifications_read
)
from optimizer.graph import build_distance_matrix
from optimizer.ga import run_ga

# --- Các hằng số màu sắc, icon, ngôn ngữ ---
CATEGORY_GRADIENTS = {
    "mountain": ("#f7b731", "#f5cd79"),
    "forest": ("#20bf6b", "#26de81"),
    "camping": ("#3867d6", "#45aaf2"),
    "tour": ("#8854d0", "#a55eea"),
    "sea": ("#0fb9b1", "#00d2d3"),
    "city": ("#fd9644", "#f6e58d")
}
COLORS = {
    "primary": "#3498db", "secondary": "#2ecc71", "danger": "#e74c3c",
    "warning": "#f39c12", "info": "#3498db", "light": "#ecf0f1",
    "dark": "#2c3e50", "success": "#27ae60", "white": "#ffffff",
    "black": "#000000", "gray": "#95a5a6", "light_gray": "#bdc3c7",
    "dark_gray": "#7f8c8d", "background": "#f5f7fa", "card": "#ffffff",
    "text": "#2c3e50", "text_light": "#ecf0f1", "border": "#dfe6e9"
}
LANG = {
    "vi": {
        "login_title": "Đăng nhập", "login_header": "ĐĂNG NHẬP HỆ THỐNG",
        "username": "Tài khoản:", "password": "Mật khẩu:", "register": "Đăng ký",
        "login": "Đăng nhập", "exit": "Thoát", "main_title": "Kế hoạch chuyến đi của bạn",
        "input_info": "NHẬP THÔNG TIN", "trip_image": "Ảnh chuyến đi",
        "choose_image": "Chọn ảnh", "click_to_view": "(Nhấn vào ảnh để xem đầy đủ)",
        "trip_name": "Tên chuyến đi:", "trip_time": "Thời gian:", "choose_date": "Chọn ngày",
        "trip_location": "Địa điểm:", "trip_budget": "Ngân sách:", "add": "Thêm",
        "delete": "Xóa", "edit": "Sửa", "save": "Lưu", "sort": "Sắp xếp",
        "logout": "Đăng xuất", "trip_list": "DANH SÁCH CHUYẾN ĐI", "side_info": "Thông tin phụ",
        "book_trip": "Đặt chuyến", "start_date": "Ngày bắt đầu:", "end_date": "Ngày kết thúc:",
        "ok": "OK", "invalid_date": "Ngày không hợp lệ!", "error": "Lỗi",
        "success": "Thành công", "warning": "Cảnh báo", "confirm": "Xác nhận",
        "fill_all": "Vui lòng nhập đầy đủ thông tin!", "login_fail": "Tài khoản hoặc mật khẩu không đúng!",
        "add_success": "Thêm chuyến đi mới thành công!", "update_success": "Cập nhật chuyến đi thành công!",
        "no_permission_edit": "Bạn không có quyền sửa chuyến đi này!",
        "no_permission_delete": "Bạn không có quyền xóa chuyến đi này!",
        "delete_success": "Xóa chuyến đi thành công!", "select_trip_delete": "Vui lòng chọn chuyến đi cần xóa!",
        "select_trip_edit": "Vui lòng chọn chuyến đi cần sửa!",
        "confirm_delete": "Bạn có chắc chắn muốn xóa chuyến đi này?",
        "confirm_logout": "Bạn có chắc chắn muốn đăng xuất?", "no_image": "Không có ảnh để hiển thị!",
        "cannot_show_image": "Không thể hiển thị ảnh này!", "sort_by_time": "Sắp xếp theo thời gian",
        "sort_by_price": "Sắp xếp theo giá", "currency": "VNĐ", "date_format": "%d %b, %Y",
        "currency_unit": ["VNĐ", "USD"], "mountain": "Núi", "forest": "Rừng",
        "camping": "Cắm trại", "tour": "Tham quan", "sea": "Biển", "city": "Thành phố",
        "close": "Đóng", "quick_view": "Xem nhanh", "detail": "Chi tiết chuyến đi",
        "timeline": "Lịch trình", "add_timeline": "Thêm lịch trình", "edit_timeline": "Sửa lịch trình",
        "category": "Loại hình", "choose_category": "Chọn loại hình", "day": "Ngày",
        "activity": "Hoạt động", "add_activity": "Thêm hoạt động", "remove_activity": "Xóa hoạt động",
        "save_timeline": "Lưu lịch trình", "no_timeline": "Chưa có lịch trình",
    },
    "en": {
        "login_title": "Login", "login_header": "LOGIN SYSTEM", "username": "Username:",
        "password": "Password:", "register": "Register", "login": "Login", "exit": "Exit",
        "main_title": "Your Personal Trip Plan", "input_info": "ENTER INFORMATION",
        "trip_image": "Trip Image", "choose_image": "Choose Image",
        "click_to_view": "(Click image to view full)", "trip_name": "Trip Name:", "trip_time": "Time:",
        "choose_date": "Pick Date", "trip_location": "Location:", "trip_budget": "Budget:",
        "add": "Add", "delete": "Delete", "edit": "Edit", "save": "Save", "sort": "Sort",
        "logout": "Logout", "trip_list": "TRIP LIST", "side_info": "Side Info",
        "book_trip": "Book Trip", "start_date": "Start date:", "end_date": "End date:",
        "ok": "OK", "invalid_date": "Invalid date!", "error": "Error", "success": "Success",
        "warning": "Warning", "confirm": "Confirm", "fill_all": "Please fill in all information!",
        "login_fail": "Incorrect username or password!", "add_success": "Added new trip successfully!",
        "update_success": "Trip updated successfully!", "no_permission_edit": "You do not have permission to edit this trip!",
        "no_permission_delete": "You do not have permission to delete this trip!",
        "delete_success": "Trip deleted successfully!", "select_trip_delete": "Please select a trip to delete!",
        "select_trip_edit": "Please select a trip to edit!", "confirm_delete": "Are you sure you want to delete this trip?",
        "confirm_logout": "Are you sure you want to logout?", "no_image": "No image to display!",
        "cannot_show_image": "Cannot display this image!", "sort_by_time": "Sort by time",
        "sort_by_price": "Sort by price", "currency": "USD", "date_format": "%b %d, %Y",
        "currency_unit": ["USD", "VNĐ"], "mountain": "Mountain", "forest": "Forest",
        "camping": "Camping", "tour": "Tour", "sea": "Sea", "city": "City", "close": "Close",
        "quick_view": "Quick View", "detail": "Trip Detail", "timeline": "Timeline",
        "add_timeline": "Add Timeline", "edit_timeline": "Edit Timeline", "category": "Category",
        "choose_category": "Choose category", "day": "Day", "activity": "Activity",
        "add_activity": "Add activity", "remove_activity": "Remove activity",
        "save_timeline": "Save timeline", "no_timeline": "No timeline yet",
    }
}
CATEGORY_COLORS = {
    "mountain": "#e67e22", "forest": "#27ae60", "camping": "#2980b9",
    "tour": "#9b59b6", "sea": "#1abc9c", "city": "#e74c3c"
}
CATEGORY_TEXT_COLORS = {
    "mountain": "#fff", "forest": "#fff", "camping": "#fff",
    "tour": "#fff", "sea": "#fff", "city": "#fff"
}
CATEGORY_ICONS = {
    "mountain": "🏔️", "forest": "🌲", "camping": "⛺",
    "tour": "🗺️", "sea": "🌊", "city": "🏙️"
}
CATEGORY_LIST = ["mountain", "forest", "camping", "tour", "sea", "city"]


# --- Lớp Cửa sổ Chính của Ứng dụng ---
class TravelApp:
    def __init__(self, master, username, role, language="vi"):
        self.master = master
        self.username = username
        self.role = role
        self.language = language
        self.avatar_path = "avatar.png" # Path mặc định
        self.current_image = None # Dùng cho việc hiển thị ảnh
        self.selected_trip_idx = None # Index của chuyến đi đang được chọn
        self.cat_buttons = {} # Dict lưu các nút category
        self.trip_selection_list = [] # Dùng cho popup gợi ý

        self.master.title('Quản Lý Du Lịch')
        self.master.geometry("1280x800")
        self.master.resizable(True, True)

        self.create_widgets()
        self.show_trip_cards() # Hiển thị danh sách chuyến đi ban đầu

    def create_widgets(self):
        # Tạo giao diện chính
        self.master.configure(bg="#d6dbf5")
        main_bg = ctk.CTkFrame(self.master, fg_color="#e9ecf5", corner_radius=40)
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        # --- Header ---
        header = ctk.CTkFrame(self.master, fg_color="#f5f7fa", corner_radius=30, height=80)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 15))
        header.grid_columnconfigure(1, weight=0) # Cho avatar và tên user chiếm ít không gian
        header.grid_columnconfigure(3, weight=1) # Cho khoảng trống sau ngày tháng giãn ra

        ctk.CTkButton(header, text="⬅️", width=40, fg_color="#fff", text_color="#222", corner_radius=20, state="disabled").grid(row=0, column=0, padx=10)

        # Avatar
        try:
            # Cố gắng load avatar từ file
            avatar_img = Image.open(self.avatar_path).resize((40, 40))
            avatar_tk = ImageTk.PhotoImage(avatar_img)
            self.avatar_label = ctk.CTkLabel(header, image=avatar_tk, text="")
            self.avatar_label.image = avatar_tk
        except Exception:
             # Nếu lỗi, hiển thị icon mặc định
            self.avatar_label = ctk.CTkLabel(header, text="🙂", font=("Arial", 24), width=40, height=40)
        self.avatar_label.grid(row=0, column=1, padx=(0,5), sticky="w")
        self.avatar_label.bind("<Button-1>", self.change_avatar) # Click để đổi avatar

        # Tên user và role
        ctk.CTkLabel(header, text=f"{self.username} ({self.role})", font=("Arial", 14, "bold"), text_color="#222").grid(row=0, column=2, padx=5, sticky="w")

        # Ngày tháng (canh phải)
        ctk.CTkButton(header, text=datetime.now().strftime(LANG[self.language]["date_format"]), fg_color="#fff", text_color="#222", corner_radius=20, state="disabled").grid(row=0, column=4, padx=10, sticky="e")

        # Các nút chức năng (canh phải)
        ctk.CTkButton(header, text="🔔", width=40, fg_color="#fff", text_color="#222", corner_radius=20, state="enable").grid(row=0, column=5, padx=5, sticky="e")
        ctk.CTkButton(header, text="⚙️", width=40, fg_color="#fff", text_color="#222", corner_radius=20, state="enable").grid(row=0, column=6, padx=5, sticky="e")
        ctk.CTkButton(header, text="🚪 " + LANG[self.language]["logout"], command=self.logout, width=100, fg_color="#ee5253", hover_color="#ff6b6b").grid(row=0, column=7, padx=5, sticky="e")
        self.lang_btn = ctk.CTkButton(header, text="🇻🇳" if self.language == "vi" else "🇬🇧", width=40, command=self.toggle_language, fg_color="#fff", text_color="#222")
        self.lang_btn.grid(row=0, column=8, padx=5, sticky="e")
        ctk.CTkButton(
            header, text="🎫 Xem vé", command=self.show_my_bookings,
            width=100, fg_color="#2980b9", hover_color="#6ab04c"
        ).grid(row=0, column=9, padx=(5,10), sticky="e")

        # --- Main Content ---
        main = ctk.CTkFrame(self.master, fg_color="#e9ecf5", corner_radius=30)
        main.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=3) # Khung giữa lớn hơn
        main.grid_columnconfigure(1, weight=1) # Khung phải nhỏ hơn

        # --- Khung Trung tâm ---
        center_card = ctk.CTkFrame(main, fg_color="#f5f7fa", corner_radius=20)
        center_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        center_card.grid_rowconfigure(7, weight=1) # Cho phép danh sách chuyến đi giãn ra
        center_card.grid_columnconfigure(0, weight=1) # Cho các phần tử căn giữa

        # Hàng nút Actions (Thêm, Sắp xếp, Sửa, Xóa, Gợi ý)
        action_frame = ctk.CTkFrame(center_card, fg_color="transparent")
        action_frame.grid(row=0, column=0, columnspan=2, pady=(10, 0), padx=(10, 0), sticky="ew")
        # Canh giữa các nút trong action_frame
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_columnconfigure(6, weight=1)

        btn_container = ctk.CTkFrame(action_frame, fg_color="transparent")
        btn_container.grid(row=0, column=1, columnspan=5)

        self.add_trip_btn = ctk.CTkButton(
            btn_container, text="➕", width=70, height=50, font=("Arial", 22, "bold"),
            fg_color="#27ae60", hover_color="#2ecc71", corner_radius=20,
            command=self.open_add_trip_popup,
            state="normal" if self.role == "admin" else "disabled")
        self.add_trip_btn.pack(side=LEFT, padx=7)

        self.sort_btn = ctk.CTkButton(btn_container, text="↕️", width=60, height=50, fg_color="#2980b9", hover_color="#6ab04c", corner_radius=20, command=self.sort_trips)
        self.sort_btn.pack(side=LEFT, padx=7)

        self.edit_btn = ctk.CTkButton(btn_container, text="✏️", width=60, height=50, fg_color="#f39c12", hover_color="#f6e58d", corner_radius=20, command=self.select_trip_to_edit,state="normal" if self.role == "admin" else "disabled")
        self.edit_btn.pack(side=LEFT, padx=7)

        self.del_btn = ctk.CTkButton(btn_container, text="🗑", width=60, height=50, fg_color="#e74c3c", hover_color="#c0392b", corner_radius=20, command=self.select_trip_to_delete,state="normal" if self.role == "admin" else "disabled")
        self.del_btn.pack(side=LEFT, padx=7)

        self.suggest_btn = ctk.CTkButton(
            btn_container, text="🧠 Gợi ý", width=70, height=50,
            fg_color="#9b59b6", hover_color="#8e44ad", corner_radius=20,
            command=self.open_suggestion_popup # Gọi hàm mới
        )
        self.suggest_btn.pack(side=LEFT, padx=7)

        # Tiêu đề chính
        ctk.CTkLabel(center_card, text=LANG[self.language]["main_title"], font=("Arial", 26, "bold"), text_color="#222").grid(row=1, column=0, columnspan=2, pady=14, sticky="ew")

        # Hàng nút Category
        category_frame = ctk.CTkFrame(center_card, fg_color="transparent") # Đổi fg_color
        category_frame.grid(row=2, column=0, columnspan=2, pady=8, sticky="ew")
        # Canh giữa các nút category
        category_frame.grid_columnconfigure(0, weight=1)
        category_frame.grid_columnconfigure(len(CATEGORY_LIST) + 1, weight=1)

        cat_btn_container = ctk.CTkFrame(category_frame, fg_color="transparent")
        cat_btn_container.grid(row=0, column=1, columnspan=len(CATEGORY_LIST))

        for i, cat in enumerate(CATEGORY_LIST):
            btn = ctk.CTkButton(
                cat_btn_container, text=f"{CATEGORY_ICONS[cat]} {LANG[self.language][cat]}", width=120,
                fg_color="#fff", text_color="#222", # Màu mặc định
                font=("Arial", 13), # Font mặc định
                corner_radius=18, hover_color=CATEGORY_COLORS[cat], # Hover theo màu category
                command=lambda c=cat: self.filter_by_category(c)
            )
            btn.pack(side=LEFT, padx=7, pady=4)
            self.cat_buttons[cat] = btn

        # Ảnh bản đồ (placeholder)
        try:
            map_img_path = os.path.join(os.path.dirname(__file__), "image", "map.webp")
            map_img = Image.open(map_img_path).resize((400, 250))
            map_tk = ImageTk.PhotoImage(map_img)
            map_label = ctk.CTkLabel(center_card, image=map_tk, text="")
            map_label.image = map_tk
        except Exception:
            map_label = ctk.CTkLabel(center_card, text="[Bản đồ]", width=350, height=220, fg_color="#e8f0fe", corner_radius=10)
        map_label.grid(row=3, column=0, columnspan=2, pady=10)

        # Rating (placeholder)
        ctk.CTkLabel(center_card, text="5.0 ★", font=("Arial", 16, "bold"), text_color="#f1c40f", fg_color="#fff", corner_radius=10, width=60).grid(row=4, column=0, columnspan=2, pady=5)

        # Danh sách chuyến đi
        ctk.CTkLabel(center_card, text=LANG[self.language]["trip_list"], font=("Arial", 16, "bold"), text_color="#222").grid(row=6, column=0, columnspan=2, pady=10)
        self.trip_card_frame = ctk.CTkScrollableFrame(center_card, fg_color="#f5f7fa", height=350)
        self.trip_card_frame.grid(row=7, column=0, columnspan=2, sticky="nsew", padx=20, pady=10)

        # --- Khung Bên phải (Placeholder) ---
        right_card = ctk.CTkFrame(main, width=350, fg_color="#fff", corner_radius=20)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        right_card.grid_propagate(False) # Ngăn không cho co lại
        right_card.grid_rowconfigure(4, weight=1) # Đẩy nút Exit xuống dưới

        ctk.CTkLabel(right_card, text=LANG[self.language]["side_info"], font=("Arial", 14, "bold"), text_color="#222").pack(pady=10)

        # Seat map (placeholder)
        seat_frame = ctk.CTkFrame(right_card, fg_color="#e8f0fe", corner_radius=10)
        seat_frame.pack(pady=10)
        for row in range(4):
            for col in range(4):
                seat = ctk.CTkButton(seat_frame, text="✓" if (row+col)%3 else "✗", width=30, height=30, fg_color="#fff" if (row+col)%3 else "#f8d7da", text_color="#222", corner_radius=8, state="disabled")
                seat.grid(row=row, column=col, padx=3, pady=3)

        ctk.CTkLabel(right_card, text="From: New York\nTo: Amsterdam\nDep: 00:00\nArr: 09:30", justify="left", font=("Arial", 11), text_color="#222", fg_color="#e8f0fe", corner_radius=10, width=180).pack(pady=5)
        ctk.CTkButton(right_card, text="🛫 " + LANG[self.language]["book_trip"], fg_color="#10ac84", hover_color="#1dd1a1", width=180).pack(pady=10)
        ctk.CTkButton(right_card, text="❌ " + LANG[self.language]["exit"], command=self.master.quit, width=180, fg_color="#bdc3c7", text_color="#333").pack(side="bottom", pady=20) # Đẩy xuống dưới

    def show_trip_cards(self):
        # Hiển thị danh sách chuyến đi trong scrollable frame
        for widget in self.trip_card_frame.winfo_children():
            widget.destroy()

        # Lấy danh sách chuyến đi (có thể đã được lọc/sắp xếp)
        # Sử dụng get_trips_with_timeline để có cả lịch trình
        trips = getattr(self, "current_trips", get_trips_with_timeline_by_user(self.username, self.role))

        self.selected_trip_idx = None # Reset lựa chọn
        # Reset highlight category nếu không có category nào đang active
        if not getattr(self, "active_category", None):
            self.reset_category_highlight()

        if not trips:
             ctk.CTkLabel(self.trip_card_frame, text="Không có chuyến đi nào.").pack(pady=20)
             return

        for idx, trip in enumerate(trips):
            card = ctk.CTkFrame(self.trip_card_frame, fg_color="#fff", corner_radius=15, height=60)
            card.pack(fill=X, pady=8, padx=5)
            card.pack_propagate(False) # Ngăn card thay đổi kích thước

            def create_select_card_handler(i, c, trip_data):
                def select_card(event=None):
                    self.selected_trip_idx = i
                    # Bỏ highlight tất cả card khác
                    for w in self.trip_card_frame.winfo_children():
                        w.configure(fg_color="#fff")
                    # Highlight card được chọn
                    c.configure(fg_color="#d1f2eb")
                    # Highlight category tương ứng
                    self.highlight_category(trip_data.get("category", "mountain"))
                    # Hiển thị timeline (có thể cần cập nhật khung bên phải)
                    # self.show_timeline_preview(trip_data.get("timeline", []))
                return select_card

            card.bind("<Button-1>", create_select_card_handler(idx, card, trip))

            # Ảnh thumbnail
            img_path = trip.get("image", "")
            img_label = ctk.CTkLabel(card, text="🖼️", width=60, height=40, fg_color="#eee")
            if img_path and os.path.exists(img_path):
                try:
                    img = Image.open(img_path).resize((60, 40))
                    img_tk = ImageTk.PhotoImage(img)
                    img_label.configure(image=img_tk, text="")
                    img_label.image = img_tk
                except Exception as e:
                    print(f"Lỗi load ảnh {img_path}: {e}") # In lỗi ra console
            img_label.pack(side=LEFT, padx=8, pady=10)
            img_label.bind("<Button-1>", create_select_card_handler(idx, card, trip)) # Cho phép click ảnh

            # Thông tin cơ bản
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side=LEFT, fill=X, expand=True, padx=8)
            info = f"{trip.get('name','-- Tên --')} | {trip.get('time','-- Thời gian --')} | {trip.get('location','-- Địa điểm --')}"
            info_label = ctk.CTkLabel(info_frame, text=info, font=("Arial", 12, "bold"), text_color="#222", anchor="w")
            info_label.pack(fill=X, pady=(5,0))
            info_label.bind("<Button-1>", create_select_card_handler(idx, card, trip)) # Click text

            # Nút chức năng trên card (canh phải)
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(side=RIGHT, padx=8, pady=10)

            ctk.CTkButton(
                btn_frame, text="👁️ " + LANG[self.language]["quick_view"], width=100,
                fg_color="#e8f0fe", hover_color="#b2bec3", text_color="#333",
                corner_radius=10, command=lambda i=idx: self.show_trip_detail(i)
            ).pack(side=LEFT, padx=5)
            ctk.CTkButton(
                btn_frame, text="🛫 " + LANG[self.language]["book_trip"], width=100,
                fg_color="#10ac84", hover_color="#1dd1a1",
                corner_radius=10, command=lambda i=idx: self.open_booking_popup(i)
            ).pack(side=LEFT, padx=5)

    def highlight_category(self, category):
        # Highlight nút category được chọn
        self.reset_category_highlight()
        btn = self.cat_buttons.get(category)
        if btn:
            btn.configure(
                fg_color=CATEGORY_COLORS.get(category, "#e67e22"),
                text_color="#fff",
                font=("Arial", 13, "bold")
            )

    def reset_category_highlight(self):
        # Bỏ highlight tất cả các nút category
        for cat, btn in self.cat_buttons.items():
            btn.configure(
                fg_color="#fff",
                text_color="#222",
                font=("Arial", 13)
            )

    def show_timeline(self, timeline, parent):
        # Hiển thị đầy đủ timeline trong popup chi tiết
        if parent is None: return

        # Xóa timeline cũ nếu có
        for widget in parent.winfo_children():
            if isinstance(widget, ctk.CTkScrollableFrame) and hasattr(widget, "is_timeline_frame"):
                 widget.destroy()

        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="#fff", corner_radius=10, height=350)
        scroll_frame.pack(pady=10, fill=BOTH, expand=True, padx=20)
        setattr(scroll_frame, "is_timeline_frame", True) # Đánh dấu để xóa sau

        if not timeline:
            ctk.CTkLabel(scroll_frame, text=LANG[self.language]["no_timeline"], text_color="#888").pack(pady=20)
        else:
            for day_data in timeline:
                day_str = day_data.get("date", "N/A")
                ctk.CTkLabel(scroll_frame, text=f"🗓️ {LANG[self.language]['day']}: {day_str}", font=("Arial", 12, "bold"), text_color="#2980b9").pack(anchor="w", padx=10, pady=(10, 2))
                activities = day_data.get("activities", [])
                if activities:
                    for act in activities:
                        ctk.CTkLabel(scroll_frame, text=f"  • {act}", text_color="#555", justify="left", wraplength=450).pack(anchor="w", padx=25, pady=1)
                else:
                     ctk.CTkLabel(scroll_frame, text="  (Chưa có hoạt động)", text_color="#888", font=("Arial", 11, "italic")).pack(anchor="w", padx=25, pady=1)

    # --- Các hàm xử lý sự kiện nút ---

    def select_trip_to_edit(self):
        # Mở popup chọn chuyến đi để sửa
        trips = get_trips_by_user(self.username, self.role)
        if not trips:
            messagebox.showwarning(LANG[self.language]["warning"], "Không có chuyến đi nào để sửa!", parent=self.master)
            return

        popup = ctk.CTkToplevel(self.master)
        popup.title(LANG[self.language]["edit"])
        popup.geometry("500x400")
        popup.grab_set()
        popup.lift()
        popup.attributes("-topmost", True)

        ctk.CTkLabel(popup, text=LANG[self.language]["select_trip_edit"], font=("Arial", 16, "bold")).pack(pady=10)
        frame = ctk.CTkScrollableFrame(popup) # Dùng scrollable nếu nhiều
        frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        for idx, trip in enumerate(trips):
            info = f"{trip.get('name','')} | {trip.get('location','')}"
            btn = ctk.CTkButton(frame, text=info, width=420, height=40, fg_color="#f5f6fa", text_color="#222",
                                command=lambda i=idx, t=trip: (popup.destroy(), self.open_add_trip_popup(edit_data=t, edit_index=i)))
            btn.pack(pady=5)

    def select_trip_to_delete(self):
         # Mở popup chọn chuyến đi để xóa
        trips = get_trips_by_user(self.username, self.role)
        if not trips:
            messagebox.showwarning(LANG[self.language]["warning"], "Không có chuyến đi nào để xóa!", parent=self.master)
            return

        popup = ctk.CTkToplevel(self.master)
        popup.title(LANG[self.language]["delete"])
        popup.geometry("500x400")
        popup.grab_set()
        popup.lift()
        popup.attributes("-topmost", True)

        ctk.CTkLabel(popup, text=LANG[self.language]["select_trip_delete"], font=("Arial", 16, "bold")).pack(pady=10)
        frame = ctk.CTkScrollableFrame(popup)
        frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        for idx, trip in enumerate(trips):
            info = f"{trip.get('name','')} | {trip.get('location','')}"
            btn = ctk.CTkButton(frame, text=info, width=420, height=40, fg_color="#f5f6fa", text_color="#222",
                                command=lambda i=idx: self.confirm_delete_trip(popup, i))
            btn.pack(pady=5)


    def confirm_delete_trip(self, popup, idx):
        # Xác nhận và xóa chuyến đi
        popup.destroy() # Đóng popup chọn trước
        trips = get_trips_by_user(self.username, self.role)
        if not (0 <= idx < len(trips)): return

        trip_name = trips[idx].get('name', f"Chuyến đi #{idx}")
        if messagebox.askyesno(LANG[self.language]["confirm"],
                               f"{LANG[self.language]['confirm_delete']}\n({trip_name})",
                               parent=self.master):
            if delete_trip(idx, self.username, self.role):
                messagebox.showinfo(LANG[self.language]["success"], LANG[self.language]["delete_success"], parent=self.master)
                self.show_trip_cards() # Refresh list
            else:
                messagebox.showerror(LANG[self.language]["error"], LANG[self.language]["no_permission_delete"], parent=self.master)

    def show_trip_detail(self, idx):
        # Hiển thị popup chi tiết chuyến đi
        # Lấy lại dữ liệu mới nhất kèm timeline
        trips = get_trips_with_timeline_by_user(self.username, self.role)
        if not (0 <= idx < len(trips)): return

        trip = trips[idx]
        detail = ctk.CTkToplevel(self.master)
        detail.title(f"{LANG[self.language]['detail']} - {trip.get('name', '')}")
        detail.geometry("520x700")
        detail.grab_set()
        detail.lift()
        detail.attributes("-topmost", True)

        # Hiển thị ảnh lớn
        img_path = trip.get("image", "")
        img_label = ctk.CTkLabel(detail, text="🖼️", width=420, height=220, fg_color="#eee")
        if img_path and os.path.exists(img_path):
            try:
                img = Image.open(img_path).resize((480, 250)) # Ảnh to hơn
                img_tk = ImageTk.PhotoImage(img)
                img_label.configure(image=img_tk, text="")
                img_label.image = img_tk
            except Exception as e:
                print(f"Lỗi load ảnh chi tiết {img_path}: {e}")
        img_label.pack(pady=12)

        # Hiển thị category
        category = trip.get('category','mountain')
        ctk.CTkLabel(detail, text=f"{CATEGORY_ICONS[category]} {LANG[self.language][category]}", font=("Arial", 16, "bold"),
                       fg_color=CATEGORY_COLORS.get(category, "#fff"), text_color=CATEGORY_TEXT_COLORS.get(category, "#fff"),
                       corner_radius=10, width=180).pack(pady=10)

        # Thông tin cơ bản
        ctk.CTkLabel(detail, text=f"{LANG[self.language]['trip_name']} {trip.get('name','')}", font=("Arial", 18, "bold")).pack(pady=6)
        ctk.CTkLabel(detail, text=f"📍 {LANG[self.language]['trip_location']} {trip.get('location','')}", font=("Arial", 14)).pack()
        ctk.CTkLabel(detail, text=f"📅 {LANG[self.language]['trip_time']} {trip.get('time','')}", font=("Arial", 14)).pack()
        ctk.CTkLabel(detail, text=f"💰 {LANG[self.language]['trip_budget']} {self.format_currency(trip.get('price',''))}", font=("Arial", 14)).pack()

        # Hiển thị timeline đầy đủ
        self.show_timeline(trip.get("timeline", []), parent=detail)

        ctk.CTkButton(detail, text=LANG[self.language]["close"], command=detail.destroy, width=120).pack(pady=20)

    def open_add_trip_popup(self, edit_data=None, edit_index=None):
        # Mở popup để thêm hoặc sửa chuyến đi
        popup = ctk.CTkToplevel(self.master)
        popup.title(LANG[self.language]["add"] if not edit_data else LANG[self.language]["edit"])
        popup.geometry("700x950")
        popup.grab_set()
        popup.lift()
        popup.attributes("-topmost", True)

        # Tạo các biến StringVars để liên kết với Entry widgets
        name = ctk.StringVar(value=edit_data.get("name", "") if edit_data else "")
        time = ctk.StringVar(value=edit_data.get("time", "") if edit_data else "")
        location = ctk.StringVar(value=edit_data.get("location", "") if edit_data else "")
        # Đảm bảo price là string
        price_val = edit_data.get("price", "") if edit_data else ""
        price = ctk.StringVar(value=str(price_val))
        image_path = ctk.StringVar(value=edit_data.get("image", "") if edit_data else "")
        currency_var = ctk.StringVar(value=LANG[self.language]["currency_unit"][0])
        category = ctk.StringVar(value=edit_data.get("category", CATEGORY_LIST[0]) if edit_data else CATEGORY_LIST[0])
        # Lấy timeline từ edit_data hoặc tạo list rỗng
        # Quan trọng: Tạo bản copy để tránh sửa đổi list gốc ngoài ý muốn
        timeline = list(edit_data.get("timeline", [])) if edit_data else []


        # --- Phần hiển thị và chọn ảnh ---
        img_label = ctk.CTkLabel(popup, text=LANG[self.language]["trip_image"], width=320, height=200, fg_color="#e8f0fe", corner_radius=10)
        img_label.pack(pady=12)

        def show_img(path):
            # Hiển thị ảnh đã chọn
            if path and os.path.exists(path):
                try:
                    img = Image.open(path).resize((320, 200))
                    img_tk = ImageTk.PhotoImage(img)
                    img_label.configure(image=img_tk, text="")
                    img_label.image = img_tk
                    # img_label.pack_configure(pady=12) # Không cần pack lại
                except Exception as e:
                    img_label.configure(image='', text=LANG[self.language]["cannot_show_image"])
                    img_label.image = None
                    print(f"Lỗi hiển thị ảnh {path}: {e}")
            else:
                img_label.configure(image='', text=LANG[self.language]["trip_image"])
                img_label.image = None
        show_img(image_path.get()) # Hiển thị ảnh ban đầu (nếu có)

        def select_img():
            # Mở dialog chọn file ảnh
            filetypes = [("Image files", "*.png *.jpg *.jpeg *.gif *.webp")]
            filename = filedialog.askopenfilename(title=LANG[self.language]["choose_image"], filetypes=filetypes,parent=popup)
            if filename:
                image_path.set(filename)
                show_img(filename)
        ctk.CTkButton(popup, text="🖼️ " + LANG[self.language]["choose_image"], command=select_img, width=180, fg_color="#10ac84", hover_color="#1dd1a1").pack(pady=(0, 12))

        # --- Form nhập liệu ---
        form = ctk.CTkFrame(popup, fg_color="transparent")
        form.pack(padx=30, pady=10, fill="x") # Tăng padx
        form.grid_columnconfigure(1, weight=1) # Cho phép entry giãn ra

        # Các trường nhập liệu
        ctk.CTkLabel(form, text=LANG[self.language]["trip_name"], text_color="#222", font=("Arial", 14)).grid(row=0, column=0, sticky="w", pady=8, padx=(0,10))
        ctk.CTkEntry(form, textvariable=name, font=("Arial", 14)).grid(row=0, column=1, pady=8, columnspan=2, sticky="ew")

        ctk.CTkLabel(form, text=LANG[self.language]["trip_time"], text_color="#222", font=("Arial", 14)).grid(row=1, column=0, sticky="w", pady=8, padx=(0,10))
        time_entry = ctk.CTkEntry(form, textvariable=time, state="readonly", font=("Arial", 14))
        time_entry.grid(row=1, column=1, pady=8, sticky="ew")
        ctk.CTkButton(form, text="📅 " + LANG[self.language]["choose_date"], command=lambda: self.select_dates_popup(time), width=120, fg_color="#3498db", text_color="white", hover_color="#2980b9").grid(row=1, column=2, padx=8) # Đổi màu nút

        ctk.CTkLabel(form, text=LANG[self.language]["trip_location"], text_color="#222", font=("Arial", 14)).grid(row=2, column=0, sticky="w", pady=8, padx=(0,10))
        ctk.CTkEntry(form, textvariable=location, font=("Arial", 14)).grid(row=2, column=1, pady=8, columnspan=2, sticky="ew")

        ctk.CTkLabel(form, text=LANG[self.language]["trip_budget"], text_color="#222", font=("Arial", 14)).grid(row=3, column=0, sticky="w", pady=8, padx=(0,10))
        budget_frame = ctk.CTkFrame(form, fg_color="transparent")
        budget_frame.grid(row=3, column=1, columnspan=2, pady=8, sticky="w")
        ctk.CTkEntry(budget_frame, textvariable=price, width=180, font=("Arial", 14)).pack(side=LEFT)
        # Dùng CTkComboBox thay cho ttk
        currency_cb = ctk.CTkComboBox(budget_frame, variable=currency_var, values=LANG[self.language]["currency_unit"], width=80, state="readonly")
        currency_cb.pack(side=LEFT, padx=8)

        # Chọn Category
        ctk.CTkLabel(form, text=LANG[self.language]["category"], text_color="#222", font=("Arial", 14)).grid(row=4, column=0, sticky="w", pady=8, padx=(0,10))
        cat_frame = ctk.CTkFrame(form, fg_color="transparent")
        cat_frame.grid(row=4, column=1, columnspan=2, pady=8, sticky="w")
        cat_buttons_in_popup = {}
        def update_cat_selection_in_popup(*_):
            selected_cat = category.get()
            for cat, btn in cat_buttons_in_popup.items():
                is_selected = (cat == selected_cat)
                btn.configure(
                    fg_color=CATEGORY_COLORS[cat] if is_selected else "#fff",
                    text_color="#fff" if is_selected else "#222"
                )
        category.trace_add("write", update_cat_selection_in_popup)

        for i, cat_key in enumerate(CATEGORY_LIST):
            btn = ctk.CTkButton(
                cat_frame, text=f"{CATEGORY_ICONS[cat_key]} {LANG[self.language][cat_key]}",
                width=120, font=("Arial", 13), corner_radius=18,
                hover_color=CATEGORY_COLORS[cat_key], # Luôn hover màu category
                command=lambda c=cat_key: category.set(c)
            )
            btn.grid(row=i//3, column=i%3, padx=5, pady=5) # Giảm padx, pady
            cat_buttons_in_popup[cat_key] = btn
        update_cat_selection_in_popup() # Cập nhật màu ban đầu

        # Nút chỉnh sửa Timeline
        def open_timeline_editor():
            if not time.get():
                messagebox.showerror(LANG[self.language]["error"], "Vui lòng chọn ngày trước khi sửa lịch trình!", parent=popup)
                return
            # Truyền bản copy của timeline vào editor
            self.timeline_editor_popup(list(timeline), time, lambda new_timeline: timeline.clear() or timeline.extend(new_timeline))
        ctk.CTkButton(form, text="🕒 " + LANG[self.language]["edit_timeline"], command=open_timeline_editor, width=150, fg_color="#9b59b6", hover_color="#8e44ad").grid(row=5, column=0, columnspan=3, pady=15)

        # --- Nút Lưu ---
        def save_trip_func():
            # Validate input
            if not all([name.get(), time.get(), location.get(), price.get()]):
                messagebox.showerror(LANG[self.language]["error"], LANG[self.language]["fill_all"], parent=popup)
                return
            try:
                # Thử chuyển đổi giá sang số
                price_value = float(price.get())
            except ValueError:
                 messagebox.showerror(LANG[self.language]["error"], "Giá tiền phải là một con số!", parent=popup)
                 return

            # Chuyển đổi sang VNĐ nếu cần
            p = price_value
            if currency_var.get() == "USD":
                p = price_value * 24000 # Tỷ giá ví dụ

            # Chuẩn bị dữ liệu
            data = {
                "name": name.get(), "time": time.get(), "location": location.get(),
                "price": str(p), # Lưu giá dưới dạng string trong JSON
                "image": image_path.get(), "category": category.get(),
                "timeline": timeline # Lưu timeline đã được cập nhật từ editor
            }
            # Thêm tọa độ nếu đang sửa và đã có sẵn
            if edit_data and 'lat' in edit_data and 'lon' in edit_data:
                data['lat'] = edit_data['lat']
                data['lon'] = edit_data['lon']
            # (Nếu là thêm mới, cần có cơ chế nhập hoặc tự tìm tọa độ ở đây)


            success = False
            if edit_index is not None:
                # Chế độ Sửa
                if update_trip(edit_index, data, self.username, self.role):
                    # Lưu timeline riêng biệt có vẻ không cần thiết nếu đã gộp vào data
                    # save_timeline(edit_index, timeline, self.username, self.role)
                    messagebox.showinfo(LANG[self.language]["success"], LANG[self.language]["update_success"], parent=popup)
                    success = True
                else:
                    messagebox.showerror(LANG[self.language]["error"], LANG[self.language]["no_permission_edit"], parent=popup)
            else:
                # Chế độ Thêm mới
                save_trip(data, self.username)
                messagebox.showinfo(LANG[self.language]["success"], LANG[self.language]["add_success"], parent=popup)
                success = True
                # Lấy index mới để lưu timeline (nếu cần lưu riêng)
                # trips = get_trips_by_user(self.username, self.role)
                # new_index = len(trips) - 1
                # save_timeline(new_index, timeline, self.username, self.role)

            if success:
                popup.destroy()
                self.show_trip_cards() # Refresh danh sách

        ctk.CTkButton(popup, text="💾 " + LANG[self.language]["save"], command=save_trip_func, width=180, height=40, font=("Arial", 14, "bold"), fg_color="#27ae60", hover_color="#2ecc71").pack(pady=20)

    


    def select_dates_popup(self, time_var):
        # Mở popup chọn ngày bắt đầu và kết thúc
        date_window = ctk.CTkToplevel(self.master)
        date_window.title(LANG[self.language]["choose_date"])
        date_window.geometry("350x200") # Điều chỉnh kích thước
        date_window.grab_set()
        date_window.lift()
        date_window.attributes("-topmost", True)
        date_window.focus_force()

        # Hàm tạo combobox cho ngày/tháng/năm
        def create_date_picker(parent, row, label_text):
            years = [str(y) for y in range(datetime.now().year, datetime.now().year + 10)] # Giới hạn năm
            months = [f"{m:02d}" for m in range(1, 13)]
            days = [f"{d:02d}" for d in range(1, 32)] # Sẽ validate sau

            ctk.CTkLabel(parent, text=label_text, text_color="#222", font=("Arial", 13)).grid(row=row, column=0, padx=5, pady=5, sticky="e")
            # Dùng CTkComboBox
            year_cb = ctk.CTkComboBox(parent, values=years, width=80, state="readonly")
            month_cb = ctk.CTkComboBox(parent, values=months, width=60, state="readonly")
            day_cb = ctk.CTkComboBox(parent, values=days, width=60, state="readonly")

            # Đặt giá trị mặc định là ngày hiện tại
            now = datetime.now()
            year_cb.set(str(now.year))
            month_cb.set(f"{now.month:02d}")
            day_cb.set(f"{now.day:02d}")

            year_cb.grid(row=row, column=1, padx=2, pady=5, sticky="w")
            month_cb.grid(row=row, column=2, padx=2, pady=5, sticky="w")
            day_cb.grid(row=row, column=3, padx=2, pady=5, sticky="w")
            return year_cb, month_cb, day_cb

        start_year, start_month, start_day = create_date_picker(date_window, 0, LANG[self.language]["start_date"])
        end_year, end_month, end_day = create_date_picker(date_window, 1, LANG[self.language]["end_date"])

        def set_dates():
            # Lấy và validate ngày đã chọn
            try:
                start_date_str = f"{start_year.get()}-{start_month.get()}-{start_day.get()}"
                end_date_str = f"{end_year.get()}-{end_month.get()}-{end_day.get()}"
                # Validate ngày tháng hợp lệ
                start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
                end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")

                if end_dt < start_dt:
                    messagebox.showerror(LANG[self.language]["error"], "Ngày kết thúc không được trước ngày bắt đầu!", parent=date_window)
                    return

                # Set giá trị cho time_var
                date_sep = " đến " if self.language == "vi" else " to "
                time_var.set(f"{start_date_str}{date_sep}{end_date_str}")
                date_window.destroy()
            except ValueError:
                messagebox.showerror(LANG[self.language]["error"], LANG[self.language]["invalid_date"], parent=date_window)
            except Exception as e:
                 messagebox.showerror(LANG[self.language]["error"], f"Lỗi không xác định: {e}", parent=date_window)


        ctk.CTkButton(date_window, text=LANG[self.language]["ok"], command=set_dates, width=120, fg_color="#10ac84", hover_color="#1dd1a1").grid(row=2, column=0, columnspan=4, pady=20)


    def sort_trips(self):
        # Mở popup chọn kiểu sắp xếp
        sort_window = ctk.CTkToplevel(self.master)
        sort_window.title(LANG[self.language]["sort"])
        sort_window.geometry("250x250") # Thu nhỏ
        sort_window.grab_set()
        sort_window.lift()
        sort_window.attributes("-topmost", True)

        def do_sort(key, reverse=False):
            # Lấy danh sách hiện tại (có thể đã lọc) hoặc toàn bộ
            trips_to_sort = getattr(self, "current_trips", get_trips_by_user(self.username, self.role)).copy()

            if key == "time":
                # Sắp xếp theo ngày bắt đầu
                def get_start_date(trip):
                    time_str = trip.get("time", "")
                    try:
                        date_part = time_str.split(" đến ")[0].split(" to ")[0]
                        return datetime.strptime(date_part, "%Y-%m-%d")
                    except (ValueError, IndexError):
                        return datetime.min # Đẩy lỗi về đầu hoặc cuối tùy reverse
                trips_to_sort.sort(key=get_start_date, reverse=reverse)
            elif key == "price":
                # Sắp xếp theo giá (ép kiểu float)
                 def get_price(trip):
                    try:
                        return float(trip.get("price", 0))
                    except ValueError:
                        return float('inf') if not reverse else float('-inf') # Đẩy lỗi
                 trips_to_sort.sort(key=get_price, reverse=reverse)

            self.current_trips = trips_to_sort # Lưu lại danh sách đã sắp xếp
            self.show_trip_cards() # Hiển thị lại
            sort_window.destroy()

        # Các nút sắp xếp
        pad_y = 10
        ctk.CTkButton(sort_window, text=LANG[self.language]["sort_by_time"] + " ↑", width=200,
                      command=lambda: do_sort("time", reverse=False), fg_color="#10ac84", hover_color="#1dd1a1").pack(pady=pad_y)
        ctk.CTkButton(sort_window, text=LANG[self.language]["sort_by_time"] + " ↓", width=200,
                      command=lambda: do_sort("time", reverse=True), fg_color="#10ac84", hover_color="#1dd1a1").pack(pady=pad_y)
        ctk.CTkButton(sort_window, text=LANG[self.language]["sort_by_price"] + " ↑", width=200,
                      command=lambda: do_sort("price", reverse=False), fg_color="#10ac84", hover_color="#1dd1a1").pack(pady=pad_y)
        ctk.CTkButton(sort_window, text=LANG[self.language]["sort_by_price"] + " ↓", width=200,
                      command=lambda: do_sort("price", reverse=True), fg_color="#10ac84", hover_color="#1dd1a1").pack(pady=pad_y)

    def change_avatar(self, event=None):
        # Cho phép người dùng chọn ảnh đại diện mới
        filetypes = [("Image files", "*.png *.jpg *.jpeg *.gif *.webp")]
        filename = filedialog.askopenfilename(title="Chọn ảnh đại diện", filetypes=filetypes, parent=self.master)
        if filename:
            try:
                self.avatar_path = filename # Lưu đường dẫn mới (có thể lưu vào file config sau)
                avatar_img = Image.open(filename).resize((40, 40))
                avatar_tk = ImageTk.PhotoImage(avatar_img)
                self.avatar_label.configure(image=avatar_tk, text="") # Cập nhật ảnh
                self.avatar_label.image = avatar_tk
            except Exception as e:
                 messagebox.showerror("Lỗi Ảnh", f"Không thể tải ảnh đại diện: {e}", parent=self.master)


    def toggle_language(self):
        # Chuyển đổi ngôn ngữ và reload toàn bộ UI
        new_lang = "en" if self.language == "vi" else "vi"
        # Xóa UI cũ
        for widget in self.master.winfo_children():
            widget.destroy()
        # Tạo lại App với ngôn ngữ mới
        TravelApp(self.master, self.username, self.role, new_lang)

    def format_currency(self, value):
        # Định dạng giá tiền theo ngôn ngữ
        try:
            value_float = float(value)
            if self.language == "en":
                # Chuyển sang USD (tỷ giá ví dụ)
                return f"${value_float / 24000:,.2f}"
            else:
                # Định dạng VNĐ
                return f"{int(value_float):,} VNĐ"
        except (ValueError, TypeError):
            return str(value) # Trả về giá trị gốc nếu không phải số

    def logout(self):
        # Đăng xuất và quay về màn hình Login
        if messagebox.askokcancel(LANG[self.language]["confirm"],
                                  LANG[self.language]["confirm_logout"],
                                  parent=self.master):
            for widget in self.master.winfo_children():
                widget.destroy()
            # Import tại chỗ để tránh vòng lặp import
            from ui.login_window import LoginWindow
            LoginWindow(self.master, self.language)

    def filter_by_category(self, category):
        # Lọc danh sách chuyến đi theo category
        if getattr(self, "active_category", None) == category:
            # Nếu click lại category đang active -> bỏ lọc
            self.active_category = None
            self.reset_category_highlight()
            delattr(self, "current_trips") # Xóa bộ lọc
        else:
            # Lọc theo category mới
            self.active_category = category
            self.highlight_category(category)
            all_trips = get_trips_by_user(self.username, self.role)
            self.current_trips = [trip for trip in all_trips if trip.get("category") == category]

        self.show_trip_cards() # Hiển thị lại danh sách

    def open_booking_popup(self, trip_idx):
        # Mở popup đặt vé
        trips = get_trips_by_user(self.username, self.role)
        if not (0 <= trip_idx < len(trips)): return
        trip = trips[trip_idx]

        popup = ctk.CTkToplevel(self.master)
        popup.title(LANG[self.language]["book_trip"])
        popup.geometry("400x350")
        popup.grab_set()
        popup.lift()
        popup.attributes("-topmost", True)

        name_var = ctk.StringVar()
        email_var = ctk.StringVar()
        quantity_var = ctk.StringVar(value="1")

        ctk.CTkLabel(popup, text=f"{LANG[self.language]['trip_name']} {trip.get('name', '')}", font=("Arial", 14, "bold")).pack(pady=10)
        ctk.CTkLabel(popup, text="Tên người đặt:", anchor="w").pack(fill="x", padx=20)
        ctk.CTkEntry(popup, textvariable=name_var).pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(popup, text="Email:", anchor="w").pack(fill="x", padx=20)
        ctk.CTkEntry(popup, textvariable=email_var).pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(popup, text="Số lượng vé:", anchor="w").pack(fill="x", padx=20)
        # Combobox chọn số lượng vé
        quantity_cb = ctk.CTkComboBox(popup, variable=quantity_var, values=[str(i) for i in range(1, 11)], state="readonly")
        quantity_cb.pack(fill="x", padx=20, pady=5)


        def save_booking_action():
            # Lưu thông tin đặt vé
            name = name_var.get().strip()
            email = email_var.get().strip()
            quantity_str = quantity_var.get()

            if not name or not email or not quantity_str.isdigit():
                messagebox.showerror(LANG[self.language]["error"], "Vui lòng nhập Tên, Email và chọn Số lượng vé hợp lệ!", parent=popup)
                return
            quantity = int(quantity_str)
            if quantity <= 0:
                 messagebox.showerror(LANG[self.language]["error"], "Số lượng vé phải lớn hơn 0!", parent=popup)
                 return

            if save_booking_to_db(trip_idx, trip.get("name", ""), self.username, name, email, quantity):
                messagebox.showinfo(LANG[self.language]["success"], "Đặt vé thành công!", parent=popup)
                # Gửi thông báo cho admin (ví dụ)
                add_notification("admin", f"User '{self.username}' vừa đặt {quantity} vé cho chuyến '{trip.get('name', '')}'.")
                popup.destroy()
            else:
                 messagebox.showerror(LANG[self.language]["error"], "Lưu vé thất bại. Vui lòng thử lại.", parent=popup)


        ctk.CTkButton(popup, text="💾 " + LANG[self.language]["save"], command=save_booking_action, fg_color="#27ae60", hover_color="#2ecc71").pack(pady=20)


    def show_my_bookings(self):
        # Hiển thị popup danh sách vé đã đặt (cho user hoặc admin)
        if self.role == "admin":
            bookings = get_all_bookings()
        else:
            bookings = get_bookings_by_user(self.username)

        popup = ctk.CTkToplevel(self.master)
        popup.title("Vé đã đặt")
        popup.geometry("800x500") # Tăng chiều rộng
        popup.grab_set()
        popup.lift()
        popup.attributes("-topmost", True)

        frame = ctk.CTkScrollableFrame(popup)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        if not bookings:
            ctk.CTkLabel(frame, text="Chưa có vé nào!").pack(pady=20)
        else:
            for booking in bookings:
                row_frame = ctk.CTkFrame(frame, fg_color="#eee" if booking[-1]=="Chờ xác nhận" else "#dff9fb") # Màu nền theo status
                row_frame.pack(fill="x", pady=3)

                if self.role == "admin":
                    booking_id, trip_name, book_user, name, email, quantity, status = booking
                    text = f"ID:{booking_id} | Chuyến: {trip_name} | User: {book_user} | Tên: {name} ({email}) | SL: {quantity} | Status: {status}"
                    ctk.CTkLabel(row_frame, text=text, anchor="w", justify="left").pack(side=LEFT, padx=5, fill="x", expand=True)

                    # Chỉ hiển thị nút nếu đang chờ
                    if status == 'Chờ xác nhận':
                        ctk.CTkButton(row_frame, text="✅ Xác nhận", width=80, fg_color="#27ae60", hover_color="#1abc9c",
                                      command=lambda bid=booking_id, user=book_user, tname=trip_name: (
                                          update_booking_status(bid, "Đã xác nhận"),
                                          add_notification(user, f"Vé #{bid} cho chuyến '{tname}' đã được xác nhận."), # Thông báo cho user
                                          popup.destroy(), self.show_my_bookings() # Refresh
                                      )).pack(side=RIGHT, padx=2)
                    ctk.CTkButton(row_frame, text="❌ Xóa", width=60, fg_color="#e74c3c", hover_color="#c0392b",
                                  command=lambda bid=booking_id: (
                                      delete_booking(bid),
                                      popup.destroy(), self.show_my_bookings() # Refresh
                                  )).pack(side=RIGHT, padx=2)
                else: # Giao diện cho User
                    booking_id, trip_name, name, email, quantity, status = booking
                    text = f"Vé #{booking_id} | Chuyến: {trip_name} | SL: {quantity} | Tình trạng: {status}"
                    ctk.CTkLabel(row_frame, text=text, anchor="w").pack(side=LEFT, padx=10, pady=5)

    def open_suggestion_popup(self):
        """
        Tạo cửa sổ popup để người dùng CHỌN CÁC CHUYẾN ĐI và nhận gợi ý.
        """
        popup = ctk.CTkToplevel(self.master)
        popup.title("Gợi ý Lộ trình Tối ưu (TSP cho Chuyến đi)")
        popup.geometry("500x750")  # Tăng chiều cao
        popup.grab_set()
        popup.lift()
        popup.attributes("-topmost", True)

        ctk.CTkLabel(popup, text="Tối ưu thứ tự Chuyến đi",
                     font=("Arial", 18, "bold")).pack(pady=10)

        # --- 1. KHUNG CHỌN CHUYẾN ĐI ---
        ctk.CTkLabel(popup, text="1. Chọn các chuyến đi muốn tối ưu:",
                     font=("Arial", 14, "bold")).pack(pady=(10, 5), anchor="w", padx=20)

        trip_select_frame = ctk.CTkScrollableFrame(popup, height=250)
        trip_select_frame.pack(fill="x", expand=True, padx=20, pady=5)

        # Sử dụng hàm get_trips_by_user để lấy dữ liệu từ QLDL.json
        all_trips = get_trips_by_user(self.username, self.role)

        # Biến tạm để lưu (biến_checkbox, dữ_liệu_chuyến_đi)
        self.trip_selection_list = []

        if not all_trips:
            ctk.CTkLabel(trip_select_frame, text="Lỗi: Không tải được data/QLDL.json").pack()
        else:
            for trip in all_trips:
                 # Chỉ hiển thị các chuyến đi CÓ lat/lon
                 if 'lat' in trip and 'lon' in trip:
                    trip_var = ctk.BooleanVar()
                    # Hiển thị thông tin chuyến đi rõ ràng
                    label = f"{trip.get('name', 'N/A')} ({trip.get('location', 'N/A')}) - {self.format_currency(trip.get('price', 0))}"
                    cb = ctk.CTkCheckBox(trip_select_frame, text=label, variable=trip_var)
                    cb.pack(anchor="w", padx=10, pady=2)
                    # Lưu cả biến và data của Chuyến đi
                    self.trip_selection_list.append((trip_var, trip))
                 else:
                     print(f"Cảnh báo: Chuyến đi '{trip.get('name')}' thiếu lat/lon, bỏ qua trong gợi ý.")


        # --- 2. KHUNG NHẬP NGÂN SÁCH ---
        ctk.CTkLabel(popup, text="2. Nhập tổng ngân sách (VNĐ):",
                     font=("Arial", 14, "bold")).pack(pady=(10, 0), anchor="w", padx=20)

        budget_entry = ctk.CTkEntry(popup, placeholder_text="Bỏ trống nếu không giới hạn", width=250)
        budget_entry.pack(pady=5)

        # --- 3. KHUNG KẾT QUẢ ---
        ctk.CTkLabel(popup, text="3. Kết quả tối ưu:",
                     font=("Arial", 14, "bold")).pack(pady=(10, 0), anchor="w", padx=20)

        result_frame = ctk.CTkScrollableFrame(popup, height=200, fg_color="#f0f0f0")
        result_frame.pack(fill="x", expand=True, padx=20, pady=10)

        ctk.CTkLabel(result_frame, text="Chọn chuyến đi, nhập ngân sách và nhấn 'Chạy'...",
                     text_color="#555").pack(pady=20, padx=10)

        # --- NÚT CHẠY ---
        run_btn = ctk.CTkButton(popup, text="🚀 Chạy Tối ưu",
                                command=lambda: self.run_optimization(budget_entry, result_frame),
                                fg_color="#27ae60", hover_color="#2ecc71",
                                height=40, font=("Arial", 14, "bold"))
        run_btn.pack(pady=20)

    def run_optimization(self, budget_entry, result_frame):
        """
        Hàm cốt lõi: LẤY CÁC CHUYẾN ĐI ĐÃ CHỌN, kiểm tra lat/lon,
        gọi GA và hiển thị kết quả.
        """
        # 1. Xóa kết quả cũ
        for widget in result_frame.winfo_children():
            widget.destroy()

        # 2. Lấy ngân sách
        try:
            budget_str = budget_entry.get()
            budget = float(budget_str) if budget_str and budget_str.strip() else None
        except ValueError:
            messagebox.showerror("Lỗi", "Ngân sách phải là một con số!", parent=result_frame.master)
            return

        # 3. (MỚI) Lọc các CHUYẾN ĐI đã được chọn
        selected_trips_for_optimizer = []
        if not hasattr(self, 'trip_selection_list'):
             messagebox.showerror("Lỗi", "Không tìm thấy danh sách Chuyến đi. Vui lòng mở lại cửa sổ.", parent=result_frame.master)
             return

        for (trip_var, trip) in self.trip_selection_list:
            if trip_var.get():  # Kiểm tra checkbox có được tick không
                # Kiểm tra lại lat/lon (dù đã lọc khi hiển thị)
                if 'lat' not in trip or 'lon' not in trip:
                    messagebox.showerror("Lỗi Dữ Liệu",
                                         f"Chuyến đi '{trip.get('name', 'N/A')}' bị thiếu 'lat' hoặc 'lon'.",
                                         parent=result_frame.master)
                    return
                selected_trips_for_optimizer.append(trip)

        # 4. (MỚI) Kiểm tra số lượng
        if len(selected_trips_for_optimizer) < 2:
            messagebox.showerror("Lỗi", "Vui lòng chọn ít nhất 2 chuyến đi để tối ưu.", parent=result_frame.master)
            return

        # 5. Xây dựng ma trận từ các chuyến đi đã chọn
        ctk.CTkLabel(result_frame, text="Đang xây dựng ma trận...").pack(pady=10)
        result_frame.master.update_idletasks()

        # 'pois' bây giờ là danh sách các chuyến đi đã chọn
        pois = selected_trips_for_optimizer

        try:
            dist_matrix = build_distance_matrix(pois)
            # Ép kiểu price sang float, xử lý lỗi nếu có
            price_list = []
            for p in pois:
                 try:
                     price_list.append(float(p['price']))
                 except (ValueError, TypeError):
                     messagebox.showerror("Lỗi Dữ Liệu", f"Giá tiền của '{p['name']}' không hợp lệ: '{p['price']}'", parent=result_frame.master)
                     return

            poi_names = [p['name'] for p in pois]
            n_points = len(pois)
        except Exception as e:
            messagebox.showerror("Lỗi Xử Lý Dữ Liệu", f"Lỗi khi chuẩn bị dữ liệu: {e}", parent=result_frame.master)
            return


        # 6. Chạy thuật toán GA
        ctk.CTkLabel(result_frame, text=f"Đang tối ưu {n_points} chuyến đi...").pack(pady=10)
        result_frame.master.update_idletasks()

        # Thêm cảnh báo về thời gian
        ctk.CTkLabel(result_frame, text="Lưu ý: Tối ưu này chỉ dựa trên khoảng cách và giá cả,\nKHÔNG xem xét ngày đi ('time').",
                     font=("Arial", 10, "italic"), text_color="#7f8c8d").pack(pady=5)
        result_frame.master.update_idletasks()


        try:
            best_route_indices, best_fit_score = run_ga(
                dist_matrix,
                price_list,
                generations=200, # Có thể tăng nếu cần kết quả tốt hơn
                pop_size=50,    # Có thể tăng nếu cần
                w1=0.7,         # Ưu tiên quãng đường
                w2=0.3,         # Ít ưu tiên chi phí hơn
                budget=budget
            )

            # 7. Xử lý và hiển thị kết quả
            total_dist = 0
            total_cost = 0
            ordered_route_names = []

            if not best_route_indices:
                 raise ValueError("Thuật toán GA không trả về kết quả.")

            # Tính toán tổng quãng đường và chi phí từ kết quả GA
            for i in range(n_points):
                idx1 = best_route_indices[i]
                idx2 = best_route_indices[(i + 1) % n_points] # Quay về điểm đầu

                # Kiểm tra index hợp lệ
                if not (0 <= idx1 < n_points and 0 <= idx2 < n_points):
                    raise IndexError(f"Index không hợp lệ: {idx1}, {idx2} trong khi chỉ có {n_points} điểm.")

                total_dist += dist_matrix[idx1][idx2]
                total_cost += price_list[idx1]
                ordered_route_names.append(poi_names[idx1])

            # Xóa các thông báo "Đang xử lý"
            for widget in result_frame.winfo_children():
                widget.destroy()

            ctk.CTkLabel(result_frame, text="Thứ tự chuyến đi tối ưu:",
                         font=("Arial", 16, "bold")).pack(pady=(10, 5))

            # Hiển thị lộ trình
            route_str = ""
            for i, name in enumerate(ordered_route_names):
                route_str += f"{i+1}. {name}\n"
            route_str += f"→ Quay lại điểm bắt đầu."

            ctk.CTkLabel(result_frame, text=route_str,
                         font=("Arial", 14), justify="left").pack(pady=10, padx=20, anchor="w")

            # Hiển thị chi phí và quãng đường
            ctk.CTkLabel(result_frame, text=f"Tổng chi phí: {total_cost:,.0f} VNĐ",
                         font=("Arial", 14, "bold"), text_color="#27ae60").pack(pady=5, anchor="w", padx=20)
            ctk.CTkLabel(result_frame, text=f"Tổng quãng đường di chuyển: {total_dist:.2f} km",
                         font=("Arial", 14, "bold"), text_color="#2980b9").pack(pady=5, anchor="w", padx=20)

            if budget and total_cost > budget:
                 ctk.CTkLabel(result_frame, text=f"⚠️ Cảnh báo: Chi phí vượt ngân sách!",
                         font=("Arial", 14, "bold"), text_color="#e74c3c").pack(pady=10, anchor="w", padx=20)

            ctk.CTkLabel(result_frame, text="*Quãng đường tính theo đường chim bay giữa các địa điểm.",
                         font=("Arial", 10, "italic"), text_color="#7f8c8d").pack(pady=10, anchor="w", padx=20)

        except IndexError as e:
             messagebox.showerror("Lỗi Index", f"Lỗi truy cập phần tử không hợp lệ trong lộ trình: {e}", parent=result_frame.master)
        except Exception as e:
            messagebox.showerror("Lỗi Thuật toán", f"Đã xảy ra lỗi khi chạy GA: {e}\nKiểm tra lại dữ liệu đầu vào và thuật toán.", parent=result_frame.master)
