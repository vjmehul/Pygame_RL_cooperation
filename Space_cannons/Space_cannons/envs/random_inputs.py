from custom_env import custom_game_env
import random
import csv
import random

env = custom_game_env()
obs = env.reset()
# env.render()
env.action_space.shape
action_len_1=3
action_len_2=3
action_len=action_len_1+action_len_2

episodes = 1000
i = 1
scores = []

while i <= episodes:
    action = []
    for i in range(0,6):
        n = random.randint(0,1)
        action.append(n)
    print(action)
    env.render()
    obs, global_reward_1, done, info = env.step(action)


