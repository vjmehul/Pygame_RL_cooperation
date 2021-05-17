import warnings
import cv2
warnings.simplefilter(action='ignore', category=FutureWarning)

from stable_baselines import DQN
from stable_baselines.bench import Monitor
from stable_baselines.common.callbacks import BaseCallback
from stable_baselines.results_plotter import load_results, ts2xy
from stable_baselines import results_plotter
import numpy as np
import matplotlib.pyplot as plt
from custom_env import custom_game_env
import os
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
import gym
import Space_cannons
import cv2

env = gym.make('SpaceCannon-v0')


print(tf.__version__)

class SaveOnBestTrainingRewardCallback(BaseCallback):
    """
    Callback for saving a model (the check is done every ``check_freq`` steps)
    based on the training reward (in practice, we recommend using ``EvalCallback``).
    :param check_freq: (int)
    :param log_dir: (str) Path to the folder where the model will be saved.
      It must contains the file created by the ``Monitor`` wrapper.
    :param verbose: (int)
    """
    def __init__(self, check_freq: int, log_dir: str, verbose=1):
        super(SaveOnBestTrainingRewardCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.log_dir = log_dir
        self.save_path = os.path.join(log_dir, 'best_model')
        self.best_mean_reward = -np.inf

    def _init_callback(self) -> None:
        # Create folder if needed
        if self.save_path is not None:
            os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self) -> bool:
        if self.n_calls % self.check_freq == 0:

          # Retrieve training reward
          x, y = ts2xy(load_results(self.log_dir), 'timesteps')
          if len(x) > 0:
              # Mean training reward over the last 100 episodes
              mean_reward = np.mean(y[-50:])
              if self.verbose > 0:
                print("Num timesteps: {}".format(self.num_timesteps))
                print("Best mean reward: {:.2f} - Last mean reward per episode: {:.2f}".format(self.best_mean_reward, mean_reward))

              # New best model, you could save the agent here
              if mean_reward > self.best_mean_reward:
                  self.best_mean_reward = mean_reward
                  # Example for saving best model
                  if self.verbose > 0:
                    print("Saving new best model to {}".format(self.save_path))
                  self.model.save(self.save_path)

        return True

# Create log dir
log_dir = "tmp/"
os.makedirs(log_dir, exist_ok=True)

# Create environment
env = custom_game_env()
env = Monitor(env, log_dir)
env._max_episode_steps = 50000
# Instantiate the agent
model = DQN('CnnPolicy', env, buffer_size=10000, learning_rate=1e-4, learning_starts=10000, 
                target_network_update_freq=1000, train_freq=4, exploration_final_eps=0.01,
                exploration_fraction=0.01, prioritized_replay_alpha=.6, prioritized_replay=True)
callback = SaveOnBestTrainingRewardCallback(check_freq=1000, log_dir=log_dir)
# Train the agent

# Train the agent
model.learn(total_timesteps=50000, callback=callback)

model.save("SpaceModel")

def evaluate(model, num_episodes=20):
    """
    Evaluate a RL agent
    :param model: (BaseRLModel object) the RL Agent
    :param num_episodes: (int) number of episodes to evaluate it
    :return: (float) Mean reward for the last num_episodes
    """
    # This function will only work for a single Environment
    env = model.get_env()
    all_episode_rewards = []
    action_hist=[]
    for i in range(num_episodes):
        episode_rewards = []
        done = False
        obs = env.reset()
        while not done:
            # env.render()
            # _states are only useful when using LSTM policies
            action, _states = model.predict(obs)

            action_hist.append(action)
            # here, action, rewards and dones are arrays
            # because we are using vectorized env
            obs, reward, done, info = env.step(action)
            episode_rewards.append(reward)
            

        all_episode_rewards.append(sum(episode_rewards))

    mean_episode_reward = np.mean(all_episode_rewards)
    print("Mean reward:", mean_episode_reward, "Num episodes:", num_episodes)

    return mean_episode_reward
model = DQN.load("SpaceModel",env=env)
evaluate(model)


results_plotter.plot_results([log_dir], 100000, results_plotter.X_TIMESTEPS, "DDPG LunarLander")
plt.show()

# Save the agent
model.save("SpaceModel")