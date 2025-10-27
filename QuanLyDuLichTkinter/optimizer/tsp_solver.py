import numpy as np

# Danh sách địa điểm
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


def nearest_neighbor(start=0):
    n = len(dist_matrix)
    visited = [False] * n
    path = [start]
    visited[start] = True
    total_distance = 0

    current = start
    for _ in range(n - 1):
        nearest = None
        nearest_dist = float("inf")

        for j in range(n):
            if not visited[j] and dist_matrix[current][j] < nearest_dist:
                nearest = j
                nearest_dist = dist_matrix[current][j]

        path.append(nearest)
        visited[nearest] = True
        total_distance += nearest_dist
        current = nearest

    # Quay lại điểm đầu
    total_distance += dist_matrix[current][start]
    path.append(start)
    return path, total_distance
def calculate_total_distance(path):
    total = 0
    for i in range(len(path) - 1):
        total += dist_matrix[path[i]][path[i + 1]]
    return total


def two_opt(path):
    best = path
    improved = True
    while improved:
        improved = False
        for i in range(1, len(path) - 2):
            for j in range(i + 1, len(path) - 1):
                if j - i == 1:
                    continue
                new_path = path[:]
                new_path[i:j] = path[j - 1:i - 1:-1]
                if calculate_total_distance(new_path) < calculate_total_distance(best):
                    best = new_path
                    improved = True
        path = best
    return best

if __name__ == "__main__":
    # Bước 1: TSP Greedy
    path, dist = nearest_neighbor(0)
    print("=== Kết quả Greedy ===")
    print(" → ".join(places[i] for i in path))
    print(f"Tổng quãng đường: {dist:.2f} km\n")

    # Bước 2: Cải thiện bằng 2-opt
    improved_path = two_opt(path)
    improved_dist = calculate_total_distance(improved_path)
    print("=== Sau khi tối ưu bằng 2-opt ===")
    print(" → ".join(places[i] for i in improved_path))
    print(f"Tổng quãng đường tối ưu: {improved_dist:.2f} km")


