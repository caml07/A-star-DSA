from PIL import Image

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

    def load_from_image(self, image_path, logical_size=(41, 41), threshold=200):
        """
        Converts a maze image into a strict logical grid.
        Uses chunking to guarantee no walls are ever lost!
        """
        try:
            img = Image.open(image_path).convert('L')
            img_w, img_h = img.size
            
            self.cols, self.rows = logical_size
            self.grid = []
            
            # Calculate the width/height of the chunks we need to scan
            chunk_w = img_w / self.cols
            chunk_h = img_h / self.rows
            
            for r in range(self.rows):
                row_data = []
                for c in range(self.cols):
                    # Define the boundaries of the chunk
                    left = int(c * chunk_w)
                    top = int(r * chunk_h)
                    right = int((c + 1) * chunk_w)
                    bottom = int((r + 1) * chunk_h)
                    
                    # Crop that chunk out of the image
                    chunk = img.crop((left, top, right, bottom))
                    
                    # min() finds the darkest pixel in the chunk. 
                    # If there's even a sliver of a black wall, it becomes a wall block!
                    if min(chunk.getdata()) < threshold:
                        row_data.append(1)  # Wall
                    else:
                        row_data.append(0)  # Path
                        
                self.grid.append(row_data)
                
            print(f"Success! Image chunked cleanly into a {self.cols}x{self.rows} logical grid.")
            
        except Exception as e:
            print(f"Error loading image: {e}")

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
            line = "".join(["██" if cell == 1 else "  " for cell in row])
            print(line)