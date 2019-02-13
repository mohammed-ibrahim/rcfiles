import sys



class Graph():

    def __init__(self, V):
        self.number_of_vertices = V
        self.graph = [[0 for column in range(self.number_of_vertices)]
                      for row in range(self.number_of_vertices)]

    # this part can be optimised
    def find_min_distance(self, distance, already_visited):

        min = sys.maxint
        min_index = 0

        for i in range(self.number_of_vertices):
            if already_visited[i] == False and min > distance[i]:
                min = distance[i]
                min_index = i

        return min_index

    def find_shortest_path(self, src):
        distance = [sys.maxint] * self.number_of_vertices
        already_visited = [False] * self.number_of_vertices
        distance[src] = 0

        for i in range(self.number_of_vertices):
            min_index = self.find_min_distance(distance, already_visited)
            already_visited[min_index] = True

            for j in range(self.number_of_vertices):
                if already_visited[j] == False and self.graph[min_index][j] > 0:
                    if distance[j] > distance[min_index] + self.graph[min_index][j]:
                        distance[j] = distance[min_index] + self.graph[min_index][j]

        self.printSolution(distance)

    def printSolution(self, dist):
        print "Vertex Distance from Source"
        for node in range(self.number_of_vertices):
            print("Node: %d distance: %d", node, dist[node])

a = [[0, 4, 0, 0, 0, 0, 0, 8, 0],
   [4, 0, 8, 0, 0, 0, 0, 11, 0],
   [0, 8, 0, 7, 0, 4, 0, 0, 2],
   [0, 0, 7, 0, 9, 14, 0, 0, 0],
   [0, 0, 0, 9, 0, 10, 0, 0, 0],
   [0, 0, 4, 14, 10, 0, 2, 0, 0],
   [0, 0, 0, 0, 0, 2, 0, 1, 6],
   [8, 11, 0, 0, 0, 0, 1, 0, 7],
   [0, 0, 2, 0, 0, 0, 6, 7, 0]
  ];

graph = Graph(9)
graph.graph = a
graph.find_shortest_path(0)
