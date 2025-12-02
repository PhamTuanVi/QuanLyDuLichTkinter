import customtkinter as ctk
from tkinter import messagebox, filedialog, LEFT, RIGHT, Y, X, BOTH
from tkinter import ttk
from datetime import datetime, timedelta
from PIL import Image, ImageTk
from ui.login_window import LoginWindow
import os
# Import các hàm từ database.py
from database import (
    init_db, get_accounts, save_accounts, add_account, verify_account,
    save_trip, get_all_trips, get_trips_by_user, delete_trip, update_trip,
    save_timeline, get_trips_with_timeline_by_user, # Sử dụng hàm này thay vì load_pois
    save_booking_to_db, get_bookings_by_user, get_all_bookings,
    update_booking_status, delete_booking,
    add_notification, get_notifications, mark_notifications_read
)
# Import các hàm từ optimizer
from optimizer.graph import build_distance_matrix
from optimizer.ga import run_ga
import numpy as np

# Khởi tạo database (bảng bookings)
init_db()

# Cài đặt giao diện
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

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


# --- Chạy ứng dụng ---
if __name__ == "__main__":
    root = ctk.CTk()
    LoginWindow(root) # Bắt đầu với cửa sổ đăng nhập
    root.mainloop()