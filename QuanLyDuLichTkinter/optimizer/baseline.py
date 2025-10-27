import heapq

def dijkstra(graph, start):
    dist = {node: float('inf') for node in graph}
    dist[start] = 0
    pq = [(0, start)]
    while pq:
        d, node = heapq.heappop(pq)
        if d > dist[node]:
            continue
        for neighbor, weight in graph[node]:
            new_d = d + weight
            if new_d < dist[neighbor]:
                dist[neighbor] = new_d
                heapq.heappush(pq, (new_d, neighbor))
    return dist
