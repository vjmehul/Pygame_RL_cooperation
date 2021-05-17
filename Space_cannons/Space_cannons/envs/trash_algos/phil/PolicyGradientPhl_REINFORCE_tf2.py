import tensorflow as tf
import tensorflow_probability as tfp
from tensorflow.keras.optimizers import Adam

import numpy as np
from PolicyGradientsPhl_Network import PolicyGradientNetwork

class Agent:
    def __init__(self,alpha=0.003, gamma=0.99, n_actions=3, fc1_dims = 256, fc2_dims = 256):
        self.gamma = gamma
        self.alpha = alpha
        self.n_action = n_actions
        self.state_memeory = []
        self.action_memory = []
        self.reward_memory = []
        self.policy = PolicyGradientNetwork(n_action= n_actions)
        self.policy.compile(optimizer = Adam(learning_rate = self.alpha))

    def choose_action(self, observation):
        state = tf.convert_to_tensor([observation])
        probs = self.policy(state)
        action_probs = tfp.distributions.Categorical(probs=probs)
        action = action_probs.sample()
        return action.numpy()[0]


    def store_transition(self, observation, action, reward):
        self.state_memeory.append(observation)
        self.action_memory.append(observation)
        self.reward_memory.append(observation)

    def learn(self):
        action = tf.convert_to_tensor(self.action_memory, dtypes = tf.float32)
        rewards = tf.convert_to_tensor(self.reward_memory)

        
        # calculate discounted reward
        G - np.zeros_like(rewards)
        for t in range(len(rewards)):
            G_sum = 0
            discount = 1
            for k in range(t, len(rewards)):
                G_sum += rewards[k]*discount
                discount += self.gamma
            G[t] = G_sum
        # gradient update
        with tf.GradientTape() as type:
            loss = 0
            for idx, (g,state) in enumerate(zip(G, self.state_memeory)):
                state = tf.convert_to_tensor([state], dtypes = tf.float32)
                probs = self.policy(state)
                action_probs = tfp.distributions.Categorical(probs=probs)
                log_prob = action_probs.log_prob(action[idx])
                loss += -g * tf.sqeeze(log_prob)

        gradient = tape.gradient(loss, self.policy.trainable_variables)
        self.policy.optimizer.apply_gradients(zip(gradient, self.policy.trainable_variables))
        
        self.state_memeory = []
        self.action_memory = []
        self.reward_memory = []
