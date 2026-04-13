from PIL import Image
import random

class Maze:
    def __init__(self):
        self.grid = []
        self.rows = 0
        self.cols = 0

    def generate_random(self, rows=41, cols=41):
        """
        Generates a structured maze using the Recursive Backtracker (DFS) algorithm.
        Creates continuous corridors instead of random static noise.
        """
        self.rows = rows if rows % 2 != 0 else rows + 1
        self.cols = cols if cols % 2 != 0 else cols + 1

        self.grid = [[1 for _ in range(self.cols)] for _ in range(self.rows)]

        start_r = random.randrange(1, self.rows, 2)
        start_c = random.randrange(1, self.cols, 2)
        self.grid[start_r][start_c] = 0

        stack = [(start_r, start_c)]

        directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

        while stack:
            current_r, current_c = stack[-1]

            unvisited = []
            for dr, dc in directions:
                nr, nc = current_r + dr, current_c + dc
                if 0 < nr < self.rows - 1 and 0 < nc < self.cols - 1:
                    if self.grid[nr][nc] == 1: 
                        unvisited.append((nr, nc, dr, dc))

            if unvisited:
                nr, nc, dr, dc = random.choice(unvisited)

                self.grid[current_r + dr//2][current_c + dc//2] = 0
                self.grid[nr][nc] = 0

                stack.append((nr, nc))
            else:
                stack.pop()

        
        for _ in range((self.rows * self.cols) // 15):
            r = random.randrange(1, self.rows - 1)
            c = random.randrange(1, self.cols - 1)
            self.grid[r][c] = 0

        print(f"Structured maze generated: {self.cols}x{self.rows}")
    def load_from_array(self, matrix):
        if not matrix or not matrix[0]:
            raise ValueError("Array cannot be empty.")

        self.grid = matrix
        self.rows = len(matrix)
        self.cols = len(matrix[0])
        print(f"Maze loaded: {self.rows}x{self.cols}")

    def load_from_image(self, image_path, logical_size=(41, 41), threshold=200):
        try:
            img = Image.open(image_path).convert("L")
            img_w, img_h = img.size

            self.cols, self.rows = logical_size
            self.grid = []

            chunk_w = img_w / self.cols
            chunk_h = img_h / self.rows

            for r in range(self.rows):
                row_data = []
                for c in range(self.cols):
                    left = int(c * chunk_w)
                    top = int(r * chunk_h)
                    right = int((c + 1) * chunk_w)
                    bottom = int((r + 1) * chunk_h)

                    chunk = img.crop((left, top, right, bottom))
                    pixel_data = list(chunk.getdata())

                    if min(pixel_data) < threshold:
                        row_data.append(1)
                    else:
                        row_data.append(0)

                self.grid.append(row_data)

            print(
                f"Success! Image chunked cleanly into a {self.cols}x{self.rows} logical grid."
            )

        except Exception as e:
            print(f"Error loading image: {e}")
    def load_from_txt(self, filename): 
        try:
            self.grid = []
            with open(filename, 'r') as f:
                for line in f:
                    clean_line = line.strip()
                    if not clean_line:
                        continue
                    
                    row = []
                    # Check if the file uses commas (like your default_maze.txt probably does)
                    if ',' in clean_line:
                        row = [int(x) for x in clean_line.split(",") if x.strip() in ['0', '1']]
                    else:
                        # Otherwise, read it character by character
                        row = [int(char) for char in clean_line if char in ['0', '1']]
                    
                    if row:
                        self.grid.append(row)
            
            self.rows = len(self.grid)
            self.cols = len(self.grid[0]) if self.rows > 0 else 0
            print(f"Maze successfully loaded from text file: {self.cols}x{self.rows}")
            
        except Exception as e:
            print(f"Error loading text file: {e}")

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
