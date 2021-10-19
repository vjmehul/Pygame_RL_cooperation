from collections import deque
from random import sample



class ReplayBuffer:
    def __init__(self, buffer_size=100000):
        self.buffer_size = buffer_size
        self.buffer =deque(maxlen=buffer_size)

    def insert(self, SARS):
        self.buffer.append(SARS)

    def sample(self, num_samples):
        assert num_samples <= len(self.buffer)
        return sample(self.buffer, num_samples)

    def print_buffer(self):
        for i in range(len(self.buffer)):
            print("action: ", self.buffer[i].action, "reward: ", self.buffer[i].reward, "buffer_ID: ", self.buffer[i].bufferID)

    def redistribute_reward(self,reward):
        print("Redistribute")
        i=80
        last_element = len(self.buffer) -1
        while i != 0:
            self.buffer[last_element].reward = reward
            last_element -= 1
            i -= 1
