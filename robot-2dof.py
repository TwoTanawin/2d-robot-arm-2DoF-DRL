import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Game variables
score = 0
score_counted = False  # Flag to track if score has been counted for Key_c and Key_v

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2DoF Robot Arm Game")

# Clock for controlling FPS
clock = pygame.time.Clock()

# Robot Arm class
class RobotArm:
    def __init__(self):
        self.base_x = WIDTH // 2
        self.base_y = HEIGHT // 2
        self.arm_length = 100
        self.angle1 = 0
        self.angle2 = 0
        self.holding = None

    def update(self, angle1_change, angle2_change):
        self.angle1 += angle1_change
        self.angle2 += angle2_change

    def draw(self):
        end_x1 = self.base_x + self.arm_length * math.cos(math.radians(self.angle1))
        end_y1 = self.base_y - self.arm_length * math.sin(math.radians(self.angle1))

        end_x2 = end_x1 + self.arm_length * math.cos(math.radians(self.angle2))
        end_y2 = end_y1 - self.arm_length * math.sin(math.radians(self.angle2))

        pygame.draw.line(screen, BLACK, (self.base_x, self.base_y), (end_x1, end_y1), 5)
        pygame.draw.line(screen, BLACK, (end_x1, end_y1), (end_x2, end_y2), 5)
        pygame.draw.circle(screen, RED, (int(end_x2), int(end_y2)), 10)

        if self.holding:
            pygame.draw.circle(screen, GREEN, (int(end_x2), int(end_y2)), 15)

    def pick(self, object_pos, object_radius):
        end_x2 = self.base_x + self.arm_length * math.cos(math.radians(self.angle1)) + \
                 self.arm_length * math.cos(math.radians(self.angle2))
        end_y2 = self.base_y - self.arm_length * math.sin(math.radians(self.angle1)) - \
                 self.arm_length * math.sin(math.radians(self.angle2))

        distance = math.sqrt((object_pos[0] - end_x2) ** 2 + (object_pos[1] - end_y2) ** 2)
        if distance < object_radius:
            self.holding = object_pos
            return True
        else:
            return False

    def place(self, target_pos, target_radius):
        if self.holding:
            end_x2 = self.base_x + self.arm_length * math.cos(math.radians(self.angle1)) + \
                     self.arm_length * math.cos(math.radians(self.angle2))
            end_y2 = self.base_y - self.arm_length * math.sin(math.radians(self.angle1)) - \
                     self.arm_length * math.sin(math.radians(self.angle2))

            distance = math.sqrt((target_pos[0] - end_x2) ** 2 + (target_pos[1] - end_y2) ** 2)
            if distance < target_radius:
                self.holding = None
                return True
        return False

    def reset(self):
        self.angle1 = 0
        self.angle2 = 0
        self.holding = None

# Function to generate a random position for the apple within the robot arm's area
def generate_apple_position():
    min_x = max(robot_arm.base_x - robot_arm.arm_length, 0)
    max_x = min(robot_arm.base_x + robot_arm.arm_length, WIDTH)
    min_y = max(robot_arm.base_y - robot_arm.arm_length, 0)
    max_y = min(robot_arm.base_y + robot_arm.arm_length, HEIGHT)
    return (random.randint(min_x, max_x), random.randint(min_y, max_y))

# Initialize robot arm
robot_arm = RobotArm()

# Apple and box positions
apple_pos = generate_apple_position()
box_pos = (3 * WIDTH // 4, HEIGHT // 2)
object_radius = 20

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                if robot_arm.pick(apple_pos, object_radius):
                    score += 10
                else:
                    score -= 10  # Deduct 10 points for wrong pick
            elif event.key == pygame.K_v:
                if robot_arm.place(box_pos, object_radius + 10):  # Adjusted target_radius for placing in the box
                    score += 10
                    apple_pos = generate_apple_position()  # Generate new random position for the apple
                else:
                    score -= 10  # Deduct 10 points for wrong place

    # Check if the game should finish
    if score >= 100:
        running = False
    elif score <= -30:  # Game over condition if score drops below -30
        running = False

    # Clear the screen
    screen.fill(WHITE)

    # Control logic
    keys = pygame.key.get_pressed()
    angle1_change = 0
    angle2_change = 0
    if keys[pygame.K_LEFT]:
        angle1_change = -1
    if keys[pygame.K_RIGHT]:
        angle1_change = 1
    if keys[pygame.K_UP]:
        angle2_change = 1
    if keys[pygame.K_DOWN]:
        angle2_change = -1

    robot_arm.update(angle1_change, angle2_change)

    # Draw the apple and box
    pygame.draw.circle(screen, BLUE, apple_pos, object_radius)
    pygame.draw.rect(screen, BLACK, (box_pos[0] - object_radius, box_pos[1] - object_radius, object_radius * 2, object_radius * 2))

    # Draw the robot arm
    robot_arm.draw()

    # Display score
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    # Update the display
    pygame.display.flip()

    # Cap the FPS
    clock.tick(FPS)

# Game over display
screen.fill(WHITE)
font = pygame.font.Font(None, 72)
if score >= 100:
    game_over_text = font.render("Game Finish", True, GREEN)
else:
    game_over_text = font.render("Game Over", True, RED)
screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2 - 50))
final_score_text = font.render(f"Final Score: {score}", True, BLACK)
screen.blit(final_score_text, (WIDTH // 2 - 180, HEIGHT // 2 + 50))
pygame.display.flip()

# Wait for a few seconds before quitting
pygame.time.delay(3000)

# Quit Pygame
pygame.quit()
