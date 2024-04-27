import gymnasium as gym
from stable_baselines3 import A2C
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
import os
import time
from customENV import CustomEnv
import pygame

import matplotlib.pyplot as plt

model_dir = f"report/ppo_Robot2DoF/model"
logdir = f"report/ppo_Robot2DoF/logs"
if not os.path.exists(model_dir):
    os.makedirs(model_dir)
if not os.path.exists(logdir):
    os.makedirs(logdir)

screen = pygame.display.set_mode((800, 600))
# Create and wrap your custom environment
env = CustomEnv(screen)  # Replace 'screen' with your screen object if needed
env = Monitor(env, logdir)  # Wrap with Monitor for logging
env.reset()

# Initialize and train the PPO model
model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=logdir, batch_size=8)

TIMESTEPS = 1000
for i in range(1, 100):
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name="PPO")
    model.save(f"{model_dir}/{TIMESTEPS*i}")

    # Render the environment in rgb_array mode after training
    obs = env.render(mode="rgb_array")

# Close the environment
env.close()