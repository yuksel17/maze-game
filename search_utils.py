import heapq

class Node:
    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost

    def path(self):
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    def __lt__(self, node):
        return self.path_cost < node.path_cost

def astar_search(problem):
    # f(n) = g(n) + h(n) değerine göre sıralama yapan Priority Queue
    node = Node(problem.initial)
    frontier = []
    heapq.heappush(frontier, (problem.h(node), node))
    explored = set()

    while frontier:
        _, node = heapq.heappop(frontier)
        if problem.goal_test(node.state):
            return node
        
        state_key = (node.state[0], tuple(node.state[1]))
        if state_key not in explored:
            explored.add(state_key)
            for action in problem.actions(node.state):
                child_state = problem.result(node.state, action)
                # Her adım maliyeti 1'dir. g(n) = node.path_cost + 1
                child = Node(child_state, node, action, node.path_cost + 1)
                heapq.heappush(frontier, (child.path_cost + problem.h(child), child))
    return None

# BFS için de aynısı (Zaten en kısayı bulur ama garantileyelim)
from collections import deque
def bfs(problem):
    node = Node(problem.initial)
    if problem.goal_test(node.state): return node
    frontier = deque([node])
    explored = { (node.state[0], tuple(node.state[1])) }
    while frontier:
        node = frontier.popleft()
        for action in problem.actions(node.state):
            child_state = problem.result(node.state, action)
            child = Node(child_state, node, action, node.path_cost + 1)
            state_key = (child.state[0], tuple(child.state[1]))
            if state_key not in explored:
                if problem.goal_test(child.state): return child
                explored.add(state_key)
                frontier.append(child)
    return None
