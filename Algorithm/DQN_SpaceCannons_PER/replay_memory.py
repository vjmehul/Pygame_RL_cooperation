from collections import deque
from random import sample
import numpy as np
from random import random, choices

from numpy.core.numeric import indices

class ReplayBuffer:
    def __init__(self, buffer_size=20000):
        self.buffer_size = buffer_size
        self.buffer =deque(maxlen=buffer_size)
        self.priorities = deque(maxlen=buffer_size)

    def insert(self, SARS):
        self.buffer.append(SARS)
        self.priorities.append(max(self.priorities, default=1))   # new experience needs to be trained on hence the max priorities

    def get_probabilities(self, priority_scale):
        scaled_priorities = np.array(self.priorities) ** priority_scale
        sample_probabilities = scaled_priorities / sum(scaled_priorities)
        return sample_probabilities

    def get_importance(self, probabilities):
        importance = 1/len(self.buffer) * 1/probabilities
        importance_normalized = importance /max(importance)
        return importance_normalized

    def sample(self, num_samples,priority_scale=1):
        assert num_samples <= len(self.buffer)
        sample_probs = self.get_probabilities(priority_scale)
        samples_indices = choices(range(len(self.buffer)), k=num_samples, weights = sample_probs)
        samples = np.array(self.buffer)[samples_indices]
        importance = self.get_importance(sample_probs[samples_indices])
        return (samples), importance, samples_indices


    def set_priorities(self, indices, errors, offset = 0.1):

        for i,e in zip(indices, errors):
            self.priorities[i] = abs(e.item()) + offset