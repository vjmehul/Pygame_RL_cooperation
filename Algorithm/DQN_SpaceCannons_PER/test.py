from random import sample

from gym import spaces
x=[spaces.Discrete(4),spaces.Discrete(4)]

for i in range(10):
    print(x[1].sample())