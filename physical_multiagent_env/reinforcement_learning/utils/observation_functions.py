import numpy as np 
from gym.spaces import Discrete, Box, Dict


class Observation_1:
    def __init__(self, num_targets):

        self.observation_space = {f'target_relative_position_{i}': Box(low=-np.inf, high=np.inf, shape=(3,)) for i in range(num_targets)}
        self.observation_space.update({f'target_relative_velocity_{i}': Box(low=-np.inf, high=np.inf, shape=(3,)) for i in range(num_targets)})
        self.observation_space.update({'obstacle_observation' :Box(low=-np.inf, high=np.inf, shape=(4,4))})
        self.observation_space = Dict(self.observation_space)

    def observation_fn_1(agent_obs, test_env=None, **kw):
        env= test_env if test_env else kw['worker'].env
        new_obs = {a:{} for a in agent_obs.keys()}

        for a in agent_obs.keys():
            agent = env.objects['agent'][a]
            for i, target in enumerate(env.objects['target']):
                new_obs[a][f'target_relative_position_{i}'] = clipping(agent.relative_position(target), 4)
                new_obs[a][f'target_relative_velocity_{i}'] = clipping(agent.relative_velocity(target), 4)
                new_obs[a]['obstacle_observation'] = np.zeros((4,4)) # relative position and dangerous_degree

                for obj_type, obj_list in env.objects.items():
                    for obj in obj_list:
                        distance = agent.distance(obj)
                        if distance < 2:
                            position = np.ceil(agent.relative_position(obj)-2)+1
                            position = position.astype(int)
                            velocity = agent.relative_velocity(obj)
                            dg = dangerous_degree(position, velocity, obj.globalScaling)
                            
                            new_obs[a]['obstacle_observation'][position[0], position[1]] =   max(new_obs[a]['obstacle_observation'][position[0], position[1]] , dg)
                            #new_obs[a]['4x4_observation'][position[0], position[1],:] = agent.relative_velocity(obj)

        return new_obs


def dangerous_degree(position, velocity, globalScaling):
    return np.dot(-position, velocity) * globalScaling

def clipping(x, maximum):
    if np.linalg.norm(x) > maximum:
        x = x * maximum / np.linalg.norm(x)
    return x

def log_scaling(x):
    norm = np.linalg.norm(x)
    if norm>1:
        x = x / norm * np.log(norm)    
    return x 