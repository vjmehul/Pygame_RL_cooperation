from phil_dqn_2 import Agent
import numpy as np
from utils import plotLearning, make_env




if __name__ == '__main__':
    env = make_env('SpaceCannon-v0')
    print('done')
    n_games = 250
    lr = 0.0001
    load_checkpoint = False
    
    agent = Agent(gamma = 0.99, epsilon=1.0, lr=lr,
                  input_dims = env.observation_space.shape,
                    n_actions = 8, mem_size = 150000, batch_size = 64,
                    epsilon_end = 0.01)
    scores = []
    eps_history = []
    