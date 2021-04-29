import json
import argparse 
import pybullet as p 
import time 

import ray 
from ray.tune.registry import register_env 
from ray import tune
from ray.rllib.agents.callbacks import DefaultCallbacks
from ray.rllib.policy.sample_batch import SampleBatch 
from ray.rllib.models import ModelCatalog 
from gym.spaces import Discrete, Box, Dict 
from ray.rllib.env.multi_agent_env import MultiAgentEnv  
from ray.rllib.agents.ppo import PPOTrainer

from physical_multiagent_env.scenarios.FollowAvoid.scenario import FollowAvoid
from physical_multiagent_env.reinforcement_learning.utils.observation_functions import Observation_CNN



# -----------------------------------------
# Train With Ray  : you must inherit MultiAgentEnv to train with ray 
#
#       CNN architecture Networks
from ray.rllib.models.torch.visionnet import VisionNetwork
from ray.rllib.models import ModelCatalog
ModelCatalog.register_custom_model("visionnet", VisionNetwork)
# -----------------------------------------

class FollowAvoidRay(FollowAvoid, MultiAgentEnv):
    def __init__(self, config={}):
        super().__init__(config)

def on_train_result(info):
    result = info["result"]
    env_config = result['config']['env_config']
    trainer = info["trainer"]

    training_iteration =  1000

    # curriculum : [obstacle, training_iteration]
    curriculum = [[[10], [0]], 
                  [[i for i  in range(1, 11)], [i for i in range(10)]], 
                  [[1, 5, 10], [0, 300, 600]]]

    c = env_config['curriculum_learning']

    for obstacle, iteration in zip(curriculum[c][0], curriculum[c][1]):
        if result['training_iteration'] > iteration:
            trainer.workers.foreach_worker(
                lambda ev: ev.foreach_env(
                    lambda env: env.set_phase(num_obstacles=obstacle)))

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
    register_env("FollowAvoidRay", lambda config:FollowAvoidRay(config))

    observation = Observation_CNN(num_targets=1, size=42, observation_range=3)
    config = {
        "env" : "FollowAvoidRay",
        "num_workers" : rllib_config['num_workers']  ,
        "num_gpus": rllib_config['num_gpus'] ,
        "env_config": env_config,
        "model" : rllib_config['model'],
        "multiagent":{
            "policies":{
                f"pol" : (None, observation.observation_space, Discrete(5) , {}) 
            },
            "policy_mapping_fn": lambda i : "pol",
            "policies_to_train":["pol"],
            "observation_fn" : Observation_CNN.observation_fn_1
        },
        'framework' : rllib_config['framework'],
        "callbacks":{"on_train_result":on_train_result}
    }

    config['env_config']['pybullet_timestep'] =  tune.grid_search([0.001, 0.01, 0.1, 1.0]) 

    if not args.test:
        if args.resume:
            checkpoint = args.checkpoint 

        analysis = tune.run(rllib_config['policy'],
                            config=config,
                            stop=rllib_config['stop'],
                            checkpoint_freq = rllib_config['checkpoint_freq'],
                            local_dir = rllib_config['local_dir'],
                            name = rllib_config['name'],
                            restore= checkpoint if args.resume else None
                    )    
    else:
        agent = PPOTrainer(config=config, env=FollowAvoidRay)
        agent.restore(args.checkpoint)

        # config['env_config']['map_size'] = 3
        config['env_config']["connect"] =p.GUI

        env = FollowAvoidRay(config['env_config'])
        obs = env.reset()
        done = env.done
        count = 0  
        while True:#not done["__all__"]:
            if count==0:
                time.sleep(5)
            alive_agents = [k for k,v in done.items() if v==False]
            obs = Observation_1.observation_fn_1(obs, env)
            actions =  {i:agent.compute_action(obs[i], policy_id=f"pol") 
                                    for i in alive_agents if i!="__all__"}
            obs, reward, done, info = env.step(actions)
            time.sleep(0.001)
            count += 1
    
    
    