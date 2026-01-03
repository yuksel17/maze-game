"""
Search (Cleaned for Guitar Riff Project)
Contains only: Problem, Node, best_first_graph_search, and astar_search.
"""

import sys
from collections import deque
from utils import *
import numpy as np

from utils4e import distance, is_in


# -----------------------------------------------------------
# Basic classes
# -----------------------------------------------------------

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


# -----------------------------------------------------------
# Search Algorithms
# -----------------------------------------------------------

def best_first_graph_search(problem, f, display=False):
    # It is the one main part of our project.

    """Search the nodes with the lowest f scores first.
    You specify the function f(node) that you want to minimize."""

    f = memoize(f, 'f')
    node = Node(problem.initial)
    frontier = PriorityQueue('min', f)  # The list of ways can be followed. (From best to worst)
    # AI does NOT try randomly, Firstly, It tries the option that has minimum f value (cost + heuristic)
    frontier.append(node)
    explored = set()  # The notes that we have already checked.

    while frontier:
        node = frontier.pop()  # Take the option which seems better than others.
        if problem.goal_test(node.state):  # Check whether it is goal
            if display:
                print(len(explored), "paths have been expanded and", len(frontier), "paths remain in the frontier")
            return node  # Done
        explored.add(node.state)  # If it's not goal state, add that node to the explored set.
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                frontier.append(child)  # If we found new path, add to the list.
            elif child in frontier:
                # If we came up to the same state with short path, update the list.
                if f(child) < frontier[child]:
                    del frontier[child]
                    frontier.append(child)
    return None


def astar_search(problem, h=None, display=False):
    # It runs best_first_graph_search with special formula.
    # The formula is lambda n = n.path_cost + h(n)
    # It means f(n) = h(n) + g(n)

    # n.path_cost : Current cost (Total movement on the guitar keyboard.)
    # h(n) : Our heuristic, for example; distance from next note.

    """A* search is best-first graph search with f(n) = g(n)+h(n).
    You need to specify the h function when you call astar_search, or
    else in your Problem subclass."""
    h = memoize(h or problem.h, 'h')
    return best_first_graph_search(problem, lambda n: n.path_cost + h(n), display)


# -----------------------------------------------------------
# Example Works
# This area for testing the best matched logic for grid structure of project.
# -----------------------------------------------------------

class GraphProblem(Problem):
    """The problem of searching a graph from one node to another."""

    def __init__(self, initial, goal, graph):
        super().__init__(initial, goal)
        self.graph = graph

    def actions(self, A):
        """The actions at a graph node are just its neighbors."""
        return list(self.graph.get(A).keys())

    def result(self, state, action):
        """The result of going to a neighbor is just that neighbor."""
        return action

    def path_cost(self, cost_so_far, A, action, B):
        return cost_so_far + (self.graph.get(A, B) or np.inf)

    def find_min_edge(self):
        """Find minimum value of edges."""
        m = np.inf
        for d in self.graph.graph_dict.values():
            local_min = min(d.values())
            m = min(m, local_min)
        return m

    def h(self, node):
        """h function is straight-line distance from a node's state to goal."""
        locs = getattr(self.graph, 'locations', None)
        if locs:
            if type(node) is str:
                return int(distance(locs[node], locs[self.goal]))
            return int(distance(locs[node.state], locs[self.goal]))
        else:
            return np.inf


# -----------------------------------------------------------
# Graph Class
# -----------------------------------------------------------

class Graph:
    """A graph connects nodes (vertices) by edges (links). Each edge can also
    have a length associated with it. The constructor call is something like:
        g = Graph({'A': {'B': 1, 'C': 2})
    this makes a graph with 3 nodes, A, B, and C, with an edge of length 1 from
    A to B,  and an edge of length 2 from A to C. You can also do:
        g = Graph({'A': {'B': 1, 'C': 2}, directed=False)
    This makes an undirected graph, so inverse links are also added. You can use g.nodes() to get a list of nodes,
    g.get('A') to get a dict of links out of A, and g.get('A', 'B') to get the
    length of the link from A to B. 'Lengths' can actually be any object at
    all, and nodes can be any hashable object."""

    def __init__(self, graph_dict=None, directed=True):
        self.graph_dict = graph_dict or {}
        self.directed = directed
        if not directed:
            self.make_undirected()

    def make_undirected(self):
        """Make a digraph into an undirected graph by adding symmetric edges."""
        for a in list(self.graph_dict.keys()):
            for (b, dist) in self.graph_dict[a].items():
                self.connect1(b, a, dist)

    def connect(self, A, B, distance=1):
        """Add a link from A and B of given distance, and also add the inverse
        link if the graph is undirected."""
        self.connect1(A, B, distance)
        if not self.directed:
            self.connect1(B, A, distance)

    def connect1(self, A, B, distance):
        """Add a link from A to B of given distance, in one direction only."""
        self.graph_dict.setdefault(A, {})[B] = distance

    def get(self, a, b=None):
        """Return a link distance or a dict of {node: distance} entries.
        .get(a,b) returns the distance or None;
        .get(a) returns a dict of {node: distance} entries, possibly {}."""
        links = self.graph_dict.setdefault(a, {})
        if b is None:
            return links
        else:
            return links.get(b)

    def nodes(self):
        """Return a list of nodes in the graph."""
        s1 = set([k for k in self.graph_dict.keys()])
        s2 = set([k2 for v in self.graph_dict.values() for k2 in v.keys()])
        nodes = s1.union(s2)
        return list(nodes)


def UndirectedGraph(graph_dict=None):
    """Build a Graph where every edge (including future ones) goes both ways."""
    return Graph(graph_dict=graph_dict, directed=False)


# -----------------------------------------------------------
# Run Romania Map Example
# -----------------------------------------------------------

if __name__ == "__main__":
    print("\nA* Algorithm Reference: Romania Map")
    print("Goal: Finding shortest path from Arad to Bucharest.\n")

    romania_map = UndirectedGraph(dict(
        Arad=dict(Zerind=75, Sibiu=140, Timisoara=118),
        Bucharest=dict(Urziceni=85, Pitesti=101, Giurgiu=90, Fagaras=211),
        Craiova=dict(Drobeta=120, Rimnicu=146, Pitesti=138),
        Drobeta=dict(Mehadia=75),
        Eforie=dict(Hirsova=86),
        Fagaras=dict(Sibiu=99),
        Hirsova=dict(Urziceni=98),
        Iasi=dict(Vaslui=92, Neamt=87),
        Lugoj=dict(Timisoara=111, Mehadia=70),
        Oradea=dict(Zerind=71, Sibiu=151),
        Pitesti=dict(Rimnicu=97),
        Rimnicu=dict(Sibiu=80),
        Urziceni=dict(Vaslui=142)
    ))

    romania_problem = GraphProblem('Arad', 'Bucharest', romania_map)
    node = astar_search(romania_problem)

    if node:
        print("\nCost of path:", node.path_cost)
        print("Followed Route:")
        for n in node.path():
            print(" ->", n.state)

        print("\nCities are represent the notes in our project.")
        print("Ways are represent the movement on the guitar keyboard.")
    else:
        print("No path.")


# -----------------------------------------------------------
# TEMPLATE OF OUR PROJECT (Guitar Riff)
# -----------------------------------------------------------

# class GuitarPathProblem(Problem):
#     def __init__(self, initial, goal_riff):
#         super().__init__(initial, goal_riff)
#         # Other variables for example guitar keyboard 'music21 library' that returns all the notes on the guitar as an array
#         # Also a guitarist uses four finger on the keyboard it can be considered as a variable.
#
#     def actions(self, state):
#         # CSP is here: Returns the next possible finger position.
#         pass
#
#     def result(self, state, action):
#         # It returns new current state (finger position)
#         pass
#
#     def path_cost(self, c, state1, action, state2):
#         # Calculate ergonomic cost (finger stretch, string changes etc.)
#         pass
#
#     def h(self, node):
#         # Heuristic: Remaining physical distance to the goal state.
#         pass



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