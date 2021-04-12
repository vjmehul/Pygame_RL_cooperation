from custom_env import custom_game_env

from PIL import Image
import random
import csv
import random

env = custom_game_env()
obs = env.reset()
env.render()

action_len_1=env.action_space_1.n
action_len_2=env.action_space_2.n
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
    obs, global_reward_1, reward_1, reward_2, penalty, done, info = env.step(action)

    # Save our observation as an image
    im = Image.fromarray(obs[:, :, 0] * 255)
    im = im.convert("L")
    im.save("algo-view.jpeg")   

    env.render()

    if done:
        print(f"Episode {i}: {info['score']}")
        scores.append(info['score'])
        env.reset()
        i += 1

print(f"\n-------\nEpisodes: {episodes}\nAverage: {sum(scores)/len(scores)}\nMax: {max(scores)}\nMin: {min(scores)}\n-------")
