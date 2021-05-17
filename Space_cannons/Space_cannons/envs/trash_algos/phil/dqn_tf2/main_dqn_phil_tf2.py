from dqn_phil_tf2 import Agent
import sys
print(sys.version_info)
import sys
is_64bits = sys.maxsize > 2**32
print(is_64bits)
import numpy as np
import gym
from utils import plotLearning
import Space_cannons
import tensorflow as tf

if __name__ == '__main__':
    tf.compat.v1.disable_eager_execution()
    
    env = gym.make('SpaceCannon-v0')
    n_games = 500
    lr = 0.001
    agent = Agent(gamma = 0.99, epsilon=1.0, lr=lr,
                  input_dims = env.observation_space.shape,
                    n_actions = 8, mem_size = 150000, batch_size = 64,
                    epsilon_end = 0.01)
    scores = []
    eps_history = []
    
    for i in range(n_games):
        done = False
        score = 0
        observation = env.reset()
        while not done:
            action = agent.choose_action(observation)
            observation_, reward, done, info = env.step(action)
            score += reward
            agent.store_transition(observation, action, reward, observation_, done)
            observation = observation_
            agent.learn()
        eps_history.append(agent.epsilon)
        scores.append(score)

        avg_score = np.mean(scores[-100:])
        print('episode: ', i, 'score %.2f' % score,
              'average_score %.2f' % avg_score,
              'epsilon %.2f' % agent.epsilon)
        filename = 'dqn_phil_1.png'
        x = [i+1 for i in range(n_games)]
        plotLearning(x, scores, eps_history,filename)
        