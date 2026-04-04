from PIL import Image


class Maze:
    def __init__(self):
        self.grid = []
        self.rows = 0
        self.cols = 0

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
