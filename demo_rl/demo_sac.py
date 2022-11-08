import sys
sys.path.append(".")
sys.path.append("..")
import os
import time

import numpy as np
import gym
from torch.utils.tensorboard import SummaryWriter

from rllib.algorithms.sac import SAC


np.random.seed(20)


def train(
    env: gym.Env, agent: SAC, num_episode: int, time_step: int, update_freq: int,
    writer: SummaryWriter
):

    action_range = [env.action_space.low, env.action_space.high]
    cnt_step = 0

    for episode in range(num_episode):
        score = 0
        state = env.reset()
        for i in range(time_step):
            env.render()
            action = agent.get_action(state)
            # action output range[-1,1],expand to allowable range
            action_in =  action * (action_range[1] - action_range[0]) / 2.0 +  (action_range[1] + action_range[0]) / 2.0

            next_state, reward, done, _ = env.step(action_in)
            done_mask = 0.0 if done else 1.0
            agent.buffer.push((state, action, reward, done_mask))

            state = next_state
            score += reward
            cnt_step += 1
            if done:
                break
            if cnt_step > update_freq:
                agent.train()
                cnt_step = 0

        print("episode:{}, Return:{}, buffer_capacity:{}".format(episode, score, len(agent.buffer)))
        writer.add_scalar("score", score, episode)
        score = 0
        
    env.close()


def tensorboard_writer(env_name):
    """Generate a tensorboard writer
    """
    current_time = time.localtime()
    timestamp = time.strftime("%Y%m%d_%H%M%S", current_time)
    writer_path = "./logs/demo_sac/%s/%s/" % (env_name, timestamp)
    if not os.path.exists(writer_path):
        os.makedirs(writer_path)
    writer = SummaryWriter(writer_path)
    return writer


def SAC_pendulum():
    # Generate environment
    env_name = "Pendulum-v1"
    env = gym.make(env_name)

    # Params
    num_episode = 500
    time_step = 300
    update_freq = 500
    configs = {
        "state_space": env.observation_space,
        "action_space": env.action_space,
        "memory_size": 10000,
    }

    # Generate agent
    agent = SAC(configs)

    # Generate tensorboard writer
    writer = tensorboard_writer(env_name)

    train(env, agent, num_episode, time_step, update_freq, writer)

def SAC_hopper():
    # Generate environment
    env_name = "Hopper-v3"
    env = gym.make(env_name)

    # Params
    episode = 1500
    time_step = 1000
    update_freq = 500
    configs = {
        "state_space": env.observation_space,
        "action_space": env.action_space,
        "buffer_size": 10000,
    }

    # Generate agent
    agent = SAC(configs)

    # Generate tensorboard writer
    writer = tensorboard_writer(env_name)

    train(env, agent, episode, time_step, update_freq, writer)


if __name__ == '__main__':
    SAC_pendulum()
    # SAC_hopper()