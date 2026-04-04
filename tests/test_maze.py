import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from maze import Maze


def run_test():
    my_maze = Maze()

    simple_grid = [
        [0, 0, 1, 0, 0],
        [1, 0, 1, 0, 1],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 1, 0],
    ]

    print("--- Loading Hardcoded Maze ---")
    my_maze.load_from_array(simple_grid)

    print("\n--- Testing is_wall ---")
    print(f"is_wall(0,0): {my_maze.is_wall(0, 0)}")
    print(f"is_wall(0,2): {my_maze.is_wall(0, 2)}")

    print("\n--- Testing get_neighbors ---")
    print(f"get_neighbors(0,0): {my_maze.get_neighbors(0, 0)}")
    print(f"get_neighbors(2,2): {my_maze.get_neighbors(2, 2)}")

    print("\n--- Testing load_from_image with default_maze.txt ---")
    maze_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "default_maze.txt")
    )
    print(f"Loading: {maze_path}")


if __name__ == "__main__":
    run_test()
