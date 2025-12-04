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
        "app_title": "Quản Lý Du Lịch",
        "no_trip_to_edit": "Không có chuyến đi nào để sửa!",
        "no_trip_to_delete": "Không có chuyến đi nào để xóa!",
        "no_activity_in_day": "(Chưa có hoạt động)",
        "need_date_before_timeline": "Vui lòng chọn ngày trước khi sửa lịch trình!",
        "price_must_be_number": "Giá tiền phải là một con số!",
        "end_date_before_start": "Ngày kết thúc không được trước ngày bắt đầu!",
        "unknown_error": "Lỗi không xác định: {e}",
        "choose_avatar": "Chọn ảnh đại diện",
        "avatar_error_title": "Lỗi Ảnh",
        "avatar_error_message": "Không thể tải ảnh đại diện: {e}",
        "customer_info_title": "Thông tin khách hàng:",
        "full_name_label": "Họ tên:",
        "email_label": "Email:",
        "choose_trips_to_book": "Chọn các chuyến đi muốn đặt:",
        "no_trips_available": "Không có chuyến đi nào khả dụng!",
        "col_select": "Chọn",
        "col_trip_name": "Tên chuyến đi",
        "col_quantity": "Số lượng",
        "must_enter_name_email": "Vui lòng nhập Tên và Email người đặt!",
        "must_select_at_least_one_trip": "Vui lòng chọn ít nhất một chuyến đi!",
        "bookings_title": "Vé đã đặt",
        "bookings_list_title": "Danh sách vé đã đặt",
        "no_bookings": "Chưa có vé nào.",
        "label_customer": "Khách",
        "label_quantity": "Số lượng",
        "label_created_at": "Đặt lúc",
        "status_approved_text": "ĐÃ XÁC NHẬN",
        "status_rejected_text": "ĐÃ TỪ CHỐI",
        "status_pending_text": "CHỜ XÁC NHẬN",
        "btn_approve": "✅ Xác nhận",
        "btn_reject": "❌ Từ chối",
        "booking_update_success": "Cập nhật trạng thái vé thành công!",
        "booking_update_failed": "Không thể cập nhật trạng thái vé.",
        "suggestion_title": "Gợi ý Lộ trình Tối ưu (TSP cho Chuyến đi)",
        "suggestion_header": "Tối ưu thứ tự Chuyến đi",
        "suggestion_step1": "1. Chọn các chuyến đi muốn tối ưu:",
        "suggestion_step2": "2. Nhập tổng ngân sách (VNĐ):",
        "budget_placeholder": "Bỏ trống nếu không giới hạn",
        "suggestion_step3": "3. Kết quả tối ưu:",
        "suggestion_result_hint": "Chọn chuyến đi, nhập ngân sách và nhấn 'Chạy'...",
        "suggestion_run_button": "🚀 Chạy Tối ưu",
        "budget_must_be_number": "Ngân sách phải là một con số!",
        "trip_list_not_found": "Không tìm thấy danh sách Chuyến đi. Vui lòng mở lại cửa sổ.",
        "missing_lat_lon": "Chuyến đi '{name}' bị thiếu 'lat' hoặc 'lon'.",
        "need_at_least_two_trips": "Vui lòng chọn ít nhất 2 chuyến đi để tối ưu.",
        "building_matrix": "Đang xây dựng ma trận...",
        "optimizing_n_trips": "Đang tối ưu {n} chuyến đi...",
        "optimize_note": "Lưu ý: Tối ưu này chỉ dựa trên khoảng cách và giá cả,\nKHÔNG xem xét ngày đi ('time').",
        "invalid_price_value": "Giá tiền của '{name}' không hợp lệ: '{price}'",
        "best_route_title": "Thứ tự chuyến đi tối ưu:",
        "back_to_start": "→ Quay lại điểm bắt đầu.",
        "total_cost_label": "Tổng chi phí",
        "total_distance_label": "Tổng quãng đường di chuyển",
        "budget_warning": "⚠️ Cảnh báo: Chi phí vượt ngân sách!",
        "distance_note": "*Quãng đường tính theo đường chim bay giữa các địa điểm.",
        "data_error": "Lỗi Dữ Liệu",
        "processing_data_error": "Lỗi khi chuẩn bị dữ liệu: {e}",
        "index_error": "Lỗi Index",
        "algorithm_error": "Lỗi Thuật toán",
        "algorithm_error_detail": "Đã xảy ra lỗi khi chạy GA: {e}\nKiểm tra lại dữ liệu đầu vào và thuật toán.",
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
        "app_title": "Travel Manager",
        "no_trip_to_edit": "There is no trip to edit!",
        "no_trip_to_delete": "There is no trip to delete!",
        "no_activity_in_day": "(No activities yet)",
        "need_date_before_timeline": "Please choose dates before editing the timeline!",
        "price_must_be_number": "Budget must be a number!",
        "end_date_before_start": "End date cannot be before start date!",
        "unknown_error": "Unknown error: {e}",
        "choose_avatar": "Choose avatar image",
        "avatar_error_title": "Avatar Error",
        "avatar_error_message": "Cannot load avatar image: {e}",
        "customer_info_title": "Customer information:",
        "full_name_label": "Full name:",
        "email_label": "Email:",
        "choose_trips_to_book": "Select trips to book:",
        "no_trips_available": "No trips available!",
        "col_select": "Select",
        "col_trip_name": "Trip name",
        "col_quantity": "Quantity",
        "must_enter_name_email": "Please enter customer's name and email!",
        "must_select_at_least_one_trip": "Please select at least one trip!",
        "bookings_title": "Booked Tickets",
        "bookings_list_title": "Booked tickets list",
        "no_bookings": "No bookings yet.",
        "label_customer": "Customer",
        "label_quantity": "Quantity",
        "label_created_at": "Booked at",
        "status_approved_text": "APPROVED",
        "status_rejected_text": "REJECTED",
        "status_pending_text": "PENDING",
        "btn_approve": "✅ Approve",
        "btn_reject": "❌ Reject",
        "booking_update_success": "Booking status updated successfully!",
        "booking_update_failed": "Cannot update booking status.",
        "suggestion_title": "Optimal Route Suggestion (TSP for Trips)",
        "suggestion_header": "Optimize trip order",
        "suggestion_step1": "1. Choose trips to optimize:",
        "suggestion_step2": "2. Enter total budget (VND):",
        "budget_placeholder": "Leave empty for no limit",
        "suggestion_step3": "3. Optimization result:",
        "suggestion_result_hint": "Select trips, enter budget and press 'Run'...",
        "suggestion_run_button": "🚀 Run Optimization",
        "budget_must_be_number": "Budget must be a number!",
        "trip_list_not_found": "Trip list not found. Please reopen the window.",
        "missing_lat_lon": "Trip '{name}' is missing 'lat' or 'lon'.",
        "need_at_least_two_trips": "Please select at least 2 trips to optimize.",
        "building_matrix": "Building distance matrix...",
        "optimizing_n_trips": "Optimizing {n} trips...",
        "optimize_note": "Note: This optimization only uses distance and cost,\nNOT trip dates ('time').",
        "invalid_price_value": "Invalid price for '{name}': '{price}'",
        "best_route_title": "Optimal trip order:",
        "back_to_start": "→ Return to starting point.",
        "total_cost_label": "Total cost",
        "total_distance_label": "Total travel distance",
        "budget_warning": "⚠️ Warning: Cost exceeds budget!",
        "distance_note": "*Distance is computed as straight-line distance between locations.",
        "data_error": "Data Error",
        "processing_data_error": "Error while preparing data: {e}",
        "index_error": "Index Error",
        "algorithm_error": "Algorithm Error",
        "algorithm_error_detail": "An error occurred while running GA: {e}\nPlease check input data and algorithm.",
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

        self.master.title(LANG[self.language]["app_title"])
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
                corner_radius=10, command=lambda t=trip: self.show_trip_detail(t)
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
                     ctk.CTkLabel(
                        scroll_frame,
                        text="  " + LANG[self.language]["no_activity_in_day"],
                        text_color="#888",
                        font=("Arial", 11, "italic")
                    ).pack(...)

    # --- Các hàm xử lý sự kiện nút ---

    def select_trip_to_edit(self):
        # Mở popup chọn chuyến đi để sửa
        trips = get_trips_by_user(self.username, self.role)
        if not trips:
            messagebox.showwarning(LANG[self.language]["warning"],
                           LANG[self.language]["no_trip_to_edit"],
                           parent=self.master)
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
            messagebox.showwarning(LANG[self.language]["warning"],
                           LANG[self.language]["no_trip_to_delete"],
                           parent=self.master)
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

    def show_trip_detail(self, idx_or_trip):
        """
        Hiển thị popup chi tiết chuyến đi.
        Tham số có thể là:
         - int: index theo danh sách gốc (giữ tương thích ngược)
         - dict: trực tiếp object chuyến đi (khuyến nghị)
        Hàm đảm bảo lấy được 'timeline' (nếu thiếu sẽ cố tìm trong dữ liệu có timeline).
        """
        # Nếu gọi bằng object trip thì dùng luôn
        if isinstance(idx_or_trip, dict):
            trip = idx_or_trip
        else:
            # legacy: nếu truyền index, lấy từ danh sách có timeline
            trips = get_trips_with_timeline_by_user(self.username, self.role)
            if not (0 <= idx_or_trip < len(trips)):
                return
            trip = trips[idx_or_trip]

        # Nếu trip chưa có timeline, cố tìm bản tương ứng trong danh sách có timeline
        if 'timeline' not in trip or trip.get('timeline') is None:
            try:
                trips_with_tl = get_trips_with_timeline_by_user(self.username, self.role)
                for t in trips_with_tl:
                    if t.get('name') == trip.get('name') and t.get('location') == trip.get('location'):
                        trip['timeline'] = t.get('timeline', [])
                        break
                else:
                    trip.setdefault('timeline', [])
            except Exception:
                trip.setdefault('timeline', [])

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
                img = Image.open(img_path).resize((480, 250))
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
                messagebox.showerror(LANG[self.language]["error"],
                     LANG[self.language]["need_date_before_timeline"],
                     parent=popup)
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
                 messagebox.showerror(LANG[self.language]["error"],
                     LANG[self.language]["price_must_be_number"],
                     parent=popup)
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
                    # save_timeline(edit_index, timeline, self.username, selfrole)
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
                    messagebox.showerror(LANG[self.language]["error"],
                     LANG[self.language]["end_date_before_start"],
                     parent=date_window)
                    return

                # Set giá trị cho time_var
                date_sep = " đến " if self.language == "vi" else " to "
                time_var.set(f"{start_date_str}{date_sep}{end_date_str}")
                date_window.destroy()
            except ValueError:
                messagebox.showerror(LANG[self.language]["error"], LANG[self.language]["invalid_date"], parent=date_window)
            except Exception as e:
                msg = LANG[self.language]["unknown_error"].format(e=e)
                messagebox.showerror(LANG[self.language]["error"], msg, parent=date_window)


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


    def open_booking_popup(self, trip_idx=None):
        # Mở popup đặt vé (Logic mới: Đặt nhiều vé cùng lúc)
        trips = get_trips_by_user(self.username, self.role)
    
        # Tạo cửa sổ popup
        popup = ctk.CTkToplevel(self.master)
        popup.title(LANG[self.language].get("book_trip", "Đặt vé")) # Dùng get để tránh lỗi key
        popup.geometry("600x650") # Tăng kích thước để chứa danh sách
        popup.grab_set()
        popup.lift()
        popup.attributes("-topmost", True)

        # --- PHẦN 1: THÔNG TIN NGƯỜI ĐẶT (Dùng chung) ---
        info_frame = ctk.CTkFrame(popup)
        info_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(info_frame, text=LANG[self.language]["customer_info_title"], font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
    
        name_var = ctk.StringVar()
        email_var = ctk.StringVar()

        # Layout nhập Tên và Email trên cùng 1 hàng hoặc 2 dòng
        ctk.CTkLabel(info_frame, text=LANG[self.language]["full_name_label"]).pack(side="left", padx=(10, 5))
        ctk.CTkEntry(info_frame, textvariable=name_var, width=180).pack(side="left", padx=5)
    
        ctk.CTkLabel(info_frame, text=LANG[self.language]["email_label"]).pack(side="left", padx=(10, 5))
        ctk.CTkEntry(info_frame, textvariable=email_var, width=180).pack(side="left", padx=5)

        # --- PHẦN 2: DANH SÁCH CHUYẾN ĐI (Scrollable) ---
        ctk.CTkLabel(popup, text=LANG[self.language]["choose_trips_to_book"], font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(10, 0))

        list_frame = ctk.CTkScrollableFrame(popup)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        trip_controls = [] # Danh sách lưu các biến điều khiển (checkbox, combobox) để lấy dữ liệu sau này

        if not trips:
            ctk.CTkLabel(list_frame, text=LANG[self.language]["no_trips_available"]).pack(pady=20)
        else:
            # Tiêu đề cột
            header_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
            header_frame.pack(fill="x", pady=2)
            ctk.CTkLabel(header_frame, text=LANG[self.language]["col_select"], width=40).pack(side="left", padx=5)
            ctk.CTkLabel(header_frame, text=LANG[self.language]["col_trip_name"], anchor="w").pack(side="left", fill="x", expand=True, padx=5)
            ctk.CTkLabel(header_frame, text=LANG[self.language]["col_quantity"], width=80).pack(side="right", padx=10)

            for i, trip in enumerate(trips):
                row_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=2)

                # 1. Checkbox chọn chuyến
                is_selected = ctk.BooleanVar(value=False)
                # Nếu trip_idx được truyền vào khớp với dòng này -> Tự động tích chọn
                if trip_idx is not None and i == trip_idx:
                    is_selected.set(True)

                chk = ctk.CTkCheckBox(row_frame, text="", variable=is_selected, width=40)
                chk.pack(side="left", padx=5)

                # 2. Tên chuyến + Giá
                trip_info = f"{trip.get('name', 'Unknown')} ({self.format_currency(trip.get('price', 0))})"
                ctk.CTkLabel(row_frame, text=trip_info, anchor="w").pack(side="left", fill="x", expand=True, padx=5)

                # 3. Chọn số lượng
                qty_var = ctk.StringVar(value="1")
                qty_cb = ctk.CTkComboBox(row_frame, variable=qty_var, values=[str(x) for x in range(1, 11)], width=70, state="readonly")
                qty_cb.pack(side="right", padx=10)

                # Lưu lại tham chiếu
                trip_controls.append({
                    "index": i,
                    "trip_data": trip,
                    "selected_var": is_selected,
                    "qty_var": qty_var
                })

        # --- PHẦN 3: HÀM LƯU (Xử lý hàng loạt) ---
        def save_booking_action():
            # Thông tin khách
            name = name_var.get().strip()
            email = email_var.get().strip()

            if not name or not email:
                messagebox.showerror(
                    LANG[self.language]["error"],
                    "Vui lòng nhập Tên và Email người đặt!",
                    parent=popup
                )
                return

            # Lọc các chuyến được tick
            selected_items = [item for item in trip_controls
                              if item["selected_var"].get()]

            if not selected_items:
                messagebox.showwarning(
                    LANG[self.language]["error"],
                    "Vui lòng chọn ít nhất một chuyến đi!",
                    parent=popup
                )
                return

            # Số lượng: lấy theo chuyến đầu tiên (coi như số lượng vé cho cả tour)
            try:
                qty = int(selected_items[0]["qty_var"].get())
            except ValueError:
                qty = 1

            # Tạo danh sách chi tiết tour
            details = []
            total_price = 0

            for item in selected_items:
                t = item["trip_data"]
                try:
                    price = float(t.get("price", 0))
                except (ValueError, TypeError):
                    price = 0

                total_price += price

                details.append({
                    "name": t.get("name", ""),
                    "location": t.get("location", ""),
                    "time": t.get("time", ""),
                    "price": price,
                    "category": t.get("category", ""),
                    "lat": t.get("lat"),
                    "lon": t.get("lon")
                })

            # Tên booking hiển thị trong danh sách vé
            if len(selected_items) == 1:
                tour_name = selected_items[0]["trip_data"].get("name", "Chuyến đi")
            else:
                tour_name = f"Tour {len(selected_items)} địa điểm"

            # Lưu 1 booking duy nhất cho cả tour
            if save_booking_to_db(
                trip_index=-1,
                trip_name=tour_name,
                username=self.username,
                customer_name=name,
                email=email,
                qty=qty,
                details=details
            ):
                # Gửi thông báo cho admin (tuỳ bạn giữ hay bỏ)
                add_notification(
                    "admin",
                    f"User '{self.username}' đặt {qty} vé cho {tour_name} ({len(details)} địa điểm)."
                )

                messagebox.showinfo(
                    LANG[self.language]["success"],
                    f"Đã đặt tour {len(details)} địa điểm thành công!",
                    parent=popup
                )
                popup.destroy()
            else:
                messagebox.showerror(
                    LANG[self.language]["error"],
                    "Có lỗi xảy ra, không thể lưu vé.",
                    parent=popup
                )

        # Nút Lưu
        ctk.CTkButton(popup, text="💾 " + LANG[self.language]["save"], command=save_booking_action, 
                      fg_color="#27ae60", hover_color="#2ecc71", height=40, font=("Arial", 14, "bold")).pack(pady=15, padx=20, fill="x")

    def show_my_bookings(self):
        """
        User thường: thấy vé của chính mình.
        Admin: thấy tất cả vé và có nút xác nhận / từ chối.
        """
        # 1. Lấy dữ liệu
        try:
            if self.role == "admin":
                bookings = get_all_bookings()
            else:
                bookings = get_bookings_by_user(self.username)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lấy dữ liệu vé: {e}", parent=self.master)
            return

        # 2. Tạo popup
        popup = ctk.CTkToplevel(self.master)
        popup.title(LANG[self.language]["bookings_title"])
        popup.geometry("800x550")
        popup.grab_set()
        popup.lift()
        popup.attributes("-topmost", True)

        ctk.CTkLabel(
             popup,
             text=LANG[self.language]["bookings_list_title"],
             font=("Arial", 20, "bold")).pack(pady=10
             )

        list_frame = ctk.CTkScrollableFrame(popup, fg_color="#ecf0f1")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        if not bookings:
            ctk.CTkLabel(list_frame,
             text=LANG[self.language]["no_bookings"]).pack(pady=20)
        else:
            # Nếu DB trả về tuple, map sang dict để dùng .get()
            FIELD_NAMES = (
                "id",           # 0
                "username",     # 1
                "trip_name",    # 2
                "customer_name",# 3
                "email",        # 4
                "qty",          # 5
                "status",       # 6
                "created_at",   # 7
            )

            for row in bookings:
                if isinstance(row, dict):
                    bk = row
                else:  # tuple / list
                    bk = dict(zip(FIELD_NAMES, row))

                booking_id = bk.get("id")
                username_booking = bk.get("username", "")
                trip_name  = bk.get("trip_name", bk.get("name", "Chuyến đi ?"))
                customer   = bk.get("customer_name", bk.get("customer", ""))
                email      = bk.get("email", "")
                qty        = bk.get("qty", bk.get("quantity", 1))
                status     = bk.get("status", "pending")
                created_at = bk.get("created_at", "")
                details    = bk.get("details", [])

                # Khung mỗi vé
                row_frame = ctk.CTkFrame(list_frame, fg_color="#ffffff", corner_radius=15)
                row_frame.pack(fill="x", pady=8, padx=10)
                row_frame.pack_propagate(False)

                # Cột trái: thông tin
                info_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, padx=20, pady=10)

                # Dòng username (in đậm)
                ctk.CTkLabel(
                    info_frame,
                    text=username_booking or "user",
                    font=("Arial", 14, "bold"),
                    anchor="w"
                ).pack(fill="x")

                # Dòng chi tiết
                detail_text = (
                    f"{LANG[self.language]['label_customer']}: {customer} | Email: {email}\n"
                    f"{LANG[self.language]['label_quantity']}: {qty} | "
                    f"{LANG[self.language]['label_created_at']}: {created_at}"
                )
                ctk.CTkLabel(
                    info_frame,
                    text=detail_text,
                    font=("Arial", 12),
                    text_color="#555",
                    justify="left",
                    anchor="w"
                ).pack(fill="x", pady=(4, 0))

                # Cột phải: trạng thái + nút admin
                right_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
                right_frame.pack(side="right", padx=20, pady=10)

                # Label trạng thái
                if status == "approved":
                    status_text = LANG[self.language]["status_approved_text"]
                    color = "#2ecc71"
                elif status == "rejected":
                    status_text = LANG[self.language]["status_rejected_text"]
                    color = "#e74c3c"
                else:
                    status_text = LANG[self.language]["status_pending_text"]

                    color = "#f1c40f"

                if details:
                    ctk.CTkButton(
                        right_frame,
                        text="🔍 Xem chi tiết",
                        width=130,
                        fg_color="#3498db",
                        hover_color="#2980b9",
                        command=lambda tn=trip_name, d=details: self.show_booking_details(tn, d)
                    ).pack(pady=(5, 0))

                ctk.CTkLabel(
                    right_frame,
                    text=status_text,
                    font=("Arial", 12, "bold"),
                    text_color="#fff",
                    fg_color=color,
                    corner_radius=10,
                    width=130,
                    height=32
                ).pack(pady=(0, 5))

                # Nếu là admin -> thêm nút hành động
                if self.role == "admin":
                    btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
                    btn_frame.pack(pady=(5, 0))

                    ctk.CTkButton(
                        btn_frame,
                        text=LANG[self.language]["btn_approve"],
                        width=120,
                        fg_color="#27ae60",
                        hover_color="#2ecc71",
                        command=lambda bid=booking_id, u=username_booking: self.change_booking_status(
                            bid, "approved", u, popup
                        )
                    ).pack(pady=2)

                    ctk.CTkButton(
                        btn_frame,
                        text=LANG[self.language]["btn_reject"],
                        width=120,
                        fg_color="#e74c3c",
                        hover_color="#c0392b",
                        command=lambda bid=booking_id, u=username_booking: self.change_booking_status(
                            bid, "rejected", u, popup
                        )
                    ).pack(pady=2)

        # Nút đóng
        ctk.CTkButton(
            popup,
            text=LANG[self.language]["close"],
            command=popup.destroy,
            width=120,
            fg_color="#bdc3c7",
            hover_color="#95a5a6"
        ).pack(pady=10)

    def open_suggestion_popup(self):
        """
        Tạo cửa sổ popup để người dùng CHỌN CÁC CHUYẾN ĐI và nhận gợi ý.
        """
        popup = ctk.CTkToplevel(self.master)
        popup.title(LANG[self.language]["suggestion_title"])
        popup.geometry("500x750")  # Tăng chiều cao
        popup.grab_set()
        popup.lift()
        popup.attributes("-topmost", True)

        ctk.CTkLabel(popup, text=LANG[self.language]["suggestion_header"],
                     font=("Arial", 18, "bold")).pack(pady=10)

        # --- 1. KHUNG CHỌN CHUYẾN ĐI ---
        ctk.CTkLabel(popup, text=LANG[self.language]["suggestion_step1"],
                     font=("Arial", 14, "bold")).pack(pady=(10, 5), anchor="w", padx=20)

        trip_select_frame = ctk.CTkScrollableFrame(popup, height=250)
        trip_select_frame.pack(fill="x", expand=True, padx=20, pady=5)

        # Sử dụng hàm get_trips_by_user để lấy dữ liệu từ QLDL.json
        all_trips = get_trips_by_user(self.username, self.role)

        # Biến tạm để lưu (biến_checkbox, dữ_liệu_chuyến_đi)
        self.trip_selection_list = []

        if not all_trips:
            ctk.CTkLabel(trip_select_frame, text=LANG[self.language]["trip_list_not_found"]).pack()
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
        ctk.CTkLabel(popup, text=LANG[self.language]["suggestion_step2"],
                     font=("Arial", 14, "bold")).pack(pady=(10, 0), anchor="w", padx=20)

        budget_entry = ctk.CTkEntry(popup, placeholder_text=LANG[self.language]["budget_placeholder"], width=250)
        budget_entry.pack(pady=5)

        # --- 3. KHUNG KẾT QUẢ ---
        ctk.CTkLabel(popup, text=LANG[self.language]["suggestion_step3"],
                     font=("Arial", 14, "bold")).pack(pady=(10, 0), anchor="w", padx=20)

        result_frame = ctk.CTkScrollableFrame(popup, height=200, fg_color="#f0f0f0")
        result_frame.pack(fill="x", expand=True, padx=20, pady=10)

        ctk.CTkLabel(result_frame, text=LANG[self.language]["suggestion_result_hint"],
                     text_color="#555").pack(pady=20, padx=10)

        # --- NÚT CHẠY ---
        run_btn = ctk.CTkButton(popup, text=LANG[self.language]["suggestion_run_button"],
                                command=lambda: self.run_optimization(budget_entry, result_frame),
                                fg_color="#27ae60", hover_color="#2ecc71",
                                height=40, font=("Arial", 14, "bold"))
        run_btn.pack(pady=20)

    def change_booking_status(self, booking_id, new_status, username_booking, popup_parent):
        """
        Admin đổi trạng thái vé và gửi thông báo cho user đã đặt.
        booking_id: id trong DB (hoặc index, tùy cách bạn lưu)
        new_status: 'approved' | 'rejected'
        username_booking: username của người đặt
        """
        try:
            # Tùy signature hàm DB của bạn, nếu khác thì sửa lại ở đây
            if update_booking_status(booking_id, new_status):
                # Gửi thông báo cho user
                if new_status == "approved":
                    msg = "Vé của bạn đã được xác nhận."
                else:
                    msg = "Vé của bạn đã bị từ chối."
                add_notification(username_booking, msg)

                messagebox.showinfo(LANG[self.language]["success"],
                    LANG[self.language]["booking_update_success"],
                    parent=popup_parent)
                # Refresh lại danh sách vé
                popup_parent.destroy()
                self.show_my_bookings()
            else:
                messagebox.showerror(LANG[self.language]["error"],
                     LANG[self.language]["booking_update_failed"],
                     parent=popup_parent)
        except Exception as e:
            msg = f"Lỗi khi cập nhật trạng thái vé: {e}" if self.language == "vi" else f"Error while updating booking status: {e}"
            messagebox.showerror(LANG[self.language]["error"], msg, parent=popup_parent)

    def show_booking_details(self, tour_name, details):
        """
        Hiển thị popup chi tiết tour (các chặng trong details).
        details là list các dict đã lưu trong bookings.json.
        """
        popup = ctk.CTkToplevel(self.master)
        popup.title(f"Chi tiết - {tour_name}")
        popup.geometry("550x450")
        popup.grab_set()
        popup.lift()
        popup.attributes("-topmost", True)

        ctk.CTkLabel(
            popup,
            text=f"Chi tiết tour: {tour_name}",
            font=("Arial", 18, "bold")
        ).pack(pady=10)

        frame = ctk.CTkScrollableFrame(popup, fg_color="#ecf0f1")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        if not details:
            ctk.CTkLabel(
                frame,
                text="Tour này chưa có danh sách địa điểm.",
                font=("Arial", 12),
                text_color="#555"
            ).pack(pady=20)
        else:
            total_price = 0
            for i, d in enumerate(details, start=1):
                name = d.get("name", "Chưa đặt tên")
                loc  = d.get("location", "")
                time = d.get("time", "")
                price = d.get("price", 0) or 0
                total_price += float(price)

                text = f"{i}. {name}"
                if loc:
                    text += f" – {loc}"
                if time:
                    text += f"\n   🕒 {time}"
                text += f"\n   💰 {self.format_currency(price)}"

                card = ctk.CTkFrame(frame, fg_color="#ffffff", corner_radius=12)
                card.pack(fill="x", padx=5, pady=5)
                ctk.CTkLabel(
                    card,
                    text=text,
                    justify="left",
                    anchor="w",
                    font=("Arial", 12),
                ).pack(fill="x", padx=10, pady=8)

            # Tổng tiền tour
            ctk.CTkLabel(
                popup,
                text=f"Tổng chi phí các chặng: {self.format_currency(total_price)}",
                font=("Arial", 13, "bold"),
                text_color="#27ae60"
            ).pack(pady=(0, 10))

        ctk.CTkButton(
            popup,
            text="Đóng",
            command=popup.destroy,
            width=120,
            fg_color="#bdc3c7",
            hover_color="#95a5a6"
        ).pack(pady=8)

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
            messagebox.showerror(LANG[self.language]["error"],
                     LANG[self.language]["budget_must_be_number"],
                     parent=result_frame.master)
            return

        # 3. (MỚI) Lọc các CHUYẾN ĐI đã được chọn
        selected_trips_for_optimizer = []
        if not hasattr(self, 'trip_selection_list'):
             messagebox.showerror(LANG[self.language]["error"],
                     LANG[self.language]["trip_list_not_found"],
                     parent=result_frame.master)
             return

        for (trip_var, trip) in self.trip_selection_list:
            if trip_var.get():  # Kiểm tra checkbox có được tick không
                # Kiểm tra lại lat/lon (dù đã lọc khi hiển thị)
                if 'lat' not in trip or 'lon' not in trip:
                    title = LANG[self.language]["data_error"]
                    msg = LANG[self.language]["missing_lat_lon"].format(
                        name=trip.get("name", "N/A")
                    )
                    messagebox.showerror(title, msg, parent=result_frame.master)
                    return
                selected_trips_for_optimizer.append(trip)

        # 4. (MỚI) Kiểm tra số lượng
        if len(selected_trips_for_optimizer) < 2:
            messagebox.showerror(LANG[self.language]["error"],
                     LANG[self.language]["need_at_least_two_trips"],
                     parent=result_frame.master)
            return

        # 5. Xây dựng ma trận từ các chuyến đi đã chọn
        ctk.CTkLabel(result_frame, text=LANG[self.language]["building_matrix"]).pack(pady=10)
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
                     title = LANG[self.language]["data_error"]
                     msg = LANG[self.language]["invalid_price_value"].format(
                         name=p.get("name", "N/A"),
                         price=p.get("price", "")
                     )
                     messagebox.showerror(title, msg, parent=result_frame.master)

                     return

            poi_names = [p['name'] for p in pois]
            n_points = len(pois)
        except Exception as e:
            messagebox.showerror("Lỗi Xử Lý Dữ Liệu", f"Lỗi khi chuẩn bị dữ liệu: {e}", parent=result_frame.master)
            return


        # 6. Chạy thuật toán GA
        ctk.CTkLabel(
            result_frame,
            text=LANG[self.language]["optimizing_n_trips"].format(n=n_points)
        ).pack(pady=10)

        result_frame.master.update_idletasks()

        # Thêm cảnh báo về thời gian
        ctk.CTkLabel(result_frame,
             text=LANG[self.language]["optimize_note"],
             font=("Arial", 10, "italic"),
             text_color="#7f8c8d").pack(pady=5)
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

            ctk.CTkLabel(result_frame,
                         text=LANG[self.language]["best_route_title"],
                         font=("Arial", 16, "bold")).pack(pady=(10, 5))

            # Hiển thị lộ trình
            route_str = ""
            for i, name in enumerate(ordered_route_names):
                route_str += f"{i+1}. {name}\n"
            route_str += LANG[self.language]["back_to_start"]

            ctk.CTkLabel(result_frame, text=route_str,
                         font=("Arial", 14), justify="left").pack(pady=10, padx=20, anchor="w")

            # Hiển thị chi phí và quãng đường
            ctk.CTkLabel(result_frame, text=f"{LANG[self.language]['total_cost_label']}: {total_cost:,.0f} VNĐ",
                         font=("Arial", 14, "bold"), text_color="#27ae60").pack(pady=5, anchor="w", padx=20)
            ctk.CTkLabel(result_frame, text=f"{LANG[self.language]['total_distance_label']}: {total_dist:.2f} km",
                         font=("Arial", 14, "bold"), text_color="#2980b9").pack(pady=5, anchor="w", padx=20)

            if budget and total_cost > budget:
                 ctk.CTkLabel(result_frame, text=LANG[self.language]["budget_warning"],
                         font=("Arial", 14, "bold"), text_color="#e74c3c").pack(pady=10, anchor="w", padx=20)

            ctk.CTkLabel(result_frame, text=ANG[self.language]["distance_note"],
                         font=("Arial", 10, "italic"), text_color="#7f8c8d").pack(pady=10, anchor="w", padx=20)

        except IndexError as e:
             messagebox.showerror(
                LANG[self.language]["index_error"],
                f"Lỗi truy cập phần tử không hợp lệ trong lộ trình: {e}" if self.language == "vi"
                else f"Invalid index in route: {e}",
                parent=result_frame.master
             )
        except Exception as e:
            msg = LANG[self.language]["algorithm_error_detail"].format(e=e)
            messagebox.showerror(LANG[self.language]["algorithm_error"], msg,
                                 parent=result_frame.master)