import pygame
import math
import sys
import time
import random
from pygame.locals import *

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3DOF Robot Arm Game")
clock = pygame.time.Clock()

ARM_LENGTH_1 = 100
ARM_LENGTH_2 = 80
ARM_LENGTH_3 = 60
BASE_X, BASE_Y = WIDTH // 2, HEIGHT // 2
BASE_RADIUS = 20
APPLE_RADIUS = 10
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
FONT_SIZE = 24

class Arm:
    def __init__(self):
        self.angle_1 = 0
        self.angle_2 = 0
        self.angle_3 = 0
        self.target_x = random.randint(BASE_X - ARM_LENGTH_1, BASE_X + ARM_LENGTH_1)
        self.target_y = random.randint(BASE_Y - ARM_LENGTH_1, BASE_Y + ARM_LENGTH_1)
        self.destination_x = random.randint(BASE_X - ARM_LENGTH_1, BASE_X + ARM_LENGTH_1)
        self.destination_y = random.randint(BASE_Y - ARM_LENGTH_1, BASE_Y + ARM_LENGTH_1)
        self.gripper_open = False
        self.score = 0
        self.target_color = RED

    def update_angles(self, angle_1, angle_2, angle_3):
        self.angle_1 = angle_1
        self.angle_2 = angle_2
        self.angle_3 = angle_3

    def toggle_gripper(self):
        self.gripper_open = not self.gripper_open

    def check_placement(self):
        if self.target_x == self.destination_x and self.target_y == self.destination_y:
            self.score += 10
            self.target_x = random.randint(BASE_X - ARM_LENGTH_1, BASE_X + ARM_LENGTH_1)
            self.target_y = random.randint(BASE_Y - ARM_LENGTH_1, BASE_Y + ARM_LENGTH_1)
            self.destination_x = random.randint(BASE_X - ARM_LENGTH_1, BASE_X + ARM_LENGTH_1)
            self.destination_y = random.randint(BASE_Y - ARM_LENGTH_1, BASE_Y + ARM_LENGTH_1)
            return True
        else:
            self.score -= 10
            return False

    def draw(self):
        end_x = BASE_X + ARM_LENGTH_1 * math.cos(self.angle_1)
        end_y = BASE_Y - ARM_LENGTH_1 * math.sin(self.angle_1)
        end_x_2 = end_x + ARM_LENGTH_2 * math.cos(self.angle_1 + self.angle_2)
        end_y_2 = end_y - ARM_LENGTH_2 * math.sin(self.angle_1 + self.angle_2)
        end_x_3 = end_x_2 + ARM_LENGTH_3 * math.cos(self.angle_1 + self.angle_2 + self.angle_3)
        end_y_3 = end_y_2 - ARM_LENGTH_3 * math.sin(self.angle_1 + self.angle_2 + self.angle_3)

        pygame.draw.line(screen, WHITE, (BASE_X, BASE_Y), (end_x, end_y), 5)
        pygame.draw.line(screen, WHITE, (end_x, end_y), (end_x_2, end_y_2), 5)
        pygame.draw.line(screen, WHITE, (end_x_2, end_y_2), (end_x_3, end_y_3), 5)

        if self.gripper_open:
            pygame.draw.line(screen, YELLOW, (self.target_x - 5, self.target_y), (self.target_x + 5, self.target_y), 3)
        else:
            pygame.draw.line(screen, YELLOW, (self.target_x - 5, self.target_y), (self.target_x + 5, self.target_y), 3)
            pygame.draw.line(screen, YELLOW, (self.target_x, self.target_y - 5), (self.target_x, self.target_y + 5), 3)

        pygame.draw.circle(screen, RED, (int(end_x_3), int(end_y_3)), 10)

    def draw_score(self):
        font = pygame.font.Font(None, FONT_SIZE)
        text = font.render("Score: {}".format(self.score), True, WHITE)
        screen.blit(text, (10, 10))

arm = Arm()
game_start_time = time.time()

def handle_keys():
    keys = pygame.key.get_pressed()
    angle_change = math.radians(1)  # Angle change increment

    if keys[K_LEFT]:
        arm.angle_1 -= angle_change
    if keys[K_RIGHT]:
        arm.angle_1 += angle_change
    if keys[K_UP]:
        arm.angle_2 -= angle_change
    if keys[K_DOWN]:
        arm.angle_2 += angle_change
    if keys[K_SPACE]:
        arm.angle_3 -= angle_change
    if keys[K_RETURN]:
        arm.angle_3 += angle_change
    if keys[K_c]:
        arm.toggle_gripper()
        arm.target_color = YELLOW if arm.gripper_open else RED
    if keys[K_v]:
        arm.destination_x, arm.destination_y = pygame.mouse.get_pos()
        if arm.check_placement():
            if arm.score >= 100:
                print("You win!")
                pygame.quit()
                sys.exit()

running = True
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    handle_keys()
    arm.draw()
    arm.draw_score()

    pygame.draw.circle(screen, arm.target_color, (arm.target_x, arm.target_y), APPLE_RADIUS)
    pygame.draw.circle(screen, GREEN, (arm.destination_x, arm.destination_y), APPLE_RADIUS)

    time_elapsed = time.time() - game_start_time
    if time_elapsed > 30:
        print("Game over! Time limit exceeded.")
        pygame.quit()
        sys.exit()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
