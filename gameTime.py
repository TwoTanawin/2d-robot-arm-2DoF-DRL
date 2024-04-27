import pygame
import math
import random
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
TIMER_LIMIT = 30  # Timer limit in seconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gym Environment")

# Clock for controlling FPS
clock = pygame.time.Clock()

# Gym environment class
class GymEnv:
    def __init__(self):
        self.robot_arm = RobotArm()
        self.apple_pos = self.generate_apple_position()
        self.box_pos = (3 * WIDTH // 4, HEIGHT // 2)
        self.object_radius = 20
        self.score = 0
        self.running = True
        self.timer_start = None  # Variable to store timer start time
        self.game_start_time = None  # Variable to store game start time

    def generate_apple_position(self):
        min_x = max(self.robot_arm.base_x - self.robot_arm.arm_length, 0)
        max_x = min(self.robot_arm.base_x + self.robot_arm.arm_length, WIDTH)
        min_y = max(self.robot_arm.base_y - self.robot_arm.arm_length, 0)
        max_y = min(self.robot_arm.base_y + self.robot_arm.arm_length, HEIGHT)
        return (random.randint(min_x, max_x), random.randint(min_y, max_y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    if self.robot_arm.pick(self.apple_pos, self.object_radius):
                        self.score += 10
                        self.timer_start = None  # Reset timer
                    else:
                        self.score -= 10
                elif event.key == pygame.K_v:
                    if self.robot_arm.place(self.box_pos, self.object_radius + 10):
                        self.score += 10
                        self.apple_pos = self.generate_apple_position()
                        self.timer_start = None  # Reset timer
                    else:
                        self.score -= 10

    def update(self, angle1_change, angle2_change):
        self.robot_arm.update(angle1_change, angle2_change)

    def draw(self):
        screen.fill(WHITE)
        pygame.draw.circle(screen, BLUE, self.apple_pos, self.object_radius)
        pygame.draw.rect(screen, BLACK, (self.box_pos[0] - self.object_radius, self.box_pos[1] - self.object_radius, self.object_radius * 2, self.object_radius * 2))
        self.robot_arm.draw()
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, BLACK)
        screen.blit(score_text, (10, 10))
        if self.timer_start is not None:
            elapsed_time = time.time() - self.timer_start
            if elapsed_time >= TIMER_LIMIT:
                self.score -= 5
                self.timer_start = None
            else:
                timer_text = font.render(f"Time left: {TIMER_LIMIT - int(elapsed_time)}s", True, RED)
                screen.blit(timer_text, (WIDTH - 160, 10))

        if self.game_start_time is not None:
            elapsed_game_time = time.time() - self.game_start_time
            game_timer_text = font.render(f"Game Time: {int(elapsed_game_time)}s", True, BLACK)
            screen.blit(game_timer_text, (10, 40))

        pygame.display.flip()

    def check_game_over(self):
        if self.score >= 100 or self.score <= -30:
            self.running = False

    def run(self):
        self.game_start_time = time.time()  # Start tracking game time
        while self.running:
            self.handle_events()
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
            self.update(angle1_change, angle2_change)
            self.draw()
            self.check_game_over()
            clock.tick(FPS)

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

# Initialize gym environment
gym_env = GymEnv()
gym_env.run()

# Quit Pygame
pygame.quit()
