import matplotlib.pyplot as plt
import json
import networkx as nx
import heapq


def load_metro_map(json_file):
    with open(json_file, 'r') as file:
        return json.load(file)


def metro_map_to_dict(metro_data):
    metro_dict = {}
    for line in metro_data['lines']:
        line_name = line['name']
        stations = [station if isinstance(station, str) else station.get(
            'name', '') for station in line['stations']]
        metro_dict[line_name] = stations
    return metro_dict


def travel_time_dict(metro_data):
    return metro_data.get("Travel time", {})


def find_shortest_path(metro_data, start_station, end_station, transfer_time=5, default_travel_time=3):
    travel_times = travel_time_dict(metro_data)
    station_lines = {}
    line_stations = {}

    for line in metro_data['lines']:
        line_name = line['name']
        stations = [station if isinstance(station, str) else station.get(
            'name', '') for station in line['stations']]
        line_stations[line_name] = stations
        for station in stations:
            station_lines.setdefault(station, set()).add(line_name)

    heap = []
    visited = {}

    for line in station_lines.get(start_station, []):
        heapq.heappush(heap, (0, 0, start_station,
                       line, [(start_station, line)]))

    best_path = None
    best_cost = float('inf')
    best_transfers = None

    while heap:
        cost, transfers, station, line, path = heapq.heappop(heap)
        key = (station, line)
        if key in visited and visited[key] <= cost:
            continue
        visited[key] = cost

        if station == end_station:
            transfer_count = sum(1 for i in range(
                1, len(path)) if path[i][1] != path[i-1][1])
            if cost < best_cost:
                best_cost = cost
                best_path = path
                best_transfers = transfer_count
            continue

        stations = line_stations[line]
        idx = stations.index(station)
        for next_idx in [idx - 1, idx + 1]:
            if 0 <= next_idx < len(stations):
                next_station = stations[next_idx]
                t = travel_times.get(line, {}).get(
                    station, default_travel_time)
                heapq.heappush(
                    heap, (cost + t, transfers, next_station, line, path + [(next_station, line)]))

        for other_line in station_lines[station]:
            if other_line != line:
                heapq.heappush(heap, (cost + transfer_time, transfers + 1,
                               station, other_line, path + [(station, other_line)]))

    if best_path is None:
        return None, None, None

    station_path = [station for station, _ in best_path]
    return station_path, best_transfers, best_cost


def user_shortest_route(metro_data):
    stations = set()
    for line in metro_data['lines']:
        for station in line['stations']:
            stations.add(station if isinstance(station, str)
                         else station.get('name', ''))
    print("Available stations:")
    for s in sorted(stations):
        print(s)
    start = input("Enter start station: ").strip()
    end = input("Enter end station: ").strip()
    path, transfers, total_time = find_shortest_path(
        metro_data, start, end)
    if path is None:
        print("No route found between the selected stations.")
    else:
        print("Shortest route:")
        print(" -> ".join(path))
        print(f"Number of transfers: {transfers}")
        print(f"Total travel time: {total_time} minutes")


def draw_metro_map(metro_data, filename="metro_map.png"):
    G = nx.Graph()
    color_map = {}
    colors = [
        'red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan'
    ]

    for idx, line in enumerate(metro_data['lines']):
        color_map[line['name']] = colors[idx % len(colors)]

    for line in metro_data['lines']:
        stations = [station if isinstance(station, str) else station.get(
            'name', '') for station in line['stations']]
        for i in range(len(stations) - 1):
            G.add_edge(stations[i], stations[i+1],
                       color=color_map[line['name']])

    edge_colors = [G[u][v]['color'] for u, v in G.edges()]

    pos = nx.kamada_kawai_layout(G)
    plt.figure(figsize=(19, 9))
    nx.draw(
        G, pos, with_labels=True, node_size=200, node_color='lightblue',
        font_size=5, font_weight='bold', edge_color=edge_colors, width=2
    )
    plt.title("Metro Map (by Line Color)")
    plt.savefig(filename, bbox_inches='tight', dpi=300)
    plt.close()


def main():

    metro_data = load_metro_map('metro.json')
    metro_dict = metro_map_to_dict(metro_data)
    draw_metro_map(metro_data)
    user_shortest_route(metro_data)


if __name__ == "__main__":
    main()
