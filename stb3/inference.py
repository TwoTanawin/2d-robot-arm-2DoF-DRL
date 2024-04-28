from customENV import CustomEnv
import pygame

screen = pygame.display.set_mode((800, 600))

env = CustomEnv(screen)
episodes = 50

for episode in range(episodes):
	done = False
	obs, info = env.reset()
	while True:#not done:
		random_action = env.action_space.sample()
		print("action",random_action)
		obs, reward, done, info, _ = env.step(random_action)
		print('reward',reward)
