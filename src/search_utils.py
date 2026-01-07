import heapq
from collections import deque

class Node:
    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost

    def child_node(self, problem, action):
        next_state = problem.result(self.state, action)
        return Node(next_state, self, action, self.path_cost + 1)

    def path(self):
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    def __lt__(self, node):
        return self.path_cost < node.path_cost

def astar_search(problem):
    """A* Search: Applies the formula f(n) = g(n) + h(n)."""
    node = Node(problem.initial)
    frontier = []
    # (f_value, node)
    heapq.heappush(frontier, (problem.h(node), node))
    explored = {}

    while frontier:
        f, node = heapq.heappop(frontier)
        if problem.goal_test(node.state): return node
        
        if node.state in explored and explored[node.state] <= node.path_cost:
            continue
        explored[node.state] = node.path_cost
        
        for action in problem.actions(node.state):
            child = node.child_node(problem, action)
            if child.state not in explored or child.path_cost < explored[child.state]:
                f_n = child.path_cost + problem.h(child)
                heapq.heappush(frontier, (f_n, child))
    return None

def bfs(problem):
    node = Node(problem.initial)
    if problem.goal_test(node.state): return node
    frontier = deque([node])
    explored = {node.state}
    while frontier:
        node = frontier.popleft()
        for action in problem.actions(node.state):
            child = node.child_node(problem, action)
            if child.state not in explored:
                if problem.goal_test(child.state): return child
                explored.add(child.state)
                frontier.append(child)
    return None

def dfs(problem):
    frontier = [Node(problem.initial)]
    explored = set()
    while frontier:
        node = frontier.pop()
        if problem.goal_test(node.state): return node
        if node.state not in explored:
            explored.add(node.state)
            for action in problem.actions(node.state):
                child = node.child_node(problem, action)
                frontier.append(child)
    return None

def greedy_search(problem):
    node = Node(problem.initial)
    frontier = []
    heapq.heappush(frontier, (problem.h(node), node))
    explored = set()
    while frontier:
        _, node = heapq.heappop(frontier)
        if problem.goal_test(node.state): return node
        explored.add(node.state)
        for action in problem.actions(node.state):
            child = node.child_node(problem, action)
            if child.state not in explored:
                heapq.heappush(frontier, (problem.h(child), child))
    return None

