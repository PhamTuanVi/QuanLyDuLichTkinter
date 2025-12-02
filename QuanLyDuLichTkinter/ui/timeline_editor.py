class TimelineEditor:
    def __init__(self, current_timeline, time_var, save_callback):
        # Mở popup chỉnh sửa lịch trình
        popup = ctk.CTkToplevel(self.master)
        popup.title(LANG[self.language]["timeline"])
        popup.geometry("600x600")
        popup.grab_set()
        popup.lift()
        popup.attributes("-topmost", True)

        scroll_frame = ctk.CTkScrollableFrame(popup)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Tạo danh sách ngày dựa trên time_var
        days = []
        try:
            time_str = time_var.get()
            if " đến " in time_str: start_str, end_str = time_str.split(" đến ")
            elif " to " in time_str: start_str, end_str = time_str.split(" to ")
            else: start_str = end_str = time_str

            start_date = datetime.strptime(start_str.strip(), "%Y-%m-%d")
            end_date = datetime.strptime(end_str.strip(), "%Y-%m-%d")
            delta = end_date - start_date
            days = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(delta.days + 1)]
        except ValueError:
            messagebox.showerror("Lỗi ngày", "Định dạng ngày không hợp lệ trong ô Thời gian.", parent=popup)
            days = [datetime.now().strftime("%Y-%m-%d")] # Ngày mặc định nếu lỗi

        # Dùng dict tạm để quản lý activities theo ngày
        temp_activities = {day: [] for day in days}
        # Nạp dữ liệu cũ vào dict tạm
        for day_data in current_timeline:
            day_key = day_data.get("date")
            if day_key in temp_activities:
                temp_activities[day_key] = list(day_data.get("activities", [])) # Tạo bản copy

        # --- Hàm nội bộ để tạo UI cho từng ngày ---
        def create_day_section(day_date):
            day_frame = ctk.CTkFrame(scroll_frame, fg_color="#f5f7fa", corner_radius=10)
            day_frame.pack(fill="x", pady=5, padx=5)

            ctk.CTkLabel(day_frame, text=f"🗓️ {LANG[self.language]['day']} {day_date}",
                           font=("Arial", 13, "bold"), text_color="#2980b9").pack(anchor="w", padx=10, pady=5)

            activities_list_frame = ctk.CTkFrame(day_frame, fg_color="transparent")
            activities_list_frame.pack(fill="x", padx=10, pady=(0,5))

            # Hiển thị các activity hiện có cho ngày này
            def render_activities_for_day(target_frame, date_key):
                # Xóa các activity cũ trước khi vẽ lại
                for w in target_frame.winfo_children():
                    w.destroy()
                # Vẽ lại từ temp_activities
                for act_text in temp_activities.get(date_key, []):
                    act_frame = ctk.CTkFrame(target_frame, fg_color="transparent")
                    act_frame.pack(fill="x", pady=2)
                    ctk.CTkLabel(act_frame, text=f"• {act_text}", font=("Arial", 12),
                                   text_color="#222", justify="left", wraplength=450
                                   ).pack(side="left", padx=(0, 5), fill="x", expand=True)
                    ctk.CTkButton(act_frame, text="❌", width=30, height=25,
                                  fg_color="#e74c3c", hover_color="#c0392b",
                                  command=lambda d=date_key, a=act_text: (
                                      temp_activities[d].remove(a),
                                      render_activities_for_day(target_frame, d) # Vẽ lại list
                                  )).pack(side="right", padx=2)

            render_activities_for_day(activities_list_frame, day_date)

            # Khung thêm activity mới
            add_act_frame = ctk.CTkFrame(day_frame, fg_color="transparent")
            add_act_frame.pack(fill="x", padx=10, pady=5)
            new_act_var = ctk.StringVar()
            new_act_entry = ctk.CTkEntry(add_act_frame, textvariable=new_act_var, placeholder_text="Nhập hoạt động mới...")
            new_act_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

            def add_new_activity_action(date_key):
                activity_text = new_act_var.get().strip()
                if activity_text:
                    temp_activities[date_key].append(activity_text)
                    new_act_var.set("") # Xóa entry
                    render_activities_for_day(activities_list_frame, date_key) # Vẽ lại
            ctk.CTkButton(add_act_frame, text="➕", width=40, height=25,
                          fg_color="#27ae60", hover_color="#2ecc71",
                          command=lambda d=day_date: add_new_activity_action(d)).pack(side="left")

        # Tạo UI cho tất cả các ngày
        for d in days:
            create_day_section(d)

        # --- Nút Lưu Timeline ---
        def save_timeline_changes():
            # Tạo lại list timeline từ dict temp_activities
            new_timeline_list = []
            for day_key in days: # Duyệt theo thứ tự ngày đúng
                if temp_activities[day_key]: # Chỉ thêm nếu có activity
                    new_timeline_list.append({
                        "date": day_key,
                        "activities": temp_activities[day_key]
                    })
            save_callback(new_timeline_list) # Gọi callback để cập nhật list timeline gốc
            popup.destroy()

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="💾 " + LANG[self.language]["save_timeline"],
                      command=save_timeline_changes, width=180, height=40,
                      fg_color="#27ae60", hover_color="#2ecc71").pack()

