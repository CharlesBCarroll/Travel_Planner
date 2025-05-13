import csv
import heapq
import math

class Location:
    def __init__(self, country, name, lat, lon):
        self.country = country
        self.name = name
        self.lat = lat
        self.lon = lon

class Graph:
    def __init__(self, cities_file, routes_file):
        self.locations = {}
        self.adj = {}
        self.load_cities(cities_file)
        self.load_routes(routes_file)

    def load_cities(self, filename):
        with open(filename, newline='') as f:
            reader = csv.reader(f)
            for country, city, lat, lon in reader:
                loc = Location(country, city, float(lat), float(lon))
                self.locations[city] = loc
                self.adj[city] = []

    def load_routes(self, filename):
        with open(filename, newline='') as f:
            reader = csv.reader(f)
            for orig, dest, transport, time, cost, note in reader:
                t = float(time)
                c = float(cost)
                if transport == 'plane':
                    c *= 3
                # undirected edge
                self.adj[orig].append((dest, t, c))
                self.adj[dest].append((orig, t, c))

    def dijkstra(self, start, weight='time'):
        dist = {name: math.inf for name in self.locations}
        dist[start] = 0
        prev = {name: None for name in self.locations}
        pq = [(0, start)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            for v, t, c in self.adj[u]:
                w = c if weight=='cost' else t
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(pq, (nd, v))
        return dist, prev

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        to_rad = math.radians
        dlat = to_rad(lat2 - lat1)
        dlon = to_rad(lon2 - lon1)
        a = (math.sin(dlat/2)**2 +
             math.cos(to_rad(lat1)) * math.cos(to_rad(lat2)) *
             math.sin(dlon/2)**2)
        return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    def shortest_distance(self, orig, dest, weight='time'):
        if weight == 'distance':
            o = self.locations[orig]
            d = self.locations[dest]
            return Graph.haversine(o.lat, o.lon, d.lat, d.lon)
        dist, _ = self.dijkstra(orig, weight)
        return dist.get(dest, math.inf)

    def tsp_path(self, cities, weight='time'):
        n = len(cities)
        if n <= 2:
            return cities[:]
        # build n x n distance matrix
        mat = [[0]*n for _ in range(n)]

        if weight == 'distance':
            # direct haversine distances
            for i, ci in enumerate(cities):
                o = self.locations[ci]
                for j, cj in enumerate(cities):
                    d = self.locations[cj]
                    mat[i][j] = Graph.haversine(o.lat, o.lon, d.lat, d.lon)
        else:
            # precompute shortest paths by Dijkstra for time or cost
            for i, ci in enumerate(cities):
                dist, _ = self.dijkstra(ci, weight)
                for j, cj in enumerate(cities):
                    mat[i][j] = dist.get(cj, math.inf)
        m = n - 2
        dp = {}
        parent = {}
        # DP over subsets of intermediate cities
        for mask in range(1<<m):
            for j in range(1, n-1):
                bit = 1<<(j-1)
                if mask & bit:
                    prev_mask = mask ^ bit
                    if prev_mask == 0:
                        dp[(mask,j)] = mat[0][j]
                        parent[(mask,j)] = 0
                    else:
                        best = math.inf
                        best_k = None
                        for k in range(1, n-1):
                            if prev_mask & (1<<(k-1)):
                                cand = dp[(prev_mask,k)] + mat[k][j]
                                if cand < best:
                                    best = cand
                                    best_k = k
                        dp[(mask,j)] = best
                        parent[(mask,j)] = best_k
        full_mask = (1<<m) - 1
        best = math.inf
        best_j = None
        for j in range(1, n-1):
            cost = dp[(full_mask,j)] + mat[j][n-1]
            if cost < best:
                best = cost
                best_j = j
        if best_j is None:
            raise ValueError("No path found")
        # reconstruct path indices
        path_indices = [n-1]
        mask = full_mask
        j = best_j
        while mask:
            path_indices.append(j)
            prev_j = parent[(mask,j)]
            mask ^= 1<<(j-1)
            j = prev_j
        path_indices.append(0)
        path_indices.reverse()
        return [cities[i] for i in path_indices]
