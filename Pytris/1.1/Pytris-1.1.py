import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions and settings
WIDTH, HEIGHT = 300, 600  # Board dimensions
GRID_SIZE = 30            # Size of a single grid cell
COLS, ROWS = WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
COLORS = [
    (0, 255, 255),  # Cyan (I)
    (0, 0, 255),    # Blue (J)
    (255, 165, 0),  # Orange (L)
    (255, 255, 0),  # Yellow (O)
    (0, 255, 0),    # Green (S)
    (128, 0, 128),  # Purple (T)
    (255, 0, 0)     # Red (Z)
]

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],               # I
    [[1, 0, 0], [1, 1, 1]],       # J
    [[0, 0, 1], [1, 1, 1]],       # L
    [[1, 1], [1, 1]],             # O
    [[0, 1, 1], [1, 1, 0]],       # S
    [[0, 1, 0], [1, 1, 1]],       # T
    [[1, 1, 0], [0, 1, 1]]        # Z
]

class Tetromino:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.row = 0
        self.col = COLS // 2 - len(shape[0]) // 2
        self.is_dropping = False
        self.drop_timer = 0

    def rotate(self):
        """Rotate the tetromino clockwise."""
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

    def undo_rotate(self):
        """Undo the rotation (counter-clockwise)."""
        self.shape = [list(row) for row in zip(*self.shape)][::-1]

def create_board():
    """Create an empty board."""
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]

def draw_grid(screen):
    """Draw the grid lines."""
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

def draw_board(screen, board):
    """Draw the game board."""
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col]:
                color = board[row][col]
                pygame.draw.rect(screen, color, (col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(screen, GRAY, (col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

def draw_tetromino(screen, tetromino):
    """Draw the current tetromino."""
    for r, row in enumerate(tetromino.shape):
        for c, cell in enumerate(row):
            if cell:
                x = (tetromino.col + c) * GRID_SIZE
                y = (tetromino.row + r) * GRID_SIZE
                pygame.draw.rect(screen, tetromino.color, (x, y, GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(screen, GRAY, (x, y, GRID_SIZE, GRID_SIZE), 1)

def check_collision(tetromino, board, dx=0, dy=0):
    """Check if the tetromino collides with the board or walls."""
    for r, row in enumerate(tetromino.shape):
        for c, cell in enumerate(row):
            if cell:
                new_row = tetromino.row + r + dy
                new_col = tetromino.col + c + dx
                if new_row >= ROWS or new_col < 0 or new_col >= COLS or (new_row >= 0 and board[new_row][new_col]):
                    return True
    return False

def place_tetromino(tetromino, board):
    """Place the tetromino on the board."""
    for r, row in enumerate(tetromino.shape):
        for c, cell in enumerate(row):
            if cell:
                board[tetromino.row + r][tetromino.col + c] = tetromino.color

def clear_lines(board):
    """Clear completed lines and return the number of cleared lines."""
    cleared = 0
    for r in range(ROWS - 1, -1, -1):
        if 0 not in board[r]:
            del board[r]
            board.insert(0, [0 for _ in range(COLS)])
            cleared += 1
    return cleared * 10  # Add 10 points per line cleared instead of 1

def draw_score(screen, score):
    """Draw the score in a seven-segment style using the custom font."""
    font = pygame.font.Font("7Segment.ttf", 48)  # Load your custom font
    score_text = font.render(f"{score:02}", True, WHITE)  # Score is always 2 digits
    text_rect = score_text.get_rect(center=(WIDTH // 2, 20))  # Centered at the top middle
    screen.blit(score_text, text_rect)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pytris")
    clock = pygame.time.Clock()

    board = create_board()
    current_tetromino = Tetromino(random.choice(SHAPES), random.choice(COLORS))
    next_tetromino = Tetromino(random.choice(SHAPES), random.choice(COLORS))

    running = True
    score = 0

    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if not current_tetromino.is_dropping:
                    if event.key == pygame.K_LEFT and not check_collision(current_tetromino, board, dx=-1):
                        current_tetromino.col -= 1
                    if event.key == pygame.K_RIGHT and not check_collision(current_tetromino, board, dx=1):
                        current_tetromino.col += 1
                    if event.key == pygame.K_UP:
                        current_tetromino.rotate()
                        if check_collision(current_tetromino, board):
                            current_tetromino.undo_rotate()
                if event.key == pygame.K_RETURN and not current_tetromino.is_dropping:
                    current_tetromino.is_dropping = True

        if current_tetromino.is_dropping:
            current_tetromino.drop_timer += clock.get_time()
            if current_tetromino.drop_timer >= 65:  # 5 times faster (originally 80)
                current_tetromino.drop_timer = 0
                if check_collision(current_tetromino, board, dy=1):
                    place_tetromino(current_tetromino, board)
                    score += clear_lines(board)
                    current_tetromino = next_tetromino
                    next_tetromino = Tetromino(random.choice(SHAPES), random.choice(COLORS))
                    if check_collision(current_tetromino, board):
                        running = False
                else:
                    current_tetromino.row += 1

        draw_board(screen, board)
        draw_tetromino(screen, current_tetromino)
        draw_grid(screen)
        draw_score(screen, score)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
