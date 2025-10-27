
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
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                coord1 = (pois[i]['lat'], pois[i]['lon'])
                coord2 = (pois[j]['lat'], pois[j]['lon'])
                dist[i][j] = haversine(coord1, coord2)
    return dist


