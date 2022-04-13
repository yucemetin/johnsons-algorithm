from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt


class PrintGraph:

    def __init__(self):
        self.visual = []
        self.G = nx.Graph()

    def addEdge(self, li):
        self.visual.append(li)

    def visualize(self, title, edges=[]):
        self.G.add_weighted_edges_from(self.visual)
        self.G.edges(data=True)
        pos = nx.circular_layout(self.G)
        labels = nx.get_edge_attributes(self.G, 'weight')
        nx.draw(self.G, pos, node_color='pink', node_size=500, font_size=15, font_color='black', edge_color='gold',
                width=1, with_labels=True)
        nx.draw_networkx_edges(self.G, pos, edgelist=edges, width=2, edge_color='red')
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=labels, font_size=10)
        ax = plt.gca()
        ax.margins(0, 0.1)
        plt.axis("off")
        plt.suptitle(title)
        plt.show()

    def clearGraph(self):
        self.visual.clear()

    def changeGraph(self, mapping):
        self.G = nx.relabel_nodes(self.G, mapping)


class Graph:

    def __init__(self, vertices):
        self.V = vertices + 1  # Node sayısı , +1 olmasının sebebi sıfırıncı node'un eklenmesi
        self.graph = []  # Graphın tutulduğu liste
        self.G = PrintGraph()
        self.nG = PrintGraph()
        self.dist = []  # Mesafelerin tutulduğu liste
        self.nodes = set()  # node'ların tutulduğu liste
        self.edges = defaultdict(list)  # kenarların tutulduğu liste
        self.distances = {}

    def checkNode(self,u):  # Sıfırıncı node'u eklerken  diğer node'lar arasında bağlantının olup olmadığını kontrol eden method
        for x in range(len(self.graph)):
            if u + 1 == self.graph[x][0]:
                return False
        return True

    def addEdge(self, u, v, w):

        if self.checkNode(u):  # Eklenen her node ile sıfırıncı nodun bağlantısı
            self.graph.append([0, u + 1, 0])
            self.G.addEdge([0, u + 1, 0])

        self.graph.append([u + 1, v + 1, w])
        self.G.addEdge([u + 1, v + 1, w])

    def BellmanFord(self, src):

        for i in range(self.V):
            self.dist.append(float("Inf"))  # İnitial node hariç tüm node'ların maliyetlerinin sonsuz yapılması
        self.dist[src] = 0
        self.G.clearGraph()

        for u, v, w in self.graph:  # Oluşturulan graphın görselleştirilmesi
            self.G.addEdge([str(u) + "/" + str(self.dist[u]), str(v) + "/" + str(self.dist[v]), w])
        self.G.visualize("Default")
        self.G.clearGraph()

        for i in range(self.V - 1):  # BellmanFord algoritması
            for u, v, w in self.graph:
                value = self.dist[v]
                if self.dist[u] != float("Inf") and self.dist[u] + w < self.dist[v]:
                    self.dist[v] = self.dist[u] + w
                edges = [[str(u) + "/" + str(self.dist[u]), str(v) + "/" + str(self.dist[v])]]
                mapping = {str(v) + "/" + str(value): str(v) + "/" + str(self.dist[v])}
                self.G.changeGraph(mapping)
                #self.G.visualize("BellmanFord", edges)
        self.G.visualize("BellmanFord")

    def Reweight(self):  # ikinci adım olarak tüm mesafelerin tekrar hesaplanarak negatif mesafelerin pozitife çevirilmesi.
        self.G.clearGraph()
        say = 0
        for u, v, w in self.graph:
            w = self.dist[u] + w - self.dist[v]
            self.graph[say][2] = w
            self.G.addEdge([str(u) + "/" + str(self.dist[u]), str(v) + "/" + str(self.dist[v]), w])
            say = say + 1

        self.G.visualize("Reweight")

    def RemoveNodeZero(self):  # üçüncü adım olarak ilk adımda eklenen sıfırıncı node'un silinmesi
        for u, v, w in self.graph:
            if u == 0:
                self.graph.remove([u, v, w])

        self.nG.clearGraph()
        for u, v, w in self.graph:
            self.nG.addEdge([str(u) + "/" + str(self.dist[u]), str(v) + "/" + str(self.dist[v]), w])
        self.nG.visualize("Delete Zero Node")

    def dijkstra(self, initial):

        for u, v, w in self.graph:
            self.nodes.add(u)

        for u, v, w in self.graph:
            self.edges[u].append(v)
            self.distances[(u, v)] = w

        visited = {initial: 0}
        path = defaultdict(list)

        nodes = set(self.nodes)
        while nodes:
            minNode = None
            for node in nodes:
                if node in visited:
                    if minNode is None:
                        minNode = node
                    elif visited[node] < visited[minNode]:
                        minNode = node
            if minNode is None:
                break

            nodes.remove(minNode)
            currentWeight = visited[minNode]
            print(self.edges[minNode])
            for edge in self.edges[minNode]:
                print("edge : " + str(edge))
                weight = currentWeight + self.distances[(minNode, edge)]
                print(self.distances[(minNode, edge)])
                if edge not in visited or weight < visited[edge]:
                    visited[edge] = weight
                    path[edge].append(minNode)

        return visited, path

    def Johnsons(self, src):
        self.BellmanFord(src)
        self.Reweight()
        self.G.clearGraph()
        self.RemoveNodeZero()
        initial = 2
        result = self.dijkstra(initial)
        self.nG.clearGraph()
        print(result)

        edges = []
        temp = initial
        say = 0
        for x in result[1]:
            for y in result[1]:
                if result[1][y][-1] == temp:
                    edges.append([temp, y])
            temp = edges[say][-1]
            say = say + 1
        print(edges)

        for y in range(1, self.V):
            if str(y) == str(initial):
                mapping = {str(y) + "/" + str(self.dist[y]): str(y) + "/" + str(0)}
            else:
                mapping = {str(y) + "/" + str(self.dist[y]): str(y) + "/" + str(float("Inf"))}
            self.nG.changeGraph(mapping)
        self.nG.visualize("Dijkstra")

        self.nG.clearGraph()
        """
        for i in range(1, self.V):
            mapping = {str(i) + "/" + str(float("Inf")): str(i) + "/" + str(result[0][i])}
            self.nG.changeLabel(mapping)
        self.nG.visualize("Dijkstra Son")"""

        gedges = []
        strPath = ""
        for edge in edges:
            strPath += str(edge[0]) + "=>" + str(edge[1]) + " | "
            gedges.append([str(edge[0]) + "/" + str(result[0][edge[0]]), str(edge[1]) + "/" + str(result[0][edge[1]])])
            mapping = {str(edge[1]) + "/" + str(float("Inf")): str(edge[1]) + "/" + str(result[0][edge[1]])}
            self.nG.changeGraph(mapping)
            self.nG.visualize(strPath, gedges)


g = Graph(5)
g.addEdge(0, 1, 3)
g.addEdge(0, 2, 8)
g.addEdge(0, 4, -4)
g.addEdge(1, 3, 1)
g.addEdge(1, 4, 7)
g.addEdge(2, 1, 4)
g.addEdge(3, 2, -5)
g.addEdge(3, 0, 2)
g.addEdge(4, 3, 6)

g.Johnsons(0)
