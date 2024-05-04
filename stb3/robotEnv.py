import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
import math
import random
import time

class CustomEnv(gym.Env):
    """Custom Environment that follows gym interface."""

    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(self, screen):
        super().__init__()
        # Constants
        self.WIDTH, self.HEIGHT = 800, 600
        self.FPS = 60
        self.TIMER_LIMIT = 5  # Timer limit in seconds

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)

        # Define action and observation space
        # self.action_space = spaces.Discrete(4)  # 4 discrete actions
        self.action_space = spaces.Discrete(5)  # 0: Do nothing, 1: Pick, 2: Place, 3: Rotate arm 1, 4: Rotate arm 2

        self.observation_space = spaces.Box(low=0, high=255, shape=(self.HEIGHT, self.WIDTH, 3), dtype=np.uint8)

        self.screen = screen
        self.clock = None
        self.robot_arm = None
        self.apple_pos = None
        self.box_pos = None
        self.object_radius = 20
        self.score = 0
        self.running = True
        self.timer_start = None  # Variable to store timer start time

        # Robot state
        self.state = [0, 0]

    def generate_apple_position(self):
        min_x = max(self.robot_arm.base_x - self.robot_arm.arm_length, 0)
        max_x = min(self.robot_arm.base_x + self.robot_arm.arm_length, self.WIDTH)
        min_y = max(self.robot_arm.base_y - self.robot_arm.arm_length, 0)
        max_y = min(self.robot_arm.base_y + self.robot_arm.arm_length, self.HEIGHT)
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
        self.screen.fill(self.WHITE)
        pygame.draw.circle(self.screen, self.BLUE, self.apple_pos, self.object_radius)
        pygame.draw.rect(self.screen, self.BLACK, (self.box_pos[0] - self.object_radius, self.box_pos[1] - self.object_radius, self.object_radius * 2, self.object_radius * 2))
        self.robot_arm.draw()
        
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score:.2f}", True, self.BLACK)
        self.screen.blit(score_text, (10, 10))

        # Additional debugging information
        angle_text = font.render(f"Arm Angles: {self.robot_arm.angle1:.2f}, {self.robot_arm.angle2:.2f}", True, self.BLACK)
        self.screen.blit(angle_text, (10, 40))

        holding_text = font.render(f"Holding: {'Yes' if self.robot_arm.holding else 'No'}", True, self.BLACK)
        self.screen.blit(holding_text, (10, 70))

        robot_state_text = font.render(f"Robot State: {self.state}", True, self.BLACK)
        self.screen.blit(robot_state_text, (10, 130))
        
        # Display distance to apple
        if hasattr(self, 'distance_to_apple'):
            distance_text = font.render(f"Distance: {self.distance_to_apple:.2f}", True, self.RED)
            self.screen.blit(distance_text, (10, 100))  # Position below the score

        if self.timer_start is not None:
            elapsed_time = time.time() - self.timer_start
            if elapsed_time >= self.TIMER_LIMIT:
                self.score -= 5
                self.timer_start = None
            else:
                timer_text = font.render(f"Time left: {self.TIMER_LIMIT - int(elapsed_time)}s", True, self.RED)
                self.screen.blit(timer_text, (self.WIDTH - 160, 10))
        
        pygame.display.flip()


    # def check_game_over(self):
    #     if self.score >= 10 or self.score <= -10:
    #         self.running = False
    def check_game_over(self):
        if self.score >= 10 or self.score <= -1000:
            print("Game Over condition met.")
            self.running = False
        if self.state == [1, 1]:
            print("Both actions completed")
            self.running = False  # Or any other action you'd like to take


    def reset(self, seed=None):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.robot_arm = RobotArm(self.WIDTH // 2, self.HEIGHT // 2, 100, self.screen, self.BLACK, self.RED, self.GREEN, self.BLUE)  # Pass colors to RobotArm constructor
        # self.apple_pos = self.generate_apple_position()
        self.apple_pos = (250, 300)
        self.box_pos = (3 * self.WIDTH // 4, self.HEIGHT // 2)
        self.score = 0
        self.running = True
        self.timer_start = None
        # self.state = [0, 0]
        return self._get_observation(), {}

    def _get_observation(self):
        # Create an observation array with dimensions (HEIGHT, WIDTH, 3)
        observation = np.zeros((self.HEIGHT, self.WIDTH, 3), dtype=np.uint8)
        
        # Draw the environment onto the observation array
        self.draw()
        
        # Convert the observation array to a Pygame surface
        surface = pygame.surfarray.make_surface(observation)
        
        # Check if the dimensions match before blitting the array
        if surface.get_size() == self.screen.get_size():
            pygame.surfarray.blit_array(surface, observation)
            return observation.transpose(1, 0, 2)  # Transpose to match the expected shape
        else:
            # Create a resized surface to match self.screen dimensions
            resized_surface = pygame.transform.scale(surface, self.screen.get_size())
            
            # Convert the resized surface back to a NumPy array
            resized_observation = pygame.surfarray.array3d(resized_surface)
            return resized_observation.transpose(1, 0, 2)  # Transpose to match the expected shape




    # def step(self, action):
    #     angle1_change = 0
    #     angle2_change = 0

    #     # Define action mappings
    #     if action == 0:
    #         angle1_change = -2
    #     elif action == 1:
    #         angle1_change = 2
    #     elif action == 2:
    #         angle2_change = 2
    #     elif action == 3:
    #         angle2_change = -2
    #     elif action == 4:  # Pick action
    #         if self.robot_arm.pick(self.apple_pos, self.object_radius):
    #             self.score += 100
    #             self.apple_pos = self.generate_apple_position()
    #             self.timer_start = None
    #         else:
    #             self.score -= 10

    #     elif action == 5:  # Place action
    #         if self.robot_arm.place(self.box_pos, self.object_radius + 10):
    #             self.score += 100
    #             self.apple_pos = self.generate_apple_position()
    #             self.timer_start = None
    #         else:
    #             self.score -= 10

    #     # Update robot arm angles based on action
    #     self.update(angle1_change, angle2_change)


    #     # Handle events (none needed for automatic actions)
    #     self.check_game_over()

    #     # Draw the environment
    #     self.draw()

    #     # Clock tick
    #     self.clock.tick(self.FPS)

    #     # Start timer if not already started
    #     if self.timer_start is None:
    #         self.timer_start = time.time()

    #     # Return all five values
    #     return self._get_observation(), self.score, not self.running, False, {}

    def step(self, action):
        angle1_change = 0
        angle2_change = 0

        # Calculate distance to apple and store it as an attribute
        end_x2 = self.robot_arm.base_x + self.robot_arm.arm_length * math.cos(math.radians(self.robot_arm.angle1)) + \
                self.robot_arm.arm_length * math.cos(math.radians(self.robot_arm.angle2))
        end_y2 = self.robot_arm.base_y - self.robot_arm.arm_length * math.sin(math.radians(self.robot_arm.angle1)) - \
                self.robot_arm.arm_length * math.sin(math.radians(self.robot_arm.angle2))
        
        self.distance_to_apple = math.sqrt((self.apple_pos[0] - end_x2) ** 2 + (self.apple_pos[1] - end_y2) ** 2)

        self.distance_to_box = math.sqrt((self.box_pos[0] - end_x2) ** 2 + (self.box_pos[1] - end_y2) ** 2)

        # Define action mappings
        if action == 0:
            angle1_change = -5
        elif action == 1:
            angle1_change = 5
        elif action == 2:
            angle2_change = 5
        elif action == 3:
            angle2_change = -5
        


        # Update robot arm angles based on action
        self.update(angle1_change, angle2_change)

        # Handle events and check game over state
        self.check_game_over()

        # Check if gripper passes over the target (apple)
        # Update robot arm angles based on action
        self.update(angle1_change, angle2_change)
        
        # Reward logic
        if self.distance_to_apple < self.object_radius:  # Gripper passes over the apple
            if self.state == [0,0]:
                if self.robot_arm.pick(self.apple_pos, self.object_radius):
                    self.score += 100  # Reward for passing over the target
                    print(f"Score after passing over apple: {self.score}") 
                    self.state[0] = 1  # Indicating the apple has been picked
                    self.state[1] = 0  # Indicating the apple has been placed
                    self.apple_pos = self.generate_apple_position()  # Generate a new apple position
                # self.timer_start = None  # Reset timer
            else:
                self.score = -10

        elif self.distance_to_box < self.object_radius:
            if self.state == [1,0]:
                if self.robot_arm.place(self.box_pos, self.object_radius):
                    self.score += 100_000
                    print(f"Score after passing over box: {self.score}")
                    # self.state == [1,1]
                    self.state[0] = 1  # Indicating the apple has been picked
                    self.state[1] = 1  # Indicating the apple has been placed
                    self.apple_pos = self.generate_apple_position()
            # if self.state == [0,0]:
            #     self.score = -20
            else:
                self.score = -20
        # Robot state [0, 0]
        elif self.distance_to_apple <= 5 and self.state == [0, 0]:
            self.score = 30
        elif (self.distance_to_apple > 5 and self.distance_to_apple <= 10) and self.state == [0, 0]:
            self.score = 20
        elif (self.distance_to_apple > 10 and self.distance_to_apple <= 15) and self.state == [0, 0]:
            self.score = 10

        elif self.distance_to_box <= 0 and self.state == [0, 0]:
            self.score = -50
        elif (self.distance_to_box > 5 and self.distance_to_box <= 10) and self.state == [0, 0]:
            self.score = -40
        elif (self.distance_to_box > 10 and self.distance_to_box <= 15) and self.state == [0, 0]:
            self.score = -30
        
        # Robot state [1,0]
        elif self.distance_to_apple <= 5 and self.state == [1, 0]:
            self.score = -50
        elif (self.distance_to_apple > 5 and self.distance_to_apple <= 10) and self.state == [1, 0]:
            self.score = -40
        elif (self.distance_to_apple > 10 and self.distance_to_apple <= 15) and self.state == [1, 0]:
            self.score = -30
        
        elif self.distance_to_box <= 0 and self.state == [1, 0]:
            self.score = 30
        elif (self.distance_to_box > 5 and self.distance_to_box <= 10) and self.state == [1, 0]:
            self.score = 20
        elif (self.distance_to_box > 10 and self.distance_to_box <= 15) and self.state == [1, 0]:
            self.score = 10

        else:
            self.score = (-1 * self.distance_to_apple)
            self.score = (-1 * self.distance_to_box)
        

        # Draw the environment
        self.draw()

        # Clock tick
        self.clock.tick(self.FPS)

        # Start timer if not already started
        if self.timer_start is None:
            self.timer_start = time.time()

        # Return observation, reward, done, and additional info
        return self._get_observation(), self.score, not self.running, False, {}


    def render(self, mode="human"):
        if mode == "human":
            pygame.display.flip()
        elif mode == "rgb_array":
            self.draw()
            observation = self._get_observation()
            return observation
        else:
            raise NotImplementedError("Only human and rgb_array rendering modes are supported.")



    def close(self):
        pygame.quit()

class RobotArm:
    def __init__(self, base_x, base_y, arm_length, screen, BLACK, RED, GREEN, BLUE):
        self.base_x = base_x
        self.base_y = base_y
        self.arm_length = arm_length
        self.angle1 = 0
        self.angle2 = 0
        self.holding = None
        self.screen = screen  # Store the screen object
        self.BLACK = BLACK
        self.RED = RED
        self.GREEN = GREEN
        self.BLUE = BLUE

    def update(self, angle1_change, angle2_change):
        self.angle1 += angle1_change
        self.angle2 += angle2_change

    def draw(self):  # Remove screen argument
        end_x1 = self.base_x + self.arm_length * math.cos(math.radians(self.angle1))
        end_y1 = self.base_y - self.arm_length * math.sin(math.radians(self.angle1))
        end_x2 = end_x1 + self.arm_length * math.cos(math.radians(self.angle2))
        end_y2 = end_y1 - self.arm_length * math.sin(math.radians(self.angle2))
        pygame.draw.line(self.screen, self.BLACK, (self.base_x, self.base_y), (end_x1, end_y1), 5)
        pygame.draw.line(self.screen, self.BLACK, (end_x1, end_y1), (end_x2, end_y2), 5)
        pygame.draw.circle(self.screen, self.RED, (int(end_x2), int(end_y2)), 10)
        if self.holding:
            pygame.draw.circle(self.screen, self.GREEN, (int(end_x2), int(end_y2)), 15)

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

# For testing the environment
# if __name__ == "__main__":
#     pygame.init()
#     screen = pygame.display.set_mode((800, 600))
#     env = CustomEnv(screen)
#     obs, info = env.reset()
#     done = False
#     while not done:
#         action = env.action_space.sample()
#         obs, reward, done, info, _ = env.step(action)
#         env.render()
#     env.close()

