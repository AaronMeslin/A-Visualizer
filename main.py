import pygame
import heapq
import random

# Initialize Pygame
pygame.init()

# Define constants
WIDTH = 800
HEIGHT = 830
ROWS = 25
COLS = 25
CELL_SIZE = WIDTH // COLS

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (220, 220, 220)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
LIGHT_GREY = (170, 170, 170)
DARK_GREY = (100, 100, 100)

# Define the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("A* Pathfinding Visualization")

# Font setup for displaying text
font = pygame.font.SysFont('Arial', 24)

# Node class for the grid
class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = row * CELL_SIZE
        self.y = col * CELL_SIZE
        self.color = WHITE
        self.neighbors = []
        self.g = float('inf')
        self.h = float('inf')
        self.f = float('inf')
        self.came_from = None

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y + 30, CELL_SIZE, CELL_SIZE))  # Offset by 30 pixels
    
    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < ROWS - 1 and not grid[self.row + 1][self.col].is_barrier():  # Down
            self.neighbors.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # Up
            self.neighbors.append(grid[self.row - 1][self.col])
        if self.col < COLS - 1 and not grid[self.row][self.col + 1].is_barrier():  # Right
            self.neighbors.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # Left
            self.neighbors.append(grid[self.row][self.col - 1])

    def is_barrier(self):
        return self.color == BLACK

    def reset(self):
        self.color = WHITE

def create_grid():
    return [[Node(i, j) for j in range(COLS)] for i in range(ROWS)]

def draw_grid():
    for i in range(ROWS):
        pygame.draw.line(screen, BLACK, (0, i * CELL_SIZE + 30), (WIDTH, i * CELL_SIZE + 30))
    for j in range(COLS):
        pygame.draw.line(screen, BLACK, (j * CELL_SIZE, 30), (j * CELL_SIZE, HEIGHT))

def draw_all(grid, text):
    screen.fill(WHITE)
    
    # Render the text
    text_surface = font.render(text, True, BLACK)
    screen.blit(text_surface, (10, 5))  # Display text at the top

    for row in grid:
        for node in row:
            node.draw()
    draw_grid()
    pygame.display.update()

def heuristic(a, b):
    return abs(a.row - b.row) + abs(a.col - b.col)

def reconstruct_path(came_from, current):
    while current in came_from:
        current = came_from[current]
        if current.color != BLUE:  # Avoid overwriting start and end nodes
            current.color = GREEN
        
        current.draw()
        pygame.display.update()

def a_star_algorithm(grid, start, end):
    count = 0
    open_set = []
    heapq.heappush(open_set, (0, count, start))
    came_from = {}
    start.g = 0
    start.f = heuristic(start, end)

    open_set_hash = {start}

    while not len(open_set) == 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = heapq.heappop(open_set)[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end)
            end.color = BLUE
            start.color = BLUE
            return True

        for neighbor in current.neighbors:
            temp_g = current.g + 1

            if temp_g < neighbor.g:
                came_from[neighbor] = current
                neighbor.g = temp_g
                neighbor.f = temp_g + heuristic(neighbor, end)
                if neighbor not in open_set_hash:
                    count += 1
                    heapq.heappush(open_set, (neighbor.f, count, neighbor))
                    open_set_hash.add(neighbor)
                    if neighbor.color != BLUE:
                        neighbor.color = RED

        draw_all(grid, "Algorithm Running...")
        if current != start and current != end:
            current.color = RED

    return False

def add_random_blockades(grid, num_blockades=50):
    for _ in range(num_blockades):
        row = random.randint(0, ROWS - 1)
        col = random.randint(0, COLS - 1)
        node = grid[row][col]
        if node.color == WHITE:
            node.color = BLACK

# Main loop
grid = create_grid()
start = None
end = None
run = True
add_random_blockades(grid, num_blockades=6*ROWS)

text = "Select start point!"

while run:
    draw_all(grid, text)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if pygame.mouse.get_pressed()[0]:  # LEFT CLICK
            pos = pygame.mouse.get_pos()
            row = pos[0] // CELL_SIZE
            col = pos[1] // CELL_SIZE
            node = grid[row][col]
            if not start and node != end:
                start = node
                start.color = BLUE
                text = "Select end point"
            elif not end and node != start:
                end = node
                end.color = BLUE
                text = "Press SPACE to run algorithm"
            elif node != end and node != start:
                node.color = BLACK

        elif event.type == pygame.KEYDOWN:  # Check for key press
            if event.key == pygame.K_SPACE and start and end:
                for row in grid:
                    for node in row:
                        node.update_neighbors(grid)
                path_found = a_star_algorithm(grid, start, end)
                text = "Path found!" if path_found else "No path found!"

pygame.quit()
