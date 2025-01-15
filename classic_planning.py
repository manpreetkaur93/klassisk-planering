from collections import deque
from dataclasses import dataclass

# Representation of the world
WORLD = [
    ["S", ".", ".", ".", "."],
    [".", "#", "#", ".", "."],
    [".", ".", "K", "#", "."],
    [".", ".", ".", ".", "D"],
    [".", ".", ".", ".", "G"]
]

# Print the world
def print_world(world):
    for row in world:
        print(" ".join(row))

print_world(WORLD)

# State representation
@dataclass(frozen=True)
class State:
    agent_pos: tuple  # Agent's position (row, col)
    has_key: bool  # True if agent has the key
    door_unlocked: bool  # True if the door is unlocked

# Initial state
initial_state = State(agent_pos=(0, 0), has_key=False, door_unlocked=False)
print(initial_state)

# Movement actions
def move_up(state, world):
    r, c = state.agent_pos
    new_r = r - 1
    if new_r < 0 or world[new_r][c] == "#" or (world[new_r][c] == "D" and not state.door_unlocked):
        return None
    return State(agent_pos=(new_r, c), has_key=state.has_key, door_unlocked=state.door_unlocked)

def move_down(state, world):
    r, c = state.agent_pos
    new_r = r + 1
    if new_r >= len(world) or world[new_r][c] == "#" or (world[new_r][c] == "D" and not state.door_unlocked):
        return None
    return State(agent_pos=(new_r, c), has_key=state.has_key, door_unlocked=state.door_unlocked)


def move_left(state, world):
    r, c = state.agent_pos
    new_c = c - 1
    if new_c < 0 or world[r][new_c] == "#" or (world[r][new_c] == "D" and not state.door_unlocked):
        return None
    return State(agent_pos=(r, new_c), has_key=state.has_key, door_unlocked=state.door_unlocked)

def move_right(state, world):
    r, c = state.agent_pos
    new_c = c + 1
    if new_c >= len(world[0]) or world[r][new_c] == "#" or (world[r][new_c] == "D" and not state.door_unlocked):
        return None
    return State(agent_pos=(r, new_c), has_key=state.has_key, door_unlocked=state.door_unlocked)

# Pick up key action
def pick_up_key(state, world):
    r, c = state.agent_pos
    if world[r][c] != "K" or state.has_key:
        return None
    return State(agent_pos=(r, c), has_key=True, door_unlocked=state.door_unlocked)

# Unlock door action
def unlock_door(state, world):
    r, c = state.agent_pos
    if not state.has_key or world[r][c] != "D":
        return None
    return State(agent_pos=(r, c), has_key=state.has_key, door_unlocked=True)

# Actions dictionary
ACTIONS = {
    "MOVE_UP": move_up,
    "MOVE_DOWN": move_down,
    "MOVE_LEFT": move_left,
    "MOVE_RIGHT": move_right,
    "PICK_UP_KEY": pick_up_key,
    "UNLOCK_DOOR": unlock_door
}

# Breadth-First Search (BFS) for planning
def bfs_plan(start_state, world, goal_test):
    frontier = deque([(start_state, [])])
    visited = set([start_state])

    while frontier:
        current_state, current_plan = frontier.popleft()

        if goal_test(current_state, world):
            return current_plan

        for action_name, action_func in ACTIONS.items():
            new_state = action_func(current_state, world)
            if new_state and new_state not in visited:
                visited.add(new_state)
                new_plan = current_plan + [action_name]
                frontier.append((new_state, new_plan))

    print(f"Utforskar: {current_state}, Handling: {action_name}, Nytt tillstånd: {new_state}")


    return None

# Sequential subgoal planning
def bfs_with_subgoals(start_state, world):
    def goal_key(state, world):
        r, c = state.agent_pos
        return world[r][c] == "K"

    plan_to_key = bfs_plan(start_state, world, goal_key)
    if not plan_to_key:
        raise ValueError("Kunde inte hitta en väg till nyckeln!")

    key_state = execute_plan_and_get_final_state(start_state, plan_to_key, world)
    key_state = State(agent_pos=key_state.agent_pos, has_key=True, door_unlocked=key_state.door_unlocked)


    def goal_door(state, world):
      r, c = state.agent_pos
      return (r, c) == (3, 4)  # Dörrens exakta koordinater


    plan_to_door = bfs_plan(key_state, world, goal_door)
    if not plan_to_door:
        raise ValueError("Kunde inte hitta en väg till dörren!")

    door_state = execute_plan_and_get_final_state(key_state, plan_to_door, world)
    door_state = State(agent_pos=door_state.agent_pos, has_key=True, door_unlocked=True)


    def goal_final(state, world):
        r, c = state.agent_pos
        return world[r][c] == "G"

    plan_to_goal = bfs_plan(door_state, world, goal_final)
    if not plan_to_goal:
        raise ValueError("Kunde inte hitta en väg till målet!")

    return plan_to_key + ["PICK_UP_KEY"] + plan_to_door + ["UNLOCK_DOOR"] + plan_to_goal

# Execute a plan and get the final state
def execute_plan_and_get_final_state(state, plan, world):
    if not plan:
        raise ValueError("Ingen plan att exekvera!")

    current_state = state
    for action_name in plan:
        action_func = ACTIONS[action_name]
        new_state = action_func(current_state, world)
        if new_state is None:
            raise ValueError(f"Misslyckades att exekvera handling: {action_name}")
        current_state = new_state
    return current_state

# Test if goal state is reached
def is_goal(state, world):
    r, c = state.agent_pos
    return (
        world[r][c] == "G" and state.has_key and state.door_unlocked
    )
#testa individuellt att dörren nås
def test_door_path():
    def goal_door(state, world):
        r, c = state.agent_pos
        return (r, c) == (3, 4)  # Dörrens exakta koordinater

    start_state = State(agent_pos=(2, 2), has_key=True, door_unlocked=False)  # Efter att nyckeln plockats
    plan_to_door = bfs_plan(start_state, WORLD, goal_door)
    print("Plan till dörren:", plan_to_door)

test_door_path()

# Execute a plan
def execute_plan(state, plan, world):
    current_state = state
    for step, action_name in enumerate(plan):
        print(f"Steg {step + 1}: {action_name}")
        action_func = ACTIONS[action_name]
        new_state = action_func(current_state, world)
        if new_state is None:
            print("Handling misslyckades!")
            return
        else:
            current_state = new_state
            print(f"Ny position: {current_state.agent_pos}, Har nyckel: {current_state.has_key}, Dörr upplåst: {current_state.door_unlocked}")

# Visualize the world with the agent
def update_world(world, state):
    updated_world = [row[:] for row in world]
    r, c = state.agent_pos
    updated_world[r][c] = "A"
    return updated_world

def print_world_with_agent(world, state):
    updated_world = update_world(world, state)
    print_world(updated_world)

# Test the full process
try:
    full_plan = bfs_with_subgoals(initial_state, WORLD)
    print("Fullständig plan:", full_plan)

    # Exekvera och visualisera
    execute_plan(initial_state, full_plan, WORLD)
except ValueError as e:
    print("Fel under exekvering:", e)

