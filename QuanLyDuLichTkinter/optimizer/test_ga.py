from ga import run_ga
import numpy as np

# Danh sách điểm
places = [
    "Hồ Hoàn Kiếm",
    "Văn Miếu Quốc Tử Giám",
    "Lăng Bác",
    "Chùa Một Cột",
    "Hoàng Thành Thăng Long"
]

# Ma trận khoảng cách (km)
dist_matrix = np.array([
    [0.00, 1.95, 2.31, 2.25, 1.65],
    [1.95, 0.00, 1.02, 0.79, 0.87],
    [2.31, 1.02, 0.00, 0.24, 0.67],
    [2.25, 0.79, 0.24, 0.00, 0.64],
    [1.65, 0.87, 0.67, 0.64, 0.00]
])

# Giá vé mẫu (ngàn đồng)
price_list = [0, 30, 40, 10, 25]

best_route, best_fit = run_ga(dist_matrix, price_list, generations=200, pop_size=40, budget=100)

route_names = [places[i] for i in best_route] + [places[best_route[0]]]
print("=== Kết quả GA ===")
print(" → ".join(route_names))
print(f"Giá trị tối ưu (fitness): {best_fit:.2f}")

