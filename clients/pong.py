import random
import pickle
import pygame
from client_sub import ClientSub
import numpy as np

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pong Game")

# Define game colors
white = (255, 255, 255)
black = (0, 0, 0)
blue = (0, 0, 255)

# Define paddles and ball
paddle_width, paddle_height = 20, 100
BALL_SIZE = 20
player_paddle = pygame.Rect(50, height // 2 - paddle_height // 2, paddle_width, paddle_height)
ai_paddle = pygame.Rect(width - 70, height // 2 - paddle_height // 2, paddle_width, paddle_height)
ball = pygame.Rect(width // 2 - BALL_SIZE // 2, height // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

MAX_BALL_SPEED = 10


# Function to reset ball position and velocity
def reset_ball():
    ball.x = width // 2 - BALL_SIZE // 2
    ball.y = height // 2 - BALL_SIZE // 2
    ball_velocity[0] = MAX_BALL_SPEED * random.choice((1, -1))
    ball_velocity[1] = MAX_BALL_SPEED * random.choice((1, -1))


# Initialize ball velocity
ball_velocity = [MAX_BALL_SPEED * random.choice((1, -1)), MAX_BALL_SPEED * random.choice((1, -1))]

# Initialize player paddle movement
PLAYER_VELOCITY = 10

# Initialize clock
clock = pygame.time.Clock()

# Setup ClientSub for data
clientSub = ClientSub(sub_port=6000)

# Load CSP filters and trained ML model
filters = np.load('../notebooks/models/csp_filters.npy')
MODEL_FILENAME = '../notebooks/models/MI_model.pkl'

with open(MODEL_FILENAME, 'rb') as file:
    loaded_model = pickle.load(file)

# Main game loop
RUNNING = True
while RUNNING:
    try:
        samplestamps, samples, _ = clientSub.get_data()
        data = samples[:, 0]  # Get data from the first channel

        filtered_data = np.dot(filters, samples)
        features = np.log(np.var(filtered_data, axis=1))
        features = features.reshape(1, -1)

        ### Control the player paddle based on LDA model predictions###
        pred = loaded_model.predict(features)

        if pred == 0:
            print("Move up!")
            player_paddle.y -= PLAYER_VELOCITY
            # Ensure the paddle doesn't go off the screen
            if player_paddle.top < 0:
                player_paddle.top = 0
        elif pred == 1:
            print("Move down!")
            player_paddle.y += PLAYER_VELOCITY
            # Ensure the paddle doesn't go off the screen
            if player_paddle.bottom > height:
                player_paddle.bottom = height

    except Exception as e:
        print("Did not get data :(", e)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNNING = False

    # Ball movement
    ball.x += ball_velocity[0]
    ball.y += ball_velocity[1]

    # Ball collision with top and bottom walls
    if ball.top <= 0 or ball.bottom >= height:
        ball_velocity[1] = -ball_velocity[1]

    # Ball collision with paddles
    if ball.colliderect(player_paddle) or ball.colliderect(ai_paddle):
        ball_velocity[0] = -ball_velocity[0]

    # Ball goes out of bounds (left or right)
    if ball.left <= 0 or ball.right >= width:
        reset_ball()

    # Move AI paddle to follow the ball
    if ai_paddle.centery < ball.centery:
        ai_paddle.y += PLAYER_VELOCITY
    if ai_paddle.centery > ball.centery:
        ai_paddle.y -= PLAYER_VELOCITY

    # Ensure the AI paddle doesn't go off the screen
    if ai_paddle.top < 0:
        ai_paddle.top = 0
    if ai_paddle.bottom > height:
        ai_paddle.bottom = height

    # Fill the screen with black
    screen.fill(white)

    # Draw the paddles and ball
    pygame.draw.rect(screen, blue, player_paddle)
    pygame.draw.rect(screen, blue, ai_paddle)
    pygame.draw.ellipse(screen, black, ball)

    # Draw the middlbe line
    pygame.draw.aaline(screen, black, (width // 2, 0), (width // 2, height))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
