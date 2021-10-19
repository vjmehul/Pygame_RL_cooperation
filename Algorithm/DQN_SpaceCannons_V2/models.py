import torch
import torch.nn as nn
from torch.nn.modules import linear
from Pygame_RL_cooperation.Parameters import Parameters_DQN as c
import torch.optim as optim

class ConvModel(nn.Module):
    
    def __init__(self, obs_shape, num_actions, lr=c.lr):
        assert(len(obs_shape)) == 3 # channel, height and width
        super(ConvModel, self).__init__()
        self.obs_shape = obs_shape
        self.num_actions = num_actions
        self.ConvNet = torch.nn.Sequential(
            torch.nn.Conv2d(4, 16, (8,8), stride=(4, 4)),
            torch.nn.ReLU(),
            torch.nn.Conv2d(16, 32, (4,4), stride=(2, 2)),
            torch.nn.ReLU(),
        )

        with torch.no_grad():
            dummy = torch.zeros((1, *obs_shape))
            x = self.ConvNet(dummy)
            s = x.shape
            fc_size = s[1] * s[2] * s[3]

        self. fc_net = torch.nn.Sequential(
            torch.nn.Linear(fc_size, 256),
            torch.nn.ReLU(),
            torch.nn.Linear(256, num_actions)
        )

        self.opt = optim.RMSprop(self.parameters(), lr=lr)

    def forward(self, x):
        convLat = self.ConvNet(x/255.0)
        return self.fc_net(convLat.view((convLat.shape[0], -1)))

if __name__ == '__main__':
    m = ConvModel((4, 84, 84), 4)
    tensor = torch.zeros(1, 4, 84, 84)
    print(m.forward(tensor))