from keras.layers import Activation, Dense, Conv2D, Flatten
from keras.models import Sequential, load_model
from keras.optimizers import Adam
from keras import backend as K
import numpy as np


class ReplayBuffer():
    def __init__(self,max_size, input_dims):
        self.mem_size = max_size
        self.mem_cntr = 0
        self.state_memory = np.zeros((self.mem_size, *input_dims),
                                     dtype=np.float32)
        self.new_state_memory = np.zeros((self.mem_size,*input_dims),
                                         dtype=np.float32)
        self.action_memory = np.zeros(self.mem_size, dtype=np.int32)
        self.reward_memory = np.zeros(self.mem_size, dtype=np.float32)
        self.terminal_memory = np.zeros(self.mem_size, dtype=np.uint8)


    def store_transition(self, state, action, reward, state_, done):

        index = self.mem_cntr % self.mem_size
        self.state_memory[index] = state
        self.new_state_memory[index] = state_
        self.reward_memory[index] = reward
        self.action_memory[index] = action
        self.terminal_memory[index] = done

        self.mem_cntr += 1

    def sample_buffer(self, batch_size):

        max_mem = min(self.mem_cntr, self.mem_size)
        batch = np.random.choice(max_mem, batch_size, replace = False)

        states = self.state_memory[batch]
        states_ = self.new_state_memory[batch]
        rewards = self.reward_memory[batch]
        actions = self.action_memory[batch]
        # terminal = self.terminal_memory[batch]
        dones = self.terminal_memory[batch]

        return states, actions, rewards, states_, dones


def build_dqn(lr, n_actions, input_dims, fc1_dims):
    model = Sequential()
    model.add(Conv2D(filters=32, kernel_size=8, strides=4, activation='relu',
                     input_shape=(*input_dims,), data_format='channels_first'))

    model.add(Conv2D(filters=64, kernel_size=4, strides=2, activation='relu',
                     data_format='channels_first'))

    model.add(Conv2D(filters=64, kernel_size=3, strides=1, activation='relu',
                     data_format='channels_first'))
    model.add(Flatten())
    model.add(Dense(fc1_dims, activation='relu'))
    model.add(Dense(n_actions))

    model.compile(optimizer=Adam(learning_rate=lr), loss = 'mean_squared_error')

    return model


class Agent():
    def __init__(self, alpha, gamma, n_actions, epsilon, batch_size, replace, input_dims, eps_dec = 1e-5, eps_min = 0.01,
                mem_size = 1000000, fname='dqn_model.h5', q_eval_fname= 'q_eval.h5', q_target_fname= 'q_target.h5'):

        self.action = [i for i in range(n_actions)]
        self.gamma = gamma
        self.epsilon = epsilon
        self.eps_dec= eps_dec
        self.eps_min = eps_min
        self.batch_size = batch_size
        self.replace=replace
        self.model_file = fname
        self.q_target_mode_filname = q_target_fname
        self.q_eval_model_file = q_eval_fname
        self.learn_step = 0
        self.memory = ReplayBuffer(mem_size, input_dims)
        self.q_eval = build_dqn(alpha, n_actions, input_dims, 512)
        self.q_next = build_dqn(alpha, n_actions, input_dims, 512)


    def replace_target_network(self):
        if self.replace !=0 and self.learn_step % self.replace ==0:
            self.q_next.set_weights(self.q_eval.get_weights())

    def store_transition(self, state, action, reward, new_state, done):
        self.memory.store_transition(state, action, reward, new_state, done)



    def choose_action(self, observation):
        if np.random.random() < self.epsilon:
            action = np.random.choice(self.action_space)
        else:
            state = np.array([observation], copy=False, dtype=np.float32)
            actions = self.q_eval.predict(state)
            action = np.argmax(actions)
        return action

    def learn(self):
        if self.memory.mem_cntr > self.batch_size:

            state, actions, rewards, states_, done = self.memory.sample_buffer(self.batch_size)
            self.replace_target_network()

            q_eval = self.q_eval.predict(state)
            q_next = self.q_eval.predict(states_)

            q_next[done]=0.0

            indices = np.arange(self.batch_size)

            q_target = np.copy(q_eval)

            q_target[indices, actions] = rewards + \
                                                    self.gamma * np.max(q_next, axis= 1)

            self.q_eval.train_on_batch(state, q_target)

            self.epsilon = self.epsilon - self.eps_dec \
                            if self.epsilon > self.eps_min else self.eps_min


            self.learn_step +=1

    def save_model(self):
        self.q_eval.save(self.q_eval_model_file)
        self.q_next.save(self.q_target_mode_filname)
        
        print('**********SAVING MODEL***********')


    def load_model(self):
        self.q_eval = load_model(self.q_eval_model_file)
        self.q_next = load_model(self.q_target_mode_filname)
        print('******LOADING MODELS********')
