import numpy as np 
from gym.spaces import Discrete, Box, Dict


class Observation_1:
    def __init__(self, num_targets):

        self.observation_space = {f'target_relative_position_{i}': Box(low=-np.inf, high=np.inf, shape=(3,)) for i in range(num_targets)}
        self.observation_space.update({f'target_relative_velocity_{i}': Box(low=-np.inf, high=np.inf, shape=(3,)) for i in range(num_targets)})
        self.observation_space.update({'4x4_observation' :Box(low=-np.inf, high=np.inf, shape=(4,4))})
        self.observation_space = Dict(self.observation_space)

    def observation_fn_1(agent_obs, test_env=None, **kw):
        env= test_env if test_env else kw['worker'].env
        new_obs = {a:{} for a in agent_obs.keys()}

        for a in agent_obs.keys():
            agent = env.objects['agent'][a]
            for i, target in enumerate(env.objects['target']):
                new_obs[a][f'target_relative_position_{i}'] = log_scaling(agent.relative_position(target))
                new_obs[a][f'target_relative_velocity_{i}'] = log_scaling(agent.relative_velocity(target))
                new_obs[a]['4x4_observation'] = np.zeros((4,4)) # relative position and dangerous_degree

                for obj_type, obj_list in env.objects.items():
                    for obj in obj_list:
                        distance = agent.distance(obj)
                        if distance < 2:
                            position = np.ceil(agent.relative_position(obj)-2)+1
                            position = position.astype(int)
                            dg = dangerous_degree(agent.velocity, obj.velocity, distance)
                            dg = max(new_obs[a]['4x4_observation'][position[0], position[1]], dg)
                            new_obs[a]['4x4_observation'][position[0], position[1]] = dg
                            #new_obs[a]['4x4_observation'][position[0], position[1],:] = agent.relative_velocity(obj)

        return new_obs


def dangerous_degree(v1, v2, distance):
    v1, v2 = np.array(v1), np.array(v2)
    return np.linalg.norm(1/(v1+v2+1)) * (1/(1+distance)) * (1 + np.linalg.norm(v1) + np.linalg.norm(v2))

def clipping(x, lower, upper):
    return np.clip(x, lower, upper)

def log_scaling(x):
    norm = np.linalg.norm(x)
    if norm>1:
        x = x / norm * np.log(norm)    
    return x 