import random
import numpy as np

# ==========================
#  GA Tối ưu hành trình du lịch
# ==========================

def calculate_distance(route, dist_matrix):
    total = 0
    for i in range(len(route) - 1):
        total += dist_matrix[route[i]][route[i + 1]]
    total += dist_matrix[route[-1]][route[0]]  # quay lại điểm đầu
    return total


def calculate_cost(route, price_list):
    return sum(price_list[i] for i in route)


def fitness(route, dist_matrix, price_list, w1=0.7, w2=0.3, budget=None):
    d = calculate_distance(route, dist_matrix)
    c = calculate_cost(route, price_list)
    penalty = 0
    if budget and c > budget:
        penalty = (c - budget) * 10
    return w1 * d + w2 * c + penalty


def create_population(size, n_points):
    population = []
    for _ in range(size):
        route = list(range(n_points))
        random.shuffle(route)
        population.append(route)
    return population


def crossover(parent1, parent2):
    start, end = sorted(random.sample(range(len(parent1)), 2))
    child = [None] * len(parent1)
    child[start:end] = parent1[start:end]
    pos = end
    for gene in parent2:
        if gene not in child:
            if pos >= len(parent1):
                pos = 0
            child[pos] = gene
            pos += 1
    return child


def mutate(route, rate=0.1):
    for i in range(len(route)):
        if random.random() < rate:
            j = random.randint(0, len(route) - 1)
            route[i], route[j] = route[j], route[i]


def run_ga(dist_matrix, price_list, generations=200, pop_size=30, w1=0.7, w2=0.3, budget=None):
    n_points = len(dist_matrix)
    population = create_population(pop_size, n_points)

    best_route = None
    best_fit = float("inf")

    for gen in range(generations):
        scored = [(route, fitness(route, dist_matrix, price_list, w1, w2, budget)) for route in population]
        scored.sort(key=lambda x: x[1])

        if scored[0][1] < best_fit:
            best_fit = scored[0][1]
            best_route = scored[0][0]

        # chọn 50% tốt nhất để sinh con
        survivors = [route for route, _ in scored[:pop_size // 2]]
        new_population = survivors.copy()

        # lai ghép sinh con
        while len(new_population) < pop_size:
            p1, p2 = random.sample(survivors, 2)
            child = crossover(p1, p2)
            mutate(child, 0.1)
            new_population.append(child)

        population = new_population

    return best_route, best_fit

