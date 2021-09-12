from collections import deque
from random import sample



class ReplayBuffer:
    def __init__(self, buffer_size=100000):
        self.buffer_size = buffer_size
        self.buffer =deque(maxlen=buffer_size)

    def insert(self, SARS):
        self.buffer.append(SARS)
        # self.buffer = self.buffer[-self.buffer_size:]

    def sample(self, num_samples):
        assert num_samples <= len(self.buffer)
        return sample(self.buffer, num_samples)