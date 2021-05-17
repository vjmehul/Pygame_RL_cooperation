import gym
import numpy as np
from PolicyGradientPhl_REINFORCE_tf2 import Agent
from utils import plotLearning
from custom_env import custom_game_env



# obs = env.reset()
# env.render()

if __name__ == '__main__':
    agent_1 = Agent(alpha = 0.0005, gamma = 0.99,
                  n_actions = 3)
    
    
    agent_2 = Agent(alpha = 0.0005, gamma = 0.99,
                  n_actions = 3)
    env = custom_game_env()

    score_history = []
    n_episodes = 2000

    for i in range(n_episodes):
        done = False
        score = 0
        observation = env.reset()


        obs_space = env.observation_space
        action_space = env.action_space_1.sample()
        print("The observation space: {}".format(obs_space))
        print("The action space: {}".format(action_space))

        while not done:
            action_1 = agent_1.choose_action(observation)
            action_2 = agent_2.choose_action(observation)


            observation_, reward, done, info = env.step(action_1)


            agent.store_transition(observation, action, reward)
            observation = observation_
            score += reward
            env.render()
        score_history.append(score)
        
        agent.learn()
        
        avg_score = np.mean(score_history[-100:])
        print('episode', i, 'score  %.1f'% score, 'avg score %.1f'% avg_score )
        
        filename = 'SpaceDragons'
    plotLearning(score_history, filename= filename, window = 100)
    