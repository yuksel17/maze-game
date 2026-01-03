
from collections import deque
from demo import setup_scenario
from src.haunted_problem import HauntedMazeProblem
from search4e import astar_search


def run_bfs(seed=1):
    maze, start, exit_pos = setup_scenario(seed)
    problem = HauntedMazeProblem(maze, start, exit_pos)

    frontier = deque([problem.initial])
    explored = set()
    parent = {problem.initial: None}

    while frontier:
        state = frontier.popleft()

        if problem.goal_test(state):
            return build_path(parent, state)

        explored.add(state)

        for action in problem.actions(state):
            child = problem.result(state, action)

            if child not in explored and child not in frontier:
                parent[child] = state
                frontier.append(child)

    return None


def run_astar(seed=1):
    maze, start, exit_pos = setup_scenario(seed)
    problem = HauntedMazeProblem(maze, start, exit_pos)
    solution = astar_search(problem)

    if solution is None:
        return None

    return [node.state for node in solution.path()]


def build_path(parent, goal):
    path = []
    while goal is not None:
        path.append(goal)
        goal = parent[goal]
    return path[::-1]

