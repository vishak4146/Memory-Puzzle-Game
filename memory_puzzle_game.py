# Import necessary libraries
import random
import pygame
import sys
from pygame.locals import *

# Initialize Pygame
pygame.init()

# --- Animation Functions ---

def reveal_box_animation(box_x, box_y):
    """
    Animate the box flipping open by gradually drawing the box.
    """
    left, top = left_top_coords_of_box(box_x, box_y)
    for i in range(BOX_SIZE):
        pygame.draw.rect(DISPLAYSURF, BG_COLOR, (left, top, i, BOX_SIZE))
        pygame.display.update()
        pygame.time.wait(5)

def cover_box_animation(box_x, box_y):
    """
    Animate the box flipping closed by gradually covering it.
    """
    left, top = left_top_coords_of_box(box_x, box_y)
    for i in range(BOX_SIZE, -1, -1):
        pygame.draw.rect(DISPLAYSURF, BOX_COLOR, (left, top, i, BOX_SIZE))
        pygame.display.update()
        pygame.time.wait(5)

# --- Game Settings and Display ---

# Window dimensions
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
BOARD_WIDTH = 4  # Number of columns
BOARD_HEIGHT = 4  # Number of rows
BOX_SIZE = 40  # Height and width of each box
GAP_SIZE = 10  # Gaps between boxes

# Calculate margins to center the board on the screen
X_MARGIN = (WINDOW_WIDTH - (BOARD_WIDTH * (BOX_SIZE + GAP_SIZE))) // 2
Y_MARGIN = (WINDOW_HEIGHT - (BOARD_HEIGHT * (BOX_SIZE + GAP_SIZE))) // 2

# Define colors
BG_COLOR = (60, 60, 100)        # Background color
BOX_COLOR = (255, 255, 255)     # Box color
HIGHLIGHT_COLOR = (0, 255, 255) # Highlight color for selected boxes

# Set up the display surface
DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Memory Puzzle")

# --- Helper Functions ---

def generate_board():
    """
    Generate a board with pairs of randomly placed icons.
    """
    icons = []
    # Create pairs of icons for the board
    for i in range(BOARD_WIDTH * BOARD_HEIGHT // 2):
        icons.append(i)
        icons.append(i)
    random.shuffle(icons)  # Shuffle icons

    board = []
    # Fill the board with icons
    for x in range(BOARD_WIDTH):
        column = []
        for y in range(BOARD_HEIGHT):
            column.append(icons.pop())
        board.append(column)
    return board

def get_box_at_pixel(x, y):
    """
    Determine which box on the board was clicked based on pixel coordinates.
    """
    for box_x in range(BOARD_WIDTH):
        for box_y in range(BOARD_HEIGHT):
            left, top = left_top_coords_of_box(box_x, box_y)
            box_rect = pygame.Rect(left, top, BOX_SIZE, BOX_SIZE)
            if box_rect.collidepoint(x, y):
                return (box_x, box_y)
    return (None, None)

def left_top_coords_of_box(box_x, box_y):
    """
    Get the top-left coordinates of a box in the grid.
    """
    left = box_x * (BOX_SIZE + GAP_SIZE) + X_MARGIN
    top = box_y * (BOX_SIZE + GAP_SIZE) + Y_MARGIN
    return (left, top)

# Initialize the revealed boxes grid
revealed_boxes = [[False] * BOARD_HEIGHT for _ in range(BOARD_WIDTH)]

# --- Game Logic Functions ---

def handle_box_click(board, revealed_boxes, first_selection):
    """
    Handle a box click, revealing it and checking for matches.
    """
    mouse_x, mouse_y = pygame.mouse.get_pos()
    box_x, box_y = get_box_at_pixel(mouse_x, mouse_y)

    # Return early if the click is outside the board
    if box_x is None or box_y is None:
        return first_selection, None

    # Reveal the box if it is currently hidden
    if not revealed_boxes[box_x][box_y]:
        reveal_box_animation(box_x, box_y)
        revealed_boxes[box_x][box_y] = True  # Mark as revealed

        if first_selection is None:
            # This is the first box selected
            return (box_x, box_y), None
        else:
            # Second box selected, check if it matches the first box
            first_box_x, first_box_y = first_selection
            icon1 = board[first_box_x][first_box_y]
            icon2 = board[box_x][box_y]

            # If icons do not match, cover both boxes again
            if icon1 != icon2:
                pygame.time.wait(500)
                cover_box_animation(first_box_x, first_box_y)
                cover_box_animation(box_x, box_y)
                revealed_boxes[first_box_x][first_box_y] = False
                revealed_boxes[box_x][box_y] = False

            # Reset the first selection after checking
            return None, None
    return first_selection, None

def draw_board(board, revealed):
    """
    Draw the entire board, showing icons for revealed boxes.
    """
    for box_x in range(BOARD_WIDTH):
        for box_y in range(BOARD_HEIGHT):
            left, top = left_top_coords_of_box(box_x, box_y)
            if not revealed[box_x][box_y]:
                pygame.draw.rect(DISPLAYSURF, BOX_COLOR, (left, top, BOX_SIZE, BOX_SIZE))
            else:
                draw_icon(board[box_x][box_y], left, top)

def draw_icon(icon, left, top):
    """
    Draw the icon (number) at the given box position.
    """
    font = pygame.font.Font(None, 40)
    text_surface = font.render(str(icon), True, (0, 0, 0))
    DISPLAYSURF.blit(text_surface, (left + 10, top + 10))

def check_for_win(revealed_boxes):
    """
    Check if all boxes have been revealed, indicating a win.
    """
    for row in revealed_boxes:
        if False in row:
            return False
    return True

def show_win_message(board, revealed_boxes):
    """
    Display a 'You Win!' message with a fade-in animation.
    """
    font = pygame.font.Font(None, 74)
    message_surf = font.render("You Win!", True, (0, 255, 0))
    message_rect = message_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    
    for _ in range(30):
        DISPLAYSURF.fill(BG_COLOR)
        draw_board(board, revealed_boxes)
        message_surf.set_alpha(_ * 8)
        DISPLAYSURF.blit(message_surf, message_rect)
        pygame.display.update()
        pygame.time.wait(50)

# --- Main Game Loop ---

def game_loop():
    """
    Main loop for the game, handling events and gameplay logic.
    """
    board = generate_board()
    revealed_boxes = [[False] * BOARD_HEIGHT for _ in range(BOARD_WIDTH)]
    first_selection = None

    while True:
        DISPLAYSURF.fill(BG_COLOR)
        draw_board(board, revealed_boxes)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                first_selection, _ = handle_box_click(board, revealed_boxes, first_selection)

        # Check for win condition and display win message
        if check_for_win(revealed_boxes):
            show_win_message(board, revealed_boxes)
            pygame.time.wait(2000)
            return  # Exit the game loop to reset the game

        pygame.display.update()

# Run the game
game_loop()
