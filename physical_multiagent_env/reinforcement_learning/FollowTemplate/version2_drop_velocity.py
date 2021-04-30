import json
import argparse 
import pybullet as p 
import time 
import numpy as np 

import ray 
from ray.tune.registry import register_env 
from ray import tune
from ray.rllib.agents.callbacks import DefaultCallbacks
from ray.rllib.policy.sample_batch import SampleBatch 
from ray.rllib.models import ModelCatalog 
from gym.spaces import Discrete, Box, Dict 
from ray.rllib.env.multi_agent_env import MultiAgentEnv  
from ray.rllib.agents.ppo import PPOTrainer
from ray.rllib.agents.dqn import DQNTrainer

from physical_multiagent_env.scenarios.FollowTemplate.scenario import FollowTemplate
from physical_multiagent_env.utils.observation_functions import Observation_CNN


class FollowTemplateRay(FollowTemplate, MultiAgentEnv):
    def __init__(self, config={}):
        super().__init__(config)


def on_train_result(info):
    result = info["result"]
    env_config = result['config']['env_config']
    trainer = info["trainer"]
    c = env_config['curriculum_learning']
    return 

    if True : 
        #phase = min(  env.phase+1, 3)
        phase = np.random.randint(3)+1
        trainer.workers.foreach_worker(
            lambda ev: ev.foreach_env(
                lambda env: env.set_phase(phase = phase)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--checkpoint", type=str)
    args = parser.parse_args()

    with open("version2.json") as f :
        general_config = json.load(f)
        rllib_config = general_config['rllib_config']
        env_config = general_config['env_config']

    ray.init()
    register_env("FollowTemplateRay", lambda config:FollowTemplateRay(config))

    observation = Observation_CNN(num_targets=1, size=100, observation_range=10)
    config = {
        "env" : "FollowTemplateRay",
        "num_workers" : rllib_config['num_workers']  ,
        "num_gpus": rllib_config['num_gpus'] ,
        "env_config": env_config,
        "multiagent":{
            "policies":{
                f"pol" : (None, observation.observation_space, Discrete(5) , {}) 
            },
            "policy_mapping_fn": lambda i : "pol",
            "policies_to_train":["pol"],
            "observation_fn" : Observation_CNN.observation_fn_2
        },
        'framework' : rllib_config['framework'],
        "callbacks":{"on_train_result":on_train_result}
    }

    if not args.test:
        if args.resume:
            checkpoint = args.checkpoint 

        from ray.tune import grid_search
        config['env_config']['phase'] = grid_search([i+1 for i in range(9)])

        analysis = tune.run(rllib_config['model'],
                            config=config,
                            stop=rllib_config['stop'],
                            checkpoint_freq = rllib_config['checkpoint_freq'],
                            checkpoint_at_end=True,
                            local_dir = rllib_config['local_dir'],
                            name = rllib_config['name'],
                            restore= checkpoint if args.resume else None
                    )    
    else:
        if rllib_config['model'] == "PPO":
            agent = PPOTrainer(config=config, env=FollowTemplateRay)
        elif rllib_config['model'] == "DQN":
            agent = DQNTrainer(config=config, env=FollowTemplateRay)
        else:
            raise ValueError()

        agent.restore(args.checkpoint)

        # config['env_config']['map_size'] = 3
        config['env_config']["connect"] =p.GUI

        env = FollowTemplateRay(config['env_config'])
        
        Reward = [] 
        for i in range(50):
            obs = env.reset()
            done = env.done
            count = 0
            Reward.append(0)
            while not done["__all__"]:
                # if count==0:
                #     time.sleep(5)
                alive_agents = [k for k,v in done.items() if v==False]
                obs = Observation_CNN.observation_fn_2(obs, env, test_config={"size":80, "observation_range":10})
                actions =  {i:agent.compute_action(obs[i], policy_id=f"pol") 
                                        for i in alive_agents if i!="__all__"}
                obs, reward, done, info = env.step(actions)
                time.sleep(0.001)
                count += 1
                Reward[-1] += sum(reward.values())/len(reward.values())
            print(i,  Reward[-1])
        print(np.mean(Reward), np.std(Reward))
    
    
    