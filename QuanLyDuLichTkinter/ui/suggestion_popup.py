class SuggestionPopup:
    def open_suggestion_popup(self,master, trips, run_callback):
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