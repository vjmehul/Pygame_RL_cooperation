import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append('../../../')
sys.path.append(dir_path)
sys.path.append('.')

import torch
import torch.nn as nn
import torch.nn.functional as F
import gym
from dataclasses import dataclass
from typing import Any
from random import sample
import wandb
from tqdm import tqdm
import numpy as np
from random import random
from Pygame_RL_cooperation.Parameters import Parameters_DQN as c
from models import ConvModel
from utils import FramestackingENV
from replay_memory import ReplayBuffer
import warnings
warnings.filterwarnings('ignore')

# create a dataclass for experience replay
@dataclass
class SARSD:
    state: Any
    action: int
    reward:float
    next_state: Any
    done: bool


def update_tgt_model(m, tgt):
    tgt.load_state_dict(m.state_dict())


# # Create huber loss function
# def l1_loss_smooth(q_state_action, q_targets, beta = 1.0):
#     loss = 0
#     diff = q_state_action-q_targets
#     x = (diff.abs() < beta)
#     loss += x * (0.5*diff**2 / beta)
#     loss += (~x) * (diff.abs() - 0.5*beta)
#     return loss.mean()

def train_step(model, state_transition, tgt, num_actions, device):

    # PreProcess the sampled data from replay memory then stack them and assign them some variable
    cur_states = torch.stack([torch.Tensor(s.state) for s in state_transition[0]]).to(device)
    rewards = torch.stack([torch.Tensor([s.reward]) for s in state_transition[0]]).to(device)
    mask = torch.stack([torch.Tensor([0]) if s.done else torch.Tensor([1]) for s in state_transition[0]]).to(device)
    next_states = torch.stack([torch.Tensor(s.next_state) for s in state_transition[0]]).to(device)
    actions = [s.action for s in state_transition[0]]
    importance = [s for s in state_transition[1]]

    # we dont need gradient update for target network
    with torch.no_grad():
        qvals_next = tgt(next_states).max(-1)[0]

    # but we update the original network
    model.opt.zero_grad()
    qvals =  model(cur_states)

    # One hot encode all the actions from the stacked variable
    one_hot_actions=F.one_hot(torch.LongTensor(actions), num_actions).to(device)


    #calculate state action
    q_state_action = torch.sum(qvals * one_hot_actions, -1)

    # calculate q_target_in with decay of 0.99
    q_target_in = rewards.squeeze() + mask[:, 0] * qvals_next * 0.99  # 0.99 is discount factor

    #calculate error
    error = q_state_action - q_target_in  # calculate TD ERROR
    loss_fn = nn.SmoothL1Loss()
    
    loss = loss_fn(q_state_action,q_target_in)

    loss = loss  *  torch.cuda.FloatTensor(importance)

    loss=loss.mean()

    # backpropogate
    loss.backward()
    model.opt.step()

    return loss, error

def run_test_episode(model1, model2, env,device='cuda'):
    frames = []
    obs = env.reset()
    frames.append(env.frame)
    done= False
    reward1 = 0
    reward2 = 0
    while not done:
        action1 = model1(torch.Tensor(obs).to(device).unsqueeze(0)).max(-1)[-1].item()
        action2 = model2(torch.Tensor(obs).to(device).unsqueeze(0)).max(-1)[-1].item()
        obs, r, done, _ = env.step([action1,action2])

        reward1 += r[0]
        reward2 += r[1]
        frames.append(env.frame)
        # env.render(mode = 'rgb_array')

    return reward1, reward2,  np.stack(frames, 0)


def main(test=False, chkpt=None, device = 'cuda', boltzmann_expo = True):

    #initialize wandb
    if not test:
         wandb.init(project="dqn-tutorial", name="dqn-SpaceCannons_PER_0.1")

    #define desired input shape for the model from environment
    input_shape = c.inputshape


    #Intiate learning environment
    env = gym.make("SpaceCannons:SpaceCannons-v2")
    env = FramestackingENV(env, input_shape[0], input_shape[1], input_shape[2])

    #Initiate testing environment
    env_test = gym.make("SpaceCannons:SpaceCannons-v2")
    env_test = FramestackingENV(env_test, input_shape[0], input_shape[1], input_shape[2])

    #reset training environment and extract the last observation
    last_observation = env.reset()


    # training hyperparameter for epsilon
    eps_max=c.eps_max
    eps_min=c.eps_min
    eps=eps_max
    eps_decay=c.eps_decay

    #replay buffer parameters
    min_rb_size=c.replay_size_PER   #minimum replay size
    sample_size= c.sample_size  #sample size from replay buffer

    env_steps_before_train = c.env_steps_before_train  # number of steps to skip before we train the model
    steps_since_train=c.steps_since_train              # Counter to find how many steps has been passed before the last ORIGINAL model update
    tgt_model_update = c.tgt_model_update              # target model update frequency
    epochs_since_tgt = c.epochs_since_tgt              # Counter to find how many steps has been passed before the last TARGET model update
    print("min_rb_size", min_rb_size)
    print("sample_size", sample_size)
    print("env_steps_before_train(number of steps to skip before we train the model)", env_steps_before_train)
    print("tgt_model_update(target model update frequency)", tgt_model_update)
    print("Boltzmann flag: ",boltzmann_expo)
    # counters to calculate rewards
    episode_reward1=[]
    rolling_reward1=0

    episode_reward2=[]
    rolling_reward2=0

    A1_kill_miniboss=0
    A2_kill_miniboss=0
    A1_kill_mini =0
    A2_kill_mini=0
    coop_kill_mini=0
    coop_kill_miniboss=0
    evasive_count_miniboss = 0
    evasive_count_mini = 0
    tot_evasive_count=0

    A1_kills=0
    A2_kills=0
    Tot_Bullet_penalty = 0
    Tot_bullet_penalty_1 = 0
    Tot_bullet_penalty_2 = 0
    Game_num=0

    # define convolution model  "Agent 1"
    m1 = ConvModel(env.observation_space.shape, 4, lr = c.lr).to(device)


    # Initiate target model    "Agent 1"
    if not test:
        tgt1 =ConvModel(env.observation_space.shape, 4).to(device)
        update_tgt_model(m1,tgt1)


    # define convolution model  "Agent 2"
    m2 = ConvModel(env.observation_space.shape, 4, lr = c.lr).to(device)


    # Initiate target model    "Agent 2"
    if not test:
        tgt2 =ConvModel(env.observation_space.shape,4).to(device)
        update_tgt_model(m2,tgt2)





    # if we are testing the model define path to extract the model parameters
    if chkpt is not None:
        m1.load_state_dict(torch.load(chkpt[0]))
        m1.load_state_dict(torch.load(chkpt[1]))

    # Initiate replay buffer agent 1
    rb1 = ReplayBuffer()
    # Initiate replay buffer agent 1
    rb2 = ReplayBuffer()

    step_num = -1*min_rb_size

    tq=tqdm()
    try:
        while Game_num!=1000:
            tq.update(1)  # time and performance statistics

            #test rendering
            if test:
                env.render()

            # calculate epsilon
            if not eps == 0:
                eps=eps_decay**(step_num)
            else:
                eps = c.eps_min

            # no exploration during testing
            if test:
                eps=0
            if boltzmann_expo ==True:
                 logits1 = m1(torch.Tensor(last_observation).to(device).unsqueeze(0))[0]
                 logits2 = m2(torch.Tensor(last_observation).to(device).unsqueeze(0))[0]
                 action1 = torch.distributions.Categorical(logits=logits1).sample().item()
                 action2 = torch.distributions.Categorical(logits=logits2).sample().item()
            else:
                # derive actions either randomly of from model "Agent 1" and "Agent 2"
                if random() <eps:
                    action1 = env.action_space[0].sample()
                    action2 = env.action_space[1].sample()
                else:
                    action1 = m1(torch.Tensor(last_observation).to(device).unsqueeze(0)).max(-1)[-1].item()
                    action2 = m2(torch.Tensor(last_observation).to(device).unsqueeze(0)).max(-1)[-1].item()

            # run the actions on the model
            observation, reward, done, info = env.step([action1,action2])


                
            #accumulate rewards
            rolling_reward1 += reward[0]
            rolling_reward2 += reward[1]

            A1_kill_miniboss += info['A1_kill_miniboss']
            A2_kill_miniboss += info['A2_kill_miniboss']
            A1_kill_mini += info['A1_kill_mini']
            A2_kill_mini += info['A2_kill_mini']
            A1_kills += info['A1_kills']
            A2_kills += info['A2_kills']

            evasive_count_miniboss  +=  info['evasive_count_miniboss']
            evasive_count_mini  +=  info['evasive_count_mini']
            tot_evasive_count += info['evasive_count_mini'] + info['evasive_count_miniboss']


            coop_kill_mini += info['coop_kill_mini']
            coop_kill_miniboss += info['coop_kill_miniboss']

            Tot_Bullet_penalty += info['Tot_Bullet_penalty']
            Tot_bullet_penalty_1 += info['Tot_bullet_penalty_1']
            Tot_bullet_penalty_2 += info['Tot_bullet_penalty_2']

            # Update replaybuffer Agent 1
            rb1.insert(SARSD(last_observation, action1, reward[0], observation, done))

            # Update replaybuffer Agent 2
            rb2.insert(SARSD(last_observation, action2, reward[1], observation, done))


            # update observations
            last_observation = observation


            # reset environment after dones and reinitiate rewards
            if done:
                episode_reward1.append(rolling_reward1)
                rolling_reward1=0
                episode_reward2.append(rolling_reward2)
                rolling_reward2=0
                observation = env.reset()
                Game_num+=1
                A1_kill_miniboss=0
                A2_kill_miniboss=0
                A1_kill_mini =0
                A2_kill_mini=0

                coop_kill_mini=0
                coop_kill_miniboss=0

                evasive_count_miniboss = 0
                evasive_count_mini = 0
                tot_evasive_count=0

                A1_kills=0
                A2_kills=0
                Tot_Bullet_penalty = 0
                Tot_bullet_penalty_1 = 0
                Tot_bullet_penalty_2 = 0

                if test:
                    print("Reward1,Reward2", [rolling_reward1,rolling_reward2])

            #Increment counters
            steps_since_train +=1
            step_num+=1


            if (not test) and len(rb1.buffer)>=min_rb_size and steps_since_train > env_steps_before_train: # condition to check if we should update our model or not

                # on update!! increment counters
                epochs_since_tgt+=1

                #Sample from buffer
                A1_sample, A1_importance, A1_sample_indices = rb1.sample(sample_size)

                A2_sample, A2_importance, A2_sample_indices = rb2.sample(sample_size)

                A1_importance=A1_importance ** (1-eps)
                A2_importance=A2_importance ** (1-eps)


                # retrive loss Agent 1
                loss1, error1 =train_step(model=m1,state_transition = (A1_sample, A1_importance), tgt = tgt1, num_actions = 4, device= device)

                # retrive loss Agent 2
                loss2, error2 =train_step(model=m2,state_transition = (A2_sample, A2_importance), tgt = tgt2, num_actions = 4, device= device)


                rb1.set_priorities(indices= A1_sample_indices, errors = error1)
                rb2.set_priorities(indices= A2_sample_indices, errors = error2)


                A1_avg_reward = np.mean(episode_reward1)
                A2_avg_reward = np.mean(episode_reward2)

                # log loss1 and loss2
                wandb.log({'loss1':loss1.detach().cpu().item(),
                           'loss2':loss2.detach().cpu().item(),

                           'eps': eps,

                           'Agent1_avg_reward': A1_avg_reward,
                           'Agent2_avg_reward': A2_avg_reward,
                           'Avg_reward': (A1_avg_reward+A2_avg_reward)/2,

                           'A1_kill_miniboss':A1_kill_miniboss,
                           'A2_kill_miniboss':A2_kill_miniboss,
                           'A1_kill_mini':A1_kill_mini,
                           'A2_kill_mini':A2_kill_mini,
                           'A1_kills':A1_kills,
                           'A2_kills':A2_kills,
                           'Total_kills':A1_kills+A2_kills,


                           'evasive_count_miniboss':evasive_count_miniboss,
                           'evasive_count_mini':evasive_count_mini,
                           'tot_evasive_count':tot_evasive_count,


                           'coop_kill_mini':coop_kill_mini,
                           'coop_kill_miniboss':coop_kill_miniboss,


                           'Tot_Bullet_penalty':Tot_Bullet_penalty,
                           'Tot_bullet_penalty_1':Tot_bullet_penalty_1,
                           'Tot_bullet_penalty_2':Tot_bullet_penalty_2,
                           'game_num':Game_num
                           }, step=step_num)

            elif len(rb1.buffer)>min_rb_size:
                wandb.log({
                           'A1_kill_miniboss':A1_kill_miniboss,
                           'A2_kill_miniboss':A2_kill_miniboss,
                           'A1_kill_mini':A1_kill_mini,
                           'A2_kill_mini':A2_kill_mini,
                           'A1_kills':A1_kills,
                           'A2_kills':A2_kills,
                           'Total_kills':A1_kills+A2_kills,


                           'evasive_count_miniboss':evasive_count_miniboss,
                           'evasive_count_mini':evasive_count_mini,
                           'tot_evasive_count':tot_evasive_count,


                           'coop_kill_mini':coop_kill_mini,
                           'coop_kill_miniboss':coop_kill_miniboss,


                           'Tot_Bullet_penalty':Tot_Bullet_penalty,
                           'Tot_bullet_penalty_1':Tot_bullet_penalty_1,
                           'Tot_bullet_penalty_2':Tot_bullet_penalty_2,
                           'game_num':Game_num,

                           }, step=step_num)


                #Reinitiate train counter after training
                steps_since_train=0
            # check if we want to update target network or replace target network with online

            if epochs_since_tgt>tgt_model_update:
                # print("Updating target model")
                update_tgt_model(m1,tgt1)
                update_tgt_model(m2,tgt2)
                epochs_since_tgt=0
                # save target model after update

            # check if we need to test the model
            if step_num % c.epochs_before_test == 0:  #epochs_since_test > epochs_before_test
                if not step_num <= 0:
                    print("Testing Initiated!!!!!")
                    rew1, rew2, frames = run_test_episode(m1, m2, env_test, device=device) # if yes use the test environment
                    wandb.log(
                        {
                            'Agent1_test_reward': rew1,
                            'Agent2_test_reward': rew2,
                            'Avg_test_reward': (rew1+rew2)/2,
                            'test_video': wandb.Video(frames.transpose(0, 3, 2, 1), "Test_performance", fps = 25, format = 'mp4',)
                            }
                        )

            if step_num % c.Save_frequency == 0:
                if not step_num <= 0:
                    print("saving _models")
                    torch.save(tgt1.state_dict(),dir_path+f"/model/TAR_{step_num}_1.pth")
                    torch.save(tgt2.state_dict(),dir_path+f"/model/TAR_{step_num}_2.pth")
                    torch.save(m1.state_dict(),dir_path+f"/model/ONLINE_{step_num}_1.pth")
                    torch.save(m2.state_dict(),dir_path+f"/model/ONLINE_{step_num}_2.pth")
                    # Check if we need to save learning model????????????????????????????

    except KeyboardInterrupt:
        env.close()

if __name__=='__main__':
    main(False, boltzmann_expo = True)
    #main(True, pth) add model to test