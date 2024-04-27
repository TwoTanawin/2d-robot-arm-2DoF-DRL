import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from customENV import CustomEnv

# Create a single environment
env = CustomEnv()

# Wrap the environment in a vectorized environment
vec_env = DummyVecEnv([lambda: env])

# Create the PPO agent
model = PPO("MlpPolicy", vec_env, verbose=1)

# Train the agent
model.learn(total_timesteps=10000)

# Test the trained agent
obs = vec_env.reset()
for _ in range(1000):
    action, _ = model.predict(obs)
    obs, reward, done, _ = vec_env.step(action)
    if done:
        obs = vec_env.reset()

# Close the environment
env.close()
