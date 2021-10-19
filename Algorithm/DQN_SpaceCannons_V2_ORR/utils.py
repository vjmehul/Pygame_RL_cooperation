import gym
import numpy as np
import cv2
from random import randint


class FramestackingENV:
    def __init__(self, env,width, height, num_stack=4):
        self.env = env
        self.width = width
        self.height = height
        self.num_stack = num_stack

        self.buffer = np.zeros((num_stack, height, width), 'uint8')
        self.frame = None

    def Preprocess_frames(self, image):
        image=image[:, 0:600]
        image = cv2.resize(image,(self.width, self.height))
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        image=cv2.rotate(image,cv2.ROTATE_90_CLOCKWISE)
        image=cv2.flip(image,1)

        return image

    def step(self, action):
        image, reward, done,  info = self.env.step(action)
        self.frame = image.copy()
        image =self.Preprocess_frames(image)
        self.buffer[1:self.num_stack, :, :] = self.buffer[0:self.num_stack-1, :, :]
        self.buffer[0, :, :] = image
        return self.buffer.copy(), reward, done, info

    def reset(self):
        image = self.env.reset()
        self.frame = image.copy()
        image = self.Preprocess_frames(image)
        self.buffer = np.stack([image]*self.num_stack, 0)
        return self.buffer.copy()


    def render(self, mode):
        if mode == 'rgb_array':
            return self.frame
        return super(FramestackingENV, self).render(mode)

    @property
    def observation_space(self):
        return np.zeros((self.num_stack, self.height, self.width))

    @property
    def action_space(self):
        return self.env.action_space



    
# if __name__ =='__main__':
#     env = gym.make("Breakout-v0")
#     # env = gym.make('Space_cannons:SpaceCannon-v1')
    
#     env = FramestackingENV(env, 480, 640)

#     # print(env.observation_space)
#     # print(env.action_space)

#     im = env.reset()
#     ims = []
#     idx = 0
#     for i in range(im.shape[-1]):
#         ims.append(im[:, :, i])
#     cv2.imwrite(f"C:/Programming/rl_cooperation/DQN_breakout/{idx}.jpg", np.hstack(ims))

#     env.step([randint(0, 4), randint(0,4)])

#     for i in range(10):
#         idx+=1
#         # im, _, _, _ = env.step(randint(0, 3))
#         im, _, _, _ = env.step([randint(0, 4), randint(0,4)])
#         ims = []
#         for i in range(im.shape[-1]):
#             ims.append(im[:, :, i])
#         cv2.imwrite(f"C:/Programming/rl_cooperation/DQN_breakout/{idx}.jpg", np.hstack(ims))