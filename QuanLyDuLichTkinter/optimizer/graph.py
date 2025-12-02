
import math

import numpy as np


# Hàm tính khoảng cách giữa 2 tọa độ (Haversine Formula)
def haversine(coord1, coord2):
    R = 6371  # Bán kính Trái Đất (km)
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    return R * 2 * math.asin(math.sqrt(a))




# Xây dựng ma trận khoảng cách (Distance Matrix)
def build_distance_matrix(pois):
    n = len(pois)
    dist = np.zeros((n, n), dtype=float)

    for i in range(n):
        for j in range(n):
            if i == j:
                dist[i][j] = 0.0
            else:
                # lấy theo key 'lat', 'lon' thay vì [0], [1]
                lat1 = float(pois[i]['lat'])
                lon1 = float(pois[i]['lon'])
                lat2 = float(pois[j]['lat'])
                lon2 = float(pois[j]['lon'])

                coord1 = (lat1, lon1)
                coord2 = (lat2, lon2)
                dist[i][j] = haversine(coord1, coord2)

    return dist

