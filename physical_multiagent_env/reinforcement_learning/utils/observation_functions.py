import numpy as np 
from gym.spaces import Discrete, Box, Dict


class Observation_1:
    """
    Partial obsevation with grid 2d space
    """
    def __init__(self, num_targets):

        
        self.observation_space = {f'target_relative_position_{i}': Box(low=-np.inf, high=np.inf, shape=(3,)) for i in range(num_targets)}
        self.observation_space.update({f'target_relative_velocity_{i}': Box(low=-np.inf, high=np.inf, shape=(3,)) for i in range(num_targets)})
        self.observation_space.update({'obstacle_observation' :Box(low=-np.inf, high=np.inf, shape=(8,8))})
        self.observation_space.update({"own_velocity" : Box(low=-np.inf, high=np.inf, shape=(3,))})
        self.observation_space = Dict(self.observation_space)

        self.observation_space2 = {f'target_relative_position_{i}': Box(low=-np.inf, high=np.inf, shape=(3,)) for i in range(num_targets)}
        self.observation_space2.update({f'target_relative_velocity_{i}': Box(low=-np.inf, high=np.inf, shape=(3,)) for i in range(num_targets)})
        self.observation_space2.update({'obstacle_observation' :Box(low=-np.inf, high=np.inf, shape=(10,3))})
        self.observation_space2 = Dict(self.observation_space2)

    def observation_fn_1(agent_obs, test_env=None, **kw):
        env= test_env if test_env else kw['worker'].env
        new_obs = {a:{} for a in agent_obs.keys()}

        for a in agent_obs.keys():
            agent = env.objects['agent'][a]
            new_obs[a]['own_velocity'] = clipping(np.array(agent.velocity), 4)
            for i, target in enumerate(env.objects['target']):
                new_obs[a][f'target_relative_position_{i}'] = clipping(agent.relative_position(target), 4)
                new_obs[a][f'target_relative_velocity_{i}'] = clipping(agent.relative_velocity(target), 4)
                new_obs[a]['obstacle_observation'] = np.zeros((8,8)) # relative position and dangerous_degree

            for obj in  env.objects['obstacle']:
                distance = agent.distance(obj)
                if distance < 2:
                    position = np.ceil(agent.relative_position(obj)/2-4)+1
                    position = position.astype(int)
                    new_obs[a]['obstacle_observation'][position[0], position[1]] =   1

        return new_obs

    def observation_fn_2(agent_obs, test_env=None, **kw):
        env = test_env if test_env else kw['worker'].env 
        new_obs = {a:{} for a in agent_obs.keys()}

        for a in agent_obs.keys():
            agent = env.objects['agent'][a]
            for i, target in enumerate(env.objects['target']):
                new_obs[a][f'target_relative_position_{i}'] = clipping(agent.relative_position(target), 4)
                new_obs[a][f'target_relative_velocity_{i}'] = clipping(agent.relative_velocity(target), 4)
                new_obs[a]['obstacle_observation'] = np.zeros((10,3)) # relative position and dangerous_degree

            count = 0
            all_distance = [(agent.distance(obj), i) for i, obj in enumerate(env.objects['obstacle'])]
            all_distance.sort(key=lambda x:x[0])
            for d, i in all_distance:
                if d > 4 or count > 9:
                    break 
                new_obs[a]['obstacle_observation'][count,:] = agent.relative_position(env.objects['obstacle'][i])
                count +=1

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