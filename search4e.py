#!/usr/bin/env python
# coding: utf-8

# In[76]:


from utils4e import is_in


class Problem:
    def __init__(self, initial, goal=None):
        self.initial = initial  # Initial state of guitarist. i.e. (String 6, Fret 5, Finger: Point Finger)
        self.goal = goal        # The riff that guitarist will achieve or last note of riff.

    def actions(self, state):
        # I am on the that state. Where can I go from here?
        # Some constraints can be considered here.
        # For example; we can not go on further from 22th fret.
        raise NotImplementedError

    def result(self, state, action):
        # What if I am done this action.
        # Let action be putting point finger to the 5th fret.
        # Result will be (String:4, Fret:5, Finger: Point Finger)
        raise NotImplementedError

    def goal_test(self, state):
        # It will check whether all the notes on the given riff is played.
        if isinstance(self.goal, list):
            return is_in(state, self.goal)
        else:
            return state == self.goal

    def path_cost(self, c, state1, action, state2):
        # Some calculations are made here. For example;
        # Current Cost = Current Cost + Fret difference + String changing penalty
        return c + 1


class Node:
    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state  # Current state of guitarist (String,Fret,Finger)
        self.parent = parent  # Previous note
        self.action = action  # Which movement is done
        self.path_cost = path_cost  # What is the cost from the beginning?

    def __lt__(self, other):
        # Needed for heapq comparisons when f(n) ties
        return id(self) < id(other)

    def expand(self, problem):
        # The notes that can be played after current note.
        return [self.child_node(problem, action)
                for action in problem.actions(self.state)]

    def child_node(self, problem, action):
        next_state = problem.result(self.state, action)
        next_node = Node(
            next_state,
            self,
            action,
            problem.path_cost(self.path_cost, self.state, action, next_state)
        )
        return next_node

    def solution(self):
        # Output of the playing queue.
        # Answer of the question : Which fingers should I press in what order?
        # It can return a list.
        return [node.action for node in self.path()[1:]]

    def path(self):
        # It can also be a solution from root node to goal node.
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))


# # Search Algorithms: Best-First
# 
# Best-first search with various *f(n)* functions gives us different search algorithms. Note that A\*, weighted A\* and greedy search can be given a heuristic function, `h`, but if `h` is not supplied they use the problem's default `h` function (if the problem does not define one, it is taken as *h(n)* = 0).

# In[77]:


from uri_template import expand
from utils4e import PriorityQueue


def best_first_search(problem, f):
    "Search nodes with minimum f(node) value first."
    node = Node(problem.initial)
    frontier = PriorityQueue([node], key=f)
    reached = {problem.initial: node}
    while frontier:
        node = frontier.pop()
        if problem.is_goal(node.state):
            return node
        for child in expand(problem, node):
            s = child.state
            if s not in reached or child.path_cost < reached[s].path_cost:
                reached[s] = child
                frontier.add(child)
    return failure


def best_first_tree_search(problem, f):
    "A version of best_first_search without the `reached` table."
    frontier = PriorityQueue([Node(problem.initial)], key=f)
    while frontier:
        node = frontier.pop()
        if problem.is_goal(node.state):
            return node
        for child in expand(problem, node):
            if not is_cycle(child):
                frontier.add(child)
    return failure


def g(n): return n.path_cost


def astar_search(problem, h=None):
    """Search nodes with minimum f(n) = g(n) + h(n)."""
    h = h or problem.h
    return best_first_search(problem, f=lambda n: g(n) + h(n))


def astar_tree_search(problem, h=None):
    """Search nodes with minimum f(n) = g(n) + h(n), with no `reached` table."""
    h = h or problem.h
    return best_first_tree_search(problem, f=lambda n: g(n) + h(n))


def weighted_astar_search(problem, h=None, weight=1.4):
    """Search nodes with minimum f(n) = g(n) + weight * h(n)."""
    h = h or problem.h
    return best_first_search(problem, f=lambda n: g(n) + weight * h(n))


def greedy_bfs(problem, h=None):
    """Search nodes with minimum h(n)."""
    h = h or problem.h
    return best_first_search(problem, f=h)


def uniform_cost_search(problem):
    "Search nodes with minimum path cost first."
    return best_first_search(problem, f=g)


def breadth_first_bfs(problem):
    "Search shallowest nodes in the search tree first; using best-first."
    return best_first_search(problem, f=len)


def depth_first_bfs(problem):
    "Search deepest nodes in the search tree first; using best-first."
    return best_first_search(problem, f=lambda n: -len(n))


def is_cycle(node, k=30):
    "Does this node form a cycle of length k or less?"
    def find_cycle(ancestor, k):
        return (ancestor is not None and k > 0 and
                (ancestor.state == node.state or find_cycle(ancestor.parent, k - 1)))
    return find_cycle(node.parent, k)



# Queues
# First-in-first-out and Last-in-first-out queues, and a PriorityQueue, which allows you to keep a collection of items, and continually remove from it the item with minimum f(item) score.
# 

# In[78]:


import heapq
from collections import deque

FIFOQueue = deque

LIFOQueue = list

class PriorityQueue:
    """A queue in which the item with minimum f(item) is always popped first."""

    def __init__(self, items=(), key=lambda x: x):
        self.key = key
        self.items = [] # a heap of (score, item) pairs
        for item in items:
            self.add(item)

    def add(self, item):
        """Add item to the queuez."""
        pair = (self.key(item), item)
        heapq.heappush(self.items, pair)

    def pop(self):
        """Pop and return the item with min f(item) value."""
        return heapq.heappop(self.items)[1]

    def top(self): return self.items[0][1]

    def __len__(self): return len(self.items)


# # Other Search Algorithms
# 
# Here are the other search algorithms:

# In[79]:


def breadth_first_search(problem):
    "Search shallowest nodes in the search tree first."
    node = Node(problem.initial)
    if problem.is_goal(problem.initial):
        return node
    frontier = FIFOQueue([node])
    reached = {problem.initial}
    while frontier:
        node = frontier.pop()
        for child in expand(problem, node):
            s = child.state
            if problem.is_goal(s):
                return child
            if s not in reached:
                reached.add(s)
                frontier.appendleft(child)
    return failure


# In[80]:


class RouteProblem(Problem):

    def actions(self, state): 
        """The places neighboring `state`."""
        return self.map.neighbors[state]

    def result(self, state, action):
        """Go to the `action` place, if the map says that is possible."""
        return action if action in self.map.neighbors[state] else state

    def action_cost(self, s, action, s1):
        """The distance (cost) to go from s to s1."""
        return self.map.distances[s, s1]

    def h(self, node):
        "Straight-line distance between state and the goal."
        locs = self.map.locations
        return straight_line_distance(locs[node.state], locs[self.goal])


def straight_line_distance(A, B):
    "Straight-line distance between two points."
    return sum(abs(a - b)**2 for (a, b) in zip(A, B)) ** 0.5


# In[81]:


from collections import defaultdict


class Map:
    def __init__(self, links, locations=None, directed=False):
        if not hasattr(links, 'items'): # Distances are 1 by default
            links = {link: 1 for link in links}
        if not directed:
            for (v1, v2) in list(links):
                links[v2, v1] = links[v1, v2]
        self.distances = links
        self.neighbors = multimap(links)
        self.locations = locations or defaultdict(lambda: (0, 0))


def multimap(pairs) -> dict:
    "Given (key, val) pairs, make a dict of {key: [val,...]}."
    result = defaultdict(list)
    for key, val in pairs:
        result[key].append(val)
    return result


# In[82]:


romania = Map(
    {('O', 'Z'):  71, ('O', 'S'): 151, ('A', 'Z'): 75, ('A', 'S'): 140, ('A', 'T'): 118, 
     ('L', 'T'): 111, ('L', 'M'):  70, ('D', 'M'): 75, ('C', 'D'): 120, ('C', 'R'): 146, 
     ('C', 'P'): 138, ('R', 'S'):  80, ('F', 'S'): 99, ('B', 'F'): 211, ('B', 'P'): 101, 
     ('B', 'G'):  90, ('B', 'U'):  85, ('H', 'U'): 98, ('E', 'H'):  86, ('U', 'V'): 142, 
     ('I', 'V'):  92, ('I', 'N'):  87, ('P', 'R'): 97},
    {'A': ( 76, 497), 'B': (400, 327), 'C': (246, 285), 'D': (160, 296), 'E': (558, 294), 
     'F': (285, 460), 'G': (368, 257), 'H': (548, 355), 'I': (488, 535), 'L': (162, 379),
     'M': (160, 343), 'N': (407, 561), 'O': (117, 580), 'P': (311, 372), 'R': (227, 412),
     'S': (187, 463), 'T': ( 83, 414), 'U': (471, 363), 'V': (535, 473), 'Z': (92, 539)})


r0 = RouteProblem('A', 'A')
r1 = RouteProblem('A', 'B')
r2 = RouteProblem('N', 'L')
r3 = RouteProblem('E', 'T')
r4 = RouteProblem('O', 'M')


# # Grid Problems
# 
# A `GridProblem` involves navigating on a 2D grid, with some cells being impassible obstacles. By default you can move to any of the eight neighboring cells that are not obstacles (but in a problem instance you can supply a `directions=` keyword to change that). Again, the default heuristic is straight-line distance to the goal. States are `(x, y)` cell locations, such as `(4, 2)`, and actions are `(dx, dy)` cell movements, such as `(0, -1)`, which means leave the `x` coordinate alone, and decrement the `y` coordinate by 1.

# In[83]:


class GridProblem(Problem):
    """Finding a path on a 2D grid with obstacles. Obstacles are (x, y) cells."""

    def __init__(self, initial=(15, 30), goal=(130, 30), obstacles=(), **kwds):
        Problem.__init__(self, initial=initial, goal=goal)

    directions = [(-1, -1), (0, -1), (1, -1),
                  (-1, 0),           (1,  0),
                  (-1, +1), (0, +1), (1, +1)]

    def action_cost(self, s, action, s1): return straight_line_distance(s, s1)

    def h(self, node): return straight_line_distance(node.state, self.goal)

    def result(self, state, action): 
        "Both states and actions are represented by (x, y) pairs."
        return action if action not in self.obstacles else state

    def actions(self, state):
        """You can move one cell in any of `directions` to a non-obstacle cell."""
        x, y = state
        return {(x + dx, y + dy) for (dx, dy) in self.directions} - self.obstacles

class ErraticVacuum(Problem):
    def actions(self, state): 
        return ['suck', 'forward', 'backward']

    def results(self, state, action): return self.table[action][state]

    table = dict(suck=    {1:{5,7}, 2:{4,8}, 3:{7}, 4:{2,4}, 5:{1,5}, 6:{8}, 7:{3,7}, 8:{6,8}},
                 forward= {1:{2}, 2:{2}, 3:{4}, 4:{4}, 5:{6}, 6:{6}, 7:{8}, 8:{8}},
                 backward={1:{1}, 2:{1}, 3:{3}, 4:{3}, 5:{5}, 6:{5}, 7:{7}, 8:{7}})


# In[84]:


import random


# Some grid routing problems

# The following can be used to create obstacles:

def random_lines(X=range(15, 130), Y=range(60), N=150, lengths=range(6, 12)):
    """The set of cells in N random lines of the given lengths."""
    result = set()
    for _ in range(N):
        x, y = random.choice(X), random.choice(Y)
        dx, dy = random.choice(((0, 1), (1, 0)))
        result |= line(x, y, dx, dy, random.choice(lengths))
    return result

def line(x, y, dx, dy, length):
    """A line of `length` cells starting at (x, y) and going in (dx, dy) direction."""
    return {(x + i * dx, y + i * dy) for i in range(length)}

random.seed(42) # To make this reproducible

frame = line(-10, 20, 0, 1, 20) | line(150, 20, 0, 1, 20)
cup = line(102, 44, -1, 0, 15) | line(102, 20, -1, 0, 20) | line(102, 44, 0, -1, 24)

d1 = GridProblem(obstacles=random_lines(N=100) | frame)
d2 = GridProblem(obstacles=random_lines(N=150) | frame)
d3 = GridProblem(obstacles=random_lines(N=200) | frame)
d4 = GridProblem(obstacles=random_lines(N=250) | frame)
d5 = GridProblem(obstacles=random_lines(N=300) | frame)
d6 = GridProblem(obstacles=cup | frame)
d7 = GridProblem(obstacles=cup | frame | line(50, 35, 0, -1, 10) | line(60, 37, 0, -1, 17) | line(70, 31, 0, -1, 19))


# In[85]:


class PlanRoute(Problem):
    """ The problem of moving the Hybrid Wumpus Agent from one place to other """

    def __init__(self, initial, goal, allowed, dimrow):
        """ Define goal state and initialize a problem """
        super().__init__(initial, goal)
        self.dimrow = dimrow
        self.goal = goal
        self.allowed = allowed

    def actions(self, state):
        """ Return the actions that can be executed in the given state.
        The result would be a list, since there are only three possible actions
        in any given state of the environment """

        possible_actions = ['Forward', 'TurnLeft', 'TurnRight']
        x, y = state.get_location()
        orientation = state.get_orientation()

        # Prevent Bumps
        if x == 1 and orientation == 'LEFT':
            if 'Forward' in possible_actions:
                possible_actions.remove('Forward')
        if y == 1 and orientation == 'DOWN':
            if 'Forward' in possible_actions:
                possible_actions.remove('Forward')
        if x == self.dimrow and orientation == 'RIGHT':
            if 'Forward' in possible_actions:
                possible_actions.remove('Forward')
        if y == self.dimrow and orientation == 'UP':
            if 'Forward' in possible_actions:
                possible_actions.remove('Forward')

        return possible_actions

    def result(self, state, action):
        """ Given state and action, return a new state that is the result of the action.
        Action is assumed to be a valid action in the state """
        x, y = state.get_location()
        proposed_loc = list()

        # Move Forward
        if action == 'Forward':
            if state.get_orientation() == 'UP':
                proposed_loc = [x, y + 1]
            elif state.get_orientation() == 'DOWN':
                proposed_loc = [x, y - 1]
            elif state.get_orientation() == 'LEFT':
                proposed_loc = [x - 1, y]
            elif state.get_orientation() == 'RIGHT':
                proposed_loc = [x + 1, y]
            else:
                raise Exception('InvalidOrientation')

        # Rotate counter-clockwise
        elif action == 'TurnLeft':
            if state.get_orientation() == 'UP':
                state.set_orientation('LEFT')
            elif state.get_orientation() == 'DOWN':
                state.set_orientation('RIGHT')
            elif state.get_orientation() == 'LEFT':
                state.set_orientation('DOWN')
            elif state.get_orientation() == 'RIGHT':
                state.set_orientation('UP')
            else:
                raise Exception('InvalidOrientation')

        # Rotate clockwise
        elif action == 'TurnRight':
            if state.get_orientation() == 'UP':
                state.set_orientation('RIGHT')
            elif state.get_orientation() == 'DOWN':
                state.set_orientation('LEFT')
            elif state.get_orientation() == 'LEFT':
                state.set_orientation('UP')
            elif state.get_orientation() == 'RIGHT':
                state.set_orientation('DOWN')
            else:
                raise Exception('InvalidOrientation')

        if proposed_loc in self.allowed:
            state.set_location(proposed_loc[0], [proposed_loc[1]])

        return state

    def goal_test(self, state):
        """ Given a state, return True if state is a goal state or False, otherwise """
        return state.get_location() == tuple(self.goal)

    def h(self, node):
        """ Return the heuristic value for a given state."""
        # Manhattan Heuristic Function
        x1, y1 = node.state.get_location()
        x2, y2 = self.goal
        return abs(x2 - x1) + abs(y2 - y1)

