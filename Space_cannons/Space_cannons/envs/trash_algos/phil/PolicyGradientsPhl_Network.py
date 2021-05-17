import tensorflow as tf
from tensorflow.keras.layers import Dense


class PolicyGradientNetwork(tf.keras.Model):
    def __init__(self, n_action, fc1_dims= 256, fc2_dims = 256):
        super(PolicyGradientNetwork, self).__init__()
        self.fc1_dims = fc1_dims
        self.fc2_dims = fc2_dims
        self.n_action = n_action

        self.fc1 = Dense(self.fc1_dims, activation = 'relu')
        self.fc2 = Dense(self.fc2_dims, activation = 'relu')
        self.pi = Dense(self.n_action, activation = 'softmax')


    def call(self,state):
        value = self.fc1(state)
        value = self.fc2(value)

        pi = self.pi(value)

        return pi
