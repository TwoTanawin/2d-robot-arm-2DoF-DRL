from stable_baselines3 import A2C, PPO
from stable_baselines3.common.monitor import Monitor
import matplotlib.pyplot as plt
import numpy as np
from customENV import CustomEnv
import pygame

screen = pygame.display.set_mode((800, 600))

env = CustomEnv(screen)

# Load the trained model
model = PPO.load("/home/two-asus/Documents/ait/drl/2d-robot-arm-2DoF-DRL/stb3/report/PPO_MLP_10K_Robot2DoF/model/10000.zip", env=env)

# Lists to store rewards and episode lengths
episode_rewards = []
episode_lengths = []

# Inference loop
episodes = 10
for _ in range(episodes):
    obs, info = env.reset()
    done = False
    episode_reward = 0
    episode_length = 0
    while not done:
        action, _ = model.predict(obs)
        obs, reward, done, info, _ = env.step(action)
        episode_reward += reward
        episode_length += 1
        env.render(mode='human')  # Render the environment in human mode during inference
        print(f"reward : {reward}")
    episode_rewards.append(episode_reward)
    episode_lengths.append(episode_length)

# Plotting rewards
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.plot(np.arange(len(episode_rewards)), episode_rewards)
plt.xlabel('Episodes')
plt.ylabel('Episode Reward')
plt.title('Episode Rewards during Inference')

plt.subplot(1, 2, 2)
plt.plot(np.arange(len(episode_lengths)), episode_lengths)
plt.xlabel('Episodes')
plt.ylabel('Episode Length')
plt.title('Episode Lengths during Inference')

plt.tight_layout()
plt.savefig("/home/two-asus/Documents/ait/drl/2d-robot-arm-2DoF-DRL/stb3/report/img/img4_ppo_mlp.jpg")
plt.show()

env.close()  # Close the environment after inference