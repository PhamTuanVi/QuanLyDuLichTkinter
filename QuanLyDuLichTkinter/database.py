import json
import os
import hashlib
import sqlite3
import sys
from datetime import datetime

def get_data_dir():
    if getattr(sys, 'frozen', False):
        # Đường dẫn khi đã đóng gói thành .exe
        base_dir = os.path.dirname(sys.executable)
    else:
        # Đường dẫn khi chạy file .py bình thường
        base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def get_image_dir():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(__file__)
    return os.path.join(base_dir, 'image')

IMAGE_PATH = os.path.join(get_image_dir(), 'map.webp')

# Đường dẫn đến các file dữ liệu
DATA_PATH = os.path.join(get_data_dir(), 'QLDL.json')
ACCOUNT_PATH = os.path.join(get_data_dir(), 'accounts.json')
TIMELINE_PATH = os.path.join(get_data_dir(), 'QLDL_timelines.json')
NOTIFY_PATH = os.path.join(get_data_dir(), 'notifications.json')
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
BOOKINGS_PATH = os.path.join(DATA_DIR, "bookings.json")
# POI_PATH = os.path.join(get_data_dir(), 'poi.json') # Không cần nữa nếu chỉ dùng QLDL.json


def ensure_dir(file_path):
    # Đảm bảo thư mục chứa file tồn tại
    os.makedirs(os.path.dirname(file_path), exist_ok=True)


def hash_password(password):
    # Băm mật khẩu
    return hashlib.sha256(password.encode()).hexdigest()


def get_accounts():
    # Lấy danh sách tài khoản từ file accounts.json
    if not os.path.exists(ACCOUNT_PATH):
        # Nếu file chưa tồn tại, tạo tài khoản mặc định
        default_accounts = [
            {'username': 'admin', 'password': hash_password('admin123'), 'role': 'admin'},
            {'username': 'user', 'password': hash_password('user123'), 'role': 'user'}
        ]
        save_accounts(default_accounts)
        return default_accounts

    try:
        with open(ACCOUNT_PATH, 'r', encoding='utf8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print(f"Lỗi: Không đọc được file {ACCOUNT_PATH} hoặc file bị lỗi.")
        return []

def save_accounts(accounts):
    # Lưu danh sách tài khoản vào file accounts.json
    ensure_dir(ACCOUNT_PATH)
    try:
        with open(ACCOUNT_PATH, 'w', encoding='utf8') as f:
            json.dump(accounts, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Lỗi khi lưu file accounts: {e}")

def add_account(username, password, role):
    # Thêm tài khoản mới
    accounts = get_accounts()
    for acc in accounts:
        if acc['username'] == username:
            return False # Tài khoản đã tồn tại

    accounts.append({
        'username': username,
        'password': hash_password(password),
        'role': role
    })
    save_accounts(accounts)
    return True

def verify_account(username, password):
    # Xác thực tài khoản khi đăng nhập
    accounts = get_accounts()
    hashed_pw = hash_password(password)
    for acc in accounts:
        if acc['username'] == username and acc['password'] == hashed_pw:
            return acc['role']
    return None


def save_trip(data, username=None):
    # Lưu một chuyến đi mới vào QLDL.json
    ensure_dir(DATA_PATH)
    data['created_by'] = username

    trips = get_all_trips()
    trips.append(data)

    try:
        with open(DATA_PATH, 'w', encoding='utf8') as f:
            json.dump(trips, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Lỗi khi lưu file chuyến đi: {e}")

def get_all_trips():
    # Lấy tất cả chuyến đi từ QLDL.json
    if not os.path.exists(DATA_PATH):
        return []

    try:
        with open(DATA_PATH, 'r', encoding='utf8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print(f"Lỗi: Không đọc được file {DATA_PATH} hoặc file bị lỗi.")
        return []

def get_trips_by_user(username=None, role=None):
    # Lấy danh sách chuyến đi (admin thấy hết, user thấy hết trong bản này)
    # Nếu muốn user chỉ thấy chuyến của họ, cần thêm logic lọc theo 'created_by'
    trips = get_all_trips()
    if role == "admin":
        return trips
    # Hiện tại user cũng thấy hết
    return trips
    # Nếu muốn user chỉ thấy chuyến họ tạo:
    # return [trip for trip in trips if trip.get('created_by') == username]


def delete_trip(index, username=None, role=None):
    # Xóa chuyến đi theo index
    trips = get_all_trips()
    if 0 <= index < len(trips):
        # Chỉ admin hoặc người tạo mới được xóa
        if role == 'admin' or trips[index].get('created_by') == username:
            trips.pop(index)
            try:
                with open(DATA_PATH, 'w', encoding='utf8') as f:
                    json.dump(trips, f, ensure_ascii=False, indent=4)
                return True
            except IOError as e:
                 print(f"Lỗi khi xóa chuyến đi: {e}")
                 return False
    return False

def update_trip(index, new_data, username=None, role=None):
    # Cập nhật thông tin chuyến đi theo index
    trips = get_all_trips()
    if 0 <= index < len(trips):
         # Chỉ admin hoặc người tạo mới được sửa
        if role == 'admin' or trips[index].get('created_by') == username:
            new_data['created_by'] = trips[index].get('created_by') # Giữ nguyên người tạo
            trips[index].update(new_data) # Dùng update để chỉ sửa các field có trong new_data
            try:
                with open(DATA_PATH, 'w', encoding='utf8') as f:
                    json.dump(trips, f, ensure_ascii=False, indent=4)
                return True
            except IOError as e:
                 print(f"Lỗi khi cập nhật chuyến đi: {e}")
                 return False
    return False

def save_timeline(trip_index, timeline, username=None, role=None):
    # Lưu lịch trình cho một chuyến đi cụ thể
    ensure_dir(TIMELINE_PATH)
    timelines = {}
    if os.path.exists(TIMELINE_PATH):
        try:
            with open(TIMELINE_PATH, 'r', encoding='utf8') as f:
                timelines = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            timelines = {}

    trips = get_all_trips()
    if 0 <= trip_index < len(trips):
         # Chỉ admin hoặc người tạo mới được sửa lịch trình
        if role == 'admin' or trips[trip_index].get('created_by') == username:
            timelines[str(trip_index)] = timeline # Dùng index làm key
            try:
                with open(TIMELINE_PATH, 'w', encoding='utf8') as f:
                    json.dump(timelines, f, ensure_ascii=False, indent=4)
                return True
            except IOError as e:
                print(f"Lỗi khi lưu timeline: {e}")
                return False
    return False

def load_json(path, default=None):
    if default is None:
        default = []
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, UnicodeDecodeError):
        return default


def save_json(path, data):
        ensure_dir(path)
        with open(path, "w", encoding="utf8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

def get_trips_with_timeline_by_user(username=None, role=None):
    # Lấy danh sách chuyến đi kèm theo lịch trình của chúng
    trips = get_trips_by_user(username, role)
    timelines = {}
    if os.path.exists(TIMELINE_PATH):
        try:
            with open(TIMELINE_PATH, 'r', encoding='utf8') as f:
                timelines = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            timelines = {}

    for idx, trip in enumerate(trips):
        trip['timeline'] = timelines.get(str(idx), []) # Lấy timeline theo index
    return trips

# --- Phần database SQLite cho Booking ---

def init_db():
    # Khởi tạo bảng bookings trong travel.db nếu chưa có
    try:
        conn = sqlite3.connect("travel.db")
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_idx INTEGER,
            trip_name TEXT,
            username TEXT,
            name TEXT,
            email TEXT,
            quantity INTEGER,
            status TEXT DEFAULT 'Chờ xác nhận'
        )''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Lỗi SQLite khi khởi tạo DB: {e}")


def save_booking_to_db(trip_index, trip_name, username,
                       customer_name, email, qty,
                       details=None):
    """
    details: có thể là list các điểm trong tour nhiều địa điểm.
    """
    bookings = load_json(BOOKINGS_PATH, [])

    # Tạo id đơn giản: số lượng hiện tại + 1
    new_id = (bookings[-1]["id"] + 1) if bookings else 1

    booking = {
        "id": new_id,
        "username": username,
        "trip_name": trip_name,
        "customer_name": customer_name,
        "email": email,
        "qty": int(qty),
        "status": "pending",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "details": details or []      # <- chỗ lưu tour nhiều địa điểm
    }

    bookings.append(booking)
    save_json(BOOKINGS_PATH, bookings)
    return True

def get_bookings_by_user(username):
    bookings = load_json(BOOKINGS_PATH, [])
    return [b for b in bookings if b.get("username") == username]

def get_all_bookings():
    return load_json(BOOKINGS_PATH, [])

def update_booking_status(booking_id, new_status):
    bookings = load_json(BOOKINGS_PATH, [])
    updated = False
    for b in bookings:
        if b.get("id") == booking_id:
            b["status"] = new_status
            updated = True
            break
    if updated:
        save_json(BOOKINGS_PATH, bookings)
    return updated

def delete_booking(booking_id):
    # Xóa booking (admin dùng)
    try:
        conn = sqlite3.connect("travel.db")
        c = conn.cursor()
        c.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Lỗi SQLite khi xóa booking: {e}")
        return False

# --- Phần Thông báo (Notifications) ---

def add_notification(username, message):
    # Thêm thông báo mới
    ensure_dir(NOTIFY_PATH)
    noti = []
    if os.path.exists(NOTIFY_PATH):
        try:
            with open(NOTIFY_PATH, 'r', encoding='utf8') as f:
                noti = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            noti = []

    noti.append({"username": username, "message": message, "read": False, "timestamp": datetime.now().isoformat()})

    try:
        with open(NOTIFY_PATH, 'w', encoding='utf8') as f:
            json.dump(noti, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Lỗi khi thêm notification: {e}")

def get_notifications(username):
    # Lấy các thông báo chưa đọc của user
    if not os.path.exists(NOTIFY_PATH):
        return []
    try:
        with open(NOTIFY_PATH, 'r', encoding='utf8') as f:
            noti = json.load(f)
        # Lọc và sắp xếp theo thời gian mới nhất trước
        user_noti = [n for n in noti if n.get("username") == username and not n.get("read")]
        user_noti.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return user_noti
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def mark_notifications_read(username):
    # Đánh dấu tất cả thông báo của user là đã đọc
    if not os.path.exists(NOTIFY_PATH):
        return
    try:
        with open(NOTIFY_PATH, 'r', encoding='utf8') as f:
            noti = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return

    updated = False
    for n in noti:
        if n.get("username") == username and not n.get("read"):
            n["read"] = True
            updated = True

    if updated:
        try:
            with open(NOTIFY_PATH, 'w', encoding='utf8') as f:
                json.dump(noti, f, ensure_ascii=False, indent=4)
        except IOError as e:
             print(f"Lỗi khi đánh dấu notification đã đọc: {e}")

