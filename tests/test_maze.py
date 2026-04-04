import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from maze import Maze

def run_test():
    my_maze = Maze()

    # 0 = Path, 1 = Wall
    # This is a clean 5x5 maze with a clear path from top-left to bottom-right
    simple_grid = [
        [0, 0, 1, 0, 0],
        [1, 0, 1, 0, 1],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 1, 0]
    ]

    print("--- Loading Hardcoded Maze ---")
    my_maze.load_from_array(simple_grid)

    print("\n--- Visual Representation ---")
    my_maze.display()

if __name__ == "__main__":
    run_test()