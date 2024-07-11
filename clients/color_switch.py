import pygame
import random
from client_sub import ClientSub
import numpy as np

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 400, 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Color Changing Square")

# Create a square
square_size = 100
square = pygame.Rect(width//2 - square_size//2, height//2 - square_size//2, square_size, square_size)

# Initialize color
color = (255, 0, 0)  # Start with red

# Main game loop
running = True
clock = pygame.time.Clock()

clientSub = ClientSub(sub_port=1000)
data = []

while running:
    try:
        samplestamps, samples, _ = clientSub.get_data()
        data = samples[:, 0] # get data from the first channel
        
        # Change color of the square if the mean of the data is past a threshold
        mean = np.mean(data)
        # print(mean)
        threshold = 800
        if mean > threshold:
            print('Change!')
            print(mean)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    except:
        print("Did not get data :(")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the screen with white
    screen.fill((255, 255, 255))

    # Draw the square with the current color
    pygame.draw.rect(screen, color, square)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()