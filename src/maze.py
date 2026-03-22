class Maze:
    def __init__(self):
        self.grid = []
        self.rows = 0
        self.cols = 0

    def load_from_array(self, matrix):
        """Loads maze from a 2D list (0 for path, 1 for wall)."""
        if not matrix or not matrix[0]:
            raise ValueError("Array cannot be empty.")
        
        self.grid = matrix
        self.rows = len(matrix)
        self.cols = len(matrix[0])
        print(f"Maze loaded: {self.rows}x{self.cols}")

    def load_from_file(self, filename):
        """Loads maze from a text file where '#' is a wall and ' ' is a path."""
        try:
            with open(filename, 'r') as f:
                self.grid = [
                    [1 if char == '#' else 0 for char in line.strip('\n')]
                    for line in f.readlines()
                ]
            self.rows = len(self.grid)
            self.cols = len(self.grid[0]) if self.rows > 0 else 0
            print(f"Maze loaded from {filename}: {self.rows}x{self.cols}")
        except FileNotFoundError:
            print("Error: File not found.")

    def is_wall(self, row, col):
        """Validates if a coordinate is a wall or out of bounds."""
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return True  # Treat out-of-bounds as a wall
        
        return self.grid[row][col] == 1

    def get_neighbors(self, row, col):
        """Returns valid adjacent movements (up, down, left, right)."""
        neighbors = []
        actions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dr, dc in actions:
            r, c = row + dr, col + dc
            if not self.is_wall(r, c):
                neighbors.append((r, c))
        return neighbors

    def display(self):
        """Prints the maze to the console."""
        for row in self.grid:
            print("".join(["█" if cell == 1 else " " for cell in row]))