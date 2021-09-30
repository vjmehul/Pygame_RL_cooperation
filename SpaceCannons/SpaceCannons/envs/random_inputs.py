from custom_env import custom_game_env
import random
import csv
import random

env = custom_game_env()
obs = env.reset()
env.render()

episodes = 1000
i = 1
scores = []

while i <= episodes:
    # action = []
    i = random.randint(0,4)
    n = random.randint(0,4)
    action=([i,n])
    print(action)
    # env.render()
    obs, global_reward_1, done, info = env.step(action)


