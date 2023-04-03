import pygame
import numpy as np
import pyaudio

# Constants
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
PLOT_WIDTH = 640
PLOT_HEIGHT = 480
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
BALL_RADIUS = 10
BALL_COLOR = (255, 255, 0)

# Initialize PyAudio
p = pyaudio.PyAudio()

# Create a stream object
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=CHUNK_SIZE)

# Initialize Pygame
pygame.init()
pygame.mixer.quit()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))                        

# Create a font object
font = pygame.font.SysFont("Arial", 20)

# Create a surface object for the plot
plot_surface = pygame.Surface((PLOT_WIDTH, PLOT_HEIGHT))

# Create a ball object
ball_pos = (PLOT_WIDTH // 2, PLOT_HEIGHT // 3)
ball_vel = (0, -10)

# Define a function to update the ball position
def update_ball():
    global ball_pos, ball_vel
    ball_pos = (ball_pos[0] + ball_vel[0], ball_pos[1] + ball_vel[1])
    if ball_pos[0] < BALL_RADIUS:
        ball_pos = (BALL_RADIUS, ball_pos[1])
        ball_vel = (-ball_vel[0], ball_vel[1])
    elif ball_pos[0] > PLOT_WIDTH - BALL_RADIUS:
        ball_pos = (PLOT_WIDTH - BALL_RADIUS, ball_pos[1])
        ball_vel = (-ball_vel[0], ball_vel[1])
    if ball_pos[1] < BALL_RADIUS:
        ball_pos = (ball_pos[0], BALL_RADIUS)
        ball_vel = (ball_vel[0], -ball_vel[1])
    elif ball_pos[1] > PLOT_HEIGHT - BALL_RADIUS:
        ball_pos = (ball_pos[0], PLOT_HEIGHT - BALL_RADIUS)
        ball_vel = (ball_vel[0], -ball_vel[1])

# Define a function to draw the ball
def draw_ball():
    pygame.draw.circle(plot_surface, BALL_COLOR, ball_pos, BALL_RADIUS)

# Define a function to draw the plot
def draw_plot(data):
    # Scale the data to fit the plot height
    data = np.frombuffer(data, dtype=np.int16)
    data = (data / 32767) * (PLOT_HEIGHT // 2) + (PLOT_HEIGHT // 2)
    
    # Clear the plot surface
    plot_surface.fill((0, 0, 0))
    
    # Draw the waveform
    for i in range(len(data) - 1):
        x1 = i * PLOT_WIDTH // CHUNK_SIZE
        y1 = 1*data[i]
        x2 = (i + 1) * PLOT_WIDTH // CHUNK_SIZE
        y2 = 1*data[i + 1]
        pygame.draw.line(plot_surface, (255, 255, 255), (x1, y1), (x2, y2))
    
    # Draw the ball
    draw_ball()

# Create a clock object to control the frame rate
clock = pygame.time.Clock()

# Start the game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Read a chunk of audio data from the stream
                data = stream.read(CHUNK_SIZE)

                # Update the ball velocity based on the audio level
                level = np.abs(np.frombuffer(data, dtype=np.int16)).mean() / 32767
                ball_vel = (int(level * 10), 0)

        # Draw the plot
        draw_plot(stream.read(CHUNK_SIZE))
        window.blit(plot_surface, (0, 0))

        # Update the ball position
        update_ball()

        # Draw the ball
        draw_ball()

        # Draw the instructions
        instructions_surface = font.render("PRETTY BUGGY", True, (255, 255, 255))
        window.blit(instructions_surface, (10, WINDOW_HEIGHT - 30))

        # Update the window
        pygame.display.flip()

        # Control the frame rate
        clock.tick(30)

stream.stop_stream()
stream.close()
p.terminate()