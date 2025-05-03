# import pygame
# import time
# import random

# # --- Pygame Initialization ---
# pygame.init()

# # --- Colors (RGB) ---
# WHITE = (255, 255, 255)
# YELLOW = (255, 255, 102)
# BLACK = (0, 0, 0)
# RED = (213, 50, 80)
# GREEN = (0, 255, 0)
# BLUE = (50, 153, 213)

# # --- Screen Dimensions ---
# SCREEN_WIDTH = 600
# SCREEN_HEIGHT = 400
# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# pygame.display.set_caption('Python Snake Game by AI')

# # --- Game Clock ---
# clock = pygame.time.Clock()

# # --- Snake Properties ---
# BLOCK_SIZE = 10
# INITIAL_SPEED = 15

# # --- Font Styles ---
# font_style = pygame.font.SysFont(None, 30)  # Default font, size 30
# score_font = pygame.font.SysFont("comicsansms", 35) # A different font for score

# # --- Function to display score ---
# def show_score(score):
#     value = score_font.render("Your Score: " + str(score), True, YELLOW)
#     screen.blit(value, [0, 0]) # Display at top-left

# # --- Function to draw the snake ---
# def draw_snake(snake_block_size, snake_list):
#     for x in snake_list:
#         pygame.draw.rect(screen, GREEN, [x[0], x[1], snake_block_size, snake_block_size])

# # --- Function to display messages ---
# def message(msg, color):
#     mesg = font_style.render(msg, True, color)
#     # Center the message
#     mesg_rect = mesg.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
#     screen.blit(mesg, mesg_rect)

# # --- Main Game Loop Function ---
# def game_loop():
#     game_over = False
#     game_close = False

#     # Initial snake position (center of the screen)
#     x1 = SCREEN_WIDTH / 2
#     y1 = SCREEN_HEIGHT / 2

#     # Change in position
#     x1_change = 0
#     y1_change = 0

#     # Snake body list (starts with one block)
#     snake_list = []
#     length_of_snake = 1

#     # Initial food position (random)
#     # Ensure food appears on the grid aligned with block size
#     food_x = round(random.randrange(0, SCREEN_WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
#     food_y = round(random.randrange(0, SCREEN_HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE

#     snake_speed = INITIAL_SPEED # Control how fast the game runs

#     while not game_over:

#         # --- Game Over Screen Loop ---
#         while game_close:
#             screen.fill(BLUE)
#             message("You Lost! Press C-Play Again or Q-Quit", RED)
#             show_score(length_of_snake - 1)
#             pygame.display.update()

#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     game_over = True
#                     game_close = False # Exit the inner loop
#                 if event.type == pygame.KEYDOWN:
#                     if event.key == pygame.K_q:
#                         game_over = True
#                         game_close = False
#                     if event.key == pygame.K_c:
#                         game_loop() # Restart the game

#         # --- Event Handling (Keyboard Input) ---
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 game_over = True
#             if event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_LEFT and x1_change == 0: # Prevent reversing
#                     x1_change = -BLOCK_SIZE
#                     y1_change = 0
#                 elif event.key == pygame.K_RIGHT and x1_change == 0: # Prevent reversing
#                     x1_change = BLOCK_SIZE
#                     y1_change = 0
#                 elif event.key == pygame.K_UP and y1_change == 0: # Prevent reversing
#                     y1_change = -BLOCK_SIZE
#                     x1_change = 0
#                 elif event.key == pygame.K_DOWN and y1_change == 0: # Prevent reversing
#                     y1_change = BLOCK_SIZE
#                     x1_change = 0
#                 elif event.key == pygame.K_q: # Allow quitting mid-game
#                      game_over = True

#         # --- Boundary Collision Check ---
#         if x1 >= SCREEN_WIDTH or x1 < 0 or y1 >= SCREEN_HEIGHT or y1 < 0:
#             game_close = True # Go to game over screen

#         # --- Update Snake Position ---
#         x1 += x1_change
#         y1 += y1_change

#         # --- Drawing ---
#         screen.fill(BLACK) # Clear screen with black background
#         pygame.draw.rect(screen, RED, [food_x, food_y, BLOCK_SIZE, BLOCK_SIZE]) # Draw food

#         # --- Snake Body Update ---
#         snake_head = []
#         snake_head.append(x1)
#         snake_head.append(y1)
#         snake_list.append(snake_head)

#         # If snake list is longer than its allowed length, remove the oldest segment (tail)
#         if len(snake_list) > length_of_snake:
#             del snake_list[0]

#         # --- Self Collision Check ---
#         # Check if the head collides with any part of the body (excluding the head itself)
#         for segment in snake_list[:-1]: # Check all segments *except* the newly added head
#             if segment == snake_head:
#                 game_close = True

#         # --- Draw the snake and score ---
#         draw_snake(BLOCK_SIZE, snake_list)
#         show_score(length_of_snake - 1)

#         # --- Update the display ---
#         pygame.display.update()

#         # --- Food Collision Check ---
#         if x1 == food_x and y1 == food_y:
#             # Place new food
#             food_x = round(random.randrange(0, SCREEN_WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
#             food_y = round(random.randrange(0, SCREEN_HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
#             # Increase snake length (score)
#             length_of_snake += 1
#             # Optional: Increase speed slightly as game progresses
#             # snake_speed += 1

#         # --- Control Game Speed ---
#         clock.tick(snake_speed)

#     # --- Uninitialize Pygame and Quit ---
#     pygame.quit()
#     quit() # Exit Python script

# # --- Start the Game ---
# game_loop()



# Reverse the array

def reverse_array(arr):
    return arr[::-1]


arr = [1, 2, 3, 4, 5]
arr.reverse()
print(arr)  # Output: [5, 4, 3, 2, 1]

# reverse subarray

def reverse_subarray(arr, start, end):
    arr[start:end+1] = arr[start:end+1][::-1]
    return arr

arr = [1, 2, 3, 4, 5]
arr = reverse_subarray(arr, 1, 3)
print(arr)  # Output: [1, 4, 3, 2, 5]

